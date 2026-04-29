# -*- coding: utf-8 -*-
"""
Motor de búsqueda semántica para chat de ciberseguridad.
Carga 7 datasets JSONL y busca respuestas por cosine similarity
usando BAAI/bge-m3 (sin prefijos query:/passage:).
"""
from __future__ import annotations

import json
import unicodedata
import re
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


DATA_DIR = Path(__file__).parent.parent / "data_base"

DEFAULT_MODEL = "BAAI/bge-m3"
DEFAULT_BASE_THRESHOLD = 0.55
DEFAULT_REL_THRESHOLD = 0.78
DEFAULT_DEDUP_THRESHOLD = 0.92


def _normalize(text: str) -> str:
    """Quita acentos, lowercase, colapsa espacios."""
    nfkd = unicodedata.normalize("NFKD", text)
    out = "".join(c for c in nfkd if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", out).strip().lower()


@dataclass
class SearchResult:
    """Un resultado de búsqueda semántica."""
    pregunta: str
    respuesta: str
    tematica: str
    score: float
    contexto_adicional: str = ""
    variantes: List[str] = field(default_factory=list)


class EmbeddingEngine:
    """Motor de embeddings para los 7 datasets de ciberseguridad."""

    def __init__(
        self,
        data_dir: str | Path | None = None,
        model_name: str = DEFAULT_MODEL,
        base_threshold: float = DEFAULT_BASE_THRESHOLD,
        rel_threshold: float = DEFAULT_REL_THRESHOLD,
        dedup_threshold: float = DEFAULT_DEDUP_THRESHOLD,
    ):
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.model_name = model_name
        self.base_threshold = base_threshold
        self.rel_threshold = rel_threshold
        self.dedup_threshold = dedup_threshold

        self.dataset: List[Dict[str, Any]] = []
        self.tematicas: List[str] = []

        # Índice
        self._index_texts: List[str] = []
        self._index_map: List[int] = []   # texto → idx en dataset
        self._embeddings: Optional[np.ndarray] = None
        self.model: Optional[SentenceTransformer] = None

        self._load_data()
        self._init_model()
        self._build_index()

    # ── Carga de datos ───────────────────────────────────────────

    def _load_data(self):
        """Carga todos los .jsonl de data_dir."""
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Directorio no encontrado: {self.data_dir}")

        seen_preguntas = set()
        files = sorted(self.data_dir.glob("*.jsonl"))
        for fpath in files:
            with open(fpath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    pregunta = item.get("pregunta", "").strip()
                    key = _normalize(pregunta)
                    if key in seen_preguntas:
                        continue
                    seen_preguntas.add(key)

                    self.dataset.append(item)

                    tematica = item.get("tematica", "general")
                    if tematica not in self.tematicas:
                        self.tematicas.append(tematica)

        self.tematicas.sort()
        print(f"✅ Datos cargados: {len(self.dataset)} entradas, "
              f"{len(self.tematicas)} temáticas, {len(files)} archivos")

    # ── Modelo ───────────────────────────────────────────────────

    def _init_model(self):
        """Carga BAAI/bge-m3 vía sentence-transformers."""
        print(f"🔄 Cargando modelo: {self.model_name} …")
        self.model = SentenceTransformer(self.model_name)
        print(f"✅ Modelo cargado ({self.model.get_sentence_embedding_dimension()} dims)")

    # ── Índice ───────────────────────────────────────────────────

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
                    if v and _normalize(v) != _normalize(pregunta):
                        self._index_texts.append(v)
                        self._index_map.append(idx)

        print(f"🔄 Generando embeddings para {len(self._index_texts)} textos …")
        # BGE-M3 no necesita prefijos query:/passage:
        self._embeddings = self.model.encode(
            self._index_texts,
            show_progress_bar=True,
            normalize_embeddings=True,
            batch_size=64,
        )
        print(f"✅ Índice listo: {self._embeddings.shape}")

    # ── Búsqueda ─────────────────────────────────────────────────

    def search(
        self, query: str, top_k: int = 5, min_score: float | None = None
    ) -> List[SearchResult]:
        """Busca las mejores coincidencias por cosine similarity."""
        if min_score is None:
            min_score = self.base_threshold

        q_emb = self.model.encode([query], normalize_embeddings=True)
        scores = cosine_similarity(q_emb, self._embeddings)[0]

        # Agrupar por ítem (mejor score de cada entrada)
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
            variantes = []
            vs = item.get("variantes_pregunta", "")
            if vs:
                variantes = [v.strip() for v in vs.split("|") if v.strip()]

            results.append(
                SearchResult(
                    pregunta=item.get("pregunta", ""),
                    respuesta=item.get("respuesta", ""),
                    tematica=item.get("tematica", ""),
                    score=sc,
                    contexto_adicional=item.get("contexto_adicional", ""),
                    variantes=variantes,
                )
            )
            if len(results) >= top_k:
                break

        return results

    def get_best_match(
        self, query: str, min_score: float | None = None
    ) -> Optional[SearchResult]:
        """Retorna la mejor coincidencia o None."""
        results = self.search(query, top_k=1, min_score=min_score)
        return results[0] if results else None

    def get_suggestions(
        self, query: str, top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retorna sugerencias relacionadas filtrando redundancia."""
        results = self.search(query, top_k=top_k + 5, min_score=self.base_threshold)
        if not results:
            return []

        best_score = results[0].score
        filtered = []
        seen_embs = []

        for r in results:
            if r.score < best_score * self.rel_threshold:
                continue

            r_emb = self.model.encode([r.pregunta], normalize_embeddings=True)
            is_dup = False
            for prev_emb in seen_embs:
                sim = float(cosine_similarity(r_emb, prev_emb)[0][0])
                if sim > self.dedup_threshold:
                    is_dup = True
                    break
            if is_dup:
                continue

            seen_embs.append(r_emb)
            filtered.append({
                "pregunta": r.pregunta,
                "tematica": r.tematica,
                "score": round(r.score, 4),
            })
            if len(filtered) >= top_k:
                break

        return filtered

    def get_topics(self) -> List[Dict[str, Any]]:
        """Retorna las temáticas con conteo de entradas."""
        counts: Dict[str, int] = {}
        for item in self.dataset:
            t = item.get("tematica", "general")
            counts[t] = counts.get(t, 0) + 1
        return [{"tematica": t, "count": c}
                for t, c in sorted(counts.items())]

    def stats(self) -> Dict[str, Any]:
        """Estadísticas del motor."""
        return {
            "model": self.model_name,
            "dimensions": int(self._embeddings.shape[1]) if self._embeddings is not None else 0,
            "dataset_size": len(self.dataset),
            "index_size": len(self._index_texts),
            "topics": len(self.tematicas),
            "thresholds": {
                "base": self.base_threshold,
                "relative": self.rel_threshold,
                "dedup": self.dedup_threshold,
            },
        }
