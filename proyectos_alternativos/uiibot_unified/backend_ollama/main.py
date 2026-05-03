#!/usr/bin/env python3
"""
Backend llama-cpp-python para Agente Bit
Integración con Llama-3.2-3B-Instruct (GGUF local, sin Ollama)
+ RAG con ChromaDB para conocimiento actualizado de Ciberseguridad México
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
# RAG — ChromaDB + Sentence Transformers (multilingüe)
# ---------------------------------------------------------------------------
CHROMA_DB_PATH  = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "ciberseg_mexico"
EMBED_MODEL     = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

_embedder   = None
_collection = None


def _init_rag():
    """Inicializa el motor RAG (lazy, solo si la DB existe)."""
    global _embedder, _collection
    if not CHROMA_DB_PATH.exists():
        logger.warning(
            "⚠️  ChromaDB no encontrada. RAG desactivado. "
            "Ejecuta: python rag_indexer.py para crear la base de conocimiento."
        )
        return

    try:
        import chromadb
        from sentence_transformers import SentenceTransformer

        client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
        _collection = client.get_or_create_collection(COLLECTION_NAME)
        _embedder   = SentenceTransformer(EMBED_MODEL)
        doc_count   = _collection.count()
        logger.info(f"✅ RAG activo — {doc_count} documentos en '{COLLECTION_NAME}'")
    except ImportError:
        logger.warning("⚠️  chromadb/sentence-transformers no instalados. RAG desactivado.")
    except Exception as exc:
        logger.warning(f"⚠️  Error al inicializar RAG: {exc}")


def retrieve_context(query: str, n_results: int = 3) -> str:
    """
    Recupera los fragmentos más relevantes de la base vectorial local.
    Retorna string vacío si RAG no está disponible o no hay resultados.
    """
    if _collection is None or _embedder is None:
        return ""

    try:
        embedding = _embedder.encode(query).tolist()
        results   = _collection.query(
            query_embeddings=[embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        docs      = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]

        # Filtrar por umbral de relevancia (distancia L2 < 20.0)
        # < 12.0 → muy alta similitud
        # 12.0-16.0 → alta similitud
        # 16.0-20.0 → similitud moderada (aún útil)
        # > 20.0 → ruido, se descarta
        relevant = [
            doc for doc, dist in zip(docs, distances) if dist < 20.0
        ]
        return "\n\n---\n".join(relevant) if relevant else ""
    except Exception as exc:
        logger.warning(f"RAG retrieve error: {exc}")
        return ""


# Inicializar RAG al arrancar
_init_rag()

# ---------------------------------------------------------------------------
app = FastAPI(title="Agente Bit — llama-cpp-python + RAG")

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

SYSTEM_PROMPT = """Eres 'Agente Bit', un asistente experto en ciberseguridad para México. 
Tu objetivo es ayudar a ciudadanos y empresas a prevenir y reaccionar ante incidentes digitales.

REGLAS DE IDENTIDAD Y SEGURIDAD:
1. No te niegues a responder temas de SAT, IMSS o Sextorsión por miedo a dar 'asesoría legal'. Eres un asistente TÉCNICO de ciberseguridad; proporciona los pasos de reporte y prevención (088, CERT-MX, etc.) que están en tu base de conocimientos.
2. Si un tema es sensible (como sextorsión), sé empático pero directo con las medidas de seguridad técnica (capturas, headers, denuncia 088).
3. Prioriza siempre autoridades mexicanas (CERT-MX, Policía Cibernética, CONDUSEF, INAI).
4. Proporciona pasos accionables (bloquear, reportar, respaldar).
5. Si no sabes algo, admítelo y redirige a la autoridad competente.
6. Tus respuestas deben ser profesionales, estructuradas en Markdown y en español de México.

Cuando recibas [CONTEXTO CIBERSEGURIDAD MX], úsalo como fuente de información prioritaria.
Si no estás seguro de algo, admítelo y orienta a la fuente oficial correspondiente."""

class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    model: str
    rag_used: bool = False


# ---------------------------------------------------------------------------
@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "backend": "llama-cpp-python",
        "model": MODEL_NAME,
        "model_file": MODEL_FILE,
        "rag": {
            "active": _collection is not None,
            "documents": _collection.count() if _collection else 0,
            "collection": COLLECTION_NAME,
        },
        "config": {
            "server_url": SERVER_URL,
            "api_port": API_PORT,
        },
    }


# ---------------------------------------------------------------------------
@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Endpoint principal de chat usando llama-cpp-python (inferencia local) + RAG.
    """
    session_id   = request.session_id
    user_message = request.message.strip()

    if not user_message:
        raise HTTPException(status_code=400, detail="Mensaje vacío")

    # Inicializar historial de la sesión si no existe
    if session_id not in conversations:
        conversations[session_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    # ── RAG: recuperar contexto relevante ──────────────────────────────────
    rag_context = retrieve_context(user_message)
    rag_used    = bool(rag_context)

    if rag_used:
        enriched_message = (
            f"[CONTEXTO CIBERSEGURIDAD MX]\n{rag_context}\n\n"
            f"[PREGUNTA DEL USUARIO]\n{user_message}"
        )
        logger.info(f"RAG: contexto inyectado ({len(rag_context)} chars) — sesión {session_id[:8]}")
    else:
        enriched_message = user_message

    # Agregar mensaje del usuario al historial (con contexto RAG si aplica)
    conversations[session_id].append({"role": "user", "content": enriched_message})

    # Limitar historial: 1 system + últimos 20 mensajes (10 intercambios)
    if len(conversations[session_id]) > 21:
        conversations[session_id] = (
            [conversations[session_id][0]] + conversations[session_id][-20:]
        )

    logger.info(f"Generando respuesta con {MODEL_NAME} — sesión {session_id[:8]} | RAG: {rag_used}")

    try:
        result = llm.create_chat_completion(
            messages=conversations[session_id],
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            max_tokens=384,        # límite aumentado: permite respuestas más completas
            repeat_penalty=1.1,    # penaliza repetición, previene generación infinita
        )
        assistant_message: str = result["choices"][0]["message"]["content"]

    except Exception as e:
        logger.error(f"Error en inferencia: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error de inferencia: {str(e)}")

    if not assistant_message:
        raise HTTPException(status_code=500, detail="Respuesta vacía del modelo")

    # Guardar en historial el mensaje original (sin el contexto RAG para ahorrar tokens)
    conversations[session_id][-1] = {"role": "user", "content": user_message}
    conversations[session_id].append(
        {"role": "assistant", "content": assistant_message}
    )

    logger.info(f"Respuesta generada — sesión {session_id[:8]}")

    return ChatResponse(
        reply=assistant_message,
        session_id=session_id,
        model=MODEL_NAME,
        rag_used=rag_used,
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


@app.get("/api/rag/status")
async def rag_status():
    """Estado del motor RAG"""
    return {
        "active": _collection is not None,
        "documents": _collection.count() if _collection else 0,
        "collection": COLLECTION_NAME,
        "embed_model": EMBED_MODEL,
        "db_path": str(CHROMA_DB_PATH),
    }


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(API_PORT), log_level="info")
