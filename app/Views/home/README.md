# Flujo: Agente Pro (`index_pro`) en `index_ollama.php`
---
## 1. Estructura de la interfaz (dónde aparece en `index_ollama.php`)
### 1.1 Tabs de navegación principal
**Ubicación:** `index_ollama.php` › bloque HTML `<div class="tabs">` (~línea 556)
```
 ┌──────────────────┬──────────────────────┬───────────────────────┐
 │  🔒 Agente Pro   │   📚 Glosario RAG   │  🤖 Agente Ollama     │
 │  (tab activo)    │   (tab.rag)          │  (tab.ollama)         │
 └──────────────────┴──────────────────────┴───────────────────────┘
 tabPro  ←── breadcrumb dinámico de navegación
```
El tab `tabPro` también sirve como **breadcrumb**: muestra la ruta de navegación actual y al hacer clic regresa al inicio.
---
### 1.2 Chips fijos de contexto Pro
**Ubicación:** función `addMsgWithChips()` en JS (~línea 704)  
Siempre presentes cuando `currentProject === 'pro'`:
 
| Chip               | Color/Borde              | Acción al clic                                          |
|--------------------|--------------------------|-------------------------------------------------------- |
| `📖 Glosario`     | dorado (`--accent-rag`)   | `switchProject('rag')` + breadcrumb GLOSARY             |
| `🤖 Asistente IA` | verde (`#6b8e23`)         |     `switchProject('ollama')` + breadcrumb OLLAMA       |
| `Formulario ciber` | morado (`añadir`)        |     `switchProject('ciberChat')` + breadcrumb CIBER |  # Integrar el proyecto chatBot
---
### 1.3 Chip de retorno (en modos RAG / Ollama)
**Ubicación:** función `addMsgWithChips()` en JS (~línea 733)  
Aparece cuando `currentProject === 'rag'` o `=== 'ollama'` o  `=== 'ciberChat'` :

| Chip                | Color/Borde             | Acción al clic                           |
|---------------------|-------------------------|------------------------------------------|
| `🏠 Volver a Menú` | morado (`--accent-pro`) | `switchProject('pro')` + breadcrumb ROOT |
--- 
### 1.4 Quick replies del backend (chips dinámicos)
**Ubicación:** función `addMsgWithChips()` en JS (~línea 746, `forEach`)  
Son los chips que llegan en `data.quick_replies` de la respuesta del backend Pro (puerto 8001).  
Al hacer clic, se ejecuta `send(label)` enviando el texto del chip como mensaje.
---
### 1.5 Cuadro de ayuda IA (solo en mensaje de bienvenida)
**Ubicación:** función `addMsgWithChips()` en JS (~línea 653)  
Aparece cuando el mensaje incluye `'Soy Agente Bit'`:
```
🤖 Asistente IA: Si eliges esta opción, podrás hacer consultas generales de seguridad.
```
(burbuja verde, `maxWidth: 300px`, marca `data-project="PRO"`)
---
### 1.6 Breadcrumb dinámico (`updateBreadcrumb`)
**Ubicación:** función `updateBreadcrumb(state, label)` en JS (~línea 825)

Mapa de estados → íconos:
| Estado                 | Ícono|
|------------------------|------|
| `ROOT`                 |  🏠  |
| `MENU`                 |  📋  |
| `CONSEJOS`             |  💡  |
| `AMENAZAS`             |  ⚠️  |
| `REPORTE`              |  📝  |
| `CIBERATAQUES`         |  🔒  |
| `DIRECTORIO`           |  📞  |
| `CATEGORIA`            |  📂  |
| `PREGUNTA`             |  ❓  |
| `GLOSARY`              |  📖  |
| *(otros)* | ícono contextual dinámico (ciberseguridad, dispositivos, etc.) |
---
### 1.7 Inicialización automática
**Ubicación:** bloque `(async () => { ... })()` al final del JS (~línea 1270)
```js
setTimeout(() => send("menu"), 500);
```
Al cargar la página, envía `"menu"` automáticamente al backend Pro (puerto 8001) y se muestra el menú raíz.
---

## -------------------------------------------------------------------------------------------------------------##

## 2. Flujo completo de estados del backend Pro (puerto 8001)
### Estado: `ROOT` / Inicio
**Llega cuando:** se envía `"menu"`, `"inicio"`, `"start"`, `"home"` (o al inicio).  
**Respuesta del bot:** `¡Hola! Soy Agente Bit, tu asistente virtual de ciberseguridad...`

**Chips (quick_replies → `ROOT_OPTIONS`):**

| # | Chip                                | Siguiente estado         |
|---|-------------------------------------|--------------------------|
| 1 | `Consejos de ciberseguridad`        | `Seguridad`              |
| 2 | `Detectar ciberamenazas`            | `Amenazas`               |
| 3 | `Reportar un incidente cibernético` | `Nombre` (formulario)    |
| 4 | `Saber sobre ciberataques`          |     `Ciberataques`       |
| 5 | `Busca el número de tu Policía Cibernética` | `Estado Policía` |

**Chips fijos de contexto (siempre en modo Pro):**  
`📖 Glosario` · `🤖 Asistente IA`
---

### Estado: `Seguridad` (Consejos de ciberseguridad)
**Llega desde:** chip `1` o palabras clave como `"contraseña"`, `"phishing"`.

**Chips (quick_replies → `SECURITY_TIPS_MENU` + `"Volver al menú"`):**
|                         Chip                          |         Siguiente estado / resultado       |
|-------------------------------------------------------|--------------------------------------------|
| `¿Cómo puedo crear una contraseña segura?`            |    `Respuesta` (mensaje + footer)          |
| `¿Cada cuánto debo cambiar mi contraseña?`            |    `Confirmar Contraseña` (pregunta Sí/No) |
| `¿Es seguro conectarme a una red Wi‑Fi pública?`      |    `Respuesta` (mensaje + footer)          |
| `¿Cómo protejo mi cuenta de redes sociales?`          |    `Confirmar Contraseña` (pregunta Sí/No) |
| `¿Qué antivirus recomiendas?`                         |    `Respuesta` (mensaje + footer)          |
| `¿Cómo identifico un correo falso (phishing)?`        |    `Phishing`                              |
| `Otro`                                                | Info contextual (permanece en `Seguridad`) |
| `Volver al menú`                                      |                  `ROOT`                    |

#### Sub-estado: `Confirmar Contraseña`
Chips: `Sí` · `No` · `Menú`  
→ `Sí`: muestra cómo crear contraseña segura → `Respuesta`  
→ `No`: regresa a `ROOT`
#### Sub-estado: `Phishing`
Muestra señales de phishing.  
Chips: `No` · `Menú`
#### Sub-estado: `Respuesta`
Chips: `Menú` · `Cerrar`
---

### Estado: `Amenazas` (Detectar ciberamenazas)
**Llega desde:** chip `2`.
**Chips (quick_replies → `THREAT_MENU` + `"Volver al menú"`):**

| Chip                                             |      Siguiente estado / resultado           |
|--------------------------------------------------|---------------------------------------------|
| `Creo que recibí un correo falso, ¿cómo lo sé?`  | `Solicitar Reporte` (chips: `No` · `Menú`)  |
| `¿Puedo revisar si un enlace es peligroso?`      | `Respuesta` (mensaje + footer)              |
| `Mi computadora está más lenta, ¿será un virus?` | `Respuesta` (mensaje + footer)              |
| `¿Qué hago si descargué un archivo sospechoso?`  | `Solicitar Reporte` (chips: `No` · `Menú`)  |
| `Otro`                                           | Info contextual (permanece en `Amenazas`)   |
| `Volver al menú`                                 |                    `ROOT`                   |

#### Sub-estado: `Solicitar Reporte`
Chips: `No` · `Menú`  
→ Si el usuario confirma: inicia el formulario de reporte → `Nombre`
---

### Estado: `Ciberataques` (Saber sobre ciberataques)
**Llega desde:** chip `4`.
**Chips (quick_replies → `CYBERATTACKS_MENU` + `"Volver al menú"`):**

| Chip                           | Tema devuelto                 | Siguiente estado    |
|--------------------------------|-------------------------------|---------------------|
| `¿Qué es el phishing?`         | 🎣 Explicación de phishing    |   `Respuesta`       |
| `¿Qué es el ransomware?`       | 🔒 Explicación de ransomware  |   `Respuesta`       |
| `¿Cómo puedo evitar malware?`  | 🦠 Explicación de malware     |   `Respuesta`       |
| `¿Qué es la ingeniería social?`| 🧠 Explicación                |   `Respuesta`       |
| `Volver al menú` | — | `ROOT`  |

---

### Estado: `Estado Policía` (Directorio)
**Llega desde:** chip `5`.

**Chips iniciales:**  
`CDMX` · `Jalisco` · `Estado de México` · `Nuevo León` · `Veracruz` · `Volver al menú`

Tras seleccionar un estado → muestra contactos (tel., WhatsApp, email, web).  
**Chips tras resultado:**  
`Buscar otro Estado` · `Volver al menú`

---

### 🗂️ Formulario de Reporte (flujo secuencial)
**Llega desde:** chip `3` ("Reportar un incidente cibernético") o desde `Solicitar Reporte`.

| Estado | Pregunta del bot | Chips disponibles |
|--------|-----------------|-------------------|
| `Nombre` | ¿Nombre completo? | `Anónimo` · `Volver al menú` |
| `Estado` | ¿En qué Estado resides? | `CDMX` · `Jalisco` · `Estado de México` · `Nuevo León` · `Veracruz` · `Volver al menú` |
| `Edad` | ¿Cuál es tu edad? | `Volver al menú` |
| `Sexo` | Sexo (opcional) | `Femenino` · `Masculino` · `Prefiero no decir` · `Volver al menú` |
| `Tipo Reporte` | Elige tipo de incidente | ver tabla abajo |
| `Descripción` *(solo ciertos tipos)* | Describe lo sucedido | `Volver al menú` |
| `Orientación` | Orientación según tipo | `Sí` · `No` · `Menú` *(varía)* |
| `Cierre Reporte` | Datos del reporte + cierre | `Menú` · `Buscar Policía Cibernética` · `Cerrar` |

#### Chips de la pregunta "Tipo Reporte" (`INCIDENT_TYPES`):

| # | Chip | Guidance / Siguiente estado |
|---|------|----------------------------|
| 1 | `Correo sospechoso` | 📩 Phishing → `Orientación` (Sí/No/Menú) |
| 2 | `Acceso no autorizado` | 🔐 Cambio de contraseña + 2FA → `Orientación` |
| 3 | `Acoso Cibernético` | 🧩 ¿Redes sociales o físico? → (Redes sociales/Físicamente/Menú) |
| 4 | `Víctima de Extorsión` | ⚠️ Recomendaciones urgentes → `Descripción` → `Orientación` |
| 5 | `Víctima de Ciberamenazas` | ⚠️ Igual que Extorsión → `Descripción` → `Orientación` |
| 6 | `Víctima de fraude` | 💳 Contacto banco + policía → `Orientación` (Sí/No/Menú) |
| 7 | `Robo a transeúnte` | 📱 Pérdida/robo dispositivo → `Orientación` (Sí/No/Menú) |
| 8 | `Otro` | 📝 Incidente genérico → `Descripción` → `Orientación` |
| — | `Volver al menú` | `ROOT` |

> **Nota:** en el estado `Orientación` con respuesta `Sí`, el bot proporciona el número de Policía Cibernética del estado registrado en el formulario.  
> El ID del reporte tiene formato: `AgentBit/{código_estado}/{seq}/{MesAño}` (ej. `AgentBit/QRO/01/Mar26`).

---

## 3. Mapa visual del flujo Pro

```
[Carga de página]
        │
        ▼ (500ms)
  send("menu")  ──────────────────────────────────────────────────────────────┐
        │                                                                      │
        ▼                                                                      │
┌────────────────────────────────────────────────────────────────┐            │
│  ROOT: "¡Hola! Soy Agente Bit..."                              │            │
│                                                                │            │
│  CHIPS:                                                        │            │
│  ┌───────────────────────────────────┐                        │            │
│  │ Consejos de ciberseguridad    [1] │──► SEGURIDAD           │            │
│  │ Detectar ciberamenazas        [2] │──► AMENAZAS            │            │
│  │ Reportar un incidente...      [3] │──► FORMULARIO          │            │
│  │ Saber sobre ciberataques      [4] │──► CIBERATAQUES        │            │
│  │ Busca el número de tu Policía [5] │──► EST. POLICÍA        │            │
│  └───────────────────────────────────┘                        │            │
│  ┌────────────────┐  ┌──────────────────┐                     │            │
│  │ 📖 Glosario    │  │  🤖 Asistente IA │  (fijos en Pro)     │            │
│  └───────┬────────┘  └────────┬─────────┘                     │            │
└──────────┼────────────────────┼───────────────────────────────┘            │
           │                    │                                             │
           ▼                    ▼                                             │
    switchProject             switchProject                                   │
       ('rag')                 ('ollama')                                     │
    [Glosario RAG]           [Asistente IA]                                   │
    🏠 Volver a Menú ────────────────────────────────────────────────────────┘


SEGURIDAD ──► 7 chips (consejos) ──► Respuesta / Confirmar Contraseña / Phishing
                                           │
                                     Chips: Menú · Cerrar / Sí · No · Menú

AMENAZAS ───► 5 chips (amenazas) ──► Respuesta / Solicitar Reporte
                                           │
                                     Chips: Menú · Cerrar / No · Menú

CIBERATAQUES ► 4 chips (ataques) ──► Respuesta
                                           │
                                     Chips: Menú · Cerrar

EST. POLICÍA ► Chips de estados ───► Contactos por estado
                                           │
                                     Chips: Buscar otro Estado · Volver al menú

FORMULARIO ──► Nombre ──► Estado ──► Edad ──► Sexo ──► Tipo Reporte
                                                              │
                                              8 tipos de incidente
                                                              │
                                           ──► Orientación (guía + Sí/No/Menú)
                                                              │
                                           ──► Cierre Reporte (ID generado)
                                                              │
                                             Chips: Menú · Buscar Policía · Cerrar
```

---

## 4. Resumen de todos los chips / etiquetas

### Chips de navegación global (tabs)
| Elemento | Tipo | Línea aprox. `index_ollama.php` |
|----------|------|----------------------------------|
| `🔒 Agente Pro` | `<div class="tab pro active">` | ~L557 HTML, `tabPro` JS ~L601 |
| `📚 Glosario RAG` | `<div class="tab rag">` | ~L560 HTML, `tabRag` JS ~L603 |
| `🤖 Agente Ollama` | `<div class="tab ollama">` | ~L563 HTML, `tabOllama` JS ~L605 |

### Chips fijos en modo Pro (en `addMsgWithChips`)
| Elemento | Línea aprox. JS |
|----------|----------------|
| `📖 Glosario` | ~L706 |
| `🤖 Asistente IA` | ~L717 |

### Chip de retorno (en modos RAG / Ollama)
| Elemento | Línea aprox. JS |
|----------|----------------|
| `🏠 Volver a Menú` | ~L733 |

### Quick replies dinámicos (del backend Pro)
| Conjunto | Chips |
|----------|-------|
| `ROOT_OPTIONS` | Consejos · Detectar · Reportar · Ciberataques · Policía |
| `SECURITY_TIPS_MENU` | 6 preguntas de seguridad + Otro + Volver |
| `THREAT_MENU` | 4 amenazas + Otro + Volver |
| `CYBERATTACKS_MENU` | Phishing · Ransomware · Malware · Ingeniería social + Volver |
| `INCIDENT_TYPES` | 8 tipos de incidente + Volver |
| Directorio | CDMX · Jalisco · EdoMex · Nuevo León · Veracruz · Volver |
| Post-resultado | Buscar otro Estado · Volver |
| Post-consejo | Menú · Cerrar |
| Post-amenaza | No · Menú |
| Confirmar | Sí · No · Menú |
| Orientación | Sí · No · Menú (varía por tipo) |
| Cierre | Menú · Buscar Policía Cibernética · Cerrar |
| Sexo | Femenino · Masculino · Prefiero no decir · Volver |

---

## 5. Archivos relacionados

| Archivo | Rol |
|---------|-----|
| [index_ollama.php](index_ollama.php) | Vista unificada — contiene tabs Pro/RAG/Ollama, chips JS y lógica de cambio de proyecto |
| [index.php](index.php) | Selector inicial — tarjetas de acceso a Pro, RAG y plataforma Unificada |
| `proyectos_alternativos/uiibot_pro/backend/app/engine.py` | Lógica de estados y chips de Pro (backend puerto 8001) |
| `proyectos_alternativos/uiibot_pro/backend/app/content.py` | Textos y listas de chips (ROOT_OPTIONS, SECURITY_TIPS_MENU, etc.) |
| `proyectos_alternativos/uiibot_pro/backend/app/main.py` | FastAPI endpoint `/api/chat` que devuelve `state` + `quick_replies` |
