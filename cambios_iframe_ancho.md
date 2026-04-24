# 📋 Documentación de Cambios — Sesión 15/Mar/2026

> Archivos modificados: `rc.php` · `index_ollama.php`  
> Ruta base: `C:\xampp\htdocs\CiberReportes\app\Views\home\`

---

## 1. Chips movidos al Header del Widget (`rc.php`)

### 🎯 Objetivo
Mover los chips `🤖 Asistente IA` y `📖 Glosario` — que anteriormente aparecían dentro de las burbujas del chat — al `<header>` del widget flotante **Ciber Agente**, colocándolos al lado del título mediante Flexbox.

### Cambios en HTML (`rc.php` — zona del widget flotante)

**Antes:**
```html
<header>
    <div class="nova-bot-title">Ciber Agente</div>
    <div class="nova-bot-actions">
        <button id="novaBotMinBtn" ...>—</button>
        <button id="novaBotCloseBtn" ...>✕</button>
    </div>
</header>
```

**Después:**
```html
<header>
    <div class="nova-bot-title-group">
        <div class="nova-bot-title">Ciber Agente</div>
        <div class="nova-bot-ia-chip" title="Cambiar a Asistente IA (Ollama)"
             onclick="document.getElementById('novaBotFrame').contentWindow
                      .postMessage({type:'nova-switch-project', project:'ollama',
                      breadcrumb:{state:'OLLAMA', label:'Asistente IA'}}, '*')">
             🤖 Asistente IA
        </div>
        <div class="nova-bot-rag-chip" title="Consultar Glosario RAG"
             onclick="document.getElementById('novaBotFrame').contentWindow
                      .postMessage({type:'nova-switch-project', project:'rag',
                      breadcrumb:{state:'GLOSARY', label:'Glosario'}}, '*')">
             📖 Glosario
        </div>
    </div>
    <div class="nova-bot-actions">
        <button id="novaBotMinBtn" ...>—</button>
        <button id="novaBotCloseBtn" ...>✕</button>
    </div>
</header>
```

### Cambios en CSS (`rc.php` — bloque `<style>` del widget)

**Añadido:**
```css
/* Flexbox para agrupar título + chips */
.nova-bot-title-group {
    display: flex;
    align-items: center;
    gap: 8px;
    flex: 1;
    min-width: 0;
    flex-wrap: nowrap;   /* ajuste posterior del usuario */
    overflow: hidden;    /* ajuste posterior del usuario */
}

/* Chip verde — Asistente IA */
.nova-bot-ia-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 999px;
    border: 1px solid rgb(107, 142, 35);
    background: rgba(107, 142, 35, 0.25);
    color: #cfe87a;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.2s, box-shadow 0.2s;
}
.nova-bot-ia-chip:hover {
    background: rgba(107, 142, 35, 0.45);
    box-shadow: 0 0 8px rgba(107, 142, 35, 0.5);
}

/* Chip dorado — Glosario */
.nova-bot-rag-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 999px;
    border: 1px solid #b8860b;
    background: rgba(184, 134, 11, 0.2);
    color: #f0c040;
    cursor: pointer;
    white-space: nowrap;
    transition: background 0.2s, box-shadow 0.2s;
}
.nova-bot-rag-chip:hover {
    background: rgba(184, 134, 11, 0.45);
    box-shadow: 0 0 8px rgba(184, 134, 11, 0.5);
}
```

**Modificado** `.nova-bot-title`:
```css
.nova-bot-title {
    font-size: 15px;
    font-weight: 700;
    letter-spacing: .3px;
    white-space: nowrap;  /* añadido */
}
```

**Modificado** `.nova-bot-panel header` — añadido `gap: 8px`:
```css
.nova-bot-panel header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 12px;
    background: linear-gradient(135deg, #611031, #611031);
    color: #fff;
    gap: 8px; /* añadido */
}
```

### Tamaño del panel ajustado por el usuario (`rc.php`)

```css
/* Antes */
inline-size: min(380px, 92vw);
block-size: 440px;

/* Después */
inline-size: min(494px, 92vw);
block-size: 480px;
```

---

## 2. Funcionalidad de los Chips via `postMessage`

### 🎯 Objetivo
Como el widget carga `index_ollama.php` dentro de un `<iframe>`, los chips del header necesitan comunicarse con el iframe usando `window.postMessage`.

### Flujo de comunicación
```
rc.php (padre)                           index_ollama.php (iframe)
───────────────                          ─────────────────────────
[🤖 Asistente IA] onclick               window.addEventListener('message')
  └─ postMessage({                         └─ switchProject('ollama')
       type: 'nova-switch-project',         └─ updateBreadcrumb('OLLAMA','Asistente IA')
       project: 'ollama',
       breadcrumb: {state:'OLLAMA',...}
     })

[📖 Glosario] onclick                   window.addEventListener('message')
  └─ postMessage({                         └─ switchProject('rag')
       type: 'nova-switch-project',         └─ updateBreadcrumb('GLOSARY','Glosario')
       project: 'rag',
       breadcrumb: {state:'GLOSARY',...}
     })
```

### Código añadido en `index_ollama.php` (al final del `<script>`)

```javascript
// ===== Listener para chips del header del widget padre (rc.php) =====
window.addEventListener('message', (e) => {
    if (!e.data || e.data.type !== 'nova-switch-project') return;
    const { project, breadcrumb } = e.data;
    if (!project) return;
    switchProject(project);
    if (breadcrumb && breadcrumb.state && breadcrumb.label) {
        updateBreadcrumb(breadcrumb.state, breadcrumb.label);
    }
});
```

---

## 3. Eliminación del Chip `📖 Glosario` del Chat (`index_ollama.php`)

### 🎯 Objetivo
Eliminar el chip de Glosario de las burbujas del chat, conservándolo **únicamente** en el header del widget.

| Eliminado | Ubicación |
|-----------|-----------|
| Tab HTML `<div class="tab rag" id="tabRag">📚 Glosario RAG</div>` | Barra de tabs superior |
| CSS `.tab.rag:hover` y `.tab.rag.active` | Bloque de estilos |
| JS creación de `ragChip` en `addMsgWithChips()` | Burbujas del chat |
| JS listener `tabRag.onclick` | Event listeners |

---

## 4. Eliminación del Chip `🤖 Asistente IA` del Chat (`index_ollama.php`)

### 🎯 Objetivo
Eliminar el chip de Asistente IA / Agente Ollama de las burbujas del chat, conservándolo **únicamente** en el header del widget.

| Eliminado | Ubicación |
|-----------|-----------|
| Tab HTML `<div class="tab ollama" id="tabOllama">🤖 Agente Ollama</div>` | Barra de tabs superior |
| CSS `.tab.ollama:hover` y `.tab.ollama.active` | Bloque de estilos |
| JS bloque `if (currentProject === 'pro') { ollamaChip... }` | `addMsgWithChips()` |
| JS listener `tabOllama.onclick` | Event listeners |

> **Nota:** La función `switchProject('ollama')` y la lógica interna de ollama fueron **conservadas** porque el `postMessage` desde el header de `rc.php` las sigue necesitando.

---

## 5. Ajustes de Layout en `index_ollama.php` (por el usuario)

| Propiedad | Antes | Después |
|-----------|-------|---------|
| `.wrap` padding | `12px` | `8px 10px` |
| `.tabs` flex-wrap | `wrap` | `nowrap` |
| `.tabs` margin-block-end | `10px` | `8px` |
| `.tabs` padding | `8px 12px` | `6px 10px` |
| `.tabs` overflow-x | _(sin definir)_ | `auto` |
| `.composer` flex-direction | _(sin definir)_ | `row` |
| `.composer` align-items | _(sin definir)_ | `center` |
| `.composer` padding | `16px` | `10px 14px` |
| `.chips` flex-direction | _(sin definir)_ | `row` |
| `.chips` gap | `8px` | `6px` |
| `.chips` margin-block-start | `12px` | `10px` |

---

## Resumen de Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `rc.php` | Header con chips, CSS nuevos, tamaño panel |
| `index_ollama.php` | Eliminación tabs/chips/CSS RAG y Ollama del chat, listener postMessage, ajustes de layout |

---

*Generado automáticamente — 15/Mar/2026 21:05*
