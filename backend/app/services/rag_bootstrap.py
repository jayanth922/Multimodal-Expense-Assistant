from pathlib import Path
from datetime import datetime
from hashlib import md5
from .rag import add_documents, reset_index, collection_count

def ensure_seed() -> bool:
    # If the index already has docs, skip
    if collection_count() > 0:
        return False
    base = Path("rag/data")
    docs = []
    for p in base.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        docs.append({
            "id": md5((p.name + str(len(text))).encode()).hexdigest(),
            "text": text,
            "metadata": {"source": str(p), "title": p.stem, "ingested_at": datetime.utcnow().isoformat()}
        })
    reset_index()
    add_documents(docs)
    return True