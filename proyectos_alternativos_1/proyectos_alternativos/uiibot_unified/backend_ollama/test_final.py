#!/usr/bin/env python3
import asyncio, httpx, json
from datetime import datetime

OLLAMA_URL = "http://localhost:8002"

TEST_QUESTIONS = [
    "¿Qué es una contraseña segura?",
    "¿Cómo proteger mi Wi-Fi?",
    "¿Qué es el phishing?",
    "¿Cómo sé si una web es segura?",
]

async def test_chat(message):
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={"session_id":f"final_test_{datetime.now().timestamp()}","message":message}
            )
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}
            data = response.json()
            reply = data.get("reply", "")
            return {
                "question": message,
                "chars": len(reply),
                "words": len(reply.split()),
                "reply_preview": reply[:120] + ("..." if len(reply) > 120 else "")
            }
    except Exception as e:
        return {"error": str(e)}

async def main():
    print("\n" + "="*70)
    print("TEST FINAL - RESPUESTAS CORTAS (Optimizado)")
    print("="*70)
    for i, q in enumerate(TEST_QUESTIONS, 1):
        result = await test_chat(q)
        if "error" not in result:
            print(f"\n[{i}] {result['question']}")
            print(f"    Caracteres: {result['chars']} | Palabras: {result['words']}")
            print(f"    Preview: {result['reply_preview']}")
        else:
            print(f"\n[{i}] Error: {result['error']}")
    print("\n" + "="*70 + "\n")

asyncio.run(main())
