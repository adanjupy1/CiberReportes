# build_kb.py
import json, os
import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

BASE_JSONL = "C:\\Users\\elelm\\Escritorio\\Data_Base\\5_quinto_data_set\\dataset_audio_user_final.jsonl"
REL_JSONL  = "C:\\Users\\elelm\\Escritorio\\Data_Base\\2_segundo_data_set\\dataset_consolidado_audio_relacionado.jsonl"
OUT_DIR    = "kb_out"

def read_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    base = read_jsonl(BASE_JSONL)  # content, response
    rel  = read_jsonl(REL_JSONL)   # Context, Response, Topic, Difficulty

    docs = []
    for i, r in enumerate(base):
        docs.append({"id": f"base:{i}", "source":"base", "q": r["content"], "a": r["response"],
                     "topic": None, "difficulty": None})
    for i, r in enumerate(rel):
        docs.append({"id": f"rel:{i}", "source":"rel", "q": r["Context"], "a": r["Response"],
                     "topic": r.get("Topic"), "difficulty": r.get("Difficulty")})

    model = SentenceTransformer(MODEL_NAME)
    texts = [d["q"] for d in docs]
    emb = model.encode(texts, normalize_embeddings=True, batch_size=64, show_progress_bar=True).astype("float32")

    np.save(os.path.join(OUT_DIR, "embeddings.npy"), emb)
    with open(os.path.join(OUT_DIR, "meta.json"), "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

    # centroides por Topic (solo rel)
    topic_vecs = defaultdict(list)
    for d, v in zip(docs, emb):
        if d["source"] == "rel" and d["topic"]:
            topic_vecs[d["topic"]].append(v)

    topic_centroids = {}
    for t, vecs in topic_vecs.items():
        c = np.mean(np.vstack(vecs), axis=0)
        c = c / (np.linalg.norm(c) + 1e-12)
        topic_centroids[t] = c.astype("float32").tolist()

    with open(os.path.join(OUT_DIR, "topic_centroids.json"), "w", encoding="utf-8") as f:
        json.dump(topic_centroids, f, ensure_ascii=False, indent=2)

    print("✅ KB lista en:", OUT_DIR)

if __name__ == "__main__":
    main()












