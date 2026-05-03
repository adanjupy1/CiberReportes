import os
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

CHROMA_DB_PATH  = Path("c:/xampp/htdocs/CiberReportes/proyectos_alternativos/uiibot_unified/backend_ollama/chroma_db")
COLLECTION_NAME = "ciberseg_mexico"
EMBED_MODEL     = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

print(f"Probando RAG desde: {CHROMA_DB_PATH}")

client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
collection = client.get_collection(COLLECTION_NAME)
embedder = SentenceTransformer(EMBED_MODEL)

queries = [
    "Recibi un SMS del SAT",
    "derechos ARCO",
    "ransomware pymes",
    "policia cibernetica"
]

for q in queries:
    print(f"\nQuery: {q}")
    emb = embedder.encode(q).tolist()
    res = collection.query(query_embeddings=[emb], n_results=3, include=["distances", "documents"])
    dists = res["distances"][0]
    docs = res["documents"][0]
    for d, doc in zip(dists, docs):
        print(f"  Dist: {d:.4f} | Doc: {doc[:50]}...")
