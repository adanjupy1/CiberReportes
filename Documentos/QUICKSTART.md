### Probar Proxy (Opcional)
```powershell
.\test_proxy.ps1
```
## 📊 URLs de Acceso
### Backends (Directo - Para Testing)
- http://localhost:8000/health - RAG Menu
- http://localhost:8001/health - Agente Bit Pro
- http://localhost:8002/health - Agente Bit Ollama
### Via Proxy (Producción)
- http://localhost:8080/api/backend-rag/health
- http://localhost:8080/api/backend-pro/health
- http://localhost:8080/api/backend-ollama/health
### Documentación API
- http://localhost:8000/docs - RAG Menu API Docs
- http://localhost:8001/docs - Pro API Docs
- http://localhost:8002/docs - Ollama API Docs

---

## 🛠️ Comandos Útiles
### Gestión de Backends
```powershell
# Iniciar todos los backends
.\start_backends.ps1
# Ver estado de backends
.\status_backends.ps1
# Detener todos los backends
.\stop_backends.ps1
# Ver logs
.\ver_logs.ps1 -Backend all
.\ver_logs.ps1 -Backend rag -Lines 50
```
### Gestión de Apache
```powershell
# Reiniciar Apache
.\reiniciar_apache.ps1
# Verificar configuración
C:\xampp\apache\bin\httpd.exe -ts
# Ver logs de Apache
Get-Content C:\xampp\htdocs\CiberReportes\logs\apache_error.log -Tail 50
```
### Testing
```powershell
# Probar proxy reverso
.\test_proxy.ps1
# Probar health check individual
curl http://localhost:8000/health
curl http://localhost:8080/api/backend-rag/health
```

---





## 🐛 Solución Rápida de Problemas

### Backend no inicia

```powershell
# Ver logs del backend
.\ver_logs.ps1 -Backend rag

# Ver procesos Python
Get-Process python -ErrorAction SilentlyContinue

# Detener y reiniciar
.\stop_backends.ps1
.\start_backends.ps1
```

### Proxy no funciona

```powershell
# Verificar Apache
Get-Process httpd -ErrorAction SilentlyContinue

# Reiniciar Apache
.\reiniciar_apache.ps1

# Probar conectividad
.\test_proxy.ps1
```

### Puerto en uso

```powershell
# Ver qué usa el puerto 8000
Get-NetTCPConnection -LocalPort 8000

# Detener proceso
Stop-Process -Id <PID> -Force
```

---

## 📁 Estructura de Archivos Importantes

```
CiberReportes/
├── .env                              # Configuración centralizada
├── ARCHITECTURE.md                   # Documentación completa
├── logs/                            # Logs de backends y Apache
│   ├── backend_rag_8000_*.log
│   ├── backend_pro_8001_*.log
│   ├── backend_ollama_8002_*.log
│   ├── apache_error.log
│   └── apache_access.log
├── apache-config/
│   ├── httpd-ciberreportes.conf    # Config Apache proxy
│   └── README_APACHE.md             # Docs Apache
└── proyectos_alternativos/
    ├── start_backends.ps1           # Iniciar backends
    ├── stop_backends.ps1            # Detener backends
    ├── status_backends.ps1          # Estado backends
    ├── reiniciar_apache.ps1         # Reiniciar Apache
    ├── test_proxy.ps1               # Probar proxy
    └── ver_logs.ps1                 # Ver logs
```

---

## ✅ Checklist Diario

Antes de empezar a trabajar:

- [ ] Apache corriendo en XAMPP Control Panel
- [ ] Backends iniciados (`.\start_backends.ps1`)
- [ ] Health checks respondiendo (`.\status_backends.ps1`)
- [ ] Ollama corriendo (si usas backend-ollama)

---




---

## 🆘 Soporte
Si encuentras problemas:
1. Revisa logs: `.\ver_logs.ps1 -Backend all`
2. Verifica estado: `.\status_backends.ps1`
3. Prueba proxy: `.\test_proxy.ps1`
4. Consulta ARCHITECTURE.md sección Troubleshooting


