# backend.ps1 - Gestión del backend Data_Base
# Uso: .\backend.ps1 [start|stop|restart]

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start","stop","restart")]
    [string]$Action
)

$WorkDir  = "C:\xampp\htdocs\Data_Base"
$Python   = "C:\xampp\htdocs\Data_Base\Chat_Env\Scripts\python.exe"
$PidFile  = "$WorkDir\backend.pid"

function Start-Backend {
    if (-not (Test-Path $Python)) {
        Write-Host "[ERROR] Entorno Chat_Env no encontrado: $Python" -ForegroundColor Red
        exit 1
    }
    if (Test-Path $PidFile) {
        $oldPid = (Get-Content $PidFile -Raw).Trim()
        if (Get-Process -Id $oldPid -ErrorAction SilentlyContinue) {
            Write-Host "[!] Backend ya corriendo (PID: $oldPid). Usa 'restart' para reiniciarlo." -ForegroundColor Yellow
            exit 0
        }
        Remove-Item $PidFile -Force
    }
    $proc = Start-Process -FilePath $Python `
        -ArgumentList "-m uvicorn app:app --host 0.0.0.0 --port 8000" `
        -WorkingDirectory $WorkDir `
        -WindowStyle Hidden -PassThru
    $proc.Id | Out-File -FilePath $PidFile -Encoding ASCII -NoNewline
    Write-Host "[OK] Backend iniciado" -ForegroundColor Green
    Write-Host "[OK] URL  : http://localhost:8000" -ForegroundColor Green
    Write-Host "[OK] Docs : http://localhost:8000/docs" -ForegroundColor Green
    Write-Host "[OK] PID  : $($proc.Id)" -ForegroundColor Green
}

function Stop-Backend {
    if (Test-Path $PidFile) {
        $oldPid = (Get-Content $PidFile -Raw).Trim()
        try {
            Stop-Process -Id $oldPid -Force -ErrorAction Stop
            Write-Host "[OK] Backend detenido (PID: $oldPid)" -ForegroundColor Green
        } catch {
            Write-Host "[!] PID $oldPid ya no estaba activo." -ForegroundColor Yellow
        }
        Remove-Item $PidFile -Force
    } else {
        $procs = Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object {
            (Get-CimInstance Win32_Process -Filter "ProcessId=$($_.Id)" -EA SilentlyContinue).CommandLine -like "*uvicorn*"
        }
        if ($procs) {
            $procs | Stop-Process -Force
            Write-Host "[OK] Proceso(s) uvicorn detenidos: $($procs.Count)" -ForegroundColor Green
        } else {
            Write-Host "[i] No hay ningún proceso uvicorn activo." -ForegroundColor Cyan
        }
    }
}

Write-Host ""
switch ($Action) {
    "start"   { Write-Host "==> Iniciando backend..." -ForegroundColor Cyan;   Start-Backend }
    "stop"    { Write-Host "==> Deteniendo backend..." -ForegroundColor Cyan;  Stop-Backend  }
    "restart" {
        Write-Host "==> Reiniciando backend..." -ForegroundColor Cyan
        Stop-Backend
        Start-Sleep -Seconds 2
        Start-Backend
    }
}
Write-Host ""
