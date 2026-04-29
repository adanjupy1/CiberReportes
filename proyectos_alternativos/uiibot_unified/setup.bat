@echo off
:: ============================================================
:: setup.bat — Instalación completa de uiibot_unified
:: Sistema: Windows | Shell: CMD / PowerShell
::
:: Uso:
::   setup.bat          -> Instalación completa
::   setup.bat --reset  -> Reinstala dependencias y reindexa RAG
:: ============================================================
setlocal EnableDelayedExpansion

echo.
echo  =====================================================
echo   uiibot_unified - Setup e Instalacion
echo   Agente Bit con llama-cpp-python + RAG
echo  =====================================================
echo.

:: Verificar Python
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo  [ERROR] Python no encontrado.
    echo  Descarga Python 3.10+ desde: https://www.python.org/downloads/
    pause
    exit /b 1
)

FOR /F "tokens=2" %%V IN ('python --version 2^>^&1') DO SET PYVER=%%V
echo  [OK] Python %PYVER% detectado.
echo.

:: Ir al directorio del backend
cd /d "%~dp0backend_ollama"

:: Verificar si ya existe venv
IF NOT EXIST "venv" (
    echo  [1/4] Creando entorno virtual...
    python -m venv venv
) ELSE (
    echo  [1/4] Entorno virtual existente detectado.
)

:: Activar venv
call venv\Scripts\activate.bat

:: Instalar dependencias
echo.
echo  [2/4] Instalando dependencias (puede tardar 5-15 min en primera ejecucion)...
echo        llama-cpp-python se compila desde fuente...
pip install --upgrade pip -q
pip install -r requirements.txt

IF ERRORLEVEL 1 (
    echo.
    echo  [ERROR] Fallo en la instalacion de dependencias.
    echo  Verifica que tienes compilador C++ instalado:
    echo  https://visualstudio.microsoft.com/visual-cpp-build-tools/
    pause
    exit /b 1
)
echo  [OK] Dependencias instaladas.

:: Copiar .env si no existe
cd /d "%~dp0"
IF NOT EXIST ".env" (
    echo.
    echo  [3/4] Creando archivo .env desde plantilla...
    copy .env.example .env
    echo  [OK] .env creado. Edita los valores si es necesario.
) ELSE (
    echo.
    echo  [3/4] .env existente, omitiendo.
)

:: Indexar base de conocimiento RAG
cd /d "%~dp0backend_ollama"
echo.
IF "%1"=="--reset" (
    echo  [4/4] Re-indexando base de conocimiento RAG desde cero...
    python rag_indexer.py --reset
) ELSE (
    echo  [4/4] Verificando / actualizando base de conocimiento RAG...
    python rag_indexer.py
)

echo.
echo  =====================================================
echo   Instalacion completada!
echo.
echo   Para iniciar el backend:
echo     cd backend_ollama
echo     venv\Scripts\activate
echo     python main.py
echo.
echo   O simplemente ejecuta: start_backend.bat
echo  =====================================================
echo.
pause
