# 📋 Documentación de Sesión — CiberReportes
**Fecha:** 15 de Marzo de 2026  
**Hora:** 18:25 – 21:05 (UTC-6)  
**Entorno activo:** `C:\xampp\htdocs\CiberReportes\CHAT_PLUS`

---

## 📌 Resumen General

Durante esta sesión se resolvieron **dos tareas principales**:

1. **Inicio de los backends Python** (FastAPI/Uvicorn) usando el entorno virtual `CHAT_PLUS`.
2. **Corrección de la página principal** `http://localhost:8080/CiberReportes` que no mostraba el formulario `rc.php`, sino un listado de directorios.

---

## 🚀 Tarea 1 — Iniciar los Backends

### Scripts involucrado
| Archivo | Ruta |
|---|---|
| `start_backends.ps1` | `C:\xampp\htdocs\CiberReportes\proyectos_alternativos\start_backends.ps1` |

### Comando ejecutado
```powershell
powershell -ExecutionPolicy Bypass -File "C:\xampp\htdocs\CiberReportes\proyectos_alternativos\start_backends.ps1"
```

### ¿Qué hace el script?
El script `start_backends.ps1` inicia **tres servidores FastAPI** en segundo plano usando el entorno virtual `CHAT_PLUS`:

| Servicio | Puerto | Directorio | Ejecutable |
|---|---|---|---|
| UIIBOT RAG Menu | `8000` | `chatbot_rag_menu/backend` | `uvicorn.exe` |
| El Agente Bit Pro | `8001` | `uiibot_pro/backend` | `uvicorn.exe` |
| Agente Bit Ollama | `8002` | `uiibot_unified/backend_ollama` | `python.exe` |

### Configuración del entorno virtual (desde el script)
```powershell
$venvPath   = "C:\xampp\htdocs\CiberReportes\CHAT_PLUS"
$pythonExe  = "$venvPath\Scripts\python.exe"
$uvicornExe = "$venvPath\Scripts\uvicorn.exe"
```

### Logs generados
Todos los logs se guardan en `C:\xampp\htdocs\CiberReportes\logs\`:

```
backend_rag_8000_stdout.log
backend_rag_8000_stderr.log
backend_pro_8001_stdout.log
backend_pro_8001_stderr.log
backend_ollama_8002_stdout.log
backend_ollama_8002_stderr.log
```

### Resultado
✅ Los tres backends iniciaron correctamente en segundo plano.

---

## 🔧 Tarea 2 — Corrección de la Página Principal (`rc.php`)

### Problema detectado
Al navegar a `http://localhost:8080/CiberReportes`, Apache mostraba un **listado de directorios** en lugar del formulario de CiberReportes (`rc.php`).

### Causa raíz
El `httpd.conf` de XAMPP tenía configurado:
```apache
DocumentRoot "C:/xampp/htdocs"
```
Como el directorio físico `C:/xampp/htdocs/CiberReportes/` **existe**, Apache lo servía directamente, ignorando la carpeta `public/` donde vive el `index.php` que carga `rc.php`.

### Arquitectura del proyecto
```
C:/xampp/htdocs/CiberReportes/
├── public/              ← DocumentRoot correcto (aquí está index.php)
│   ├── index.php        ← Enrutador principal
│   ├── .htaccess        ← Rewrite rules
│   ├── css/
│   ├── js/
│   ├── img/
│   └── vendor/
├── app/
│   └── Views/
│       └── home/
│           └── rc.php   ← Vista principal (cargada por index.php)
├── CHAT_PLUS/           ← Entorno virtual Python
├── proyectos_alternativos/
├── vendor/
└── .env
```

### Flujo correcto de carga
```
http://localhost:8080/CiberReportes
        ↓
VirtualHost captura la petición
        ↓
DocumentRoot = C:/xampp/htdocs/CiberReportes/public/
        ↓
index.php (enrutador)
        ↓
app/Views/home/rc.php (vista principal)
```

---

## 📝 Archivos Modificados

### 1. `C:\xampp\apache\conf\extra\httpd-vhosts.conf`

**Antes:** Solo comentarios de ejemplo, sin configuración activa.

**Después:** Se agregó un `VirtualHost` para mapear el puerto 8080 al directorio `public/`:

```apache
# =========================================
# CiberReportes VirtualHost
# http://localhost:8080 y http://localhost:8080/CiberReportes
# sirven desde C:/xampp/htdocs/CiberReportes/public
# =========================================
<VirtualHost *:8080>
    ServerName localhost
    DocumentRoot "C:/xampp/htdocs/CiberReportes/public"

    <Directory "C:/xampp/htdocs/CiberReportes/public">
        Options Indexes FollowSymLinks Includes ExecCGI
        AllowOverride All
        Require all granted
        DirectoryIndex index.php
    </Directory>

    # Redirigir /CiberReportes y /CiberReportes/ a la raiz del sitio
    RedirectMatch ^/CiberReportes/?$ /

    ErrorLog  "C:/xampp/htdocs/CiberReportes/logs/apache_error.log"
    CustomLog "C:/xampp/htdocs/CiberReportes/logs/apache_access.log" combined
</VirtualHost>
```

**¿Por qué VirtualHost y no Alias?**  
Se intentó primero con `Alias /CiberReportes "..."` pero Apache ignoraba el Alias porque el directorio físico `CiberReportes/` existe bajo el `DocumentRoot` real, y Apache prioriza el directorio físico sobre el Alias. El VirtualHost sobreescribe el `DocumentRoot` para todo el puerto 8080.

---

### 2. `C:\xampp\htdocs\CiberReportes\public\.htaccess`

**Antes:**
```apache
RewriteEngine On

# Excluir /api/rag/ del rewrite (para proxy backend)
RewriteCond %{REQUEST_URI} !^/api/rag/

# Excluir proyectos_alternativos del rewrite
RewriteCond %{REQUEST_URI} !^/proyectos_alternativos/

# Solo reescribir si no es un archivo o directorio existente
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d

RewriteRule ^ index.php [QSA,L]
```

**Después:**
```apache
RewriteEngine On
RewriteBase /

# Excluir /api/rag/ del rewrite (para proxy backend)
RewriteCond %{REQUEST_URI} !^/api/rag/

# Excluir proyectos_alternativos del rewrite
RewriteCond %{REQUEST_URI} !^/proyectos_alternativos/

# Solo reescribir si no es un archivo o directorio existente
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d

RewriteRule ^ index.php [QSA,L]
```

**Cambio:** Se añadió `RewriteBase /` (antes no existía, después se intentó `/CiberReportes` y finalmente se dejó en `/` porque el `DocumentRoot` del VirtualHost ya apunta a `public/`, por lo que la base correcta es la raíz `/`).

---

## 🔄 Proceso de reinicio de Apache

El reinicio con `-k restart` no aplicaba los cambios del VirtualHost en ocasiones (el proceso no se terminaba completamente). La solución fue:

```powershell
# Matar todos los procesos httpd existentes
Stop-Process -Name "httpd" -Force -ErrorAction SilentlyContinue

# Esperar 2 segundos
Start-Sleep -Seconds 2

# Relanzar Apache con la configuración correcta
Start-Process -FilePath "C:\xampp\apache\bin\httpd.exe" `
    -ArgumentList "-f", "C:\xampp\apache\conf\httpd.conf" `
    -WindowStyle Hidden
```

---

## ✅ Resultado Final

| URL | Resultado |
|---|---|
| `http://localhost:8080/CiberReportes` | ✅ Redirige a `/` y muestra el formulario `rc.php` |
| `http://localhost:8080/` | ✅ Muestra el formulario `rc.php` directamente |
| `http://localhost:8080/CiberReportes/public/` | ✅ También funciona (ruta directa) |
| `http://localhost:8000` | ✅ Backend RAG activo |
| `http://localhost:8001` | ✅ Backend Pro activo |
| `http://localhost:8002` | ✅ Backend Ollama activo |

---

## ⚠️ Consideraciones Importantes

> **Para próximos reinicios de Apache:** Si reinicias Apache desde el panel de XAMPP o desde la línea de comandos, los cambios en `httpd-vhosts.conf` se mantienen porque el archivo fue editado permanentemente. No es necesario volver a ejecutar los comandos.

> **Para próximos arranques del sistema:** Los backends Python **no se inician automáticamente** al arrancar Windows. Deberás ejecutar `start_backends.ps1` manualmente cada vez que reinicies el equipo (o configurar una tarea programada).

---

## 🗂️ Scripts de gestión de backends

| Script | Función |
|---|---|
| `start_backends.ps1` | Inicia los 3 backends en segundo plano |
| `stop_backends.ps1` | Detiene todos los backends |
| `status_backends.ps1` | Muestra el estado de los backends |

Todos ubicados en: `C:\xampp\htdocs\CiberReportes\proyectos_alternativos\`

---

*Documentación generada el 15/03/2026 — Sesión de configuración Apache + Backends CiberReportes*
