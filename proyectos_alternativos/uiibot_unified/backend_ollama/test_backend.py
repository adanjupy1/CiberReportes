#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
"""
test_backend.py — Suite de pruebas de funcionalidad y congruencia
para el backend Agente Bit (llama-cpp-python + RAG)

Uso:
    python test_backend.py
    python test_backend.py --url http://localhost:8002
    python test_backend.py --quick   # Solo health + RAG status

Requiere: pip install requests
"""

import argparse
import json
import sys
import time
import uuid
from datetime import datetime

try:
    import requests
except ImportError:
    print("ERROR: pip install requests")
    sys.exit(1)

# ─────────────────────────────────────────────────────────────────────────────
BASE_URL   = "http://localhost:8002"
SESSION_ID = f"test-{uuid.uuid4().hex[:8]}"
TIMEOUT    = 120   # segundos por request (modelo CPU puede tardar)

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

results = []


def log(label: str, status: str, detail: str = ""):
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {status}  {label}"
    if detail:
        line += f"\n         → {detail}"
    print(line)
    results.append({"label": label, "status": status, "detail": detail})


def req_get(path):
    return requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)


def req_post(path, payload):
    return requests.post(f"{BASE_URL}{path}", json=payload, timeout=TIMEOUT)


def req_delete(path):
    return requests.delete(f"{BASE_URL}{path}", timeout=TIMEOUT)


# ─────────────────────────────────────────────────────────────────────────────
# TEST SUITE
# ─────────────────────────────────────────────────────────────────────────────

def test_health():
    """1. Health check — servidor activo y modelo cargado."""
    try:
        r = req_get("/health")
        assert r.status_code == 200
        d = r.json()
        assert d["ok"] is True
        assert "model" in d
        rag_docs = d.get("rag", {}).get("documents", 0)
        rag_ok   = d.get("rag", {}).get("active", False)
        log("Health check", PASS, f"modelo={d['model']} | RAG activo={rag_ok} | docs={rag_docs}")
        return True
    except Exception as e:
        log("Health check", FAIL, str(e))
        return False


def test_rag_status():
    """2. RAG status — base vectorial disponible."""
    try:
        r = req_get("/api/rag/status")
        assert r.status_code == 200
        d = r.json()
        docs = d.get("documents", 0)
        active = d.get("active", False)
        status = PASS if (active and docs >= 10) else WARN
        log("RAG status", status, f"activo={active} | documentos={docs} | colección={d.get('collection')}")
        return active
    except Exception as e:
        log("RAG status", FAIL, str(e))
        return False


def test_empty_message():
    """3. Mensaje vacío debe retornar HTTP 400."""
    try:
        r = req_post("/api/chat", {"session_id": SESSION_ID, "message": ""})
        assert r.status_code == 400
        log("Mensaje vacío → 400", PASS, f"status={r.status_code}")
    except Exception as e:
        log("Mensaje vacío → 400", FAIL, str(e))


def test_basic_cybersecurity():
    """4. Pregunta básica de ciberseguridad — respuesta coherente."""
    try:
        r = req_post("/api/chat", {
            "session_id": SESSION_ID,
            "message": "¿Qué es el phishing y cómo puedo protegerme?"
        })
        assert r.status_code == 200
        d = r.json()
        reply = d.get("reply", "")
        assert len(reply) > 50, "Respuesta demasiado corta"

        # Verificar que mencione conceptos clave
        keywords = ["phishing", "correo", "enlace", "contraseña", "proteg", "segur"]
        found = [kw for kw in keywords if kw.lower() in reply.lower()]
        congruent = len(found) >= 2

        status = PASS if congruent else WARN
        log("Pregunta: phishing", status,
            f"longitud={len(reply)} chars | RAG usado={d.get('rag_used')} | keywords={found}")
        print(f"\n    📝 Respuesta:\n    {reply[:300]}{'...' if len(reply)>300 else ''}\n")
    except Exception as e:
        log("Pregunta: phishing", FAIL, str(e))


def test_mexico_context():
    """5. Pregunta con contexto México — debe mencionar autoridades/números MX."""
    try:
        r = req_post("/api/chat", {
            "session_id": SESSION_ID,
            "message": "Me robaron dinero de mi cuenta bancaria por internet, ¿a quién debo reportarlo en México?"
        })
        assert r.status_code == 200
        d = r.json()
        reply = d.get("reply", "").lower()

        mx_keywords = ["condusef", "banco", "policía", "088", "800", "inai", "ministerio", "denuncia", "sspc"]
        found = [kw for kw in mx_keywords if kw in reply]
        congruent = len(found) >= 1

        status = PASS if congruent else WARN
        log("Contexto México: fraude bancario", status,
            f"keywords MX encontrados={found} | RAG={d.get('rag_used')}")
        print(f"\n    📝 Respuesta:\n    {d['reply'][:400]}{'...' if len(d['reply'])>400 else ''}\n")
    except Exception as e:
        log("Contexto México: fraude bancario", FAIL, str(e))


def test_sat_phishing():
    """6. Pregunta sobre phishing SAT — RAG debe activarse."""
    try:
        r = req_post("/api/chat", {
            "session_id": SESSION_ID,
            "message": "Recibí un correo del SAT diciendo que tengo un adeudo. ¿Qué hago?"
        })
        assert r.status_code == 200
        d = r.json()
        reply = d.get("reply", "").lower()
        rag_used = d.get("rag_used", False)

        sat_keywords = ["sat", "phishing", "fraude", "oficial", "sat.gob", "no haga clic", "sospechoso", "falso"]
        found = [kw for kw in sat_keywords if kw in reply]

        status = PASS if (len(found) >= 1) else WARN
        log("RAG activado: phishing SAT", status,
            f"RAG usado={rag_used} | keywords={found}")
        print(f"\n    📝 Respuesta:\n    {d['reply'][:400]}{'...' if len(d['reply'])>400 else ''}\n")
    except Exception as e:
        log("RAG activado: phishing SAT", FAIL, str(e))


def test_legal_context():
    """7. Pregunta sobre derechos ARCO / LFPDPPP."""
    try:
        r = req_post("/api/chat", {
            "session_id": SESSION_ID,
            "message": "¿Qué son los derechos ARCO y cómo los ejerzo en México?"
        })
        assert r.status_code == 200
        d = r.json()
        reply = d.get("reply", "").lower()

        arco_keywords = ["acceso", "rectificación", "cancelación", "oposición", "inai", "datos personales", "lfpdppp"]
        found = [kw for kw in arco_keywords if kw in reply]
        congruent = len(found) >= 2

        status = PASS if congruent else WARN
        log("Derechos ARCO / LFPDPPP", status,
            f"RAG={d.get('rag_used')} | keywords={found}")
        print(f"\n    📝 Respuesta:\n    {d['reply'][:400]}{'...' if len(d['reply'])>400 else ''}\n")
    except Exception as e:
        log("Derechos ARCO / LFPDPPP", FAIL, str(e))


def test_ransomware():
    """8. Pregunta sobre ransomware — respuesta con pasos concretos."""
    try:
        r = req_post("/api/chat", {
            "session_id": SESSION_ID,
            "message": "Mi computadora de la empresa fue infectada con ransomware. ¿Qué debo hacer?"
        })
        assert r.status_code == 200
        d = r.json()
        reply = d.get("reply", "").lower()

        keywords = ["ransomware", "respaldo", "backup", "desconect", "pagar", "rescate", "cert", "reportar"]
        found = [kw for kw in keywords if kw in reply]

        status = PASS if len(found) >= 2 else WARN
        log("Ransomware: pasos concretos", status,
            f"RAG={d.get('rag_used')} | keywords={found}")
        print(f"\n    📝 Respuesta:\n    {d['reply'][:400]}{'...' if len(d['reply'])>400 else ''}\n")
    except Exception as e:
        log("Ransomware: pasos concretos", FAIL, str(e))


def test_conversation_history():
    """9. Historial de conversación — coherencia multi-turno."""
    session2 = f"test-multi-{uuid.uuid4().hex[:6]}"
    try:
        # Turno 1
        r1 = req_post("/api/chat", {
            "session_id": session2,
            "message": "Hola, me llamo Carlos y quiero aprender sobre ciberseguridad."
        })
        assert r1.status_code == 200
        reply1 = r1.json().get("reply", "")

        # Turno 2 — referencia al contexto anterior
        r2 = req_post("/api/chat", {
            "session_id": session2,
            "message": "¿Cuál es el primer consejo que me darías?"
        })
        assert r2.status_code == 200
        reply2 = r2.json().get("reply", "")
        assert len(reply2) > 30

        log("Historial multi-turno", PASS,
            f"Turno1={len(reply1)} chars | Turno2={len(reply2)} chars")
        print(f"\n    📝 Turno 2:\n    {reply2[:300]}\n")

        # Limpiar sesión de prueba
        req_delete(f"/api/session/{session2}")
    except Exception as e:
        log("Historial multi-turno", FAIL, str(e))


def test_session_management():
    """10. Gestión de sesiones — crear, listar y eliminar."""
    session3 = f"test-mgmt-{uuid.uuid4().hex[:6]}"
    try:
        # Crear sesión con un mensaje
        req_post("/api/chat", {"session_id": session3, "message": "Test de sesión."})

        # Listar sesiones
        r = req_get("/api/sessions")
        assert r.status_code == 200
        sessions = r.json().get("sessions", [])
        assert session3 in sessions

        # Eliminar sesión
        rd = req_delete(f"/api/session/{session3}")
        assert rd.status_code == 200
        assert rd.json().get("ok") is True

        # Verificar eliminación
        r2 = req_get("/api/sessions")
        assert session3 not in r2.json().get("sessions", [])

        log("Gestión de sesiones", PASS, f"Sesión creada, listada y eliminada correctamente")
    except Exception as e:
        log("Gestión de sesiones", FAIL, str(e))


def test_off_topic():
    """11. Pregunta fuera de tema — debe mantenerse en rol."""
    try:
        r = req_post("/api/chat", {
            "session_id": SESSION_ID,
            "message": "¿Cuál es la receta del pozole rojo?"
        })
        assert r.status_code == 200
        reply = r.json().get("reply", "").lower()

        # No debe dar receta detallada; debe redirigir a su área
        off_topic_signs = ["ingrediente", "cocinar", "hervir", "chile", "maíz"]
        in_role = not any(sign in reply for sign in off_topic_signs)

        status = PASS if in_role else WARN
        log("Fuera de tema: mantiene rol", status,
            f"Redirigió al tema: {in_role}")
        print(f"\n    📝 Respuesta:\n    {reply[:300]}\n")
    except Exception as e:
        log("Fuera de tema: mantiene rol", FAIL, str(e))


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def print_banner():
    print("\n" + "="*60)
    print("  [BOT] Agente Bit - Suite de Pruebas de Funcionalidad")
    print(f"  URL: {BASE_URL}")
    print(f"  Sesion: {SESSION_ID}")
    print("="*60 + "\n")


def print_summary():
    total  = len(results)
    passed = sum(1 for r in results if r["status"] == PASS)
    warned = sum(1 for r in results if r["status"] == WARN)
    failed = sum(1 for r in results if r["status"] == FAIL)

    print("\n" + "="*60)
    print("  RESUMEN DE PRUEBAS")
    print("="*60)
    print(f"  Total:   {total}")
    print(f"  [PASS]:  {passed}")
    print(f"  [WARN]:  {warned}")
    print(f"  [FAIL]:  {failed}")
    print("="*60 + "\n")

    if failed > 0:
        print("  Pruebas fallidas:")
        for r in results:
            if r["status"] == FAIL:
                print(f"    - {r['label']}: {r['detail']}")
        print()

    return failed == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8002", help="URL base del backend")
    parser.add_argument("--quick", action="store_true", help="Solo health + RAG (sin inferencia)")
    args = parser.parse_args()

    BASE_URL = args.url
    print_banner()

    # 1 & 2 — Siempre
    server_ok = test_health()
    if not server_ok:
        print(f"\n  [ERROR] Servidor no responde en {BASE_URL}. Asegurate de que main.py este corriendo.\n")
        sys.exit(1)

    test_rag_status()

    if args.quick:
        print_summary()
        sys.exit(0)

    # 3-11 -- Pruebas completas de inferencia
    print("\n  -- Pruebas de inferencia (pueden tardar 1-3 min en CPU) --\n")
    test_empty_message()
    test_basic_cybersecurity()
    test_mexico_context()
    test_sat_phishing()
    test_legal_context()
    test_ransomware()
    test_conversation_history()
    test_session_management()
    test_off_topic()

    ok = print_summary()
    sys.exit(0 if ok else 1)
