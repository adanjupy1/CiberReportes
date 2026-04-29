# uiibot_unified — Agente Bit Backend

Backend de inferencia local para **Agente Bit**, un asistente especializado en ciberseguridad para ciudadanos y empresas mexicanas.

Usa [`llama-cpp-python`](https://github.com/abetlen/llama-cpp-python) para ejecutar **Llama-3.2-3B-Instruct** (GGUF cuantizado) directamente en CPU, sin necesitar GPU ni Ollama. Incluye RAG con ChromaDB y embeddings multilingüe para respuestas enriquecidas con datos de CERT-MX, CONDUSEF, INAI y Policía Cibernética.

---

## Requisitos del sistema

| Componente | Mínimo recomendado |
|---|---|
| **OS** | Windows 10/11, Ubuntu 20.04+, macOS 12+ |
| **Python** | 3.10 o superior |
| **RAM** | 8 GB (el modelo ocupa ~2.5 GB en memoria) |
| **Disco** | 5 GB libres (modelo GGUF + ChromaDB + dependencias) |
| **CPU** | 4+ cores (más cores = generación más rápida) |
| **GPU** | Opcional (CUDA mejora velocidad ~10x) |
| **Compilador C++** | Requerido para `llama-cpp-python` |

### Compilador C++ por sistema
- **Windows:** [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (instalar "Desarrollo de escritorio con C++")
- **Linux:** `sudo apt install build-essential cmake`
- **macOS:** `xcode-select --install`

---

## Instalación rápida

### Windows
```bat
:: Doble clic en setup.bat, o desde terminal:
setup.bat
```

### Linux / macOS
```bash
chmod +x setup.sh
./setup.sh
```

### Docker (cualquier sistema)
```bash
# Construir y ejecutar con docker-compose
docker compose up --build

# O manualmente
docker build -t agentebit-backend .
docker run -p 8002:8002 agentebit-backend
```

---

## Arranque del backend

### Windows
```bat
:: Desde la raíz del proyecto:
start_backend.bat

:: O manualmente:
cd backend_ollama
venv\Scripts\activate
python main.py
```

### Linux / macOS
```bash
cd backend_ollama
source venv/bin/activate
python main.py
```

El backend quedará disponible en: **http://localhost:8002**

---

## Endpoints de la API

| Método | Endpoint | Descripción |
|---|---|---|
| `GET` | `/health` | Estado del servidor, modelo y RAG |
| `POST` | `/api/chat` | Enviar mensaje y recibir respuesta |
| `GET` | `/api/rag/status` | Estado de la base de conocimiento |
| `GET` | `/api/sessions` | Listar sesiones activas |
| `DELETE` | `/api/session/{id}` | Eliminar historial de sesión |

### Ejemplo de uso
```bash
# Health check
curl http://localhost:8002/health

# Enviar mensaje
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "mi-sesion-1", "message": "¿Qué es el phishing?"}'
```

### Respuesta de `/api/chat`
```json
{
  "reply": "El phishing es una técnica de ingeniería social...",
  "session_id": "mi-sesion-1",
  "model": "llama-3.2-3b-instruct",
  "rag_used": true
}
```

---

## Base de conocimiento RAG

La base vectorial (`chroma_db/`) contiene **17 documentos** de ciberseguridad México:

| Fuente | Temas |
|---|---|
| CERT-MX UNAM | Phishing SAT/IMSS, Ransomware PYMES, Vishing bancario |
| CONDUSEF | Fraude digital 2024, Smishing, Derechos del usuario bancario |
| INAI / LFPDPPP | Derechos ARCO, Avisos de privacidad, Brechas de datos |
| Policía Cibernética SSPC | Contacto denuncias (088), Sextorsión |
| Buenas prácticas | Contraseñas, Wi-Fi pública, Actualizaciones |
| Estadísticas | Kaspersky/IBM 2024, Marco legal penal federal |

### Gestión del índice RAG
```bash
cd backend_ollama

# Agregar nuevos documentos (omite duplicados)
python rag_indexer.py

# Ver estadísticas
python rag_indexer.py --stats

# Reiniciar desde cero
python rag_indexer.py --reset
```

---

## Configuración

Crea un archivo `.env` en la raíz del proyecto (o copia `.env.example`):

```env
API_PORT_OLLAMA=8002
SERVER_URL=http://localhost
```

---

## Pruebas

```bash
cd backend_ollama

# Suite completa (11 pruebas, ~10 min en CPU)
python -X utf8 test_backend.py

# Solo health + RAG (rápido, sin inferencia)
python -X utf8 test_backend.py --quick

# Contra URL remota
python -X utf8 test_backend.py --url http://mi-servidor:8002
```

### Resultados esperados
```
Total:   11
[PASS]:  10
[WARN]:  1   (off-topic: comportamiento conocido en modelos 3B)
[FAIL]:  0
```

---

## Estructura del proyecto

```
uiibot_unified/
│
├── backend_ollama/
│   ├── main.py              # FastAPI backend + RAG integrado
│   ├── rag_indexer.py       # Indexador ChromaDB (conocimiento MX)
│   ├── test_backend.py      # Suite de pruebas (11 tests)
│   ├── requirements.txt     # Dependencias Python
│   ├── start_backend.bat    # Arranque rápido Windows
│   └── chroma_db/           # Base vectorial (se crea al indexar)
│
├── .env.example             # Plantilla de variables de entorno
├── .gitignore               # Excluye modelos grandes y cache
├── setup.bat                # Instalación Windows
├── setup.sh                 # Instalación Linux/macOS
├── Dockerfile               # Imagen Docker
├── docker-compose.yml       # Orquestación Docker
└── README.md                # Este archivo
```

---

## Modelo utilizado

| Parámetro | Valor |
|---|---|
| **Modelo base** | Meta Llama 3.2 3B Instruct |
| **Formato** | GGUF (Q4_K_M cuantizado) |
| **Repositorio HF** | `bartowski/Llama-3.2-3B-Instruct-GGUF` |
| **Tamaño en disco** | ~2 GB |
| **Descarga** | Automática en primer arranque |
| **Contexto** | 4096 tokens |

> **Nota:** El modelo se descarga automáticamente desde HuggingFace la primera vez. No se incluye en el paquete por su tamaño (~2GB).

---

## Troubleshooting

### Error: `No module named 'fastapi'`
```bash
# Asegúrate de tener el venv activado
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/macOS
```

### Error compilando `llama-cpp-python`
```bash
# Windows: instalar Build Tools de Visual Studio
# Linux:
sudo apt install build-essential cmake libopenblas-dev

# macOS:
xcode-select --install
brew install cmake openblas
```

### Backend muy lento (>2 min por respuesta)
- Aumentar `n_threads` en `main.py` (línea `n_threads=os.cpu_count()`)
- Usar una máquina con más cores o RAM
- Activar GPU si está disponible: `CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python`

### RAG no se activa
```bash
# Verificar que la base de conocimiento existe
python rag_indexer.py --stats
# Si dice 0 documentos, re-indexar:
python rag_indexer.py
```

---

## Licencia

Proyecto de uso interno — **CiberReportes / UIIBOT Unified**  
Modelo Llama 3.2: sujeto a [Meta Llama 3.2 Community License](https://www.llama.com/llama3_2/license/)
