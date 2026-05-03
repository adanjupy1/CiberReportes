#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analisis_respuestas_v2.py — Análisis profundo de calidad de respuestas
con sesiones aisladas para evitar timeouts y evaluar RAG con umbral 1.8.
"""
import os, sys, json, uuid, time, requests
from datetime import datetime

os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8002"
TIMEOUT  = 200

PREGUNTAS = [
    {
        "id": "P01", "categoria": "PHISHING", "dificultad": "Basico",
        "pregunta": "¿Qué es el phishing y cómo puedo identificar un correo fraudulento?",
        "keywords_tecnicas": ["phishing", "correo", "enlace", "remitente", "sospechoso", "falso"],
        "keywords_mx": [], "contactos_mx": [], "rag_esperado": False,
    },
    {
        "id": "P02", "categoria": "PHISHING", "dificultad": "Especifico MX",
        "pregunta": "Recibi un SMS del SAT diciendo que tengo una devolucion de impuestos pendiente con un link. ¿Es real?",
        "keywords_tecnicas": ["sat", "phishing", "link", "falso"],
        "keywords_mx": ["sat.gob.mx", "sat", "autenticidad"],
        "contactos_mx": ["cert", "sat"], "rag_esperado": True,
    },
    {
        "id": "P03", "categoria": "PHISHING", "dificultad": "Especifico MX",
        "pregunta": "Me llego un correo del IMSS pidiendo verificar mis semanas cotizadas con un formulario. ¿Qué hago?",
        "keywords_tecnicas": ["imss", "phishing", "verificar"],
        "keywords_mx": ["imss.gob.mx", "imss", "nss"],
        "contactos_mx": ["800-623-2323", "imss"], "rag_esperado": True,
    },
    {
        "id": "P04", "categoria": "FRAUDE BANCARIO", "dificultad": "Basico",
        "pregunta": "¿Qué es el vishing y cómo funciona el fraude por llamada telefónica?",
        "keywords_tecnicas": ["vishing", "llamada", "banco", "nip", "token"],
        "keywords_mx": [], "contactos_mx": [], "rag_esperado": False,
    },
    {
        "id": "P05", "categoria": "FRAUDE BANCARIO", "dificultad": "Urgente MX",
        "pregunta": "Me robaron dinero de mi cuenta BBVA por internet, hicieron transferencias que yo no autorice. ¿Qué hago ahorita?",
        "keywords_tecnicas": ["bloquear", "transferencia", "denuncia"],
        "keywords_mx": ["condusef", "banco"],
        "contactos_mx": ["condusef", "800"], "rag_esperado": True,
    },
    {
        "id": "P06", "categoria": "FRAUDE BANCARIO", "dificultad": "Especifico MX",
        "pregunta": "¿Cuánto tiempo tiene mi banco para responder mi reclamación por fraude?",
        "keywords_tecnicas": ["plazo", "dias", "respuesta"],
        "keywords_mx": ["condusef", "dias habiles", "sipres"],
        "contactos_mx": ["condusef"], "rag_esperado": True,
    },
    {
        "id": "P07", "categoria": "RANSOMWARE", "dificultad": "Basico",
        "pregunta": "¿Qué es el ransomware y por qué es peligroso para las empresas?",
        "keywords_tecnicas": ["ransomware", "cifra", "rescate", "datos", "empresa"],
        "keywords_mx": [], "contactos_mx": [], "rag_esperado": False,
    },
    {
        "id": "P08", "categoria": "RANSOMWARE", "dificultad": "Critico MX",
        "pregunta": "La computadora de mi empresa fue infectada con ransomware, los archivos estan cifrados y piden rescate en Bitcoin. Pasos a seguir.",
        "keywords_tecnicas": ["desconectar", "apagar", "respaldo", "pagar", "rescate"],
        "keywords_mx": ["cert", "policia"],
        "contactos_mx": ["cert", "088"], "rag_esperado": True,
    },
    {
        "id": "P09", "categoria": "RANSOMWARE", "dificultad": "Prevencion",
        "pregunta": "¿Qué medidas debe tomar una PYME mexicana para protegerse del ransomware?",
        "keywords_tecnicas": ["backup", "actualizacion", "antivirus", "mfa"],
        "keywords_mx": ["pyme"], "contactos_mx": [], "rag_esperado": True,
    },
    {
        "id": "P10", "categoria": "PRIVACIDAD", "dificultad": "Legal MX",
        "pregunta": "¿Qué son los derechos ARCO y cómo los ejerzo si una empresa tiene mis datos sin mi consentimiento?",
        "keywords_tecnicas": ["acceso", "rectificacion", "cancelacion", "oposicion", "datos personales"],
        "keywords_mx": ["inai", "lfpdppp"],
        "contactos_mx": ["inai", "800-835-4324"], "rag_esperado": True,
    },
    {
        "id": "P11", "categoria": "PRIVACIDAD", "dificultad": "Legal MX",
        "pregunta": "Una empresa filtró mis datos personales. ¿Tienen obligación de avisarme y qué puedo hacer?",
        "keywords_tecnicas": ["brecha", "notificacion", "filtracion", "denuncia"],
        "keywords_mx": ["inai", "lfpdppp"],
        "contactos_mx": ["inai"], "rag_esperado": True,
    },
    {
        "id": "P12", "categoria": "SMISHING", "dificultad": "Especifico MX",
        "pregunta": "Recibi un SMS de mi banco diciendo que mi tarjeta fue bloqueada y que ingrese mis datos en una liga. ¿Qué hago?",
        "keywords_tecnicas": ["smishing", "sms", "liga", "fraude", "falso"],
        "keywords_mx": ["condusef", "banco"],
        "contactos_mx": ["condusef", "800"], "rag_esperado": True,
    },
    {
        "id": "P13", "categoria": "SEXTORSION", "dificultad": "Urgente MX",
        "pregunta": "Alguien en redes sociales tiene fotos intimas mias y me pide dinero para no publicarlas. ¿Qué hago?",
        "keywords_tecnicas": ["extorsion", "no pagar", "evidencia", "bloquear", "denuncia", "headers", "captura", "url", "logs"],
        "keywords_mx": ["policia cibernetica", "088"],
        "contactos_mx": ["088", "policia"], "rag_esperado": True,
    },
    {
        "id": "P14", "categoria": "BUENAS PRACTICAS", "dificultad": "Basico",
        "pregunta": "¿Cómo crear una contraseña segura y qué es la autenticación de dos factores?",
        "keywords_tecnicas": ["contrasena", "caracteres", "mayusculas", "2fa", "mfa"],
        "keywords_mx": [], "contactos_mx": [], "rag_esperado": False,
    },
    {
        "id": "P15", "categoria": "BUENAS PRACTICAS", "dificultad": "Intermedio",
        "pregunta": "¿Es seguro conectarme a la red WiFi pública de un café para revisar mi cuenta bancaria?",
        "keywords_tecnicas": ["wifi", "publica", "inseguro", "vpn", "mitm"],
        "keywords_mx": [], "contactos_mx": [], "rag_esperado": True,
    },
    {
        "id": "P16", "categoria": "MARCO LEGAL", "dificultad": "Legal MX",
        "pregunta": "¿Qué leyes mexicanas regulan los delitos informaticos y cuáles son las penas?",
        "keywords_tecnicas": ["codigo penal", "delito informatico", "prision", "federal"],
        "keywords_mx": ["codigo penal federal", "211"],
        "contactos_mx": ["fgr", "088"], "rag_esperado": True,
    },
    {
        "id": "P17", "categoria": "ESTADISTICAS", "dificultad": "Informativo",
        "pregunta": "¿Cuáles son las principales amenazas de ciberseguridad en México en 2024?",
        "keywords_tecnicas": ["ataque", "phishing", "ransomware", "fraude", "amenaza"],
        "keywords_mx": ["mexico", "kaspersky"], "contactos_mx": [], "rag_esperado": True,
    },
]

def fuzzy_keyword_match(text, keywords):
    """Búsqueda flexible de palabras clave (ignora tildes y busca fragmentos)."""
    import unicodedata
    def normalize(s):
        return "".join(c for c in unicodedata.normalize('NFD', s.lower())
                       if unicodedata.category(c) != 'Mn')
    
    norm_text = normalize(text)
    found = []
    for k in keywords:
        norm_k = normalize(k)
        if norm_k in norm_text:
            found.append(k)
    return found

def puntuar_respuesta(respuesta: str, item: dict) -> dict:
    r = respuesta.lower()
    
    # Evaluación con búsqueda flexible
    kw_tecnicas = item["keywords_tecnicas"]
    encontradas_tec = fuzzy_keyword_match(respuesta, kw_tecnicas)
    pct_tecnicas = len(encontradas_tec) / len(kw_tecnicas) * 100 if kw_tecnicas else 100

    kw_mx = item["keywords_mx"]
    encontradas_mx = fuzzy_keyword_match(respuesta, kw_mx)
    pct_mx = len(encontradas_mx) / len(kw_mx) * 100 if kw_mx else 100

    contactos = item["contactos_mx"]
    encontrados_c = fuzzy_keyword_match(respuesta, contactos)
    pct_contactos = len(encontrados_c) / len(contactos) * 100 if contactos else 100

    largo = len(respuesta)
    pct_longitud = 100 if 100 <= largo <= 1500 else 50
    tiene_estructura = any(c in respuesta for c in ["**", "1.", "2.", "-", "*"])
    pct_estructura = 100 if tiene_estructura else 50
    info_peligrosa = any(f in r for f in ["pague el rescate", "transfer bitcoin"])
    pct_seguridad = 0 if info_peligrosa else 100

    score = (pct_tecnicas * 0.35 + pct_mx * 0.25 + pct_contactos * 0.15 + 
             pct_longitud * 0.10 + pct_estructura * 0.10 + pct_seguridad * 0.05)
    
    return {
        "score_total": round(score, 1),
        "pct_tecnicas": round(pct_tecnicas, 0),
        "pct_mx": round(pct_mx, 0),
        "pct_contactos": round(pct_contactos, 0),
        "longitud": largo,
        "keywords_encontradas": encontradas_tec,
        "mx_encontradas": encontradas_mx,
        "contactos_encontrados": encontrados_c,
    }

def main():
    print("\n" + "="*70)
    print("  ANALISIS DE RESPUESTAS V2 — SESIONES AISLADAS (UMBRAL 1.8)")
    print("="*70)

    resultados = []
    for i, item in enumerate(PREGUNTAS, 1):
        # Sesión única por pregunta
        session_id = f"v2-test-{uuid.uuid4().hex[:6]}"
        print(f"\n[{i:02d}/{len(PREGUNTAS)}] {item['id']} | {item['categoria']}")
        print(f"  P: {item['pregunta'][:70]}...")

        t0 = time.time()
        try:
            resp = requests.post(f"{BASE_URL}/api/chat", 
                                json={"session_id": session_id, "message": item["pregunta"]}, 
                                timeout=TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            reply = data.get("reply", "")
            rag_used = data.get("rag_used", False)
            elapsed = round(time.time() - t0, 1)
            
            metricas = puntuar_respuesta(reply, item)
            calidad = "[EXCELENTE]" if metricas["score_total"] >= 85 else "[BUENO]" if metricas["score_total"] >= 70 else "[ACEPTABLE]" if metricas["score_total"] >= 55 else "[DEFICIENTE]"
            
            print(f"  {calidad} Score:{metricas['score_total']} RAG:{'SI' if rag_used else 'NO'} {elapsed}s {len(reply)}chars")
            resultados.append({**item, "reply": reply, "rag_used": rag_used, "elapsed": elapsed, **metricas, "calidad": calidad})
        except Exception as e:
            print(f"  ERROR: {e}")
            resultados.append({**item, "error": str(e), "score_total": 0, "rag_used": False, "elapsed": TIMEOUT})

    # Guardar JSON
    with open("analisis_resultados_v2.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
