from __future__ import annotations
from typing import List, Dict, Any, Optional
import os, pathlib
import chromadb
from chromadb.config import Settings as ChromaSettings

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "local").lower()
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-004")
INDEX_DIR = os.getenv("RAG_INDEX_DIR", str(pathlib.Path("rag/index").resolve()))

# --- Embeddings (unchanged from your current file) ---
if EMBEDDING_PROVIDER == "local":
    from sentence_transformers import SentenceTransformer
    _model_name = os.getenv("LOCAL_EMBED_MODEL", "all-MiniLM-L6-v2")
    _st_model = SentenceTransformer(_model_name)
    def _embed(texts: List[str]) -> List[List[float]]:
        arr = _st_model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return arr.tolist()
else:
    from google import genai
    from app.core.settings import settings
    _client_g = genai.Client(api_key=settings.GOOGLE_API_KEY)
    def _embed(texts: List[str]) -> List[List[float]]:
        res = _client_g.models.embed_content(model=EMBEDDING_MODEL, contents=texts)
        return [v.values for v in res.embeddings]

# --- Chroma setup with safe (re)creation ---
_client = chromadb.PersistentClient(path=INDEX_DIR, settings=ChromaSettings(allow_reset=True))
_collection_name = "guides"
_collection = None  # defer until first use

def _ensure_collection():
    global _collection
    if _collection is None:
        _collection = _client.get_or_create_collection(_collection_name)
    return _collection

def collection_count() -> int:
    try:
        return _collection.count()
    except Exception:
        return 0

def reset_index():
    global _collection
    try:
        _client.delete_collection(_collection_name)
    except Exception:
        pass
    _collection = None
    return _ensure_collection()

def add_documents(docs: List[Dict[str, Any]]) -> int:
    if not docs:
        return 0
    col = _ensure_collection()
    ids = [d["id"] for d in docs]
    texts = [d["text"] for d in docs]
    metas = [d.get("metadata", {}) for d in docs]
    embeds = _embed(texts)
    col.add(ids=ids, embeddings=embeds, documents=texts, metadatas=metas)
    return len(ids)

def search(query: str, k: int = 5, n_results: Optional[int] = None) -> List[Dict[str, Any]]:
    if n_results is not None:
        k = n_results
    col = _ensure_collection()
    embeds = _embed([query])[0]
    res = col.query(
        query_embeddings=[embeds],
        n_results=k,
        include=["documents", "metadatas", "distances", "ids"]
    )
    out = []
    ids = res.get("ids", [[]])[0] if res.get("ids") else []
    docs = res.get("documents", [[]])[0] if res.get("documents") else []
    metas = res.get("metadatas", [[]])[0] if res.get("metadatas") else []
    dists = res.get("distances", [[]])[0] if res.get("distances") else []
    for i in range(min(len(ids), len(docs), len(metas), len(dists))):
        out.append({
            "id": ids[i],
            "text": docs[i],
            "metadata": metas[i],
            "score": float(dists[i]),
        })
    return out
