# ==========================================
# Dockerfile — uiibot_unified/backend_ollama
# Imagen: Python 3.12 slim
#
# Build:
#   docker build -t agentebit-backend .
#
# Run:
#   docker run -p 8002:8002 agentebit-backend
#
# Con variables de entorno:
#   docker run -p 8002:8002 -e API_PORT_OLLAMA=8002 agentebit-backend
# ==========================================

FROM python:3.12-slim

# Dependencias de compilación para llama-cpp-python
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiar requirements primero (cache de capas Docker)
COPY backend_ollama/requirements.txt ./requirements.txt

# Instalar dependencias Python
# CMAKE_ARGS permite compilar llama-cpp sin GPU (CPU only)
ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente del backend
COPY backend_ollama/ ./

# Copiar .env si existe (opcional)
COPY .env* ./

# Variables de entorno por defecto
ENV API_PORT_OLLAMA=8002
ENV SERVER_URL=http://localhost

# Puerto expuesto
EXPOSE 8002

# Indexar RAG al arrancar (si chroma_db no existe) y luego lanzar el backend
CMD ["sh", "-c", "python rag_indexer.py && python main.py"]
