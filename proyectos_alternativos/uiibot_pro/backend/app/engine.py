# -*- coding: utf-8 -*-
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional
import re

from .utils import normalize, is_yes, is_no, month_year_code, load_json
from . import content

POLICE_DATA = load_json("data/cyber_police_mx.json")

def resolve_state(user_text: str) -> Optional[str]:
    t = normalize(user_text)
    if not t:
        return None
    aliases = POLICE_DATA.get("state_aliases", {})
    if t in aliases:
        return aliases[t]
    # fuzzy-ish: contains
    for k, v in aliases.items():
        if k in t:
            return v
    return None

def get_state_contacts(state: str) -> list[dict[str, Any]]:
    return (POLICE_DATA.get("states", {}) or {}).get(state, [])

def state_code(state: str) -> str:
    return (POLICE_DATA.get("state_codes", {}) or {}).get(state, "UNK")

@dataclass
class BotReply:
    text: str
    quick_replies: list[str]
    debug: dict[str, Any] | None = None

def _root() -> BotReply:
    return BotReply(text=content.ROOT_WELCOME, quick_replies=content.ROOT_OPTIONS)

def _help_footer() -> str:
    return "\n\nTe invito a llenar el formulario del Reporte Cibernetico"

def handle_message(session: dict[str, Any], user_text: str, storage=None) -> tuple[str, dict[str, Any], BotReply]:
    """
    Returns: (new_state, new_context, reply)
    """
    t = normalize(user_text)
    state = session.get("state", "Inicio")
    ctx: dict[str, Any] = session.get("context", {}) or {}

    # Global commands
    if t in {"menu", "inicio", "start", "home"}:
        return "Inicio", {}, _root()
    if t in {"salir", "cancelar", "reiniciar", "reset"}:
        return "Inicio", {}, BotReply(text="Listo. Reinicié la conversación.\n\n" + content.ROOT_WELCOME, quick_replies=content.ROOT_OPTIONS)

    # Routing by current state (forms / menus)
    if state == "Inicio":
        # accept numeric selection too
        if t in {"1", "consejos", "consejos de seguridad", "consejos de ciberseguridad"}:
            return "Seguridad", ctx, BotReply("Elige una opción:", content.SECURITY_TIPS_MENU + ["Volver al menú"])
        if t in {"2", "detectar amenazas", "amenazas", "detectar ciberamenazas", "ciberamenazas"}:
            return "Amenazas", ctx, BotReply("Elige una opción:", content.THREAT_MENU + ["Volver al menú"])
        if t in {"3", "reportar", "reportar un incidente", "reportar un incidente cibernetico", "incidente"}:
            ctx = {"report": {}}
            return "Nombre", ctx, BotReply(
                "Gracias por reportar con El Agente Bit.\n"
                "Para poder realizar tu reporte, por favor indica:\n"
                "1) Nombre completo (o escribe *anónimo*)",
                ["Anónimo", "Volver al menú"],
            )
        if t in {"4", "ciberataques", "saber sobre ciberataques"}:
            return "Ciberataques", ctx, BotReply("¿Qué tema quieres aprender?", content.CYBERATTACKS_MENU + ["Volver al menú"])
        if t in {"5", "policia cibernetica", "policía cibernética", "buscar numero", "busca el numero de tu policia cibernetica"}:
            return "Estado Policía", ctx, BotReply("Dime tu **Estado** (ej. Jalisco, CDMX, Nuevo León):", ["CDMX", "Jalisco", "Estado de México", "Nuevo León", "Veracruz", "Volver al menú"])
        # intent fallback
        # keyword-based jump
        if any(k in t for k in ["contraseña", "contrasena", "password"]):
            return "Seguridad", ctx, BotReply("Perfecto. Entra a **Consejos de ciberseguridad** y elige:", content.SECURITY_TIPS_MENU + ["Volver al menú"])
        if any(k in t for k in ["phishing", "correo falso", "correo sospechoso"]):
            return "Phishing", ctx, _security_phishing()
        return "Inicio", ctx, BotReply("No estoy seguro de cuál opción quieres. Elige una:", content.ROOT_OPTIONS)

    if state == "Seguridad":
        if t in {"volver", "volver al menu", "menu"} or user_text.strip().lower().startswith("volver"):
            return "Inicio", {}, _root()
        return _handle_security_menu_selection(t, ctx)

    if state == "Amenazas":
        if "volver" in t:
            return "Inicio", {}, _root()
        return _handle_threat_menu_selection(t, ctx)

    if state == "Ciberataques":
        if "volver" in t:
            return "Inicio", {}, _root()
        return _handle_cyberattacks_selection(t, ctx)

    if state == "Estado Policía":
        if "volver" in t:
            return "Inicio", {}, _root()
        resolved = resolve_state(user_text)
        if not resolved:
            return state, ctx, BotReply("¿Cual estado? (ej. *Querétaro*, *San Luis Potosí*, *CDMX*).", ["Volver al menú"])
        cards = get_state_contacts(resolved)
        if not cards:
            return "Inicio", {}, BotReply(f"No encontré datos para **{resolved}**. ¿Quieres intentar otro estado?", ["Volver al menú"])
        msg = [f"📞 **Policía Cibernética – {resolved}**"]
        for c in cards:
            if c.get("unit_name"):
                msg.append(f"\n**{c['unit_name']}**")
            if c.get("url"):
                msg.append(f"Sitio: {c['url']}")
            if c.get("phone"):
                msg.append(f"Tel: {c['phone']}")
            if c.get("whatsapp"):
                msg.append(f"WhatsApp: {c['whatsapp']}")
            if c.get("facebook"):
                msg.append(f"Facebook: {c['facebook']}")
            if c.get("twitter"):
                msg.append(f"Twitter: {c['twitter']}")
            if c.get("email"):
                msg.append(f"Email: {c['email']}")
        return "Estado Policía", ctx, BotReply("\n".join(msg), ["Buscar otro Estado", "Volver al menú"])

    # Incident report form
    if state in ["Nombre", "Estado", "Edad", "Sexo", "Tipo Reporte", "Descripción", "Orientación", "Cierre Reporte"]:
        return _handle_report_form(state, ctx, user_text, storage=storage)

    # default
    return "Inicio", {}, _root()

def _handle_security_menu_selection(t: str, ctx: dict[str, Any]) -> tuple[str, dict[str, Any], BotReply]:
    # map numbers to items
    if t in {"1"} or "contraseña" in t or "contrasena" in t:
        msg = (
            "🔐 **Contraseñas seguras**\n"
            "• Usa al menos 12 caracteres, combinando letras, números y símbolos.\n"
            "• Evita nombres, fechas o palabras comunes.\n"
            "Ejemplo: “Mi gato come a las 8” → `Mgc@l8`"
        )
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    if t in {"2"} or "cambiar" in t:
        msg = "Cámbiala cada **3 a 6 meses**, o de inmediato si sospechas que fue comprometida.\n\n¿Quieres saber cómo generar una contraseña segura?"
        return "Confirmar Contraseña", ctx, BotReply(msg, ["Sí", "No", "Menú"])
    if t in {"3"} or "wifi" in t:
        msg = "📶 **Wi‑Fi pública**\nEvita transacciones o banca en redes abiertas. Si es necesario, usa una **VPN**."
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    if t in {"4"} or "redes" in t:
        msg = (
            "🔒 **Redes sociales**\n"
            "• Configura la privacidad de tus publicaciones.\n"
            "• Revisa quién puede etiquetarte.\n"
            "• Evita compartir información personal (lugares frecuentes, rutinas).\n"
            "• Mantén tu perfil privado.\n"
            "• Ten una contraseña segura y actualiza medios de recuperación.\n\n"
            "¿Quieres saber cómo generar una contraseña segura?"
        )
        return "Confirmar Contraseña", ctx, BotReply(msg, ["Sí", "No", "Menú"])
    if t in {"5"} or "antivirus" in t:
        msg = "🛡️ Mantén actualizado tu sistema operativo y el antivirus. Algunos confiables: **Bitdefender** y **Windows Defender**."
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    if t in {"6"} or "phishing" in t or "correo falso" in t:
        return "Phishing", ctx, _security_phishing()
    # other
    return "Seguridad", ctx, BotReply("Cuéntame más (por ejemplo: ¿qué pasó? ¿en qué app?), y te guío.", ["Menú", "Reportar un incidente", "Cerrar"])

def _security_phishing() -> BotReply:
    msg = (
        "🚨 **Señales de phishing**\n"
        "• Tiene errores o tono urgente.\n"
        "• La dirección del remitente no coincide.\n"
        "• Te pide hacer clic o ingresar contraseñas.\n\n"
        "Te invito a llenar el formulario del Reporte Cibernético."
    )
    return BotReply(msg, ["No", "Menú"])

def _handle_threat_menu_selection(t: str, ctx: dict[str, Any]) -> tuple[str, dict[str, Any], BotReply]:
    if t in {"1"} or "correo" in t:
        msg = (
            "📩 **Correo sospechoso**\n"
            "Revisa: dirección del remitente, tono urgente/amenaza, y enlaces raros o acortados.\n"
            "Puedes verificar enlaces en VirusTotal.\n\n"
            "Si dudas, no hagas clic. Te invito a llenar el formulario del Reporte Cibernético."
        )
        return "Solicitar Reporte", ctx, BotReply(msg, ["No", "Menú"])
    if t in {"2"} or "enlace" in t or "link" in t:
        msg = (
            "🔎 **Comprobar un sitio web**\n"
            "1) Verifica que use `https://`.\n"
            "2) Revisa el candado (certificado SSL/TLS válido).\n"
            "3) Confirma dominio legítimo (.com, .org, .gob) y que no tenga letras raras.\n"
            "4) Busca reputación/opiniones.\n"
            "5) Debe tener política de privacidad clara."
        )
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    if t in {"3"} or "lenta" in t or "computadora" in t:
        msg = (
            "🐢 **Computadora lenta**\n"
            "Podría ser malware si notas: programas que se abren solos, anuncios inesperados, bloqueos.\n"
            "Haz un escaneo completo con tu antivirus y desinstala apps que no reconozcas.\n\n"
            "Si no hay nada inusual: revisa actualizaciones, espacio, RAM y sobrecalentamiento."
        )
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    if t in {"4"} or "archivo" in t or "descarg" in t:
        msg = (
            "📁 **Archivo sospechoso**\n"
            "1) Desconéctate de internet si notas actividad rara.\n"
            "2) No lo abras.\n"
            "3) Escanéalo con tu antivirus.\n"
            "4) Si puedes, súbelo a VirusTotal.\n"
            "5) Si ya lo ejecutaste y hay señales, considera respaldar y pedir apoyo.\n\n"
            "Te invito a llenar el formulario del Reporte Cibernético."
        )
        return "Solicitar Reporte", ctx, BotReply(msg, ["No", "Menú"])
    return "Amenazas", ctx, BotReply("Cuéntame más (¿qué viste exactamente?) y te guío.", ["Menú", "Reportar un incidente", "Cerrar"])

def _handle_cyberattacks_selection(t: str, ctx: dict[str, Any]) -> tuple[str, dict[str, Any], BotReply]:
    if "phishing" in t or t == "1":
        msg = (
            "🎣 **Phishing**\n"
            "Es un engaño para que compartas datos personales.\n"
            "Ejemplo: un correo que dice “actualiza tu cuenta bancaria aquí”.\n"
            "Revisa siempre la dirección del remitente antes de hacer clic."
        )
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    if "ransomware" in t or t == "2":
        msg = (
            "🔒 **Ransomware**\n"
            "Bloquea tus archivos y pide dinero para liberarlos.\n"
            "Prevélo con copias de seguridad y actualizaciones frecuentes."
        )
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    if "malware" in t or t == "3":
        msg = (
            "🦠 **Malware**\n"
            "Software malicioso (virus, troyano, spyware).\n"
            "Mantén antivirus activo y evita descargas piratas."
        )
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    if "ingenieria social" in t or "ingeniería social" in t or t == "4":
        msg = (
            "🧠 **Ingeniería social**\n"
            "Manipulación psicológica para que compartas información confidencial.\n"
            "Ejemplo: alguien se hace pasar por soporte técnico.\n"
            "Verifica siempre la identidad antes de proporcionar datos."
        )
        return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
    return "Ciberataques", ctx, BotReply("Elige una opción:", content.CYBERATTACKS_MENU + ["Volver al menú"])

def _handle_report_form(state: str, ctx: dict[str, Any], user_text: str, storage=None) -> tuple[str, dict[str, Any], BotReply]:
    t = normalize(user_text)

    if "report" not in ctx:
        ctx["report"] = {}

    if t in {"volver", "volver al menu", "menu"} or "volver" in t:
        return "Inicio", {}, _root()

    # Step 1: name
    if state == "Nombre":
        name = user_text.strip()
        if not name:
            return state, ctx, BotReply("Por favor escribe tu nombre, o escribe *anónimo*.", ["Anónimo", "Volver al menú"])
        if normalize(name) in {"anonimo", "anónimo"}:
            name = "Anónimo"
        ctx["report"]["name"] = name
        return "Estado", ctx, BotReply("2) ¿En qué **Estado** resides?", ["CDMX", "Jalisco", "Estado de México", "Nuevo León", "Veracruz", "Volver al menú"])

    if state == "Estado":
        resolved = resolve_state(user_text)
        if not resolved:
            return state, ctx, BotReply("¿Cual estado? (ej. *Querétaro*, *San Luis Potosí*, *CDMX*).", ["Volver al menú"])
        ctx["report"]["state"] = resolved
        return "Edad", ctx, BotReply("3) ¿Cuál es tu **edad**? (solo número)", ["Volver al menú"])

    if state == "Edad":
        m = re.match(r"^\D*(\d{1,3})\D*$", user_text.strip())
        if not m:
            return state, ctx, BotReply("Escribe tu edad como número (ej. 27).", ["Volver al menú"])
        age = int(m.group(1))
        if age < 1 or age > 120:
            return state, ctx, BotReply("Esa edad se ve rara 😅. Intenta de nuevo (ej. 27).", ["Volver al menú"])
        ctx["report"]["age"] = age
        return "Sexo", ctx, BotReply("4) Sexo (opcional):", ["Femenino", "Masculino", "Prefiero no decir", "Volver al menú"])

    if state == "Sexo":
        sex = user_text.strip()
        if normalize(sex) in {"prefiero no decir", "no decir", "na", "n/a", "prefiero no"}:
            sex = "No especificado"
        ctx["report"]["sex"] = sex

        # generate report id now
        if storage is not None:
            seq = storage.next_report_seq()
        else:
            seq = 1
        st = ctx["report"].get("state") or "UNK"
        code = state_code(st)
        import datetime
        mmmyy = month_year_code(datetime.datetime.utcnow())
        report_id = f"AgentBit/{code}/{seq:02d}/{mmmyy}"
        ctx["report"]["report_id"] = report_id

        # Construir resumen de datos capturados
        summary = (
            f"📋 **Datos registrados:**\n"
            f"• Nombre: {ctx['report'].get('name', 'N/A')}\n"
            f"• Estado: {ctx['report'].get('state', 'N/A')}\n"
            f"• Edad: {ctx['report'].get('age', 'N/A')}\n"
            f"• Sexo: {ctx['report'].get('sex', 'N/A')}\n\n"
            f"*** Ahora elige la opción de acuerdo con tu incidente: ***"
        )

        return "Tipo Reporte", ctx, BotReply(
            summary,
            content.INCIDENT_TYPES + ["Volver al menú"],
        )

    if state == "Tipo Reporte":
        # normalize selection
        chosen = None
        for opt in content.INCIDENT_TYPES:
            if normalize(opt) == t:
                chosen = opt; break
        if t.isdigit():
            idx = int(t) - 1
            if 0 <= idx < len(content.INCIDENT_TYPES):
                chosen = content.INCIDENT_TYPES[idx]
        if not chosen:
            return state, ctx, BotReply("Elige una opción de la lista:", content.INCIDENT_TYPES + ["Volver al menú"])
        ctx["report"]["incident_type"] = chosen

        # some types need a free-text description
        if chosen in {"Víctima de Extorsión", "Víctima de Amenazas", "Otro"}:
            return "Descripción", ctx, BotReply("Por favor describe lo sucedido de manera clara y concisa:", ["Volver al menú"])

        # immediate guidance
        reply = incident_guidance(chosen)
        return "Orientación", ctx, reply

    if state == "Descripción":
        desc = user_text.strip()
        if not desc:
            return state, ctx, BotReply("Describe brevemente qué sucedió.", ["Volver al menú"])
        ctx["report"]["description"] = desc
        # guidance for extortion/threat/other
        it = ctx["report"].get("incident_type") or "Otro"
        reply = incident_guidance(it, description=desc)
        return "Orientación", ctx, reply

    if state == "Orientación":
        # offer police contact
        if "policia" in t or "policía" in t or is_yes(user_text) or t in {"si, proporcionar", "si proporcionar", "si"}:
            st = ctx["report"].get("state")
            if st:
                cards = get_state_contacts(st)
                if cards:
                    msg = [f"📞 **Policía Cibernética – {st}**"]
                    for c in cards:
                        if c.get("unit_name"): msg.append(f"\n**{c['unit_name']}**")
                        if c.get("phone"): msg.append(f"Tel: {c['phone']}")
                        if c.get("email"): msg.append(f"Email: {c['email']}")
                        if c.get("facebook"): msg.append(f"Facebook: {c['facebook']}")
                        if c.get("url"): msg.append(f"Sitio: {c['url']}")
                    return "Cierre Reporte", ctx, BotReply("\n".join(msg) + "\n\nTe invito a llenar el formulario de Reporte cibernético o contacta a tu UPC", ["Menú", "Cerrar"])
            return "Cierre Reporte", ctx, BotReply("No encontré contactos para tu estado. Te invito a llenar el formulario de Reporte cibernético o contacta a tu UPC", ["Menú", "Cerrar"])

        if is_no(user_text) or t in {"cerrar", "no", "no gracias"}:
            return "Cierre", ctx, BotReply(content.CLOSING, ["Menú"])
        return "Cierre Reporte", ctx, BotReply("Te invito a llenar el formulario de Reporte cibernético o contacta a tu UPC", ["Menú", "Cerrar", "Buscar Policía Cibernética"])

    if state == "Cierre Reporte":
        if "policia" in t:
            return "Estado Policía", ctx, BotReply("Dime tu **Estado**:", ["CDMX", "Jalisco", "Estado de México", "Nuevo León", "Veracruz", "Volver al menú"])
        if "menu" in t or is_yes(user_text):
            return "Inicio", {}, _root()
        if "cerrar" in t or is_no(user_text):
            return "Cierre", ctx, BotReply(content.CLOSING, ["Menú"])
        return state, ctx, BotReply("Elige: Menú, Buscar Policía Cibernética, o Cerrar.", ["Menú", "Buscar Policía Cibernética", "Cerrar"])

    # post-answer helper states
    if state == "Confirmar Contraseña":
        if is_yes(user_text):
            msg = (
                "🔐 **Contraseñas seguras**\n"
                "• Usa al menos 12 caracteres, combinando letras, números y símbolos.\n"
                "• Evita nombres, fechas o palabras comunes.\n"
                "Ejemplo: “Mi gato come a las 8” → `Mgc@l8`"
            )
            return "Respuesta", ctx, BotReply(msg + _help_footer(), ["Menú", "Cerrar"])
        if is_no(user_text):
            return "Inicio", {}, _root()
        return state, ctx, BotReply("Responde Sí o No 🙂", ["Sí", "No", "Menú"])

    if state == "Solicitar Reporte" or state == "Phishing":
        if "report" in t or is_yes(user_text) or t.startswith("si"):
            # jump to report start
            ctx = {"report": {}}
            return "Nombre", ctx, BotReply(
                "Perfecto. Iniciemos tu reporte.\n"
                "1) Nombre completo (o escribe *anónimo*)",
                ["Anónimo", "Volver al menú"],
            )
        if is_no(user_text):
            return "Cierre", ctx, BotReply(content.CLOSING, ["Menú"])
        return state, ctx, BotReply("Te invito a llenar el formulario del Reporte Cibernético.", ["No", "Menú"])

    # Fallback for report states
    return "Inicio", {}, _root()

def incident_guidance(incident_type: str, description: str|None = None) -> BotReply:
    it = incident_type

    if it == "Correo sospechoso":
        msg = (
            "📩 **Correo sospechoso (phishing)**\n"
            "Suele ser un mensaje falso (paquetes, virus, etc.).\n\n"
            "Pasos recomendados:\n"
            "• Analiza si solicitaste un paquete.\n"
            "• Márcalo como spam y/o elimínalo.\n"
            "• Haz caso omiso.\n"
            "• Escanea con tu antivirus."
        )
        return BotReply(msg + "\n\n¿Quieres que te proporcione el número de tu Policía Cibernética?", ["Sí", "No", "Menú"])

    if it == "Acceso no autorizado":
        msg = (
            "🔐 **Intento de acceso no autorizado**\n"
            "• Cambia tu contraseña de inmediato.\n"
            "• Activa verificación en dos pasos.\n\n"
            "¿Quieres saber cómo hacerlo en WhatsApp?"
        )
        return BotReply(msg, ["Sí, WhatsApp", "No", "Menú"])

    if it == "Acoso Cibernético":
        msg = (
            "🧩 **Acoso Cibernético**\n"
            "¿Esto sucede mediante redes sociales o físicamente?"
        )
        return BotReply(msg, ["Redes sociales", "Físicamente", "Menú"])

    if it in {"Víctima de Extorsión", "Víctima de Amenazas"}:
        msg = (
            "⚠️ **Extorsión/Amenazas**\n"
            "Recomendaciones inmediatas:\n"
            "• No contestes llamadas ni mensajes de números desconocidos.\n"
            "• Deja de mantener contacto con la persona agresora.\n"
            "• Avisa a tus familiares.\n"
            "• Contacta a la Policía Cibernética de tu localidad.\n"
            "• Realiza tu denuncia ante la fiscalía.\n\n"
            "¿Quieres que te proporcione el número de tu Policía Cibernética?"
        )
        return BotReply(msg, ["Sí", "No", "Menú"])

    if it == "Víctima de fraude":
        msg = (
            "💳 **Fraude**\n"
            "• Contacta a tu institución bancaria para reportar tu cuenta.\n"
            "• Ten a la mano el sitio web/publicación a reportar.\n"
            "• Contacta a la Policía Cibernética.\n"
            "• Realiza tu denuncia ante la fiscalía.\n\n"
            "¿Quieres que te proporcione el número de tu Policía Cibernética?"
        )
        return BotReply(msg, ["Sí", "No", "Menú"])

    if it == "Robo a transeúnte":
        msg = (
            "📱 **Pérdida o robo de dispositivo**\n"
            "• Informa a familiares y amigos.\n"
            "• Cambia contraseñas de redes sociales.\n"
            "• Contacta a tu banco para cancelar tarjetas.\n"
            "• Denuncia ante la fiscalía de tu localidad.\n\n"
            "¿Quieres que te proporcione el número de tu Policía Cibernética?"
        )
        return BotReply(msg, ["Sí", "No", "Menú"])

    if it == "Otro":
        msg = (
            "📝 **Otro incidente**\n"
            "Gracias por la información.\n"
            "Si hay riesgo inmediato, marca al 9‑1‑1.\n\n"
            "¿Quieres que te proporcione el número de tu Policía Cibernética?"
        )
        return BotReply(msg, ["Sí", "No", "Menú"])

    # Special branches for WhatsApp 2FA + acoso
    # These are handled in main handler by looking at state; to keep it simple we respond here as well if needed.
    return BotReply("Entiendo. ¿Quieres que te proporcione el número de tu Policía Cibernética?", ["Sí", "No", "Menú"])
