# -*- coding: utf-8 -*-
"""
Motor de búsqueda semántica para Directorio de Policía Cibernética.
Carga datos de 08_directorio.jsonl y busca estados por cosine similarity.
"""
from __future__ import annotations

import json
import re
import unicodedata
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


def _normalize(text: str) -> str:
    """Normaliza texto: quita acentos, lowercase, colapsa espacios."""
    nfkd = unicodedata.normalize("NFKD", text)
    out = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", out).strip().lower()


@dataclass
class DirectoryResult:
    """Resultado de búsqueda del directorio."""
    estado: str
    respuesta: str
    telefono: str
    direccion: str
    area: str
    correo: str
    score: float
    variantes: List[str] = field(default_factory=list)


def _parse_contact(respuesta: str) -> Dict[str, str]:
    """Extrae campos estructurados de la respuesta."""
    fields = {"telefono": "", "direccion": "", "area": "", "correo": ""}

    # TELEFONO
    m = re.search(r"TELEFONO:\s*(.+?)(?:\s*,\s*DIREC|\s*,\s*NOMBRE|\s*$)", respuesta, re.I)
    if m:
        fields["telefono"] = m.group(1).strip().rstrip(",").strip()

    # DIRECCIÓN
    m = re.search(r"DIRECCI[OÓ]N:\s*(.+?)(?:\s*,\s*NOMBRE|\s*,\s*CORREO|\s*$)", respuesta, re.I)
    if m:
        fields["direccion"] = m.group(1).strip().rstrip(",").strip()

    # NOMBRE DEL AREA
    m = re.search(r"NOMBRE DEL AREA:\s*(.+?)(?:\s*,\s*CORREO|\s*$)", respuesta, re.I)
    if m:
        fields["area"] = m.group(1).strip().rstrip(",").strip()

    # CORREO
    m = re.search(r"CORREO(?: OFICIAL)?:\s*(.+?)$", respuesta, re.I)
    if m:
        fields["correo"] = m.group(1).strip()

    return fields


class DirectoryEngine:
    """Motor de búsqueda semántica para el directorio telefónico."""

    def __init__(
        self,
        data_path: str,
        model_name: str = "intfloat/multilingual-e5-large",
        base_threshold: float = 0.50,
    ):
        self.data_path = Path(data_path)
        self.model_name = model_name
        self.base_threshold = base_threshold
        self.dataset: List[Dict[str, Any]] = []
        self.states: List[str] = []

        # Textos indexados y embeddings
        self._index_texts: List[str] = []
        self._index_map: List[int] = []
        self._embeddings: Optional[np.ndarray] = None
        self.model: Optional[SentenceTransformer] = None

        self._load_data()
        self._init_model()
        self._is_e5 = "e5" in model_name.lower()
        self._build_index()

    def _load_data(self):
        """Carga el JSONL del directorio."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self.dataset.append(item)

                # Extraer nombre del estado
                pregunta = item.get("pregunta", "")
                estado = pregunta.replace("contacto policía cibernética ", "").rstrip("?").strip()
                item["_estado"] = estado
                self.states.append(estado)

        self.states.sort(key=lambda s: _normalize(s))
        print(f"✅ Directorio cargado: {len(self.dataset)} estados")

    def _init_model(self):
        """Carga el modelo sentence-transformers."""
        print(f"🔄 Cargando modelo: {self.model_name} …")
        self.model = SentenceTransformer(self.model_name)
        print("✅ Modelo cargado")

    def _build_index(self):
        """Genera embeddings para preguntas + variantes."""
        for idx, item in enumerate(self.dataset):
            pregunta = item.get("pregunta", "").strip()
            if pregunta:
                self._index_texts.append(pregunta)
                self._index_map.append(idx)

            variantes_str = item.get("variantes_pregunta", "")
            if variantes_str:
                for v in variantes_str.split("|"):
                    v = v.strip()
                    if v and v.lower() != pregunta.lower():
                        self._index_texts.append(v)
                        self._index_map.append(idx)

        print(f"🔄 Generando embeddings para {len(self._index_texts)} textos …")
        texts_to_encode = (
            [f"passage: {t}" for t in self._index_texts]
            if self._is_e5
            else self._index_texts
        )
        self._embeddings = self.model.encode(
            texts_to_encode, show_progress_bar=True, normalize_embeddings=True
        )
        print(f"✅ Índice listo: {self._embeddings.shape}")

    def search(
        self, query: str, top_k: int = 5, min_score: float | None = None
    ) -> List[DirectoryResult]:
        """Busca las mejores coincidencias por cosine similarity."""
        if min_score is None:
            min_score = self.base_threshold

        q_text = f"query: {query}" if self._is_e5 else query
        q_emb = self.model.encode([q_text], normalize_embeddings=True)
        scores = cosine_similarity(q_emb, self._embeddings)[0]

        # Agrupar por ítem (mejor score)
        best: Dict[int, float] = {}
        for i, sc in enumerate(scores):
            ds_idx = self._index_map[i]
            if sc > best.get(ds_idx, 0.0):
                best[ds_idx] = float(sc)

        results = []
        for ds_idx, sc in sorted(best.items(), key=lambda x: x[1], reverse=True):
            if sc < min_score:
                continue
            item = self.dataset[ds_idx]
            contact = _parse_contact(item.get("respuesta", ""))
            variantes = []
            vs = item.get("variantes_pregunta", "")
            if vs:
                variantes = [v.strip() for v in vs.split("|") if v.strip()]

            results.append(
                DirectoryResult(
                    estado=item.get("_estado", ""),
                    respuesta=item.get("respuesta", ""),
                    telefono=contact["telefono"],
                    direccion=contact["direccion"],
                    area=contact["area"],
                    correo=contact["correo"],
                    score=sc,
                    variantes=variantes,
                )
            )
            if len(results) >= top_k:
                break

        return results

    def get_best_match(
        self, query: str, min_score: float | None = None
    ) -> Optional[DirectoryResult]:
        """Retorna la mejor coincidencia o None."""
        results = self.search(query, top_k=1, min_score=min_score)
        return results[0] if results else None

    def get_all_states(self) -> List[Dict[str, Any]]:
        """Retorna todos los estados con su info de contacto."""
        result = []
        for item in sorted(self.dataset, key=lambda x: _normalize(x.get("_estado", ""))):
            contact = _parse_contact(item.get("respuesta", ""))
            result.append({
                "estado": item.get("_estado", ""),
                "telefono": contact["telefono"],
                "direccion": contact["direccion"],
                "area": contact["area"],
                "correo": contact["correo"],
            })
        return result

    def get_state_by_name(self, name: str) -> Optional[DirectoryResult]:
        """Busca un estado exacto por nombre (con normalización)."""
        norm_name = _normalize(name)
        for idx, item in enumerate(self.dataset):
            if _normalize(item.get("_estado", "")) == norm_name:
                contact = _parse_contact(item.get("respuesta", ""))
                return DirectoryResult(
                    estado=item.get("_estado", ""),
                    respuesta=item.get("respuesta", ""),
                    telefono=contact["telefono"],
                    direccion=contact["direccion"],
                    area=contact["area"],
                    correo=contact["correo"],
                    score=1.0,
                )
        # Fallback: búsqueda semántica
        return self.get_best_match(name, min_score=0.40)
