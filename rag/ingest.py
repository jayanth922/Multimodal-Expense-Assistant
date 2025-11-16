from pathlib import Path
from datetime import datetime
from hashlib import md5
from app.services.rag import add_documents, reset_index

def load_docs():
    # Resolve data folder relative to THIS script, regardless of CWD
    base = Path(__file__).resolve().parent / "data"
    docs = []
    for p in base.glob("*.md"):
        text = p.read_text(encoding="utf-8")
        docs.append({
            "id": md5((p.name + str(len(text))).encode()).hexdigest(),
            "text": text,
            "metadata": {"source": str(p), "title": p.stem, "ingested_at": datetime.utcnow().isoformat()}
        })
    return docs

if __name__ == "__main__":
    reset_index()
    docs = load_docs()
    if not docs:
        print("No docs found in rag/data. Create *.md files and re-run.")
    else:
        n = add_documents(docs)
        print(f"Ingested {n} docs.")
