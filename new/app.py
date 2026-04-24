import os
import json
import time
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv
load_dotenv()  # carga variables desde .env

import numpy as np
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, Field
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer

# =========================
# Config
# =========================
MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
KB_DIR = os.getenv("KB_DIR", "kb_out")

BASE_THRESHOLD_DEFAULT = float(os.getenv("BASE_THRESHOLD", "0.85"))
REL_THRESHOLD_DEFAULT  = float(os.getenv("REL_THRESHOLD", "0.82"))

# Protege /reload-kb con un token simple (ponlo en variable de entorno)
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "")  # ejemplo: setx ADMIN_TOKEN "mi_token_super"

# =========================
# Globals (carga única)
# =========================
app = FastAPI(title="Chat Retrieval API (MiniLM CPU)")

model: Optional[SentenceTransformer] = None
emb: Optional[np.ndarray] = None
meta: Optional[List[Dict[str, Any]]] = None
topic_centroids: Dict[str, np.ndarray] = {}

base_idx: List[int] = []
rel_idx: List[int] = []
base_questions: List[tuple] = []  # (idx, question)

# =========================
# Schemas
# =========================
class AskRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(3, ge=1, le=10)
    min_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    include_related: bool = True

    session_id: Optional[str] = None
    user_id: Optional[str] = None

class Hit(BaseModel):
    q: str
    score: float
    source: str
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    id: Optional[str] = None

class AskResponse(BaseModel):
    answer: str
    score: float
    source: str
    id: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    related: List[Hit] = []

class SuggestRequest(BaseModel):
    query: str = Field(..., min_length=1)
    k: int = Field(5, ge=1, le=15)

class SuggestResponse(BaseModel):
    suggestions: List[Hit]

class FeedbackRequest(BaseModel):
    query: str
    answer_id: Optional[str] = None
    helpful: bool
    notes: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None

# =========================
# Helpers
# =========================
def _load_kb():
    global emb, meta, topic_centroids, base_idx, rel_idx, base_questions

    emb_path = os.path.join(KB_DIR, "embeddings.npy")
    meta_path = os.path.join(KB_DIR, "meta.json")
    cent_path = os.path.join(KB_DIR, "topic_centroids.json")

    if not (os.path.exists(emb_path) and os.path.exists(meta_path)):
        raise RuntimeError(f"No encuentro KB en {KB_DIR}. Falta embeddings.npy o meta.json")

    emb = np.load(emb_path).astype("float32")

    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    topic_centroids = {}
    if os.path.exists(cent_path):
        with open(cent_path, "r", encoding="utf-8") as f:
            cent = json.load(f)
        topic_centroids = {k: np.array(v, dtype="float32") for k, v in cent.items()}

    base_idx = [i for i, d in enumerate(meta) if d.get("source") == "base"]
    rel_idx  = [i for i, d in enumerate(meta) if d.get("source") == "rel"]
    base_questions = [(i, meta[i]["q"]) for i in base_idx]

def _load_model():
    global model
    model = SentenceTransformer(MODEL_NAME)

def _topk_cosine(query_vec: np.ndarray, idx_list: List[int], k: int):
    # emb ya normalizado => cosine = dot
    scores = emb[idx_list] @ query_vec
    top = np.argsort(-scores)[:k]
    return [(idx_list[i], float(scores[i])) for i in top]

def _predict_topic(query_vec: np.ndarray):
    if not topic_centroids:
        return None, 0.0
    topics = list(topic_centroids.keys())
    C = np.vstack([topic_centroids[t] for t in topics])
    scores = C @ query_vec
    j = int(np.argmax(scores))
    return topics[j], float(scores[j])

def _hit_to_model(i: int, score: float) -> Hit:
    d = meta[i]
    return Hit(
        q=d["q"],
        score=score,
        source=d.get("source", ""),
        topic=d.get("topic"),
        difficulty=d.get("difficulty"),
        id=d.get("id"),
    )

# =========================
# Startup
# =========================
@app.on_event("startup")
def startup_event():
    _load_model()
    _load_kb()

# =========================
# Endpoints
# =========================
@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL_NAME,
        "kb_loaded": emb is not None and meta is not None,
        "base_items": len(base_idx),
        "rel_items": len(rel_idx),
    }

@app.get("/topics")
def topics():
    # Solo topics disponibles
    ts = sorted({d.get("topic") for d in meta if d.get("source") == "rel" and d.get("topic")})
    return {"topics": ts}

@app.post("/reload-kb")
def reload_kb(authorization: Optional[str] = Header(None)):
    # Authorization: Bearer <token>
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="ADMIN_TOKEN no configurado en el servidor.")
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Falta Authorization: Bearer <token>")
    token = authorization.split(" ", 1)[1].strip()
    if token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Token inválido")

    _load_kb()
    return {"status": "reloaded", "kb_dir": KB_DIR, "base_items": len(base_idx), "rel_items": len(rel_idx)}

@app.post("/suggest", response_model=SuggestResponse)
def suggest(req: SuggestRequest):
    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="query vacío")

    qv = model.encode([q], normalize_embeddings=True)[0].astype("float32")
    hits = _topk_cosine(qv, base_idx + rel_idx, k=req.k)
    return SuggestResponse(suggestions=[_hit_to_model(i, s) for i, s in hits])

@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    t0 = time.time()
    q = req.query.strip()
    if not q:
        raise HTTPException(status_code=400, detail="query vacío")

    # Umbral: si el usuario no manda min_score, usamos defaults
    min_score = req.min_score
    base_thr = min_score if min_score is not None else BASE_THRESHOLD_DEFAULT
    rel_thr  = min_score if min_score is not None else REL_THRESHOLD_DEFAULT

    # 0) Fuzzy exact (barato) sobre base
    best_fuzzy = None
    for i, bq in base_questions:
        sc = fuzz.token_set_ratio(q, bq)
        if best_fuzzy is None or sc > best_fuzzy[1]:
            best_fuzzy = (i, sc)

    if best_fuzzy and best_fuzzy[1] >= 95:
        d = meta[best_fuzzy[0]]
        related = []
        if req.include_related:
            qv = model.encode([q], normalize_embeddings=True)[0].astype("float32")
            rel_hits = _topk_cosine(qv, rel_idx, k=req.top_k)
            related = [_hit_to_model(i, s) for i, s in rel_hits]

        return AskResponse(
            answer=d["a"],
            score=1.0,
            source="base",
            id=d.get("id"),
            topic=None,
            difficulty=None,
            related=related,
        )

    # 1) Embedding
    qv = model.encode([q], normalize_embeddings=True)[0].astype("float32")

    # 2) Search base principal
    base_hits = _topk_cosine(qv, base_idx, k=req.top_k)
    best_base_i, best_base_s = base_hits[0]

    if best_base_s >= base_thr:
        d = meta[best_base_i]
        related = []
        if req.include_related:
            rel_hits = _topk_cosine(qv, rel_idx, k=req.top_k)
            related = [_hit_to_model(i, s) for i, s in rel_hits]

        return AskResponse(
            answer=d["a"],
            score=best_base_s,
            source="base",
            id=d.get("id"),
            topic=None,
            difficulty=None,
            related=related,
        )

    # 3) Fallback: Topic routing + búsqueda en sub-base
    topic, _ts = _predict_topic(qv)
    rel_filtered = rel_idx
    if topic:
        tf = [i for i in rel_idx if meta[i].get("topic") == topic]
        rel_filtered = tf if tf else rel_idx

    rel_hits = _topk_cosine(qv, rel_filtered, k=req.top_k)
    best_rel_i, best_rel_s = rel_hits[0]

    if best_rel_s >= rel_thr:
        d = meta[best_rel_i]
        return AskResponse(
            answer=d["a"],
            score=best_rel_s,
            source="rel",
            id=d.get("id"),
            topic=d.get("topic"),
            difficulty=d.get("difficulty"),
            related=[],
        )

    # 4) No match: devuelve sugerencias en related y un mensaje seguro
    suggestions = [_hit_to_model(i, s) for i, s in rel_hits]
    latency_ms = int((time.time() - t0) * 1000)
    return AskResponse(
        answer=f"No encontré una respuesta con suficiente confianza (latencia {latency_ms} ms). "
               f"¿Te refieres a alguna de estas opciones?",
        score=max(best_base_s, best_rel_s),
        source="none",
        related=suggestions,
    )

@app.post("/feedback")
def feedback(req: FeedbackRequest):
    # Implementación simple: append a un archivo local
    os.makedirs("logs", exist_ok=True)
    path = os.path.join("logs", "feedback.jsonl")
    record = req.model_dump()
    record["ts"] = time.time()
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return {"status": "ok"}











