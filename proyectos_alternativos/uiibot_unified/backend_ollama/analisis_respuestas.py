#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analisis_respuestas.py — Análisis profundo de calidad de respuestas
de ciberseguridad para Agente Bit (llama-cpp + RAG)

Evalúa: precisión técnica, contexto México, activación RAG,
coherencia, completitud y congruencia de respuestas.
"""
import os, sys
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

import json
import uuid
import time
import requests
from datetime import datetime

BASE_URL = "http://localhost:8002"
TIMEOUT  = 180

# ─────────────────────────────────────────────────────────────────────────────
# BATERIA DE PREGUNTAS POR CATEGORIA
# Cada pregunta tiene: texto, categoria, palabras_clave esperadas,
#                      contactos_mx esperados, nivel de dificultad
# ─────────────────────────────────────────────────────────────────────────────
PREGUNTAS = [

    # ── PHISHING ─────────────────────────────────────────────────────────────
    {
        "id": "P01",
        "categoria": "PHISHING",
        "dificultad": "Basico",
        "pregunta": "¿Qué es el phishing y cómo puedo identificar un correo fraudulento?",
        "keywords_tecnicas": ["phishing", "correo", "enlace", "remitente", "sospechoso", "falso", "verificar"],
        "keywords_mx": [],
        "contactos_mx": [],
        "rag_esperado": False,
    },
    {
        "id": "P02",
        "categoria": "PHISHING",
        "dificultad": "Especifico MX",
        "pregunta": "Recibi un SMS del SAT diciendo que tengo una devolucion de impuestos pendiente con un link. ¿Es real?",
        "keywords_tecnicas": ["sat", "phishing", "smishing", "link", "fraude", "falso", "oficial"],
        "keywords_mx": ["sat.gob.mx", "sat", "certificado", "autenticidad"],
        "contactos_mx": ["cert", "sat"],
        "rag_esperado": True,
    },
    {
        "id": "P03",
        "categoria": "PHISHING",
        "dificultad": "Especifico MX",
        "pregunta": "Me llego un correo del IMSS pidiendo verificar mis semanas cotizadas con un formulario. ¿Qué hago?",
        "keywords_tecnicas": ["imss", "phishing", "datos", "verificar", "fraudulento"],
        "keywords_mx": ["imss.gob.mx", "imss", "nss", "curp"],
        "contactos_mx": ["800-623-2323", "imss"],
        "rag_esperado": True,
    },

    # ── FRAUDE BANCARIO / VISHING ────────────────────────────────────────────
    {
        "id": "P04",
        "categoria": "FRAUDE BANCARIO",
        "dificultad": "Basico",
        "pregunta": "¿Qué es el vishing y cómo funciona el fraude por llamada telefónica?",
        "keywords_tecnicas": ["vishing", "llamada", "banco", "nip", "token", "ingenieria social"],
        "keywords_mx": [],
        "contactos_mx": [],
        "rag_esperado": False,
    },
    {
        "id": "P05",
        "categoria": "FRAUDE BANCARIO",
        "dificultad": "Urgente MX",
        "pregunta": "Me robaron dinero de mi cuenta BBVA por internet, hicieron transferencias que yo no autorice. ¿Qué hago ahorita?",
        "keywords_tecnicas": ["reporte", "banco", "bloquear", "transferencia", "denuncia"],
        "keywords_mx": ["condusef", "banco", "ministerio"],
        "contactos_mx": ["condusef", "800"],
        "rag_esperado": True,
    },
    {
        "id": "P06",
        "categoria": "FRAUDE BANCARIO",
        "dificultad": "Especifico MX",
        "pregunta": "¿Cuánto tiempo tiene mi banco para responder mi reclamación por fraude?",
        "keywords_tecnicas": ["reclamacion", "plazo", "dias", "respuesta", "investigacion"],
        "keywords_mx": ["condusef", "dias habiles", "sipres"],
        "contactos_mx": ["condusef"],
        "rag_esperado": True,
    },

    # ── RANSOMWARE ───────────────────────────────────────────────────────────
    {
        "id": "P07",
        "categoria": "RANSOMWARE",
        "dificultad": "Basico",
        "pregunta": "¿Qué es el ransomware y por qué es peligroso para las empresas?",
        "keywords_tecnicas": ["ransomware", "cifra", "rescate", "datos", "backup", "empresa"],
        "keywords_mx": [],
        "contactos_mx": [],
        "rag_esperado": False,
    },
    {
        "id": "P08",
        "categoria": "RANSOMWARE",
        "dificultad": "Critico MX",
        "pregunta": "La computadora de mi empresa fue infectada con ransomware, los archivos estan cifrados y piden rescate en Bitcoin. Pasos a seguir.",
        "keywords_tecnicas": ["desconectar", "apagar", "respaldo", "backup", "pagar", "rescate", "reportar"],
        "keywords_mx": ["cert", "policia"],
        "contactos_mx": ["cert", "088"],
        "rag_esperado": True,
    },
    {
        "id": "P09",
        "categoria": "RANSOMWARE",
        "dificultad": "Prevencion",
        "pregunta": "¿Qué medidas debe tomar una PYME mexicana para protegerse del ransomware?",
        "keywords_tecnicas": ["backup", "actualizacion", "antivirus", "mfa", "parche", "empleados", "capacitar"],
        "keywords_mx": ["pyme"],
        "contactos_mx": [],
        "rag_esperado": True,
    },

    # ── PRIVACIDAD / DATOS PERSONALES ────────────────────────────────────────
    {
        "id": "P10",
        "categoria": "PRIVACIDAD",
        "dificultad": "Legal MX",
        "pregunta": "¿Qué son los derechos ARCO y cómo los ejerzo si una empresa tiene mis datos sin mi consentimiento?",
        "keywords_tecnicas": ["acceso", "rectificacion", "cancelacion", "oposicion", "datos personales"],
        "keywords_mx": ["inai", "lfpdppp"],
        "contactos_mx": ["inai", "800-835-4324"],
        "rag_esperado": True,
    },
    {
        "id": "P11",
        "categoria": "PRIVACIDAD",
        "dificultad": "Legal MX",
        "pregunta": "Una empresa filtró mis datos personales. ¿Tienen obligación de avisarme y qué puedo hacer?",
        "keywords_tecnicas": ["brecha", "notificacion", "filtracion", "denuncia", "sancion"],
        "keywords_mx": ["inai", "lfpdppp"],
        "contactos_mx": ["inai"],
        "rag_esperado": True,
    },

    # ── INGENIERIA SOCIAL / SMISHING ─────────────────────────────────────────
    {
        "id": "P12",
        "categoria": "SMISHING",
        "dificultad": "Especifico MX",
        "pregunta": "Recibi un SMS de mi banco diciendo que mi tarjeta fue bloqueada y que ingrese mis datos en una liga. ¿Qué hago?",
        "keywords_tecnicas": ["smishing", "sms", "liga", "tarjeta", "banco", "fraude", "falso"],
        "keywords_mx": ["condusef", "banco"],
        "contactos_mx": ["condusef", "800"],
        "rag_esperado": True,
    },

    # ── SEXTORSION ───────────────────────────────────────────────────────────
    {
        "id": "P13",
        "categoria": "SEXTORSION",
        "dificultad": "Urgente MX",
        "pregunta": "Alguien en redes sociales tiene fotos intimas mias y me pide dinero para no publicarlas. ¿Qué hago?",
        "keywords_tecnicas": ["sextorsion", "extorsion", "no pagar", "evidencia", "bloquear", "denuncia"],
        "keywords_mx": ["policia cibernetica", "088", "sspc"],
        "contactos_mx": ["088", "policia"],
        "rag_esperado": True,
    },

    # ── BUENAS PRACTICAS ─────────────────────────────────────────────────────
    {
        "id": "P14",
        "categoria": "BUENAS PRACTICAS",
        "dificultad": "Basico",
        "pregunta": "¿Cómo crear una contraseña segura y qué es la autenticación de dos factores?",
        "keywords_tecnicas": ["contrasena", "caracteres", "mayusculas", "numeros", "2fa", "mfa", "gestor"],
        "keywords_mx": [],
        "contactos_mx": [],
        "rag_esperado": False,
    },
    {
        "id": "P15",
        "categoria": "BUENAS PRACTICAS",
        "dificultad": "Intermedio",
        "pregunta": "¿Es seguro conectarme a la red WiFi pública de un café para revisar mi cuenta bancaria?",
        "keywords_tecnicas": ["wifi", "publica", "inseguro", "vpn", "datos moviles", "mitm", "cifrado"],
        "keywords_mx": [],
        "contactos_mx": [],
        "rag_esperado": True,
    },

    # ── MARCO LEGAL MX ───────────────────────────────────────────────────────
    {
        "id": "P16",
        "categoria": "MARCO LEGAL",
        "dificultad": "Legal MX",
        "pregunta": "¿Qué leyes mexicanas regulan los delitos informaticos y cuáles son las penas?",
        "keywords_tecnicas": ["codigo penal", "delito informatico", "prision", "pena", "art", "federal"],
        "keywords_mx": ["codigo penal federal", "211", "fgr", "ministerio publico"],
        "contactos_mx": ["fgr", "088"],
        "rag_esperado": True,
    },
    {
        "id": "P17",
        "categoria": "ESTADISTICAS",
        "dificultad": "Informativo",
        "pregunta": "¿Cuáles son las principales amenazas de ciberseguridad en México en 2024?",
        "keywords_tecnicas": ["ataque", "phishing", "ransomware", "fraude", "amenaza", "sector"],
        "keywords_mx": ["mexico", "latinoamerica", "kaspersky", "pymes"],
        "contactos_mx": [],
        "rag_esperado": True,
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# FUNCIONES DE ANALISIS
# ─────────────────────────────────────────────────────────────────────────────

def puntuar_respuesta(respuesta: str, item: dict) -> dict:
    """Evalúa la calidad de la respuesta en múltiples dimensiones."""
    r = respuesta.lower()

    # 1. Palabras clave técnicas presentes
    kw_tecnicas = item["keywords_tecnicas"]
    encontradas_tec = [kw for kw in kw_tecnicas if kw.lower() in r]
    pct_tecnicas = len(encontradas_tec) / len(kw_tecnicas) * 100 if kw_tecnicas else 100

    # 2. Contexto México
    kw_mx = item["keywords_mx"]
    encontradas_mx = [kw for kw in kw_mx if kw.lower() in r]
    pct_mx = len(encontradas_mx) / len(kw_mx) * 100 if kw_mx else 100

    # 3. Contactos/autoridades MX
    contactos = item["contactos_mx"]
    encontrados_c = [c for c in contactos if c.lower() in r]
    pct_contactos = len(encontrados_c) / len(contactos) * 100 if contactos else 100

    # 4. Longitud adecuada (50-600 chars ideal para 256 max_tokens)
    largo = len(respuesta)
    if largo < 50:
        pct_longitud = 20
    elif largo > 50 and largo <= 800:
        pct_longitud = 100
    else:
        pct_longitud = 80

    # 5. Estructura (usa formato markdown / listas)
    tiene_estructura = any(c in respuesta for c in ["**", "1.", "2.", "3.", "-", "*", "•"])
    pct_estructura = 100 if tiene_estructura else 50

    # 6. No da información peligrosa (no dice "pague el rescate")
    info_peligrosa = any(f in r for f in ["pague el rescate", "transfer bitcoin", "envie dinero al atacante"])
    pct_seguridad = 0 if info_peligrosa else 100

    # Score final ponderado
    score = (
        pct_tecnicas   * 0.30 +
        pct_mx         * 0.20 +
        pct_contactos  * 0.15 +
        pct_longitud   * 0.15 +
        pct_estructura * 0.10 +
        pct_seguridad  * 0.10
    )

    return {
        "score_total": round(score, 1),
        "pct_tecnicas": round(pct_tecnicas, 0),
        "pct_mx": round(pct_mx, 0),
        "pct_contactos": round(pct_contactos, 0),
        "pct_longitud": round(pct_longitud, 0),
        "tiene_estructura": tiene_estructura,
        "info_peligrosa": info_peligrosa,
        "keywords_encontradas": encontradas_tec,
        "mx_encontradas": encontradas_mx,
        "contactos_encontrados": encontrados_c,
        "longitud": largo,
    }


def clasificar_score(score: float) -> str:
    if score >= 85:  return "[EXCELENTE]"
    if score >= 70:  return "[BUENO    ]"
    if score >= 55:  return "[ACEPTABLE]"
    if score >= 40:  return "[DEFICIENTE]"
    return                  "[MALO     ]"


def ask(pregunta: str, session_id: str) -> dict:
    """Envía pregunta al backend y retorna la respuesta completa."""
    try:
        r = requests.post(
            f"{BASE_URL}/api/chat",
            json={"session_id": session_id, "message": pregunta},
            timeout=TIMEOUT
        )
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        return {"reply": "", "rag_used": False, "_error": "TIMEOUT"}
    except Exception as e:
        return {"reply": "", "rag_used": False, "_error": str(e)}


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*70)
    print("  ANALISIS DE RESPUESTAS — AGENTE BIT (llama-cpp + RAG)")
    print(f"  Backend: {BASE_URL}")
    print(f"  Fecha:   {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"  Total preguntas: {len(PREGUNTAS)}")
    print("="*70)

    resultados = []
    session_id = f"analisis-{uuid.uuid4().hex[:8]}"

    for i, item in enumerate(PREGUNTAS, 1):
        print(f"\n[{i:02d}/{len(PREGUNTAS)}] {item['id']} | {item['categoria']} | {item['dificultad']}")
        print(f"  P: {item['pregunta'][:80]}...")

        t0 = time.time()
        resp_data = ask(item["pregunta"], session_id)
        elapsed = round(time.time() - t0, 1)

        if "_error" in resp_data:
            print(f"  ERROR: {resp_data['_error']}")
            resultados.append({**item, "error": resp_data["_error"], "score_total": 0,
                               "elapsed": elapsed, "rag_used": False, "reply": ""})
            continue

        reply     = resp_data.get("reply", "")
        rag_used  = resp_data.get("rag_used", False)
        metricas  = puntuar_respuesta(reply, item)
        calidad   = clasificar_score(metricas["score_total"])

        print(f"  {calidad}  Score: {metricas['score_total']}/100  |  RAG: {'SI' if rag_used else 'NO'}  |  {elapsed}s  |  {metricas['longitud']} chars")
        print(f"  Keywords tecnicas: {metricas['pct_tecnicas']}% ({metricas['keywords_encontradas']})")
        if item["keywords_mx"]:
            print(f"  Contexto MX:       {metricas['pct_mx']}% ({metricas['mx_encontradas']})")
        if item["contactos_mx"]:
            print(f"  Contactos MX:      {metricas['pct_contactos']}% ({metricas['contactos_encontrados']})")

        # Mostrar primeras 3 líneas de la respuesta
        lineas = [l.strip() for l in reply.split('\n') if l.strip()][:3]
        for linea in lineas:
            print(f"    > {linea[:100]}")

        resultados.append({
            **item,
            "reply": reply,
            "rag_used": rag_used,
            "elapsed": elapsed,
            **metricas,
            "calidad": calidad,
        })

        # Pequeña pausa entre preguntas para no saturar el modelo
        if i < len(PREGUNTAS):
            time.sleep(1)

    # ── RESUMEN FINAL ─────────────────────────────────────────────────────────
    validos = [r for r in resultados if "error" not in r]
    errores = [r for r in resultados if "error" in r]

    scores       = [r["score_total"] for r in validos]
    avg_score    = round(sum(scores) / len(scores), 1) if scores else 0
    max_score    = max(scores) if scores else 0
    min_score    = min(scores) if scores else 0

    rag_activado = sum(1 for r in validos if r.get("rag_used"))
    rag_esperado_y_activado = sum(
        1 for r in validos if r.get("rag_used") and r.get("rag_esperado")
    )

    elapsed_vals = [r["elapsed"] for r in validos]
    avg_tiempo   = round(sum(elapsed_vals) / len(elapsed_vals), 1) if elapsed_vals else 0

    excelentes  = sum(1 for r in validos if r["score_total"] >= 85)
    buenos      = sum(1 for r in validos if 70 <= r["score_total"] < 85)
    aceptables  = sum(1 for r in validos if 55 <= r["score_total"] < 70)
    deficientes = sum(1 for r in validos if r["score_total"] < 55)

    print("\n\n" + "="*70)
    print("  RESUMEN DEL ANALISIS")
    print("="*70)
    print(f"  Preguntas ejecutadas: {len(validos)}/{len(PREGUNTAS)}")
    print(f"  Errores/Timeouts:     {len(errores)}")
    print()
    print(f"  SCORE PROMEDIO:  {avg_score}/100")
    print(f"  Score maximo:    {max_score}/100")
    print(f"  Score minimo:    {min_score}/100")
    print()
    print(f"  Calidad de respuestas:")
    print(f"    [EXCELENTE] >= 85:  {excelentes}")
    print(f"    [BUENO]     70-84:  {buenos}")
    print(f"    [ACEPTABLE] 55-69:  {aceptables}")
    print(f"    [DEFICIENTE] <55:   {deficientes}")
    print()
    print(f"  RAG activado:    {rag_activado}/{len(validos)} respuestas")
    print(f"  RAG cuando esperado: {rag_esperado_y_activado}/{sum(1 for r in validos if r.get('rag_esperado'))}")
    print(f"  Tiempo promedio: {avg_tiempo}s por respuesta")
    print()

    # Peores respuestas
    peores = sorted(validos, key=lambda x: x["score_total"])[:3]
    print("  Respuestas con menor puntaje (para mejora):")
    for r in peores:
        print(f"    {r['id']} | {r['categoria']} | Score: {r['score_total']} | {r['pregunta'][:60]}...")

    # Mejores respuestas
    mejores = sorted(validos, key=lambda x: x["score_total"], reverse=True)[:3]
    print()
    print("  Respuestas con mayor puntaje:")
    for r in mejores:
        print(f"    {r['id']} | {r['categoria']} | Score: {r['score_total']} | {r['pregunta'][:60]}...")

    print()
    print("="*70)

    # Guardar resultados JSON
    output_file = "analisis_resultados.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "fecha": datetime.now().isoformat(),
            "backend": BASE_URL,
            "total_preguntas": len(PREGUNTAS),
            "score_promedio": avg_score,
            "score_max": max_score,
            "score_min": min_score,
            "excelentes": excelentes,
            "buenos": buenos,
            "aceptables": aceptables,
            "deficientes": deficientes,
            "rag_activado": rag_activado,
            "tiempo_promedio": avg_tiempo,
            "resultados": [{
                "id": r["id"],
                "categoria": r["categoria"],
                "dificultad": r["dificultad"],
                "pregunta": r["pregunta"],
                "score_total": r.get("score_total", 0),
                "calidad": r.get("calidad", "ERROR"),
                "rag_usado": r.get("rag_used", False),
                "elapsed": r.get("elapsed", 0),
                "longitud": r.get("longitud", 0),
                "keywords_encontradas": r.get("keywords_encontradas", []),
                "reply_preview": r.get("reply", "")[:200],
            } for r in resultados]
        }, f, ensure_ascii=False, indent=2)
    print(f"  Resultados guardados en: {output_file}")
    print("="*70 + "\n")

    return avg_score


if __name__ == "__main__":
    main()
