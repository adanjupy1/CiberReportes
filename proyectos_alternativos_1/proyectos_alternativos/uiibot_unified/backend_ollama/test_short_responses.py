#!/usr/bin/env python3
"""
Script de test para verificar que el backend Ollama devuelve respuestas más cortas
Uso: python3 test_short_responses.py
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuración
OLLAMA_URL = "http://localhost:8002"
MODEL_NAME = "llama3.2:3b"

# Preguntas de prueba relacionadas con ciberseguridad
TEST_QUESTIONS = [
    "¿Qué es una contraseña segura?",
    "¿Cómo proteger mi Wi-Fi?",
    "¿Qué es el phishing?",
    "¿Cómo sé si una web es segura?",
]

async def test_chat_response(session_id: str, message: str) -> dict:
    """Realizar una prueba de chat y retornar estadísticas"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/chat",
                json={
                    "session_id": session_id,
                    "message": message
                }
            )
            
            if response.status_code != 200:
                return {
                    "question": message,
                    "error": f"HTTP {response.status_code}",
                    "success": False
                }
            
            data = response.json()
            reply = data.get("reply", "")
            char_count = len(reply)
            word_count = len(reply.split())
            paragraph_count = len([p for p in reply.split('\n\n') if p.strip()])
            
            return {
                "question": message,
                "reply": reply[:200] + ("..." if len(reply) > 200 else ""),
                "char_count": char_count,
                "word_count": word_count,
                "paragraph_count": paragraph_count,
                "model": data.get("model", "unknown"),
                "success": True
            }
    except Exception as e:
        return {
            "question": message,
            "error": str(e),
            "success": False
        }

async def main():
    """Ejecutar pruebas de respuestas cortas"""
    print("\n" + "="*70)
    print("TEST DE RESPUESTAS CORTAS - Backend Ollama")
    print("="*70)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Endpoint: {OLLAMA_URL}/api/chat")
    print(f"Modelo: {MODEL_NAME}")
    print(f"Configuración:")
    print("  - temperature: 0.5 (reducido de 0.7)")
    print("  - top_p: 0.85 (reducido de 0.9)")
    print("  - top_k: 30 (reducido de 40)")
    print("  - num_predict: 256 (reducido de 512)")
    print("="*70 + "\n")
    
    session_id = "test_session_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    results = []
    
    print(f"📋 Ejecutando {len(TEST_QUESTIONS)} pruebas...\n")
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"[{i}/{len(TEST_QUESTIONS)}] Probando: {question}")
        result = await test_chat_response(session_id, question)
        results.append(result)
        
        if result["success"]:
            print(f"    ✓ Caracteres: {result['char_count']}")
            print(f"    ✓ Palabras: {result['word_count']}")
            print(f"    ✓ Párrafos: {result['paragraph_count']}")
            print(f"    Preview: {result['reply']}")
        else:
            print(f"    ✗ Error: {result.get('error', 'Unknown error')}")
        print()
    
    # Estadísticas generales
    successful = [r for r in results if r["success"]]
    if successful:
        avg_chars = sum(r["char_count"] for r in successful) / len(successful)
        avg_words = sum(r["word_count"] for r in successful) / len(successful)
        avg_paragraphs = sum(r["paragraph_count"] for r in successful) / len(successful)
        
        max_chars = max(r["char_count"] for r in successful)
        min_chars = min(r["char_count"] for r in successful)
        
        print("="*70)
        print("📊 RESUMEN DE ESTADÍSTICAS")
        print("="*70)
        print(f"Respuestas exitosas: {len(successful)}/{len(TEST_QUESTIONS)}")
        print(f"\nPromedio de caracteres: {avg_chars:.1f}")
        print(f"  - Mínimo: {min_chars}")
        print(f"  - Máximo: {max_chars}")
        print(f"\nPromedio de palabras: {avg_words:.1f}")
        print(f"Promedio de párrafos: {avg_paragraphs:.1f}")
        
        # Validación de respuestas cortas
        print("\n" + "="*70)
        print("✅ VALIDACIÓN: Respuestas cortas (< 500 caracteres)")
        print("="*70)
        short_responses = [r for r in successful if r["char_count"] < 500]
        print(f"Respuestas cortas: {len(short_responses)}/{len(successful)}")
        
        if len(short_responses) == len(successful):
            print("✓ ¡Todas las respuestas son cortas!")
        else:
            print(f"⚠ {len(successful) - len(short_responses)} respuesta(s) exceden 500 caracteres")
    
    print("\n" + "="*70)
    print("Test completado")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(main())
