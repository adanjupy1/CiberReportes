# Script para verificar el estado de los backends
# Comprueba si los procesos están activos y si responden en sus puertos

# Configurar codificación UTF-8 para la salida
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "Verificando estado de backends..." -ForegroundColor Cyan
Write-Host ""

# Verificar procesos
$processes = Get-Process -Name python, uvicorn -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*CHAT_PLUS*"
}

Write-Host "===============================================" -ForegroundColor DarkGray
Write-Host "PROCESOS ACTIVOS" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor DarkGray

if ($processes) {
    foreach ($proc in $processes) {
        $uptime = (Get-Date) - $proc.StartTime
        Write-Host "[OK] PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor Green
        Write-Host "  Tiempo activo: $([int]$uptime.TotalMinutes) minutos" -ForegroundColor Gray
        Write-Host "  Memoria: $([math]::Round($proc.WorkingSet64/1MB, 2)) MB" -ForegroundColor Gray
    }
} else {
    Write-Host "[X] No hay procesos activos" -ForegroundColor Red
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor DarkGray
Write-Host "CONECTIVIDAD DE SERVICIOS" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor DarkGray

# Verificar conectividad a cada puerto
$services = @(
    @{Name="UIIBOT RAG Menu"; Port=8000; Url="http://localhost:8000/health"},
    @{Name="El Agente Bit Pro"; Port=8001; Url="http://localhost:8001/health"},
    @{Name="Agente Bit Ollama"; Port=8002; Url="http://localhost:8002/health"}
)

foreach ($service in $services) {
    try {
        $response = Invoke-RestMethod -Uri $service.Url -Method GET -TimeoutSec 3 -ErrorAction Stop
        Write-Host "[OK] $($service.Name)" -ForegroundColor Green
        Write-Host "  URL: $($service.Url)" -ForegroundColor Gray
        Write-Host "  Estado: Respondiendo correctamente" -ForegroundColor Gray
    }
    catch {
        # Verificar si al menos el puerto está escuchando
        $conn = Get-NetTCPConnection -LocalPort $service.Port -State Listen -ErrorAction SilentlyContinue
        if ($conn) {
            Write-Host "[!] $($service.Name)" -ForegroundColor Yellow
            Write-Host "  URL: $($service.Url)" -ForegroundColor Gray
            Write-Host "  Puerto activo pero no responde al health check" -ForegroundColor Gray
        }
        else {
            Write-Host "[X] $($service.Name)" -ForegroundColor Red
            Write-Host "  URL: $($service.Url)" -ForegroundColor Gray
            Write-Host "  Estado: No responde" -ForegroundColor Gray
        }
    }
    Write-Host ""
}

Write-Host "===============================================" -ForegroundColor DarkGray
Write-Host "LOGS RECIENTES" -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor DarkGray

$logsDir = "C:\xampp\htdocs\CiberReportes\logs"
if (Test-Path $logsDir) {
    $logFiles = Get-ChildItem "$logsDir\backend_*stderr.log" -ErrorAction SilentlyContinue | 
                Sort-Object LastWriteTime -Descending
    
    if ($logFiles) {
        Write-Host "Archivos de log disponibles:" -ForegroundColor Gray
        foreach ($log in $logFiles) {
            Write-Host "  - $($log.Name) (Última modificación: $($log.LastWriteTime))" -ForegroundColor Gray
        }
    }
    else {
        Write-Host "No hay archivos de log disponibles" -ForegroundColor Gray
    }
}
else {
    Write-Host "Directorio de logs no existe" -ForegroundColor Gray
}

Write-Host ""
Write-Host "===============================================" -ForegroundColor DarkGray
Write-Host "`nComandos disponibles:" -ForegroundColor Cyan
Write-Host "  .\start_backends.ps1  - Iniciar todos los backends" -ForegroundColor White
Write-Host "  .\stop_backends.ps1   - Detener todos los backends" -ForegroundColor White
Write-Host "  .\status_backends.ps1 - Ver este estado" -ForegroundColor White
