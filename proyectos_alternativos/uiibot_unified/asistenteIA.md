# asistenteIA.md — Documentación de Implementación
## Agente Bit: Asistente de Ciberseguridad con IA Local + RAG

> **Proyecto:** `uiibot_unified`
> **Ruta:** `C:\xampp\htdocs\CiberReportes\proyectos_alternativos\uiibot_unified\`
> **Entorno activo:** `CHAT_PLUS`
> **Fecha de documentación:** 2026-04-29
> **Estado verificado:** OPERATIVO ✅

---

## 1. Visión General

**Agente Bit** es un asistente de inteligencia artificial especializado en ciberseguridad para ciudadanos y empresas mexicanas. Opera completamente **en local**, sin depender de servicios cloud ni de GPU dedicada, combinando dos tecnologías:

| Componente | Tecnología | Propósito |
|---|---|---|
| **Modelo de lenguaje** | Llama-3.2-3B-Instruct (GGUF Q4_K_M) | Generación de respuestas en lenguaje natural |
| **Base de conocimiento** | RAG + ChromaDB + Sentence Transformers | Respuestas enriquecidas con datos actualizados de México |

### Problema que resuelve

Los modelos de lenguaje base tienen un corte de conocimiento y no incluyen datos específicos de ciberseguridad en México (CERT-MX, CONDUSEF, INAI, Policía Cibernética). Sin entrenamiento especializado, el modelo respondería con información genérica o incorrecta sobre el contexto mexicano.

**Solución adoptada:** RAG (*Retrieval-Augmented Generation*) — en lugar de reentrenar el modelo (que requiere GPU), se construyó una base vectorial local con documentos curados de fuentes oficiales mexicanas que se inyectan dinámicamente en cada consulta relevante.

---

## 2. Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENTORNO CHAT_PLUS                            │
│          C:\xampp\htdocs\CiberReportes\                         │
│                                                                  │
│  Frontend PHP (index_ollama.php)                                 │
│    └─── API_OLLAMA = http://localhost:8002                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP POST /api/chat
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND — Puerto 8002                               │
│         backend_ollama/main.py (FastAPI + Uvicorn)              │
│                                                                  │
│  1. Recibe mensaje del usuario                                   │
│  2. [RAG] Busca contexto relevante en ChromaDB                  │
│  3. Construye prompt enriquecido                                 │
│  4. [LLM] llama-cpp-python genera la respuesta                  │
│  5. Retorna JSON con reply + rag_used                           │
└────────────┬────────────────────────┬───────────────────────────┘
             │                        │
             ▼                        ▼
┌────────────────────┐   ┌────────────────────────────────────────┐
│  ChromaDB          │   │  Llama-3.2-3B-Instruct (GGUF Q4_K_M)  │
│  (chroma_db/)      │   │  ~2 GB en RAM                          │
│  17 documentos     │   │  CPU-only, sin GPU                     │
│  ciberseg_mexico   │   │  n_ctx=4096, n_threads=CPU cores       │
└────────────────────┘   └────────────────────────────────────────┘
```

### Flujo RAG detallado

```
Pregunta usuario
      │
      ▼
Sentence Transformer encode()  <── paraphrase-multilingual-MiniLM-L12-v2
      │ (vector 384 dims)
      ▼
ChromaDB.query(n_results=3, distancia_coseno < 1.5)
      │
      ├── distancia < 0.8  → muy alta similitud → incluir
      ├── 0.8 - 1.2        → alta similitud → incluir
      ├── 1.2 - 1.5        → similitud moderada → incluir
      └── > 1.5            → ruido → descartar
      │
      ▼
[CONTEXTO CIBERSEGURIDAD MX]
{fragmentos relevantes}
[PREGUNTA DEL USUARIO]
{pregunta original}
      │
      ▼
llm.create_chat_completion(
    messages=[system_prompt + historial + contexto_enriquecido],
    max_tokens=256, temperature=0.7, repeat_penalty=1.1
)
      │
      ▼
Respuesta → cliente
```

---

## 3. Stack Tecnológico

### Backend
| Librería | Versión | Función |
|---|---|---|
| `fastapi` | >= 0.115.0 | Framework API REST |
| `uvicorn[standard]` | >= 0.30.0 | Servidor ASGI |
| `llama-cpp-python` | >= 0.3.0 | Inferencia GGUF en CPU |
| `chromadb` | >= 1.0.0 | Base de datos vectorial local |
| `sentence-transformers` | >= 3.0.0 | Embeddings multilingüe |
| `python-dotenv` | >= 1.0.0 | Variables de entorno |
| `pydantic` | >= 2.0.0 | Validación de datos |

### Modelo de Lenguaje
| Parámetro | Valor |
|---|---|
| **Nombre** | Llama-3.2-3B-Instruct |
| **Formato** | GGUF (Q4_K_M — cuantizado 4-bit) |
| **Repositorio** | `bartowski/Llama-3.2-3B-Instruct-GGUF` |
| **Descarga** | Automática vía HuggingFace Hub |
| **Tamaño en disco** | ~2 GB |
| **RAM requerida** | ~2.5 GB en ejecución |
| **Contexto** | 4096 tokens |

### Modelo de Embeddings
| Parámetro | Valor |
|---|---|
| **Nombre** | paraphrase-multilingual-MiniLM-L12-v2 |
| **Dimensiones** | 384 |
| **Idiomas** | 50+ idiomas (incluye español) |
| **Ejecución** | CPU (~120 MB) |

---

## 4. Estructura de Archivos

```
uiibot_unified/
│
├── README.md                   <- Guía de instalación y uso
├── asistenteIA.md              <- Este documento
├── .env.example                <- Plantilla de variables de entorno
├── .gitignore                  <- Excluye modelos y cache
├── setup.bat                   <- Instalador automático Windows
├── setup.sh                    <- Instalador automático Linux/macOS
├── Dockerfile                  <- Imagen Docker portable
├── docker-compose.yml          <- Orquestación Docker
│
└── backend_ollama/
    ├── main.py                 <- Servidor FastAPI + RAG (298 líneas)
    ├── rag_indexer.py          <- Base de conocimiento + indexador (365 líneas)
    ├── test_backend.py         <- Suite de 11 pruebas funcionales
    ├── requirements.txt        <- Dependencias Python
    ├── start_backend.bat       <- Arranque rápido Windows
    ├── modelo.MD               <- Documentación técnica del modelo
    └── chroma_db/              <- Base vectorial ChromaDB (persistente)
        ├── chroma.sqlite3      <- 385 KB — índice principal
        └── b131fd3c-.../       <- Segmentos vectoriales
```

---

## 5. Base de Conocimiento RAG

### Fuentes indexadas (17 documentos)

| ID del documento | Fuente | Categoría |
|---|---|---|
| `certmx_phishing_sat_2024` | CERT-MX UNAM 2024 | phishing |
| `certmx_phishing_imss_2024` | CERT-MX UNAM 2024 | phishing |
| `certmx_ransomware_pymes_2024` | CERT-MX UNAM 2024 | ransomware |
| `certmx_vishing_bancario_2024` | CERT-MX UNAM 2024 | vishing |
| `condusef_fraude_digital_stats_2024` | CONDUSEF 2024 | fraude_financiero |
| `condusef_smishing_2024` | CONDUSEF 2024 | smishing |
| `condusef_derechos_usuarios_banca` | CONDUSEF | derechos_usuario |
| `inai_derechos_arco` | INAI / LFPDPPP | privacidad |
| `inai_aviso_privacidad` | INAI / LFPDPPP | privacidad |
| `inai_brecha_seguridad` | INAI | privacidad |
| `policia_cibernetica_contacto` | Policía Cibernética SSPC | denuncia |
| `policia_cibernetica_sextorsion` | Policía Cibernética SSPC | sextorsion |
| `bp_contrasenas_seguras` | Buenas Prácticas | prevencion |
| `bp_wifi_publica` | Buenas Prácticas | prevencion |
| `bp_actualizaciones_seguridad` | Buenas Prácticas | prevencion |
| `stats_ciberataques_mexico_2024` | Kaspersky / IBM Security 2024 | estadisticas |
| `stats_delitos_informaticos_mexico` | Código Penal Federal México | marco_legal |

---

## 6. API Endpoints (verificados 2026-04-29)

| Método | Endpoint | Estado | Descripción |
|---|---|---|---|
| `GET` | `/health` | 200 OK | Estado del servidor, modelo y RAG |
| `POST` | `/api/chat` | 200 OK | Chat con historial + RAG |
| `GET` | `/api/rag/status` | 200 OK | Estado de ChromaDB |
| `GET` | `/api/sessions` | 200 OK | Listar sesiones activas |
| `DELETE` | `/api/session/{id}` | 200 OK | Eliminar historial de sesión |

### Respuesta real de `/health`
```json
{
  "ok": true,
  "backend": "llama-cpp-python",
  "model": "llama-3.2-3b-instruct",
  "model_file": "Llama-3.2-3B-Instruct-Q4_K_M.gguf",
  "rag": {
    "active": true,
    "documents": 17,
    "collection": "ciberseg_mexico"
  },
  "config": {
    "server_url": "https://localhost:8080",
    "api_port": "8002"
  }
}
```

---

## 7. System Prompt

```
Eres Agente Bit, un asistente especializado en ciberseguridad creado para ayudar
a ciudadanos y empresas mexicanas.

CONTEXTO MEXICO 2024-2025:
- México es el 2do país más atacado en Latinoamérica (Kaspersky 2024)
- Amenazas activas: phishing SAT/IMSS, ransomware a PYMES, fraude bancario digital,
  vishing, smishing
- Marco legal: LFPDPPP, Código Penal Federal arts. 211-bis, regulaciones CNBV
- Autoridades: CERT-MX (cert@unam.mx), CONDUSEF (800-999-8080),
  Policía Cibernética (088), INAI (800-835-4324)

TUS RESPONSABILIDADES:
- Explicar amenazas y conceptos de forma clara y accesible
- Proporcionar consejos prácticos adaptados a México
- Orientar sobre derechos ARCO (INAI) y protección de datos personales
- Guiar ante fraudes financieros digitales (CONDUSEF)
- Dar pasos concretos ante incidentes de seguridad
- Usar lenguaje profesional pero amigable, accesible para no técnicos
- Incluir números de contacto mexicanos cuando sea relevante
```

---

## 8. Gestión del Historial de Conversación

```python
# Estructura en memoria (por sesión)
conversations["session-id"] = [
    {"role": "system",    "content": SYSTEM_PROMPT},
    {"role": "user",      "content": "pregunta 1"},
    {"role": "assistant", "content": "respuesta 1"},
    ...
]

# Límite: 1 system + últimos 20 mensajes (10 intercambios)
# Al exceder 21 entradas: conservar [0] + [-20:]
```

---

## 9. Parámetros de Inferencia

```python
llm.create_chat_completion(
    messages=conversations[session_id],
    temperature=0.7,       # balance creatividad/coherencia
    top_p=0.9,             # nucleus sampling
    top_k=40,              # top-k sampling
    max_tokens=256,        # reducido de 512 para evitar loops en CPU
    repeat_penalty=1.1,    # previene repetición y generación infinita
)
```

---

## 10. Estado de Backends (verificado 2026-04-29)

| Puerto | Backend | Estado |
|---|---|---|
| **8002** | Agente Bit (llama-cpp-python + RAG) | ACTIVO |
| **8001** | Agente Pro | ACTIVO |
| **8000** | Agente RAG | ACTIVO |
| **11434** | Ollama | INACTIVO (no requerido) |

---

## 11. Resultados de Pruebas (test_backend.py)

| # | Prueba | Resultado |
|---|---|---|
| 1 | Health check | PASS |
| 2 | RAG status | PASS |
| 3 | Mensaje vacío → HTTP 400 | PASS |
| 4 | Pregunta phishing | PASS |
| 5 | Fraude bancario México | PASS |
| 6 | Phishing SAT | PASS |
| 7 | Derechos ARCO / LFPDPPP | PASS |
| 8 | Ransomware pasos concretos | PASS |
| 9 | Historial multi-turno | PASS |
| 10 | Gestión de sesiones CRUD | PASS |
| 11 | Fuera de tema (rol) | WARN* |

**Final: 10 PASS / 1 WARN / 0 FAIL**

*WARN esperado: Llama-3.2-3B sin RLHF de dominio estricto puede responder preguntas off-topic.

---

## 12. Proceso de Instalación

```bash
# 1. Instalar compilador C++ (Windows)
#    https://visualstudio.microsoft.com/visual-cpp-build-tools/

# 2. Instalar dependencias
pip install fastapi "uvicorn[standard]" python-dotenv llama-cpp-python chromadb sentence-transformers

# 3. Configurar variables de entorno
copy .env.example .env
# Editar: API_PORT_OLLAMA=8002, SERVER_URL=http://localhost

# 4. Indexar base de conocimiento RAG
cd backend_ollama
python rag_indexer.py
# Resultado: 17 documentos indexados en ChromaDB

# 5. Iniciar backend
python main.py
# Puerto: 0.0.0.0:8002
# Tiempo arranque: ~30-60 seg
```

---

## 13. Integración con CHAT_PLUS

El frontend `index_ollama.php` se conecta mediante:

```javascript
const API_OLLAMA = CONFIG.API_OLLAMA;  // http://localhost:8002

fetch(`${API_OLLAMA}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message: userMessage })
})
.then(r => r.json())
.then(data => {
    // data.reply    -> respuesta del modelo
    // data.rag_used -> true si se usó contexto RAG
});
```

CORS configurado en `main.py` con `allow_origins=["*"]`.

---

## 14. Comandos de Gestión

```bash
# Iniciar backend
python main.py

# Verificar estado
curl http://localhost:8002/health

# Estadísticas RAG
python rag_indexer.py --stats

# Agregar documentos al RAG
python rag_indexer.py

# Reiniciar RAG desde cero
python rag_indexer.py --reset

# Pruebas funcionales completas
python -X utf8 test_backend.py

# Verificación rápida (sin inferencia)
python -X utf8 test_backend.py --quick
```

---

## 15. Rendimiento en CPU

| Escenario | Tiempo |
|---|---|
| Primera carga (descarga modelo) | 5-15 min (solo primera vez) |
| Arranque del servidor | 30-60 seg |
| Generación de respuesta (4 cores) | 60-120 seg |
| Generación de respuesta (8+ cores) | 20-60 seg |
| Embedding RAG por consulta | < 1 seg |
| Consulta ChromaDB | < 0.1 seg |

Para mayor velocidad con GPU NVIDIA:
```bash
CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python --force-reinstall
```

---

## 16. Roadmap de Mejoras

| Mejora | Prioridad | Esfuerzo estimado |
|---|---|---|
| Guardrail de dominio (bloquear off-topic) | Alta | ~30 min |
| Scraper automático CERT-MX | Media | ~2 horas |
| Persistencia de historial en SQLite | Media | ~3 horas |
| Soporte GPU (CUDA) | Baja | ~10 min si hay GPU |
| Fine-tuning LoRA con dataset MX | Baja | ~8 horas (GPU cloud) |
| Autenticación de API (API Key) | Media | ~1 hora |

---

*Documentacion generada: 2026-04-29 | Sistema: CiberReportes / uiibot_unified*
