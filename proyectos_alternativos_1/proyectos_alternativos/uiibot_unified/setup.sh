#!/usr/bin/env bash
# ============================================================
# setup.sh — Instalación completa de uiibot_unified
# Sistema: Linux / macOS
#
# Uso:
#   chmod +x setup.sh && ./setup.sh
#   ./setup.sh --reset   -> Reinstala y reindexa RAG desde cero
# ============================================================
set -e

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'

echo ""
echo -e "${BLUE} ====================================================="
echo "  uiibot_unified - Setup e Instalacion"
echo "  Agente Bit con llama-cpp-python + RAG"
echo -e " =====================================================${NC}"
echo ""

# --- Verificar Python 3.10+ ---
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[ERROR] python3 no encontrado. Instala Python 3.10+${NC}"
    exit 1
fi

PYVER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo -e "${GREEN}[OK] Python $PYVER detectado.${NC}"

# --- Entorno virtual ---
BACKEND_DIR="$(dirname "$0")/backend_ollama"
cd "$BACKEND_DIR"

echo ""
if [ ! -d "venv" ]; then
    echo "[1/4] Creando entorno virtual..."
    python3 -m venv venv
else
    echo "[1/4] Entorno virtual existente detectado."
fi

source venv/bin/activate

# --- Dependencias ---
echo ""
echo "[2/4] Instalando dependencias..."
echo "      (llama-cpp-python puede tardar 5-10 min en compilar)"
pip install --upgrade pip -q
pip install -r requirements.txt

echo -e "${GREEN}[OK] Dependencias instaladas.${NC}"

# --- .env ---
cd "$(dirname "$0")"
echo ""
if [ ! -f ".env" ]; then
    echo "[3/4] Creando .env desde plantilla..."
    cp .env.example .env
    echo -e "${GREEN}[OK] .env creado.${NC}"
else
    echo "[3/4] .env existente, omitiendo."
fi

# --- RAG ---
cd "$BACKEND_DIR"
echo ""
if [ "$1" == "--reset" ]; then
    echo "[4/4] Re-indexando RAG desde cero..."
    python rag_indexer.py --reset
else
    echo "[4/4] Verificando base de conocimiento RAG..."
    python rag_indexer.py
fi

echo ""
echo -e "${GREEN} ====================================================="
echo "  Instalacion completada!"
echo ""
echo "  Para iniciar el backend:"
echo "    cd backend_ollama"
echo "    source venv/bin/activate"
echo "    python main.py"
echo -e " =====================================================${NC}"
echo ""
