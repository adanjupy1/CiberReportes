@echo off
powershell -ExecutionPolicy Bypass -NoProfile -File "%~dp0backend.ps1" -Action start
pause
