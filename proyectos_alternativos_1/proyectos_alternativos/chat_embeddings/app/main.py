# -*- coding: utf-8 -*-
"""
API FastAPI – Chat de Ciberseguridad con embeddings BGE-M3
Puerto: 8004
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from pathlib import Path
from dotenv import load_dotenv

from .embedding_engine import EmbeddingEngine

# ── Configuración ─────────────────────────────────────────────────
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

SERVER_URL = os.getenv("SERVER_URL", "https://localhost")
API_PORT = os.getenv("API_PORT_EMBED", "8004")
EMBED_MODEL = os.getenv("EMBED_MODEL_CHAT", "BAAI/bge-m3")
BASE_THRESHOLD = float(os.getenv("BASE_THRESHOLD_CHAT", "0.55"))
REL_THRESHOLD = float(os.getenv("REL_THRESHOLD_CHAT", "0.78"))
DEDUP_THRESHOLD = float(os.getenv("DEDUP_THRESHOLD_CHAT", "0.92"))

DATA_DIR = str(Path(__file__).parent.parent / "data_base")

# ── FastAPI app ───────────────────────────────────────────────────
app = FastAPI(
    title="Chat Ciberseguridad – Embeddings BGE-M3",
    version="2.0.0",
    description="Chat semántico de ciberseguridad con BAAI/bge-m3",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Motor ─────────────────────────────────────────────────────────
engine = EmbeddingEngine(
    data_dir=DATA_DIR,
    model_name=EMBED_MODEL,
    base_threshold=BASE_THRESHOLD,
    rel_threshold=REL_THRESHOLD,
    dedup_threshold=DEDUP_THRESHOLD,
)

# ── Sesiones ──────────────────────────────────────────────────────
sessions: dict = {}

# ── Modelos Pydantic ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="ID de sesión único")
    message: str = Field(..., description="Mensaje del usuario")


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    score: float = 0.0
    tematica: str = ""
    pregunta_match: str = ""
    suggestions: list[dict] = []
    source: str = "embeddings"


# ── Helpers ───────────────────────────────────────────────────────
SALUDO_KEYWORDS = {
    "hola", "buenas", "buen dia", "buenos dias", "que tal",
    "hey", "hi", "hello", "menu", "inicio", "start",
}

WELCOME_TEXT = (
    "🛡️ <strong>Chat de Ciberseguridad</strong>\n\n"
    "Puedo ayudarte con temas como:\n"
    "• Contraseñas y autenticación\n"
    "• Amenazas y ataques\n"
    "• Fraudes y compras en línea\n"
    "• Redes, privacidad y dispositivos\n"
    "• Protección y buenas prácticas\n"
    "• Menores y legislación digital\n\n"
    "Escribe tu pregunta sobre ciberseguridad."
)

NO_MATCH_TEXT = (
    "🤔 No encontré una respuesta para tu consulta.\n\n"
    "Intenta reformular tu pregunta o consulta sobre alguno de estos temas:\n"
    "• Contraseñas seguras\n"
    "• Phishing y fraudes\n"
    "• Protección de dispositivos\n"
    "• Privacidad en redes"
)


def _is_greeting(text: str) -> bool:
    normalized = text.lower().replace("á", "a").replace("é", "e") \
                     .replace("í", "i").replace("ó", "o").replace("ú", "u")
    words = set(normalized.split())
    if len(words) > 4:
        return False
    return bool(words & SALUDO_KEYWORDS)


# ── Endpoints ─────────────────────────────────────────────────────

@app.get("/health")
def health():
    stats = engine.stats()
    return {
        "ok": True,
        **stats,
        "config": {
            "server_url": SERVER_URL,
            "api_port": API_PORT,
        },
    }


@app.get("/api/topics")
def topics():
    """Lista de temáticas con conteo."""
    return engine.get_topics()


@app.get("/api/stats")
def stats():
    """Estadísticas del motor."""
    return engine.stats()


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Chat semántico con búsqueda por embeddings."""
    text = req.message.strip()

    if req.session_id not in sessions:
        sessions[req.session_id] = {"history": []}

    session = sessions[req.session_id]
    session["history"].append({"role": "user", "content": text})

    # Saludo / menú
    if _is_greeting(text):
        session["history"].append({"role": "bot", "content": WELCOME_TEXT})
        topic_names = [t["tematica"] for t in engine.get_topics()]
        return ChatResponse(
            session_id=req.session_id,
            reply=WELCOME_TEXT,
            suggestions=[{"pregunta": t, "tematica": "temática", "score": 1.0}
                         for t in topic_names],
            source="menu",
        )

    # Búsqueda semántica
    best = engine.get_best_match(text)

    if best:
        suggestions_raw = engine.get_suggestions(text, top_k=3)
        # Quitar la pregunta principal de las sugerencias
        suggestions = [s for s in suggestions_raw
                       if s["pregunta"] != best.pregunta]

        reply = best.respuesta
        session["history"].append({"role": "bot", "content": reply})

        return ChatResponse(
            session_id=req.session_id,
            reply=reply,
            score=best.score,
            tematica=best.tematica,
            pregunta_match=best.pregunta,
            suggestions=suggestions[:3],
            source="embeddings",
        )

    # Sin coincidencia
    session["history"].append({"role": "bot", "content": NO_MATCH_TEXT})
    return ChatResponse(
        session_id=req.session_id,
        reply=NO_MATCH_TEXT,
        source="no_match",
    )


@app.delete("/api/session/{session_id}")
def delete_session(session_id: str):
    """Elimina una sesión."""
    if session_id in sessions:
        del sessions[session_id]
        return {"ok": True, "message": "Sesión eliminada"}
    return {"ok": False, "message": "Sesión no encontrada"}
