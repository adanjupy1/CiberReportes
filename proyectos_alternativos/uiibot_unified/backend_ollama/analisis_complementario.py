#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, uuid, time, requests
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE    = "http://localhost:8002"
TIMEOUT = 180

preguntas = [
    ("P11","PRIVACIDAD",
     "Una empresa filtro mis datos personales. Tienen obligacion de avisarme y que puedo hacer?",
     ["brecha","notificacion","filtracion","denuncia"],["inai"],["inai"]),
    ("P12","SMISHING",
     "Recibi un SMS de mi banco diciendo que mi tarjeta fue bloqueada y que ingrese mis datos en una liga. Que hago?",
     ["smishing","sms","liga","fraude","falso"],["condusef"],["condusef","800"]),
    ("P13","SEXTORSION",
     "Alguien tiene fotos intimas mias y pide dinero para no publicarlas. Que hago?",
     ["no pagar","evidencia","bloquear","denuncia"],["policia cibernetica","088"],["088","policia"]),
    ("P14","BUENAS PRACTICAS",
     "Como crear una contrasena segura y que es la autenticacion de dos factores?",
     ["caracteres","mayusculas","numeros","2fa","mfa","gestor"],[],[]),
    ("P15","BUENAS PRACTICAS",
     "Es seguro conectarme al WiFi publico de un cafe para revisar mi cuenta bancaria?",
     ["wifi","inseguro","vpn","mitm","cifrado"],[],[]),
    ("P16","MARCO LEGAL",
     "Que leyes mexicanas regulan los delitos informaticos y cuales son las penas?",
     ["codigo penal","delito informatico","prision","federal"],
     ["codigo penal federal","211"],["fgr","088"]),
    ("P17","ESTADISTICAS",
     "Cuales son las principales amenazas de ciberseguridad en Mexico en 2024?",
     ["ataque","phishing","ransomware","fraude","amenaza"],["mexico","kaspersky"],[]),
]

print("="*60)
print("  ANALISIS COMPLEMENTARIO (sesiones independientes)")
print("="*60)

resultados = []

for pid, cat, preg, kw_tec, kw_mx, contactos in preguntas:
    sid = "ind-" + uuid.uuid4().hex[:6]
    print(f"\n[{pid}] {cat}")
    print(f"  P: {preg[:70]}...")
    t0 = time.time()
    try:
        resp = requests.post(f"{BASE}/api/chat",
            json={"session_id": sid, "message": preg}, timeout=TIMEOUT)
        d     = resp.json()
        reply = d.get("reply", "")
        rag   = d.get("rag_used", False)
        elapsed = round(time.time() - t0, 1)
        rl = reply.lower()

        enc_tec = [k for k in kw_tec if k in rl]
        enc_mx  = [k for k in kw_mx  if k in rl]
        enc_c   = [k for k in contactos if k in rl]
        pct_tec = round(len(enc_tec)/len(kw_tec)*100) if kw_tec else 100
        pct_mx  = round(len(enc_mx) /len(kw_mx) *100) if kw_mx  else 100
        pct_c   = round(len(enc_c)  /len(contactos)*100) if contactos else 100
        largo   = len(reply)
        score   = pct_tec*0.40 + pct_mx*0.30 + pct_c*0.20 + (100 if largo > 100 else 50)*0.10

        if score >= 85:   cal = "[EXCELENTE]"
        elif score >= 70: cal = "[BUENO    ]"
        elif score >= 55: cal = "[ACEPTABLE]"
        else:             cal = "[DEFICIENTE]"

        rag_str = "SI" if rag else "NO"
        print(f"  {cal}  Score:{round(score,1)}  RAG:{rag_str}  {elapsed}s  {largo}chars")
        print(f"  Tecnicas:{pct_tec}% {enc_tec}")
        if kw_mx:     print(f"  MX:{pct_mx}% {enc_mx}")
        if contactos: print(f"  Contactos:{pct_c}% {enc_c}")
        lineas = [x.strip() for x in reply.split('\n') if x.strip()][:2]
        for l in lineas:
            print(f"    > {l[:100]}")
        resultados.append({"id": pid, "cat": cat, "score": round(score,1),
                            "cal": cal, "rag": rag, "elapsed": elapsed})
    except Exception as e:
        print(f"  ERROR: {e}")
        resultados.append({"id": pid, "cat": cat, "score": 0,
                            "cal": "ERROR", "rag": False, "elapsed": TIMEOUT})

print("\n" + "="*60)
print("  RESUMEN COMPLEMENTARIO")
print("="*60)
ok = [r for r in resultados if r["cal"] != "ERROR"]
if ok:
    avg = round(sum(r["score"] for r in ok) / len(ok), 1)
    print(f"  Score promedio: {avg}/100")
    print(f"  Completadas: {len(ok)}/{len(resultados)}")
    for r in ok:
        print(f"  {r['id']}  {r['cat']:<20s}  {r['cal']}  {r['score']}")
print("="*60)
