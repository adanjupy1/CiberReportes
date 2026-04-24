# Chatbot CiberReportes - Backend API
Este servicio proporciona respuestas inteligentes sobre el formulario de Registro de Reportes Cibernéticos.  
## 🚀 Características

- **FastAPI**: API REST de alto rendimiento
- **Embeddings**: Usa sentence-transformers para búsqueda semántica
- **RAG**: Recuperación de información con topic routing
- **Fuzzy Matching**: Búsqueda aproximada con RapidFuzz
- **Multilingüe**: Soporte para español

## 📦 Instalación
### Requisitos Previos

- Python 3.10+
- Entorno virtual CHAT_PLUS configurado

### Instalar Dependencias

```bash
cd C:\xampp\htdocs\CiberReportes\proyectos_alternativos\chatbot_ciberreportes
C:\xampp\htdocs\CiberReportes\CHAT_PLUS\Scripts\activate
pip install -r requirements.txt
```

## 🏃 Ejecución

### Iniciar el Backend

```bash
# Desde el directorio backend/
cd backend
uvicorn app:app --host 127.0.0.1 --port 8003 --reload
```
### Verificar Estado
```bash
curl http://localhost:8003/health
```
## 📚 API Endpoints
### GET /health
Verifica el estado del servicio
**Respuesta:**
```json
{
  "status": "ok",
  "model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
  "kb_loaded": true,
  "base_items": 100,
  "rel_items": 50
}
```

### POST /ask
Realiza una consulta al chatbot

**Request:**
```json
{
  "query": "¿Qué es el folio?",
  "top_k": 3,
  "min_score": 0.62,
  "include_related": true,
  "session_id": "abc123",
  "user_id": "user1"
}
```

**Response:**
```json
{
  "answer": "Una vez finalizado el reporte te aparecerá un número de folio...",
  "score": 0.95,
  "source": "base",
  "id": "base:5",
  "topic": null,
  "difficulty": null,
  "related": [...]
}
```

### POST /suggest
Obtiene sugerencias de preguntas similares

**Request:**
```json
{
  "query": "reporte",
  "k": 5
}
```

**Response:**
```json
{
  "suggestions": [
    {
      "q": "¿Cómo registro un reporte?",
      "score": 0.85,
      "source": "base",
      "topic": null,
      "difficulty": null,
      "id": "base:1"
    }
  ]
}
```

### POST /feedback
Envía feedback sobre una respuesta

**Request:**
```json
{
  "query": "¿Qué es el folio?",
  "answer_id": "base:5",
  "helpful": true,
  "notes": "Respuesta clara",
  "session_id": "abc123",
  "user_id": "user1"
}
```

### POST /reload-kb
Recarga la base de conocimiento (requiere autenticación)

**Headers:**
```
Authorization: Bearer <ADMIN_TOKEN>
```

### GET /topics
Lista todos los tópicos disponibles

**Response:**
```json
{
  "topics": ["Registro", "Evidencias", "Formulario"]
}
```

## 🔧 Configuración
### Variables de Entorno
Crea un archivo `.env` en el directorio raíz:
```ini
# Modelo de embeddings
EMBED_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
# Directorio de la base de conocimiento
KB_DIR=../kb_out
# Umbrales de confianza
BASE_THRESHOLD=0.62
REL_THRESHOLD=0.58
# Token de administración (para /reload-kb)
ADMIN_TOKEN=tu_token_secreto_aqui
```

## 🛠️ Construcción de la Base de Conocimiento
Para actualizar la base de conocimiento con nuevos datos:
```bash
# Desde el directorio raíz del proyecto
python build_kb.py
```
El script:
1. Lee los datasets JSONL de `data/`
2. Genera embeddings con sentence-transformers
3. Calcula centroides de tópicos
4. Guarda todo en `kb_out/`

### Estructura de Datos

**dataset_audio.jsonl** (formato messages):
```json
{
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "pregunta"},
    {"role": "assistant", "content": "respuesta"}
  ]
}
```

**dataset_consolidado_audio_relacionado.jsonl** (formato alternativo):
```json
{
  "Context": "pregunta",
  "Response": "respuesta",
  "Topic": "Formulario",
  "Difficulty": "Básico"
}
```

## 🔄 Integración con CiberReportes
### Apache Proxy
Agregar en `httpd.conf`:
```apache
# Backend Chatbot - Puerto 8003
ProxyPass        /api/backend-chatbot http://127.0.0.1:8003
ProxyPassReverse /api/backend-chatbot http://127.0.0.1:8003
```

### PowerShell Scripts
Agregar en `start_backends.ps1`:
```powershell
# Puerto 8003 - chatbot_ciberreportes
cd C:\xampp\htdocs\CiberReportes\proyectos_alternativos\chatbot_ciberreportes\backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
  "& 'C:\xampp\htdocs\CiberReportes\CHAT_PLUS\Scripts\python.exe' -m uvicorn app:app --host 127.0.0.1 --port 8003"
```
## 📊 Estructura del Proyecto

```
chatbot_ciberreportes/
├── backend/
│   └── app.py              # API FastAPI
├── data/
│   ├── dataset_audio.jsonl # Dataset principal
│   └── dataset_consolidado_audio_relacionado.jsonl (opcional)
├── kb_out/
│   ├── embeddings.npy      # Embeddings pre-calculados
│   ├── meta.json           # Metadata de documentos
│   └── topic_centroids.json # Centroides de tópicos
├── logs/
│   └── feedback.jsonl      # Logs de feedback
├── build_kb.py             # Script para construir KB
├── requirements.txt        # Dependencias Python
└── README.md              # Esta documentación
```
### ================== Error: "No encuentro KB en kb_out" ========================================== ##
Ejecuta el script de construcción:
```bash
python build_kb.py
```
### ==================  Error: "Module not found" ================================================== ##
Instala las dependencias:
```bash
pip install -r requirements.txt
```
### ================== Puerto 8003 en uso ========================================================== ##
Cambia el puerto en el comando de inicio o detén el proceso:
```bash
# Windows
netstat -ano | findstr :8003
taskkill /PID <PID> /F
```
## ================================================================================================= ##
### Modelo no descarga
El modelo se descarga automáticamente en el primer inicio. Requiere conexión a internet.

## 📝 Logs
Los logs de feedback se guardan en `logs/feedback.jsonl` con el siguiente formato:

```json
{
  "query": "¿Qué es el folio?",
  "answer_id": "base:5",
  "helpful": true,
  "notes": "Muy útil",
  "session_id": "abc123",
  "user_id": "user1",
  "ts": 1708214400.123
}
```
## 🔐 Seguridad
- El endpoint `/reload-kb` requiere token de autenticación
- Usa HTTPS en producción
- Configura CORS apropiadamente
- No expongas el ADMIN_TOKEN
## 🤝 Contribuir
Para agregar nuevas preguntas y respuestas:
1. Edita los archivos JSONL en `data/`
2. Ejecuta `python build_kb.py`
3. Reinicia el servidor

