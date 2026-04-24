#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a Llama-3.2 Instruct SFT dataset (JSONL with `messages`) from a transcript.

Usage:
  python build_dataset_from_transcript.py --transcript transcript.txt --out dataset_audio.jsonl

Notes:
- This script is deterministic and does NOT call external APIs.
- It creates Q/A pairs by extracting transcript sentences that mention specific keywords.
"""

import argparse
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple

KEYWORDS = [
  ("registro de reportes cibernéticos", ["registro", "reportes cibernéticos", "reporte cibernético"]),
  ("folio", ["folio", "confirmación", "acuse"]),
  ("captcha", ["captcha", "no soy un robot"]),
  ("anónimo", ["anónimo", "anonimo"]),
  ("persona física", ["persona física", "persona fisica"]),
  ("teléfono", ["teléfono", "telefono", "10 dígitos", "10 digitos", "celular"]),
  ("correo", ["correo", "email", "e-mail"]),
  ("medio", ["medio", "facebook", "whatsapp", "correo electrónico", "sms", "llamada"]),
  ("descripción del incidente", ["descripción", "descripcion", "incidente", "hechos", "narrar"]),
  ("URL o liga", ["url", "liga", "enlace", "sitio", "página", "pagina"]),
  ("carga de archivos", ["archivo", "adjuntar", "subir", "evidencia", "captura", "pdf", "imagen"]),
]

SYSTEM = (
  "Eres un asistente que ayuda a una persona a entender y llenar el formulario "
  "de Registro de Reportes Cibernéticos. Responde en español, claro y paso a paso. "
  "Si falta información, pide el dato exacto que falta."
)

def normalize(s: str) -> str:
  s = s.lower()
  s = re.sub(r"\s+", " ", s).strip()
  return s

def split_sentences(text: str) -> List[str]:
  # Simple sentence splitter for Spanish text.
  text = re.sub(r"\s+", " ", text).strip()
  if not text:
    return []
  # Split on ., ?, ! keeping it.
  parts = re.split(r"(?<=[\.!\?\!])\s+", text)
  # Filter very short fragments.
  return [p.strip() for p in parts if len(p.strip()) >= 12]

def pick_sentences(sentences: List[str], needles: List[str], max_sent: int = 3) -> List[str]:
  out = []
  for sent in sentences:
    ns = normalize(sent)
    if any(n in ns for n in needles):
      out.append(sent)
      if len(out) >= max_sent:
        break
  return out

def make_example(user_q: str, assistant_a: str) -> Dict:
  return {
    "messages": [
      {"role": "system", "content": SYSTEM},
      {"role": "user", "content": user_q},
      {"role": "assistant", "content": assistant_a.strip()},
    ]
  }

def main():
  ap = argparse.ArgumentParser()
  ap.add_argument("--transcript", required=True, help="Path to transcript .txt (Spanish preferred).")
  ap.add_argument("--out", required=True, help="Output JSONL path.")
  ap.add_argument("--max_per_topic", type=int, default=3, help="Max Q/A examples per topic.")
  args = ap.parse_args()

  text = Path(args.transcript).read_text(encoding="utf-8", errors="ignore")
  sentences = split_sentences(text)

  dataset = []

  # Global: full summary (first ~8 sentences)
  summary = " ".join(sentences[:8]).strip()
  if summary:
    dataset.append(make_example("Resume el contenido del video en 5-8 frases.", summary))

  # Topic-based Q/A
  for topic, needles in KEYWORDS:
    picked = pick_sentences(sentences, [normalize(n) for n in needles], max_sent=args.max_per_topic)
    if not picked:
      continue
    answer = " ".join(picked)
    dataset.append(make_example(f"¿Qué menciona el video sobre {topic}?", answer))

    # Create a second variant question
    dataset.append(make_example(
      f"Explícame {topic} como si fuera la primera vez que lleno el formulario.",
      answer
    ))

  # Process / step-by-step: heuristics over imperative verbs
  step_sents = []
  for s in sentences:
    ns = normalize(s)
    if any(w in ns for w in ["selecciona", "seleccione", "ingresa", "ingrese", "captura", "capturar", "da clic", "haz clic", "enviar", "continúa", "continuar"]):
      step_sents.append(s)
    if len(step_sents) >= 10:
      break
  if step_sents:
    dataset.append(make_example("Dame los pasos para llenar el formulario según el video.", " ".join(step_sents)))

  # Write JSONL
  outp = Path(args.out)
  with outp.open("w", encoding="utf-8") as f:
    for ex in dataset:
      f.write(json.dumps(ex, ensure_ascii=False) + "\n")

  print(f"OK: wrote {len(dataset)} examples -> {outp}")

if __name__ == "__main__":
  main()
