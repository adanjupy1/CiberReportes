@echo off
:: ============================================================
:: start_backend.bat — Arranque del Backend Agente Bit
:: Ejecutar desde: uiibot_unified\
:: ============================================================
setlocal

echo.
echo  ==========================================
echo   Agente Bit - Backend llama-cpp + RAG
echo  ==========================================
echo.

cd /d "%~dp0backend_ollama"

:: Activar venv si existe, si no usar Python global
IF EXIST "venv\Scripts\activate.bat" (
    echo  Activando entorno virtual...
    call venv\Scripts\activate.bat
) ELSE (
    echo  [AVISO] venv no encontrado. Usando Python global.
    echo  Para un entorno limpio ejecuta primero: setup.bat
    echo.
)

:: 1. Verificar / crear base de conocimiento RAG
echo  [1/2] Verificando base de conocimiento RAG...
python rag_indexer.py --stats 2>nul
IF NOT EXIST "chroma_db" (
    echo  Base no encontrada. Indexando documentos...
    python rag_indexer.py
) ELSE (
    echo  Base vectorial OK.
)

echo.

:: 2. Iniciar backend FastAPI
echo  [2/2] Iniciando backend en puerto 8002...
echo.
python main.py

pause
