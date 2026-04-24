#!/usr/bin/env python3
"""
Backend llama-cpp-python para Agente Bit
Integración con Llama-3.2-3B-Instruct (GGUF local, sin Ollama)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, List
from llama_cpp import Llama

# Cargar variables de entorno desde ubicación centralizada
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)

# Obtener configuración
SERVER_URL = os.getenv("SERVER_URL", "https://localhost")
API_PORT = os.getenv("API_PORT_OLLAMA", "8002")

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cargar modelo GGUF una sola vez al arrancar (descarga automática desde HF)
# ---------------------------------------------------------------------------
MODEL_REPO   = "bartowski/Llama-3.2-3B-Instruct-GGUF"
MODEL_FILE   = "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
MODEL_NAME   = "llama-3.2-3b-instruct"   # nombre identificador para respuestas

logger.info(f"Cargando modelo {MODEL_NAME} desde HuggingFace ({MODEL_REPO})…")
llm = Llama.from_pretrained(
    repo_id=MODEL_REPO,
    filename=MODEL_FILE,
    n_ctx=4096,          # ventana de contexto
    n_threads=os.cpu_count() or 4,
    verbose=False,
)
logger.info("Modelo cargado correctamente.")

# ---------------------------------------------------------------------------
app = FastAPI(title="Agente Bit — llama-cpp-python")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Historial de conversaciones por sesión
conversations: dict[str, list] = {}

SYSTEM_PROMPT = (
    "Eres Agente Bit, un asistente especializado en ciberseguridad creado para ayudar "
    "a ciudadanos mexicanos.\n\n"
    "Tus responsabilidades:\n"
    "- Explicar términos y conceptos de ciberseguridad de forma clara y accesible\n"
    "- Proporcionar consejos prácticos de seguridad digital\n"
    "- Ayudar a identificar amenazas y vulnerabilidades\n"
    "- Orientar sobre buenas prácticas en internet\n"
    "- Ser conciso pero informativo\n"
    "- Usar lenguaje profesional pero amigable\n\n"
    "Responde de manera directa, clara y útil. Si no estás seguro de algo, admítelo."
)


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    model: str


# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "backend": "llama-cpp-python",
        "model": MODEL_NAME,
        "model_file": MODEL_FILE,
        "config": {
            "server_url": SERVER_URL,
            "api_port": API_PORT,
        },
    }


# ---------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal de chat usando llama-cpp-python (inferencia local).
    """
    session_id = request.session_id
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    # Inicializar historial de la sesión si no existe
    if session_id not in conversations:
        conversations[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # Agregar mensaje del usuario al historial
    conversations[session_id].append({"role": "user", "content": user_message})

    # Limitar historial: 1 system + últimos 20 mensajes (10 intercambios)
    if len(conversations[session_id]) > 21:
        conversations[session_id] = (
            [conversations[session_id][0]] + conversations[session_id][-20:]
        )

    logger.info(f"Generando respuesta con {MODEL_NAME} — sesión {session_id[:8]}")

    try:
        result = llm.create_chat_completion(
            messages=conversations[session_id],
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            max_tokens=512,
        )
        assistant_message: str = result["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Error en inferencia: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error de inferencia: {str(e)}")

    if not assistant_message:
        raise HTTPException(status_code=500, detail="Respuesta vacía del modelo")

    # Guardar respuesta en historial
    conversations[session_id].append(
        {"role": "assistant", "content": assistant_message}
    )

    logger.info(f"Respuesta generada — sesión {session_id[:8]}")

    return ChatResponse(
        reply=assistant_message,
        session_id=session_id,
        model=MODEL_NAME,
    )


# ---------------------------------------------------------------------------
@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """Limpiar historial de una sesión"""
    if session_id in conversations:
        del conversations[session_id]
        return {"ok": True, "message": "Sesión eliminada"}
    return {"ok": False, "message": "Sesión no encontrada"}


@app.get("/api/sessions")
async def list_sessions():
    """Listar sesiones activas"""
    return {
        "sessions": list(conversations.keys()),
        "count": len(conversations),
    }


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(API_PORT), log_level="info")
