# Script para detener todos los backends
# Cierra los procesos de Python relacionados con los backends

Write-Host "Deteniendo backends..." -ForegroundColor Yellow

# Obtener procesos de Python del entorno virtual CHAT_PLUS
$processes = Get-Process -Name python, uvicorn -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*CHAT_PLUS*"
}

if ($processes) {
    Write-Host "`nProcesos encontrados:" -ForegroundColor Cyan
    foreach ($proc in $processes) {
        Write-Host "  - PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor White
    }
    
    Write-Host "`nCerrando procesos..." -ForegroundColor Yellow
    $processes | Stop-Process -Force
    
    Write-Host "`n[OK] Todos los backends han sido detenidos!" -ForegroundColor Green
} else {
    Write-Host "`nNo se encontraron procesos activos de los backends." -ForegroundColor Yellow
}

Write-Host "`nPara reiniciar los backends, ejecuta:" -ForegroundColor Cyan
Write-Host "  .\start_backends.ps1" -ForegroundColor White
