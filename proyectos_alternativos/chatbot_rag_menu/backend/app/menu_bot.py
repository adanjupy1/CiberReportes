# -*- coding: utf-8 -*-
"""
Motor de conversación con estados y menús dinámicos
Integra RAG para respuestas contextuales
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, List
import re
try:
    from .rag_engine import RAGEngine
except ImportError:
    from rag_engine import RAGEngine

@dataclass
class BotReply:
    """Respuesta del bot"""
    text: str
    quick_replies: List[str]
    source: str = "menu"  # "menu", "rag", "fallback"
    debug: dict[str, Any] | None = None

class MenuBot:
    """Bot basado en menús con asistencia RAG"""
    
    def __init__(self, dataset_path: str):
        self.rag = RAGEngine(dataset_path)
        self.menu_structure = self._build_menu_structure()
        self.example_questions = self._build_example_questions()
    
    def _build_menu_structure(self) -> dict:
        """Construye estructura de menús basada en temáticas del dataset"""
        topics = self.rag.get_topics_list()
        
        # Agrupar temáticas por categorías principales
        categorias = {
            "🔐 Autenticación y Contraseñas": [],
            "📧 Phishing y Fraudes": [],
            "💰 Delitos Financieros": [],
            "👤 Privacidad y Datos": [],
            "🎯 Amenazas y Ataques": [],
            "📱 Seguridad Móvil": [],
            "🌐 Navegación Segura": [],
            "⚠️ Otros Riesgos": []
        }
        
        # Clasificar temáticas
        for topic in topics:
            topic_lower = topic.lower()
            if any(k in topic_lower for k in ['contraseña', 'autenticación', '2fa', 'password']):
                categorias["🔐 Autenticación y Contraseñas"].append(topic)
            elif any(k in topic_lower for k in ['phishing', 'fraude', 'estafa', 'scam', 'correo falso']):
                categorias["📧 Phishing y Fraudes"].append(topic)
            elif any(k in topic_lower for k in ['bancario', 'financiero', 'préstamo', 'montadeuda', 'tarjeta']):
                categorias["💰 Delitos Financieros"].append(topic)
            elif any(k in topic_lower for k in ['privacidad', 'datos', 'información', 'personal']):
                categorias["👤 Privacidad y Datos"].append(topic)
            elif any(k in topic_lower for k in ['malware', 'virus', 'ransomware', 'troyano', 'ataque']):
                categorias["🎯 Amenazas y Ataques"].append(topic)
            elif any(k in topic_lower for k in ['móvil', 'movil', 'app', 'aplicación', 'smartphone']):
                categorias["📱 Seguridad Móvil"].append(topic)
            elif any(k in topic_lower for k in ['web', 'navegación', 'internet', 'sitio']):
                categorias["🌐 Navegación Segura"].append(topic)
            else:
                categorias["⚠️ Otros Riesgos"].append(topic)
        
        # Eliminar categorías vacías
        return {k: v for k, v in categorias.items() if v}
    
    def _build_example_questions(self) -> dict:
        """Construye ejemplos de preguntas por categoría desde el dataset"""
        examples = {}
        
        # Palabras clave para cada categoría
        keywords = {
            "🔐 Autenticación y Contraseñas": ["contraseña", "autenticación", "2fa", "verificación", "password"],
            "📧 Phishing y Fraudes": ["phishing", "fraude", "estafa", "correo falso", "suplantación"],
            "💰 Delitos Financieros": ["montadeuda", "bancario", "financiero", "préstamo", "tarjeta"],
            "👤 Privacidad y Datos": ["privacidad", "datos personales", "información personal", "protección de datos"],
            "🎯 Amenazas y Ataques": ["malware", "virus", "ransomware", "ataque", "hackeo"],
            "📱 Seguridad Móvil": ["móvil", "celular", "app", "smartphone", "dispositivo móvil"],
            "🌐 Navegación Segura": ["navegación", "https", "vpn", "internet seguro", "cookies"],
            "⚠️ Otros Riesgos": ["acoso", "sextorsión", "menores", "grooming", "ciberacoso"]
        }
        
        # Obtener preguntas reales del dataset para cada categoría
        for category, keywords_list in keywords.items():
            questions = []
            for keyword in keywords_list:
                # Buscar en el dataset
                results = self.rag.search(keyword, top_k=2, min_score=0.3)
                for result in results:
                    if result.pregunta and len(result.pregunta) > 10:
                        # Evitar duplicados
                        if result.pregunta not in questions:
                            questions.append(result.pregunta)
                            if len(questions) >= 5:
                                break
                if len(questions) >= 5:
                    break
            
            # Si no encontramos suficientes, usar las temáticas
            if len(questions) < 3:
                topics = self.menu_structure.get(category, [])
                for topic in topics[:3]:
                    topic_items = self.rag.get_by_topic(topic, limit=2)
                    for item in topic_items:
                        if item.get('pregunta') and item['pregunta'] not in questions:
                            questions.append(item['pregunta'])
                            if len(questions) >= 5:
                                break
                    if len(questions) >= 5:
                        break
            
            examples[category] = questions[:5]
        
        return examples
    
    def normalize(self, text: str) -> str:
        """Normaliza texto de entrada"""
        return self.rag.normalize_text(text)
    
    def handle_message(self, session: dict[str, Any], user_text: str) -> tuple[str, dict[str, Any], BotReply]:
        """
        Procesa mensaje del usuario
        Returns: (new_state, new_context, reply)
        """
        text_norm = self.normalize(user_text)
        state = session.get("state", "Inicio")
        ctx: dict[str, Any] = session.get("context", {}) or {}
        
        # Comandos globales
        if text_norm in {"menu", "inicio", "start", "home", "volver"}:
            return self._root_menu()
        
        if text_norm in {"hacer una pregunta", "hacer pregunta", "preguntar", "ejemplos"}:
            return self._show_question_examples()
        
        if text_norm in {"ayuda", "help", "?"}:
            return "Ayuda", ctx, BotReply(
                "🤖 **Agente Bit RAG - Ayuda**\n\n"
                "Puedes:\n"
                "• Navegar por menús (escribe el número o categoría)\n"
                "• Hacer preguntas directas (ej: ¿Qué es phishing?)\n"
                "• Escribir **menu** para volver al inicio\n"
                "• Escribir **temas** para ver todas las categorías",
                ["Menú", "Temas disponibles"]
            )
        
        if text_norm in {"temas", "categorias", "ver temas"}:
            return self._show_categories()
        
        # Router por estado
        if state == "Inicio":
            return self._handle_root(text_norm, user_text, ctx)
        
        elif state == "Categorías":
            return self._handle_category_selection(text_norm, user_text, ctx)
        
        elif state == "Temas":
            return self._handle_topic_questions(text_norm, user_text, ctx)
        
        elif state == "Pregunta":
            # En este estado, cualquier mensaje es una consulta RAG directa
            return self._try_rag_answer(user_text, ctx)
        
        elif state == "Ejemplos":
            # Maneja selección de categoría para ver ejemplos
            return self._handle_example_category(text_norm, user_text, ctx)
        
        elif state == "Categoría":
            # Maneja selección de pregunta ejemplo
            return self._handle_example_question(text_norm, user_text, ctx)
        
        elif state == "Respuesta":
            # Después de una respuesta RAG, permitir preguntas de seguimiento
            if text_norm in {"mas sobre esto", "mas", "más", "mas info", "relacionadas"}:
                last_question = ctx.get("last_question")
                if last_question:
                    return self._show_related_answers(last_question, ctx)
            
            # Volver al tema desde una respuesta RAG
            if text_norm in {"volver al tema", "volver", "regresar al tema", "tema"}:
                last_topic = ctx.get("last_topic")
                if last_topic:
                    return self._show_topic_info(last_topic, ctx)
                # Si no hay tema guardado, ir al menú
                return self._root_menu()
            
            return self._try_rag_answer(user_text, ctx)
        
        elif state == "Sugerencias":
            # Maneja selección de sugerencias múltiples
            return self._handle_rag_suggestions(text_norm, user_text, ctx)
        
        elif state == "Relacionadas":
            # Maneja selección de respuestas relacionadas
            return self._handle_related_selection(text_norm, user_text, ctx)
        
        # Default: intento RAG
        return self._try_rag_answer(user_text, ctx)
    
    def _root_menu(self) -> tuple[str, dict, BotReply]:
        """Menú principal"""
        categories = list(self.menu_structure.keys())
        
        msg = (
            "🤖 **Bienvenido a Agente Bit RAG**\n\n"
            "Asistente de ciberseguridad con búsqueda inteligente.\n\n"
            "**Categorías disponibles:**\n"
        )
        
        for i, cat in enumerate(categories, 1):
            msg += f"{i}. {cat}\n"
        
        msg += "\n💡 También puedes hacer preguntas directas."
        
        quick_replies = categories[:6] + ["Ayuda", "Hacer una pregunta"]
        
        return "Inicio", {}, BotReply(msg, quick_replies, source="menu")
    
    def _show_categories(self) -> tuple[str, dict, BotReply]:
        """Muestra todas las categorías disponibles"""
        categories = list(self.menu_structure.keys())
        
        msg = "📚 **Temáticas disponibles:**\n\n"
        for i, cat in enumerate(categories, 1):
            topics_count = len(self.menu_structure[cat])
            msg += f"{i}. {cat} ({topics_count} temas)\n"
        
        msg += "\nEscribe el número o nombre de la categoría."
        
        return "Inicio", {}, BotReply(msg, categories[:8] + ["Menú"], source="menu")
    
    def _show_question_examples(self) -> tuple[str, dict, BotReply]:
        """Muestra categorías para elegir ejemplos de preguntas"""
        categories = list(self.example_questions.keys())
        
        msg = "💡 **Ejemplos de preguntas por categoría:**\n\n"
        msg += "Elige una categoría para ver ejemplos de preguntas:\n\n"
        
        for i, cat in enumerate(categories, 1):
            msg += f"{i}. {cat}\n"
        
        msg += "\n✍️ También puedes escribir tu pregunta directamente."
        
        quick_replies = categories[:4] + ["Menú"]
        
        return "Ejemplos", {}, BotReply(msg, quick_replies, source="menu")
    
    def _handle_example_category(self, text_norm: str, user_text: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Maneja selección de categoría para ver ejemplos"""
        categories = list(self.example_questions.keys())
        
        # Por número
        if text_norm.isdigit():
            idx = int(text_norm) - 1
            if 0 <= idx < len(categories):
                category = categories[idx]
                return self._show_category_examples(category, ctx)
        
        # Por nombre de categoría
        for cat in categories:
            cat_norm = self.normalize(cat)
            if cat_norm in text_norm or text_norm in cat_norm:
                return self._show_category_examples(cat, ctx)
        
        # Si no es una categoría, tratar como pregunta directa
        return self._try_rag_answer(user_text, ctx)
    
    def _show_category_examples(self, category: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Muestra ejemplos de preguntas de una categoría"""
        examples = self.example_questions.get(category, [])
        
        if not examples:
            return self._show_question_examples()
        
        msg = f"**{category}**\n\n"
        msg += "Preguntas de ejemplo (elige un número):\n\n"
        
        for i, question in enumerate(examples, 1):
            msg += f"{i}. {question}\n"
        
        msg += "\n💬 O escribe tu propia pregunta sobre este tema."
        
        ctx["example_category"] = category
        ctx["example_questions"] = examples
        
        quick_replies = [str(i) for i in range(1, min(len(examples)+1, 6))] + ["Ver categorías", "Menú"]
        
        return "Categoría", ctx, BotReply(msg, quick_replies, source="menu")
    
    def _handle_example_question(self, text_norm: str, user_text: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Maneja selección de pregunta ejemplo"""
        examples = ctx.get("example_questions", [])
        
        # Por número
        if text_norm.isdigit():
            idx = int(text_norm) - 1
            if 0 <= idx < len(examples):
                question = examples[idx]
                
                # Primero intentar coincidencia exacta
                result = self.rag.get_best_match(question, min_score=0.85)
                
                # Si no hay coincidencia exacta, buscar semánticamente
                if not result:
                    results = self.rag.search(question, top_k=3, min_score=0.4)
                    if results:
                        result = results[0]
                
                if not result:
                    return "Categoría", ctx, BotReply(
                        f"🤔 No encontré información específica sobre:\n\n**{question}**\n\n"
                        "Intenta con otra pregunta de la lista o escribe tu propia pregunta.",
                        ["Ver categorías", "Menú"],
                        source="fallback"
                    )
                
                # Mostrar la respuesta encontrada
                msg = f"✅ **{result.pregunta}**\n\n{result.respuesta}"
                if result.tematica:
                    msg += f"\n\n_Tema: {result.tematica}_"
                
                ctx["last_topic"] = result.tematica
                ctx["last_question"] = result.pregunta
                
                return "Respuesta", ctx, BotReply(
                    msg,
                    ["Más sobre esto", "Otra pregunta", "Menú"],
                    source="rag",
                    debug={"score": result.score, "original_q": question}
                )
        
        # Si no es un número, tratar como pregunta directa
        return self._try_rag_answer(user_text, ctx)
    
    def _handle_root(self, text_norm: str, user_text: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Maneja selección desde menú raíz"""
        categories = list(self.menu_structure.keys())
        
        # Intentar por número
        if text_norm.isdigit():
            idx = int(text_norm) - 1
            if 0 <= idx < len(categories):
                category = categories[idx]
                return self._show_category(category, ctx)
        
        # Intentar por nombre de categoría
        for cat in categories:
            cat_norm = self.normalize(cat)
            if cat_norm in text_norm or text_norm in cat_norm:
                return self._show_category(cat, ctx)
        
        # Si no match de menú, intentar RAG
        return self._try_rag_answer(user_text, ctx)
    
    def _show_category(self, category: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Muestra temas de una categoría"""
        topics = self.menu_structure.get(category, [])
        
        if not topics:
            return "Inicio", ctx, BotReply(
                f"No encontré temas en **{category}**",
                ["Menú", "Ayuda"]
            )
        
        msg = f"**{category}**\n\nTemas disponibles:\n\n"
        
        for i, topic in enumerate(topics[:20], 1):
            msg += f"{i}. {topic}\n"
        
        msg += "\nEscribe el número o nombre del tema."
        
        ctx["current_category"] = category
        quick_replies = topics[:6] + ["Volver al menú"]
        
        return "Categorías", ctx, BotReply(msg, quick_replies, source="menu")
    
    def _handle_category_selection(self, text_norm: str, user_text: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Maneja selección de tema dentro de categoría"""
        category = ctx.get("current_category")
        if not category:
            return self._root_menu()
        
        topics = self.menu_structure.get(category, [])
        
        # Por número
        if text_norm.isdigit():
            idx = int(text_norm) - 1
            if 0 <= idx < len(topics):
                topic = topics[idx]
                return self._show_topic_info(topic, ctx)
        
        # Por nombre de tema
        for topic in topics:
            topic_norm = self.normalize(topic)
            if topic_norm in text_norm or text_norm in topic_norm:
                return self._show_topic_info(topic, ctx)
        
        # RAG fallback
        return self._try_rag_answer(user_text, ctx)
    
    def _show_topic_info(self, topic: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Muestra información de un tema específico usando RAG con filtro de redundancia"""
        items = self.rag.get_by_topic(topic, limit=20)  # Obtener más para filtrar
        
        if not items:
            return "Temas", ctx, BotReply(
                f"No encontré información específica sobre **{topic}**.\n\n¿Tienes alguna pregunta concreta?",
                ["Volver", "Menú"]
            )
        
        # Función para verificar similitud entre preguntas
        def is_too_similar(q1: str, q2: str) -> bool:
            """Detecta similitud semántica entre preguntas"""
            norm1 = self.normalize(q1)
            norm2 = self.normalize(q2)
            
            # Caso 1: Una pregunta contiene a la otra completamente
            if norm1 in norm2 or norm2 in norm1:
                return True
            
            words1 = set(norm1.split())
            words2 = set(norm2.split())
            
            if len(words1) == 0 or len(words2) == 0:
                return False
            
            # Caso 2: Similitud Jaccard
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            jaccard = intersection / union if union > 0 else 0
            
            # Caso 3: Para preguntas cortas (< 6 palabras), ser más estricto
            if max(len(words1), len(words2)) < 6:
                return jaccard > 0.4  # Si comparten >40% de palabras, son redundantes
            else:
                return jaccard > 0.5  # Para preguntas más largas, usar umbral de 50%
        
        # Filtrar preguntas únicas (sin redundancia)
        unique_questions = []
        for item in items:
            pregunta = item.get('pregunta', '')
            if not pregunta or len(pregunta) < 10:
                continue
            
            # Verificar que no sea muy similar a las ya seleccionadas
            is_redundant = False
            for uq in unique_questions:
                if is_too_similar(pregunta, uq):
                    is_redundant = True
                    break
            
            if not is_redundant:
                unique_questions.append(pregunta)
                if len(unique_questions) >= 5:  # Limitar a 5 preguntas únicas
                    break
        
        if not unique_questions:
            return "Temas", ctx, BotReply(
                f"No encontré preguntas variadas sobre **{topic}**.\n\n¿Tienes alguna pregunta concreta?",
                ["Volver", "Menú"]
            )
        
        msg = f"📖 **{topic}**\n\n"
        msg += "**Preguntas frecuentes:**\n\n"
        
        for i, pregunta in enumerate(unique_questions, 1):
            short_q = pregunta[:80] + "..." if len(pregunta) > 80 else pregunta
            msg += f"{i}. {short_q}\n"
        
        msg += "\nEscribe el número para ver la respuesta o haz tu pregunta."
        
        ctx["current_topic"] = topic
        ctx["current_questions"] = unique_questions
        
        quick_replies = [f"P{i}" for i in range(1, min(len(unique_questions)+1, 6))] + ["Otra pregunta", "Volver"]
        
        return "Temas", ctx, BotReply(msg, quick_replies, source="rag")
    
    def _handle_topic_questions(self, text_norm: str, user_text: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Maneja preguntas dentro de un tema"""
        questions = ctx.get("current_questions", [])
        current_topic = ctx.get("current_topic")
        
        # Comando "Volver al tema" - regresa a la lista de preguntas del tema
        if text_norm in {"volver al tema", "volver", "regresar al tema", "tema"}:
            if current_topic:
                return self._show_topic_info(current_topic, ctx)
            # Si no hay tema guardado, ir al menú
            return self._root_menu()
        
        # Comando "Otra pregunta" - muestra categorías con ejemplos
        if text_norm in {"otra pregunta", "otra", "pregunta", "nueva pregunta", "hacer una pregunta"}:
            return self._show_question_examples()
        
        # Por número o P1, P2, etc
        match = re.match(r'[p]?(\d+)', text_norm)
        if match:
            idx = int(match.group(1)) - 1
            if 0 <= idx < len(questions):
                query = questions[idx]
                result = self.rag.get_best_match(query, min_score=0.7)
                if result:
                    msg = f"**{result.pregunta}**\n\n{result.respuesta}"
                    if result.tematica:
                        msg += f"\n\nTema: {result.tematica}_"
                    
                    ctx["last_question"] = result.pregunta
                    ctx["last_topic"] = result.tematica
                    
                    return "Temas", ctx, BotReply(
                        msg,
                        ["Otra pregunta", "Volver al tema", "Menú"],
                        source="rag"
                    )
        
        # Pregunta libre
        return self._try_rag_answer(user_text, ctx)
    
    def _try_rag_answer(self, user_text: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Intenta responder usando RAG con detección de menús"""
        user_norm = self.normalize(user_text)
        
        # PASO 1: Detectar si la pregunta coincide con una categoría
        categories = list(self.menu_structure.keys())
        for category in categories:
            cat_norm = self.normalize(category)
            # Extraer palabras clave de la categoría (sin emoji)
            cat_words = cat_norm.replace("autenticacion", "").replace("contrasenas", "").strip()
            if cat_words and (cat_words in user_norm or user_norm in cat_words):
                # La pregunta parece referirse a una categoría → mostrar temas
                return self._show_category(category, ctx)
        
        # PASO 2: Detectar si coincide con un tema específico
        for category, topics in self.menu_structure.items():
            for topic in topics:
                topic_norm = self.normalize(topic)
                # Si hay coincidencia alta con un tema
                if len(topic_norm) > 5 and (topic_norm in user_norm or user_norm in topic_norm):
                    # Ir directo a las preguntas del tema
                    return self._show_topic_info(topic, ctx)
        
        # PASO 3: Búsqueda RAG semántica
        results = self.rag.search(user_text, top_k=10, min_score=0.55)
        
        if not results:
            return "Pregunta", ctx, BotReply(
                "🤔 No encontré información sobre eso.\n\n"
                "Intenta reformular tu pregunta o navega por las categorías.",
                ["Ver categorías", "Menú", "Ayuda"],
                source="fallback"
            )
        
        best = results[0]
        
        if best.score > 0.75:
            # Respuesta de alta confianza
            msg = f"✅ **{best.pregunta}**\n\n{best.respuesta}"
            if best.tematica:
                msg += f"\n\n_Tema: {best.tematica}_"
            
            quick_replies = ["Más sobre esto", "Otra pregunta", "Menú"]
            ctx["last_topic"] = best.tematica
            ctx["last_question"] = best.pregunta
            
            return "Respuesta", ctx, BotReply(msg, quick_replies, source="rag")
        
        else:
            # Múltiples opciones - FILTRAR REDUNDANCIA MEJORADO V2
            def extract_keywords(text: str) -> set:
                """Extrae palabras clave importantes (más de 3 letras, no stopwords)"""
                norm = self.normalize(text)
                words = norm.split()
                # Filtrar stopwords comunes y palabras muy cortas
                stopwords = {'que', 'como', 'para', 'por', 'con', 'una', 'mas', 'del', 'los', 'las', 
                            'esto', 'ese', 'cual', 'donde', 'cuando', 'quien', 'ayer', 'porfa', 'rapido', 'ayudame'}
                keywords = {w for w in words if len(w) > 3 and w not in stopwords}
                return keywords
            
            def is_too_similar(q1: str, q2: str) -> bool:
                """Detecta similitud semántica entre preguntas con análisis de keywords"""
                norm1 = self.normalize(q1)
                norm2 = self.normalize(q2)
                
                # Caso 1: Una pregunta contiene a la otra completamente
                if norm1 in norm2 or norm2 in norm1:
                    return True
                
                words1 = set(norm1.split())
                words2 = set(norm2.split())
                
                if len(words1) == 0 or len(words2) == 0:
                    return False
                
                # Caso 2: Extraer keywords importantes
                keywords1 = extract_keywords(q1)
                keywords2 = extract_keywords(q2)
                
                # NUEVO: Si ambas preguntas tienen pocas keywords (1-2) y comparten la principal, son redundantes
                if len(keywords1) <= 2 and len(keywords2) <= 2:
                    common_keywords = keywords1 & keywords2
                    if common_keywords:  # Si comparten al menos 1 keyword importante
                        return True
                
                # Si ambas preguntas tienen keywords y comparten todas las keywords de la más corta
                if keywords1 and keywords2:
                    shorter_keywords = keywords1 if len(keywords1) <= len(keywords2) else keywords2
                    longer_keywords = keywords2 if len(keywords1) <= len(keywords2) else keywords1
                    
                    # Si todas las keywords de la pregunta más corta están en la más larga
                    if shorter_keywords.issubset(longer_keywords):
                        return True
                    
                    # Si comparten >70% de sus keywords (bajado de 80%)
                    kw_intersection = len(keywords1 & keywords2)
                    kw_union = len(keywords1 | keywords2)
                    kw_similarity = kw_intersection / kw_union if kw_union > 0 else 0
                    if kw_similarity > 0.7:
                        return True
                
                # Caso 3: Similitud Jaccard general
                intersection = len(words1 & words2)
                union = len(words1 | words2)
                jaccard = intersection / union if union > 0 else 0
                
                # Para preguntas cortas (< 6 palabras), ser más estricto
                if max(len(words1), len(words2)) < 6:
                    return jaccard > 0.4  # Si comparten >40% de palabras, son redundantes
                else:
                    return jaccard > 0.5  # Para preguntas más largas, usar umbral de 50%
            
            # Filtrar resultados únicos con algoritmo mejorado
            unique_results = []
            for r in results:
                is_redundant = False
                for ur in unique_results:
                    if is_too_similar(r.pregunta, ur.pregunta):
                        is_redundant = True
                        break
                if not is_redundant:
                    unique_results.append(r)
                    if len(unique_results) >= 3:
                        break
            
            # Si después del filtrado solo queda 1 resultado, devolverlo directamente
            if len(unique_results) == 1:
                best = unique_results[0]
                msg = f"✅ **{best.pregunta}**\n\n{best.respuesta}"
                if best.tematica:
                    msg += f"\n\n_Tema: {best.tematica}_"
                
                quick_replies = ["Más sobre esto", "Otra pregunta", "Menú"]
                ctx["last_topic"] = best.tematica
                ctx["last_question"] = best.pregunta
                
                return "Respuesta", ctx, BotReply(msg, quick_replies, source="rag")
            
            msg = "📋 Encontré varios temas relacionados:\n\n"
            for i, r in enumerate(unique_results[:3], 1):
                short_q = r.pregunta[:70] + "..." if len(r.pregunta) > 70 else r.pregunta
                msg += f"{i}. {short_q} ({int(r.score*100)}% relevante)\n"
            
            msg += "\nEscribe el número para ver la respuesta completa."
            
            ctx["rag_results"] = [r.pregunta for r in unique_results[:3]]
            # Generar chips solo para las opciones reales disponibles
            quick_replies = [str(i) for i in range(1, len(unique_results[:3]) + 1)] + ["Menú"]
            
            return "Sugerencias", ctx, BotReply(msg, quick_replies, source="rag")
    
    def _handle_rag_suggestions(self, text_norm: str, user_text: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Maneja selección de sugerencias RAG"""
        rag_results = ctx.get("rag_results", [])
        
        if text_norm.isdigit():
            idx = int(text_norm) - 1
            if 0 <= idx < len(rag_results):
                query = rag_results[idx]
                result = self.rag.get_best_match(query, min_score=0.5)
                if result:
                    msg = f"✅ **{result.pregunta}**\n\n{result.respuesta}"
                    if result.tematica:
                        msg += f"\n\n_Tema: {result.tematica}_"
                    
                    ctx["last_topic"] = result.tematica
                    ctx["last_question"] = result.pregunta  # Guardar pregunta
                    
                    return "Respuesta", ctx, BotReply(
                        msg,
                        ["Más sobre esto", "Otra pregunta", "Menú"],
                        source="rag"
                    )
        
        # Si no es un número válido, intenta como nueva pregunta
        return self._try_rag_answer(user_text, ctx)
    
    def _show_related_answers(self, question: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Muestra respuestas relacionadas a la pregunta actual con diferentes contextos"""
        last_topic = ctx.get("last_topic")
        
        # Estrategia 1: Buscar por la temática del tema
        related_by_topic = []
        if last_topic:
            topic_items = self.rag.get_by_topic(last_topic, limit=10)
            for item in topic_items:
                q = item.get('pregunta', '')
                if q and q != question and len(q) > 10:
                    related_by_topic.append(q)
        
        # Estrategia 2: Buscar semánticamente pero filtrar redundantes
        semantic_results = self.rag.search(question, top_k=15, min_score=0.3)
        
        # Función para calcular similitud entre preguntas (evitar redundancia)
        def is_too_similar(q1: str, q2: str) -> bool:
            """Detecta similitud semántica entre preguntas"""
            norm1 = self.normalize(q1)
            norm2 = self.normalize(q2)
            
            # Caso 1: Una pregunta contiene a la otra completamente
            if norm1 in norm2 or norm2 in norm1:
                return True
            
            words1 = set(norm1.split())
            words2 = set(norm2.split())
            
            if len(words1) == 0 or len(words2) == 0:
                return False
            
            # Caso 2: Similitud Jaccard
            intersection = len(words1 & words2)
            union = len(words1 | words2)
            jaccard = intersection / union if union > 0 else 0
            
            # Caso 3: Para preguntas cortas (< 6 palabras), ser más estricto
            if max(len(words1), len(words2)) < 6:
                return jaccard > 0.4  # Si comparten >40% de palabras, son redundantes
            else:
                return jaccard > 0.5  # Para preguntas más largas, usar umbral de 50%
        
        # Filtrar resultados semánticos para evitar redundancia
        unique_questions = []
        for r in semantic_results:
            if r.pregunta == question:
                continue
            # Verificar que no sea muy similar a las ya seleccionadas
            is_redundant = False
            for uq in unique_questions:
                if is_too_similar(r.pregunta, uq):
                    is_redundant = True
                    break
            if not is_redundant:
                unique_questions.append(r.pregunta)
        
        # Combinar resultados: priorizar las del mismo tema, luego las semánticas únicas
        final_questions = []
        seen = set()
        
        # Agregar primero las del mismo tema (variedad)
        for q in related_by_topic[:3]:
            if q not in seen and not is_too_similar(q, question):
                final_questions.append(q)
                seen.add(q)
        
        # Completar con búsqueda semántica única
        for q in unique_questions:
            if len(final_questions) >= 5:
                break
            if q not in seen:
                final_questions.append(q)
                seen.add(q)
        
        if len(final_questions) == 0:
            return "Respuesta", ctx, BotReply(
                "🤔 No encontré más preguntas relacionadas con contextos diferentes.\n\nPuedes hacer otra pregunta o explorar categorías.",
                ["Otra pregunta", "Ver categorías", "Menú"],
                source="rag"
            )
        
        msg = "📚 **Preguntas relacionadas (diferentes contextos):**\n\n"
        
        for i, q in enumerate(final_questions[:5], 1):
            short_q = q[:75] + "..." if len(q) > 75 else q
            msg += f"{i}. {short_q}\n"
        
        msg += "\nEscribe el número para ver la respuesta completa."
        
        ctx["related_questions"] = final_questions[:5]
        quick_replies = [str(i) for i in range(1, min(len(final_questions)+1, 6))] + ["Otra pregunta", "Menú"]
        
        return "Relacionadas", ctx, BotReply(msg, quick_replies, source="rag")
    
    def _handle_related_selection(self, text_norm: str, user_text: str, ctx: dict) -> tuple[str, dict, BotReply]:
        """Maneja selección de una respuesta relacionada"""
        related_questions = ctx.get("related_questions", [])
        
        if text_norm.isdigit():
            idx = int(text_norm) - 1
            if 0 <= idx < len(related_questions):
                query = related_questions[idx]
                result = self.rag.get_best_match(query, min_score=0.5)
                if result:
                    msg = f"✅ **{result.pregunta}**\n\n{result.respuesta}"
                    if result.tematica:
                        msg += f"\n\n_Tema: {result.tematica}_"
                    
                    ctx["last_topic"] = result.tematica
                    ctx["last_question"] = result.pregunta
                    
                    return "Respuesta", ctx, BotReply(
                        msg,
                        ["Más sobre esto", "Otra pregunta", "Menú"],
                        source="rag"
                    )
        
        # Si no es un número válido, intenta como nueva pregunta
        return self._try_rag_answer(user_text, ctx)


def create_bot(dataset_path: str) -> MenuBot:
    """Factory para crear instancia del bot"""
    return MenuBot(dataset_path)
