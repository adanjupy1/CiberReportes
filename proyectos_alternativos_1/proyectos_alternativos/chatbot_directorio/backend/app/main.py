# -*- coding: utf-8 -*-
"""
API principal con FastAPI
Directorio de Policía Cibernética con búsqueda semántica por embeddings
Puerto: 8000
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from pathlib import Path
from dotenv import load_dotenv

from .embedding_engine import DirectoryEngine

# ── Configuración ─────────────────────────────────────────────────
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

SERVER_URL = os.getenv("SERVER_URL", "https://localhost")
API_PORT = os.getenv("API_PORT_DIRECT", "8000")
EMBED_MODEL = os.getenv("EMBED_MODEL", "intfloat/multilingual-e5-large")
BASE_THRESHOLD = float(os.getenv("BASE_THRESHOLD_DIRECT", "0.50"))

# Ruta al dataset
DATA_FILE = str(Path(__file__).parent.parent.parent / "db_direct" / "08_directorio.jsonl")

# ── FastAPI app ───────────────────────────────────────────────────
app = FastAPI(
    title="Directorio Policía Cibernética",
    version="1.0.0",
    description="Directorio telefónico de policía cibernética con búsqueda semántica",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Inicializar motor ────────────────────────────────────────────
engine = DirectoryEngine(
    data_path=DATA_FILE,
    model_name=EMBED_MODEL,
    base_threshold=BASE_THRESHOLD,
)

# ── Sesiones en memoria ─────────────────────────────────────────
sessions: dict = {}

# ── Modelos Pydantic ─────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="ID de sesión único")
    message: str = Field(..., description="Mensaje del usuario")


class StateContact(BaseModel):
    estado: str
    telefono: str = ""
    direccion: str = ""
    area: str = ""
    correo: str = ""


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    score: float = 0.0
    estado: str = ""
    telefono: str = ""
    direccion: str = ""
    area: str = ""
    correo: str = ""
    quick_replies: list[str] = []
    source: str = "embeddings"


# ── Helpers ──────────────────────────────────────────────────────
SALUDO_KEYWORDS = {"hola", "buenas", "buen dia", "buenos dias", "que tal", "hey", "hi", "hello", "menu", "inicio", "start"}

WELCOME_TEXT = (
    "👮 <strong>Directorio de Policía Cibernética</strong>\n\n"
    "Selecciona un estado de la lista desplegable o escribe el nombre "
    "del estado para obtener los datos de contacto de la policía cibernética.\n\n"
    "También puedes preguntar cosas como:\n"
    "• \"teléfono policía cibernética Jalisco\"\n"
    "• \"correo Nuevo León\"\n"
    "• \"dónde denuncio en CDMX?\""
)

NO_MATCH_TEXT = (
    "🤔 No encontré un estado que coincida con tu consulta.\n\n"
    "Intenta seleccionar un estado de la lista desplegable o escribe "
    "el nombre exacto del estado."
)


def _is_greeting(text: str) -> bool:
    normalized = text.lower().replace("á", "a").replace("é", "e") \
                     .replace("í", "i").replace("ó", "o").replace("ú", "u")
    words = set(normalized.split())
    if len(words) > 4:
        return False
    return bool(words & SALUDO_KEYWORDS)


# ── Endpoints ────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "ok": True,
        "dataset_size": len(engine.dataset),
        "index_size": len(engine._index_texts),
        "states_count": len(engine.states),
        "model": engine.model_name,
        "threshold": engine.base_threshold,
        "config": {
            "server_url": SERVER_URL,
            "api_port": API_PORT,
        },
    }


@app.get("/api/states", response_model=list[StateContact])
def get_states():
    """Retorna la lista completa de estados con datos de contacto."""
    return engine.get_all_states()


@app.get("/api/state/{state_name}")
def get_state(state_name: str):
    """Busca un estado por nombre exacto."""
    result = engine.get_state_by_name(state_name)
    if result:
        return {
            "ok": True,
            "estado": result.estado,
            "telefono": result.telefono,
            "direccion": result.direccion,
            "area": result.area,
            "correo": result.correo,
            "respuesta": result.respuesta,
            "score": result.score,
        }
    return {"ok": False, "message": f"Estado '{state_name}' no encontrado"}


@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Endpoint de chat con búsqueda semántica."""
    text = req.message.strip()

    if req.session_id not in sessions:
        sessions[req.session_id] = {"history": []}

    session = sessions[req.session_id]
    session["history"].append({"role": "user", "content": text})

    # Saludo / menú
    if _is_greeting(text):
        session["history"].append({"role": "bot", "content": WELCOME_TEXT})
        return ChatResponse(
            session_id=req.session_id,
            reply=WELCOME_TEXT,
            quick_replies=engine.states[:10],
            source="menu",
        )

    # Búsqueda semántica
    results = engine.search(text, top_k=3)

    if results:
        best = results[0]
        reply = best.respuesta

        # Sugerencias: otros estados cercanos
        suggestions = [r.estado for r in results[1:] if r.score > 0.40]

        session["history"].append({"role": "bot", "content": reply})

        return ChatResponse(
            session_id=req.session_id,
            reply=reply,
            score=best.score,
            estado=best.estado,
            telefono=best.telefono,
            direccion=best.direccion,
            area=best.area,
            correo=best.correo,
            quick_replies=suggestions,
            source="embeddings",
        )

    # Sin coincidencia
    session["history"].append({"role": "bot", "content": NO_MATCH_TEXT})
    return ChatResponse(
        session_id=req.session_id,
        reply=NO_MATCH_TEXT,
        quick_replies=engine.states[:6],
        source="fallback",
    )


@app.delete("/api/session/{session_id}")
def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
        return {"ok": True, "message": "Sesión eliminada"}
    return {"ok": False, "message": "Sesión no encontrada"}
