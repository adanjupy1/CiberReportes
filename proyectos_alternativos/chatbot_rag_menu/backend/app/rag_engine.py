# -*- coding: utf-8 -*-
"""
Motor RAG (Retrieval-Augmented Generation) para chatbot
Búsqueda semántica en dataset JSONL
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class RAGResult:
    """Resultado de búsqueda RAG"""
    pregunta: str
    respuesta: str
    tematica: str
    score: float
    variantes: List[str] = None

class RAGEngine:
    """Motor de búsqueda y recuperación basado en dataset JSONL"""
    
    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.dataset = []
        self.tematicas = set()
        self._load_dataset()
    
    def _load_dataset(self):
        """Carga el dataset JSONL en memoria"""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset no encontrado: {self.dataset_path}")
        
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    self.dataset.append(item)
                    if 'tematica' in item:
                        self.tematicas.add(item['tematica'])
                except json.JSONDecodeError:
                    continue
        
        print(f"[OK] Dataset cargado: {len(self.dataset)} entradas, {len(self.tematicas)} tematicas")
    
    def normalize_text(self, text: str) -> str:
        """Normaliza texto para comparación"""
        if not text:
            return ""
        text = text.lower()
        # Normalizar acentos
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'ñ': 'n', 'ü': 'u'
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        # Remover puntuación excepto espacios
        text = re.sub(r'[¿?¡!.,;:\-_(){}[\]"\']+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calcula similitud entre dos textos (word overlap + boost por contención)"""
        words1 = set(self.normalize_text(text1).split())
        words2 = set(self.normalize_text(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        base_score = intersection / union if union > 0 else 0
        
        # Boost si un texto contiene al otro
        norm1 = self.normalize_text(text1)
        norm2 = self.normalize_text(text2)
        if norm1 in norm2 or norm2 in norm1:
            base_score += 0.3
        
        return min(1.0, base_score)
    
    def search(self, query: str, top_k: int = 5, min_score: float = 0.3) -> List[RAGResult]:
        """Busca en el dataset las mejores coincidencias"""
        results = []
        
        for item in self.dataset:
            # Buscar en pregunta principal
            score = self.calculate_similarity(query, item.get('pregunta', ''))
            
            # Buscar en variantes si existen
            variantes_str = item.get('variantes_pregunta', '')
            variantes = []
            if variantes_str:
                variantes = [v.strip() for v in variantes_str.split('|')]
                for variante in variantes:
                    if variante:
                        variant_score = self.calculate_similarity(query, variante)
                        score = max(score, variant_score)
            
            # Agregar si supera umbral
            if score >= min_score:
                results.append(RAGResult(
                    pregunta=item.get('pregunta', ''),
                    respuesta=item.get('respuesta', ''),
                    tematica=item.get('tematica', ''),
                    score=score,
                    variantes=variantes
                ))
        
        # Ordenar por score descendente
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:top_k]
    
    def get_by_topic(self, topic: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene entradas por temática"""
        results = []
        topic_norm = self.normalize_text(topic)
        
        for item in self.dataset:
            item_topic_norm = self.normalize_text(item.get('tematica', ''))
            if topic_norm in item_topic_norm or item_topic_norm in topic_norm:
                results.append(item)
                if len(results) >= limit:
                    break
        
        return results
    
    def get_topics_list(self) -> List[str]:
        """Retorna lista de temáticas disponibles"""
        return sorted(list(self.tematicas))
    
    def get_best_match(self, query: str, min_score: float = 0.5) -> Optional[RAGResult]:
        """Obtiene la mejor coincidencia si supera el umbral"""
        results = self.search(query, top_k=1, min_score=min_score)
        return results[0] if results else None
