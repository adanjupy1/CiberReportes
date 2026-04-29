#!/bin/bash
# Inicia el backend del directorio en el puerto 8000
cd "$(dirname "$0")"
exec /opt/venvs/CHAT_PLUS/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
