# -*- coding: utf-8 -*-
"""
API principal con FastAPI
Chatbot de menús asistido con RAG
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import os
from pathlib import Path
from dotenv import load_dotenv

from .menu_bot import create_bot

# Cargar variables de entorno desde ubicación centralizada
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Obtener configuración
SERVER_URL = os.getenv("SERVER_URL", "https://localhost")   
API_PORT = os.getenv("API_PORT_RAG", "8000")

# Crear app
app = FastAPI(
    title="UIIBOT RAG Menu",
    version="1.0.0",
    description="Chatbot de ciberseguridad con menús dinámicos y RAG"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar bot con dataset
DATASET_PATH = r"C:\xampp\htdocs\CiberReportes\proyectos_alternativos\chatbot_rag_menu\data_set\dataset_2000.jsonl"
bot = create_bot(DATASET_PATH)

# Almacenamiento de sesiones en memoria (para demo)
sessions = {}

# Modelos Pydantic
class ChatRequest(BaseModel):
    session_id: str = Field(..., description="ID de sesión único")
    message: str = Field(..., description="Mensaje del usuario")

class ChatResponse(BaseModel):
    session_id: str
    state: str
    reply: str
    quick_replies: list[str] = []
    source: str = "menu"
    debug: dict | None = None

# Endpoints
@app.get("/health")
def health():
    """Health check"""
    return {
        "ok": True,
        "dataset_loaded": len(bot.rag.dataset),
        "categories": len(bot.menu_structure),
        "config": {
            "server_url": SERVER_URL,
            "api_port": API_PORT
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    """Endpoint principal de chat"""
    # Obtener o crear sesión
    if req.session_id not in sessions:
        sessions[req.session_id] = {
            "state": "ROOT",
            "context": {}
        }
    
    session = sessions[req.session_id]
    
    # Procesar mensaje
    new_state, new_ctx, reply = bot.handle_message(session, req.message)
    
    # Actualizar sesión
    sessions[req.session_id] = {
        "state": new_state,
        "context": new_ctx
    }
    
    return ChatResponse(
        session_id=req.session_id,
        state=new_state,
        reply=reply.text,
        quick_replies=reply.quick_replies,
        source=reply.source,
        debug=reply.debug
    )

@app.get("/api/stats")
def stats():
    """Estadísticas del bot"""
    return {
        "active_sessions": len(sessions),
        "dataset_size": len(bot.rag.dataset),
        "topics_count": len(bot.rag.tematicas),
        "categories": list(bot.menu_structure.keys())
    }

@app.delete("/api/session/{session_id}")
def delete_session(session_id: str):
    """Elimina una sesión"""
    if session_id in sessions:
        del sessions[session_id]
        return {"ok": True, "message": "Sesión eliminada"}
    return {"ok": False, "message": "Sesión no encontrada"}

@app.get("/")
def root():
    """Raíz"""
    return {
        "message": "UIIBOT RAG Menu API",
        "version": "1.0.0",
        "docs": "/docs"
    }
