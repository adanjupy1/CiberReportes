# -*- coding: utf-8 -*-
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field 
import os
from pathlib import Path
from dotenv import load_dotenv

from .storage import Storage
from .engine import handle_message
from . import content

# Cargar variables de entorno desde ubicación centralizada
env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(env_path)

# Obtener configuración
SERVER_URL = os.getenv("SERVER_URL", "https://localhost") 
API_PORT = os.getenv("API_PORT_PRO", "8001")

app = FastAPI(title="El Agente Bit Pro", version="1.0.0")

# CORS: allow local dev + static frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

storage = Storage(db_path="uiibot.db")

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Client-generated session id (uuid recommended)")
    message: str

class ChatResponse(BaseModel):
    session_id: str
    state: str
    reply: str
    quick_replies: list[str] = []
    debug: dict | None = None

@app.get("/health")
def health():
    return {
        "ok": True,
        "config": {
            "server_url": SERVER_URL,
            "api_port": API_PORT
        }
    }

@app.post("/api/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session = storage.get_session(req.session_id)
    new_state, new_ctx, reply = handle_message(session, req.message, storage=storage)

    # Persist report when it is created and we have minimum fields
    if "report" in new_ctx and new_ctx["report"].get("report_id") and not new_ctx["report"].get("_saved"):
        r = new_ctx["report"]
        storage.save_report(
            report_id=r.get("report_id"),
            session_id=req.session_id,
            name=r.get("name"),
            state=r.get("state"),
            age=r.get("age"),
            sex=r.get("sex"),
            incident_type=r.get("incident_type"),
            description=r.get("description"),
            extra={"raw": r},
        )
        new_ctx["report"]["_saved"] = True

    storage.save_session(req.session_id, new_state, new_ctx)
    return ChatResponse(
        session_id=req.session_id,
        state=new_state,
        reply=reply.text,
        quick_replies=reply.quick_replies,
        debug=reply.debug,
    )

@app.get("/")
def root():
    return {"message": "El Agente Bit Pro is running. Open /docs for Swagger UI."}
