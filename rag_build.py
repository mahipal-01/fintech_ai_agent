import os, glob
from sentence_transformers import SentenceTransformer
import chromadb

DATA_DIR = "data"
PERSIST_DIR = "vectorstore"

print("Loading local embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path=PERSIST_DIR)
# create or get collection
try:
    collection = client.get_collection("fintech_docs")
    existing = collection.get(include=["ids"]) or {}
    ids = existing.get("ids", [])
    if ids:
        collection.delete(ids=ids)
except Exception:
    collection = client.create_collection("fintech_docs")

# read txt files
docs = []
metas = []
ids = []
for fp in glob.glob(os.path.join(DATA_DIR, "*.txt")):
    with open(fp, "r", encoding="utf-8") as f:
        text = f.read()
    # naive split by double newline for chunks
    parts = [p.strip() for p in text.split("\n\n") if p.strip()]
    for i, p in enumerate(parts):
        docs.append(p)
        metas.append({"source": os.path.basename(fp)})
        ids.append(f"{os.path.basename(fp)}_{i}")

if not docs:
    print("No documents found in data/. Add .txt files and re-run.")
    raise SystemExit(1)

print(f"Creating embeddings for {len(docs)} chunks...")
embeddings = embed_model.encode(docs, show_progress_bar=True, batch_size=32)

print("Adding to Chroma... (this may take a bit)")
collection.add(documents=docs, metadatas=metas, ids=ids, embeddings=embeddings)
print("✅ Done. Vectorstore saved to", PERSIST_DIR)