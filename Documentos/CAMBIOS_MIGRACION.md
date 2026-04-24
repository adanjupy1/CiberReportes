
## 🎯
Mover las vistas de Agente Bit desde `public/proyectos_alternativos/vistas/` a `app/Views/home/` para integrarlas en el flujo de rc.php.
## 📦
| Archivo Original | Nueva Ubicación | Estado |
|-----------------|-----------------|---------|
| `public/proyectos_alternativos/vistas/index.php` | `app/Views/home/index.php` | ✅ Movido |
| `public/proyectos_alternativos/vistas/index_ollama.php` | `app/Views/home/index_ollama.php` | ✅ Movido |
| `public/proyectos_alternativos/vistas/index_pro.php` | `app/Views/home/index_pro.php` | ✅ Movido |
| `public/proyectos_alternativos/vistas/index_rag.php` | `app/Views/home/index_rag.php` | ✅ Movido |
## 🔧
### 1. ViewsController.php
**Ubicación:** `app/Controllers/ViewsController.php`

**Métodos añadidos:**
```php
public function Index() {
    require_once __DIR__ . '/../Views/home/index.php';
}

public function IndexOllama() {
    require_once __DIR__ . '/../Views/home/index_ollama.php';
}

public function IndexPro() {
    require_once __DIR__ . '/../Views/home/index_pro.php';
}

public function IndexRag() {
    require_once __DIR__ . '/../Views/home/index_rag.php';
}

public function TestRoutes() {
    require_once __DIR__ . '/../Views/home/test_routes.php';
}
```
### 2. .env
**Ubicación:** `.env`
**Variables modificadas:**
```env
# Antes
ASSISTANT_IFRAME_PATH=/proyectos_alternativos/vistas/index_ollama.php
# Después
ASSISTANT_IFRAME_PATH=/Views/IndexOllama
```
---
### Acceso a través del Enrutador
| URL                                      |    Descripción          |           Archivo                 |
|                                          |                         |                                   |
| `http://localhost:8080/`                 | Formulario RC(Principal)|  `app/Views/home/rc. php`         |
| `http://localhost:8080/Views/Index`      | Selector de Interfaces  |  `app/Views/home/index.php`       |
| `http://localhost:8080/Views/IndexOllama`| Plataforma Unificada    |  `app/Views/home/index_ollama.php`|
| `http://localhost:8080/Views/IndexPro`   | Agente Bit Pro          |  `app/Views/home/index_pro.php`   |
| `http://localhost:8080/Views/IndexRag`   | Glosario RAG            |  `app/Views/home/index_rag.php`   |
| `http://localhost:8080/Views/TestRoutes` | Página de Prueba        |  `app/Views/home/test_routes.php` |
---
## 🔗 Integración con rc.php
El botón flotante del asistente en `rc.php` ahora carga dinámicamente la URL desde `.env`:
```html
<iframe id="novaBotFrame" class="nova-bot-iframe" 
        src="<?php echo $assistantPath; ?>" 
        title="Asistente en línea">
</iframe>
```
Donde `$assistantPath = '/Views/IndexOllama'` (cargado desde `.env`)


## 📡 Backends y APIs
Los backends siguen funcionando igual a través de Apache:
|   Backend   |  Puerto | Proxy Apache          |   Estado  |
|-------------|---------|-----------------------|-----------|
|   RAG Menu  |  8000   | `/api/backend-rag`    |   Online  |
|   Bit Pro   |  8001   | `/api/backend-pro`    |   Online  |
|   Ollama    |  8002    | `/api/backend-ollama`|   Online  |
## 📋 Archivos Nuevos Creados

1. **README_VISTAS_AGENTE_BIT.md**
   - Ubicación: `app/Views/home/`
   - Contenido: Documentación completa de las rutas y configuración
2. **test_routes.php**
   - Ubicación: `app/Views/home/`
   - Contenido: Página de prueba con enlaces a todas las vistas y estado de backends
3. **CAMBIOS_MIGRACION.md** (este archivo)
   - Ubicación: `app/Views/home/`
   - Contenido: Resumen de todos los cambios realizados



### Pasos para Verificar la Migración:
1. **Probar la página de prueba:**
   http://localhost:8080/Views/TestRoutes
2. **Verificar rc.php:**
   - Acceder a: `http://localhost:8080/`
   - Hacer clic en el botón flotante 🤖
   - Debería abrir el iframe con la Plataforma Unificada

3. **Probar cada vista individualmente:**
   - Index: `http://localhost:8080/Views/Index`
   - Ollama: `http://localhost:8080/Views/IndexOllama`
   - Pro: `http://localhost:8080/Views/IndexPro`
   - RAG: `http://localhost:8080/Views/IndexRag`
4. **Verificar backends:**
   - Todos deberían responder con estado 200
   - La página de prueba muestra el estado en tiempo real
## 🎨 Estructura de Directorios
CiberReportes/
├── app/
│   ├── Controllers/
│   │   └── ViewsController.php ✅ Actualizado
│   └── Views/
│       └── home/
│           ├── rc.php (existente)
│           ├── index.php ✅ Movido
│           ├── index_ollama.php ✅ Movido
│           ├── index_pro.php ✅ Movido
│           ├── index_rag.php ✅ Movido
│           ├── test_routes.php ✅ Nuevo
│           ├── README_VISTAS_AGENTE_BIT.md ✅ Nuevo
│           └── CAMBIOS_MIGRACION.md ✅ Nuevo
├── public/
│   ├── index.php (enrutador principal)
│   └── proyectos_alternativos/
│       ├── frontend/
│       │   └── config.js (sin cambios)
│       └── vistas/ (vacío, puede eliminarse)
└── .env ✅ Actualizado

### Iniciar Backends
```powershell
& "C:\xampp\htdocs\CiberReportes\CHAT_PLUS\Scripts\Activate.ps1"
& "C:\xampp\htdocs\CiberReportes\proyectos_alternativos\start_backends.ps1"
```
### Detener Backends
```powershell
cd C:\xampp\htdocs\CiberReportes\proyectos_alternativos
.\stop_backends.ps1
```
### Ver Estado de Backends
```powershell
cd C:\xampp\htdocs\CiberReportes\proyectos_alternativos
.\status_backends.ps1
```
## 📚 Documentación Relacionada
- [README_VISTAS_AGENTE_BIT.md](README_VISTAS_AGENTE_BIT.md): Documentación completa
- [test_routes.php](http://localhost:8080/Views/TestRoutes): Página de prueba interactiva

## 🌐 URLs de Acceso
### Forma 1: A través del Controlador (Recomendado)
Accede a las vistas mediante el enrutador de la aplicación:
http://localhost:8080/Views/Index
http://localhost:8080/Views/IndexOllama
http://localhost:8080/Views/IndexPro
http://localhost:8080/Views/IndexRag
#### 🏠 Index Principal
**URL:** `http://localhost:8080/Views/Index`
**Archivo:** `app/Views/home/index.php`
**Descripción:** Página principal con selector visual de las tres interfaces de Agente Bit, incluye indicadores de estado en tiempo real.
#### 🤖 Index Ollama (Unified)
**URL:** `http://localhost:8080/Views/IndexOllama`
**Archivo:** `app/Views/home/index_ollama.php`
**Descripción:** Plataforma unificada con acceso a los tres backends (Pro, RAG, Ollama) desde una sola interfaz con tabs.
#### 🔒 Index Pro
**URL:** `http://localhost:8080/Views/IndexPro`
**Archivo:** `app/Views/home/index_pro.php`
**Descripción:** Chatbot especializado con menús interactivos para reportes de ciberseguridad y directorio de Policía Cibernética.
#### 📚 Index RAG
**URL:** `http://localhost:8080/Views/IndexRag`
**Archivo:** `app/Views/home/index_rag.php`
**Descripción:** Sistema de consulta inteligente con búsqueda semántica en glosario de términos de ciberseguridad.
## 🔧 Variables de Entorno (.env)
```env
# Frontend Config
CONFIG_JS_PATH=/proyectos_alternativos/frontend/config.js
ASSISTANT_IFRAME_PATH=/Views/IndexOllama
```
## 📡 Integración con rc.php
El botón flotante del asistente en `rc.php` ahora apunta a:
```html
<iframe src="<?php echo $assistantPath; ?>" title="Asistente en línea"></iframe>
```
Donde `$assistantPath` carga desde `.env`:
```php
$assistantPath = getEnvOrDefault('ASSISTANT_IFRAME_PATH', '/Views/IndexOllama');
```
## 🌐 Backends y Proxies
Todos los backends siguen funcionando igual a través de Apache:
```apache
# Backend RAG (Puerto 8000)
ProxyPass /api/backend-rag http://localhost:8000
ProxyPassReverse /api/backend-rag http://localhost:8000
# Backend Pro (Puerto 8001)
ProxyPass /api/backend-pro http://localhost:8001
ProxyPassReverse /api/backend-pro http://localhost:8001
# Backend Ollama (Puerto 8002)
ProxyPass /api/backend-ollama http://localhost:8002
ProxyPassReverse /api/backend-ollama http://localhost:8002
```
## 📝 Rutas de Assets
Las vistas acceden a los recursos en `public/` mediante rutas absolutas:
- CSS: `/css/`
- JS: `/js/`
- Images: `/img/`
- Vendor: `/vendor/`
- Config: `/proyectos_alternativos/frontend/config.js`

# Activar entorno virtual y ejecutar
& "C:\xampp\htdocs\CiberReportes\CHAT_PLUS\Scripts\Activate.ps1"
& "C:\xampp\htdocs\CiberReportes\proyectos_alternativos\start_backends.ps1"

## 🔗 Flujo de Acceso desde rc.php
1. Usuario accede a: `http://localhost:8080/`
2. Se carga `rc.php` (formulario de reportes)
3. El botón flotante 🤖 en `rc.php` abre el iframe con:
   - URL: `/Views/IndexOllama`
   - Vista: Plataforma Unificada de Agente Bit
4. Usuario puede interactuar con los 3 backends desde el iframe

