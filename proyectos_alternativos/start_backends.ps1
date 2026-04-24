# Script para iniciar los tres backends en segundo plano
# Mantiene los procesos activos sin bloquear la terminal
# Con logging habilitado

Write-Host "Iniciando backends..." -ForegroundColor Green

# Ruta del entorno virtual
$venvPath = "C:\xampp\htdocs\CiberReportes\CHAT_PLUS"
$pythonExe = "$venvPath\Scripts\python.exe"
$uvicornExe = "$venvPath\Scripts\uvicorn.exe"

# Directorio de logs
$logsDir = "C:\xampp\htdocs\CiberReportes\logs"
if (-not (Test-Path $logsDir)) {
    New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    Write-Host "Directorio de logs creado: $logsDir" -ForegroundColor Cyan
}

# Verificar que el entorno virtual existe
if (-not (Test-Path $pythonExe)) {
    Write-Host "Error: No se encontro el entorno virtual en $venvPath" -ForegroundColor Red
    exit 1
}

# Directorios de los backends
$chatbotRagDir = "C:\xampp\htdocs\CiberReportes\proyectos_alternativos\chatbot_rag_menu\backend"
$uiibotProDir = "C:\xampp\htdocs\CiberReportes\proyectos_alternativos\uiibot_pro\backend"
$uiibotUnifiedDir = "C:\xampp\htdocs\CiberReportes\proyectos_alternativos\uiibot_unified\backend_ollama"

Write-Host ""
Write-Host "Iniciando UIIBOT RAG Menu (Puerto 8000)..." -ForegroundColor Cyan
$logFile8000 = "$logsDir\backend_rag_8000.log"
Start-Process -FilePath $uvicornExe `
    -ArgumentList "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info" `
    -WorkingDirectory $chatbotRagDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput "$logsDir\backend_rag_8000_stdout.log" `
    -RedirectStandardError "$logsDir\backend_rag_8000_stderr.log"

Start-Sleep -Seconds 2

Write-Host "Iniciando El Agente Bit Pro (Puerto 8001)..." -ForegroundColor Cyan
$logFile8001 = "$logsDir\backend_pro_8001.log"
Start-Process -FilePath $uvicornExe `
    -ArgumentList "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info" `
    -WorkingDirectory $uiibotProDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput "$logsDir\backend_pro_8001_stdout.log" `
    -RedirectStandardError "$logsDir\backend_pro_8001_stderr.log"

Start-Sleep -Seconds 2

Write-Host "Iniciando Agente Bit Ollama (Puerto 8002)..." -ForegroundColor Cyan
$logFile8002 = "$logsDir\backend_ollama_8002.log"
Start-Process -FilePath $pythonExe `
    -ArgumentList "main.py" `
    -WorkingDirectory $uiibotUnifiedDir `
    -WindowStyle Hidden `
    -RedirectStandardOutput "$logsDir\backend_ollama_8002_stdout.log" `
    -RedirectStandardError "$logsDir\backend_ollama_8002_stderr.log"


Write-Host ""
Write-Host "Todos los backends han sido iniciados!" -ForegroundColor Green
Write-Host ""
Write-Host "Servicios activos:" -ForegroundColor Yellow
Write-Host "  - UIIBOT RAG Menu:      http://localhost:8000" -ForegroundColor White
Write-Host "  - El Agente Bit Pro:    http://localhost:8001" -ForegroundColor White
Write-Host "  - Agente Bit Ollama:    http://localhost:8002" -ForegroundColor White
Write-Host ""
Write-Host "Logs disponibles en:" -ForegroundColor Yellow
Write-Host "  - $logsDir\backend_rag_8000_*.log" -ForegroundColor Gray
Write-Host "  - $logsDir\backend_pro_8001_*.log" -ForegroundColor Gray
Write-Host "  - $logsDir\backend_ollama_8002_*.log" -ForegroundColor Gray
Write-Host ""
Write-Host "Para detener todos los backends, ejecuta:" -ForegroundColor Yellow
Write-Host "  .\stop_backends.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Para ver el estado, ejecuta:" -ForegroundColor Yellow
Write-Host "  .\status_backends.ps1" -ForegroundColor White
Write-Host ""
