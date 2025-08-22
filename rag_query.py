import os, chromadb

PERSIST_DIR = "vectorstore"
client = chromadb.PersistentClient(path=PERSIST_DIR)
collection = client.get_collection("fintech_docs")

def query_knowledge_base(query, n_results=3):
    res = collection.query(query_texts=[query], n_results=n_results, include=["documents","metadatas"])
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    out = []
    for d, m in zip(docs, metas):
        if m and m.get("source"):
            out.append(f"Source ({m.get('source')}): {d}")
        else:
            out.append(d)
    return out