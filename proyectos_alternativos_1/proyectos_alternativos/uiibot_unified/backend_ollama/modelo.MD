# 📖 modelo.MD — Backend `backend_ollama` (llama-cpp-python)

> **Proyecto:** Uiibot Unified — Agente Bit  
> **Ruta:** `proyectos_alternativos/uiibot_unified/backend_ollama/`  
> **Última revisión:** 2026-04-26  
> **Motor de inferencia:** `llama-cpp-python` (inferencia local, sin Ollama)  
> **Puerto por defecto:** `8002`

---

## 1. Descripción General

`backend_ollama` es el servicio FastAPI que expone la inteligencia conversacional de **Agente Bit**, un chatbot especializado en ciberseguridad para ciudadanos mexicanos. A pesar del nombre del directorio (heredado de una iteración anterior), **este backend NO usa Ollama**; utiliza directamente `llama-cpp-python` para ejecutar inferencia local con un modelo GGUF descargado automáticamente desde HuggingFace.

### Flujo de funcionamiento

```
Frontend (config.js → API_PORT_OLLAMA: 8002)
    │
    ▼  POST /api/chat
FastAPI (main.py)
    │
    ▼  Llama.create_chat_completion()
llama-cpp-python  ──►  Llama-3.2-3B-Instruct-Q4_K_M.gguf  (caché local HF)
    │
    ▼  JSON response
Frontend
```

---

## 2. Modelo de Lenguaje (LLM)

| Parámetro       | Valor                                                   |
|-----------------|---------------------------------------------------------|
| **Repositorio** | `bartowski/Llama-3.2-3B-Instruct-GGUF` (HuggingFace)  |
| **Archivo**     | `Llama-3.2-3B-Instruct-Q4_K_M.gguf`                   |
| **Nombre ID**   | `llama-3.2-3b-instruct`                                |
| **Cuantización**| Q4_K_M (4-bit, equilibrio calidad/rendimiento)         |
| **Parámetros**  | 3.2 Billion                                            |
| **Arquitectura**| Meta LLaMA 3.2 — Instruct                              |
| **Descarga**    | Automática con `Llama.from_pretrained()` al iniciar    |

### Parámetros de inferencia

| Parámetro       | Valor  | Descripción                               |
|-----------------|--------|-------------------------------------------|
| `n_ctx`         | 4096   | Ventana de contexto (tokens)              |
| `n_threads`     | Auto   | Número de CPUs lógicas disponibles        |
| `temperature`   | 0.7    | Balance creatividad/coherencia            |
| `top_p`         | 0.9    | Nucleus sampling                          |
| `top_k`         | 40     | Candidatos por token                      |
| `max_tokens`    | 512    | Límite de tokens en la respuesta          |
| `verbose`       | False  | Sin logs del modelo en consola            |

---

## 3. Estructura del Módulo

```
backend_ollama/
├── main.py          # Única fuente — servidor FastAPI + carga del modelo
├── modelo.MD        # Este documento
└── __pycache__/     # Bytecode generado por Python (ignorar)
```

> El módulo es intencionalmente compacto: un solo archivo `main.py` de ~185 líneas que agrupa la carga del modelo, las rutas y la lógica de sesiones.

---

## 4. Dependencias

Declaradas en `proyectos_alternativos/requirements.txt`:

```txt
fastapi
uvicorn[standard]
python-dotenv
httpx
llama-cpp-python>=0.3.20   # motor principal de inferencia
diskcache>=5.6.1            # (disponible, actualmente no usado en este módulo)
```

### Instalación

```bash
pip install -r proyectos_alternativos/requirements.txt
```

> **Nota:** `llama-cpp-python` puede requerir compilación nativa. En Windows se recomienda usar la wheel pre-compilada con soporte CUDA o CPU disponible en los [releases oficiales](https://github.com/abetlen/llama-cpp-python/releases).

---

## 5. Variables de Entorno

El archivo `.env` debe ubicarse en la **raíz del repositorio** (`CiberReportes/.env`). El backend lo carga con:

```python
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(env_path)
```

| Variable          | Valor por defecto    | Descripción                                |
|-------------------|----------------------|--------------------------------------------|
| `SERVER_URL`      | `https://localhost`  | URL base del servidor                      |
| `API_PORT_OLLAMA` | `8002`               | Puerto en el que escucha este backend      |

### Ejemplo de `.env`

```dotenv
SERVER_URL=https://localhost
API_PORT_OLLAMA=8002
```

---

## 6. API — Endpoints

### `GET /health`

Verificación de estado del servicio y del modelo cargado.

**Respuesta exitosa (200):**
```json
{
  "ok": true,
  "backend": "llama-cpp-python",
  "model": "llama-3.2-3b-instruct",
  "model_file": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
  "config": {
    "server_url": "https://localhost",
    "api_port": "8002"
  }
}
```

---

### `POST /api/chat`

Endpoint principal de conversación con el Agente Bit.

**Request body:**
```json
{
  "session_id": "string",
  "message": "string"
}
```

| Campo        | Tipo   | Requerido | Descripción                              |
|--------------|--------|-----------|------------------------------------------|
| `session_id` | string | ✅        | Identificador único de la sesión/usuario |
| `message`    | string | ✅        | Mensaje del usuario (no puede ser vacío) |

**Respuesta exitosa (200) — `ChatResponse`:**
```json
{
  "reply": "string",
  "session_id": "string",
  "model": "llama-3.2-3b-instruct"
}
```

**Errores posibles:**

| Código | Detalle                     | Causa                          |
|--------|-----------------------------|--------------------------------|
| 400    | `"Mensaje vacío"`           | `message` en blanco o vacío    |
| 500    | `"Error de inferencia: ..."` | Fallo en `llama-cpp-python`   |
| 500    | `"Respuesta vacía del modelo"` | El modelo devolvió vacío    |

---

### `DELETE /api/session/{session_id}`

Elimina el historial de conversación de una sesión específica.

**Respuesta — sesión encontrada (200):**
```json
{ "ok": true, "message": "Sesión eliminada" }
```

**Respuesta — sesión no encontrada (200):**
```json
{ "ok": false, "message": "Sesión no encontrada" }
```

---

### `GET /api/sessions`

Lista todas las sesiones activas en memoria.

**Respuesta (200):**
```json
{
  "sessions": ["abc123", "xyz789"],
  "count": 2
}
```

> ⚠️ Las sesiones son **in-memory**: se pierden al reiniciar el servidor.

---

## 7. Gestión de Sesiones y Contexto

El historial de cada sesión se almacena en el diccionario en memoria `conversations`:

```python
conversations: dict[str, list] = {}
```

### Estructura del historial por sesión

```
conversations["session_id"] = [
    {"role": "system",    "content": SYSTEM_PROMPT},
    {"role": "user",      "content": "mensaje del usuario"},
    {"role": "assistant", "content": "respuesta del agente"},
    ...
]
```

### Política de truncado

Para evitar superar la ventana de contexto del modelo (4096 tokens), el historial se **trunca automáticamente**:

- **Máximo:** 1 mensaje `system` + 20 mensajes recientes (= 10 intercambios completos)
- **Regla:** si `len(historial) > 21` → se conserva `[system] + [-20:]`

```python
if len(conversations[session_id]) > 21:
    conversations[session_id] = (
        [conversations[session_id][0]] + conversations[session_id][-20:]
    )
```

---

## 8. System Prompt — Personalidad del Agente Bit

```
Eres Agente Bit, un asistente especializado en ciberseguridad creado para ayudar
a ciudadanos mexicanos.

Tus responsabilidades:
- Explicar términos y conceptos de ciberseguridad de forma clara y accesible
- Proporcionar consejos prácticos de seguridad digital
- Ayudar a identificar amenazas y vulnerabilidades
- Orientar sobre buenas prácticas en internet
- Ser conciso pero informativo
- Usar lenguaje profesional pero amigable

Responde de manera directa, clara y útil. Si no estás seguro de algo, admítelo.
```

---

## 9. CORS

Configurado para aceptar cualquier origen (modo desarrollo):

```python
CORSMiddleware(
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

> ⚠️ En producción se recomienda restringir `allow_origins` al dominio real del frontend.

---

## 10. Arranque del Servidor

### Modo desarrollo (directo)

```bash
cd proyectos_alternativos/uiibot_unified/backend_ollama
python main.py
```

### Con Uvicorn (recomendado)

```bash
uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```

### Con Uvicorn usando puerto de .env

```bash
uvicorn main:app --host 0.0.0.0 --port ${API_PORT_OLLAMA:-8002}
```

> La primera vez que se inicie el servidor, `llama-cpp-python` descargará automáticamente el archivo GGUF (~2 GB) desde HuggingFace y lo guardará en el caché local de HF (`~/.cache/huggingface/`).

---

## 11. Integración con el Frontend

El frontend (`public/proyectos_alternativos/frontend/config.js`) apunta a este backend con:

```javascript
API_PORT_OLLAMA: '8002',  // uiibot_unified
```

La URL completa de cada llamada es: `{SERVER_URL}:{API_PORT_OLLAMA}/api/chat`

El frontend puede sobreescribir el puerto desde `localStorage`:

```javascript
if (localStorage.getItem('API_PORT_OLLAMA')) {
    CONFIG.API_PORT_OLLAMA = localStorage.getItem('API_PORT_OLLAMA');
}
```

---

## 12. Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    UIIBOT UNIFIED                        │
│                                                          │
│  Frontend (config.js)                                    │
│      │  API_PORT_OLLAMA = 8002                          │
│      │                                                   │
│      ▼  POST http://localhost:8002/api/chat             │
│  ┌────────────────────────────────────┐                 │
│  │  FastAPI — main.py                 │                 │
│  │                                    │                 │
│  │  Rutas:                            │                 │
│  │    GET  /health                    │                 │
│  │    POST /api/chat                  │                 │
│  │    GET  /api/sessions              │                 │
│  │    DEL  /api/session/{id}         │                 │
│  │                                    │                 │
│  │  Estado en memoria:                │                 │
│  │    conversations: dict[str, list]  │                 │
│  └──────────────┬─────────────────────┘                 │
│                 │  Llama.create_chat_completion()        │
│                 ▼                                        │
│  ┌─────────────────────────────────┐                    │
│  │  llama-cpp-python               │                    │
│  │  Llama-3.2-3B-Instruct-Q4_K_M  │                    │
│  │  (~2 GB GGUF, caché HF local)  │                    │
│  └─────────────────────────────────┘                    │
│                                                          │
│  .env (raíz repositorio):                               │
│    SERVER_URL=https://localhost                          │
│    API_PORT_OLLAMA=8002                                  │
└─────────────────────────────────────────────────────────┘
```

---

## 13. Notas Técnicas y Consideraciones

| # | Tema | Detalle |
|---|------|---------|
| 1 | **Sin persistencia** | Las sesiones viven en memoria RAM. Al reiniciar el proceso se pierden todos los historiales. |
| 2 | **Carga en arranque** | El modelo se carga una sola vez al iniciar (`llm = Llama.from_pretrained(...)`). Las peticiones no incurren en overhead de carga. |
| 3 | **Hilos CPU** | `n_threads=os.cpu_count()` aprovecha todos los núcleos lógicos. Útil en servidores sin GPU. |
| 4 | **Compatibilidad GPU** | Para habilitar GPU (CUDA) instalar la wheel de `llama-cpp-python` con soporte CUDA y agregar `n_gpu_layers=-1` al constructor `Llama`. |
| 5 | **Nombre del directorio** | `backend_ollama` es un nombre heredado. El código **no usa Ollama** en ninguna parte. |
| 6 | **CORS abierto** | `allow_origins=["*"]` es adecuado en desarrollo local; debe restringirse en producción. |
| 7 | **diskcache** | La dependencia está declarada en `requirements.txt` pero **no se usa** actualmente en este módulo. Puede ser para iteraciones futuras (caché de respuestas). |
