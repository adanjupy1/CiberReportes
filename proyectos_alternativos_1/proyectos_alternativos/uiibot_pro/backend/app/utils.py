# -*- coding: utf-8 -*-
import re, unicodedata, datetime, json, os
from pathlib import Path

def normalize(text: str) -> str:
    text = (text or "").strip()
    text = text.replace("\u00a0", " ")
    # remove accents, lowercase
    t = unicodedata.normalize("NFD", text)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = t.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t

def is_yes(text: str) -> bool:
    t = normalize(text)
    return t in {"si", "sí", "s", "claro", "va", "ok", "de acuerdo", "dale", "afirmativo"}

def is_no(text: str) -> bool:
    t = normalize(text)
    return t in {"no", "n", "nop", "negativo", "para nada"}

def month_year_code(dt: datetime.datetime) -> str:
    # mm + yy (e.g. 1125)
    return dt.strftime("%m%y")

def load_json(rel_path: str):
    base = Path(__file__).resolve().parent
    p = base / rel_path
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)
