# -*- coding: utf-8 -*-
"""
Agente Bit content extracted/derived from the provided script.
Keep the text here (not hard-coded in logic) so you can update it without breaking the bot.
"""

ROOT_WELCOME = (
    "¡Hola! Soy Agente Bit, tu asistente virtual de ciberseguridad.\n"
    "Puedo ayudarte a proteger tu información, detectar ciberamenazas o reportar ciberincidentes.\n"
    "Selecciona alguna de las siguientes opciones:" 
)

ROOT_OPTIONS = [
    "Consejos de ciberseguridad",
    "Detectar ciberamenazas",
    "Reportar un incidente cibernético",
    "Saber sobre ciberataques",
    "Busca el número de tu Policía Cibernética",
]

SECURITY_TIPS_MENU = [
    "¿Cómo puedo crear una contraseña segura?",
    "¿Cada cuánto debo cambiar mi contraseña?",
    "¿Es seguro conectarme a una red Wi‑Fi pública?",
    "¿Cómo protejo mi cuenta de redes sociales?",
    "¿Qué antivirus recomiendas?",
    "¿Cómo identifico un correo falso (phishing)?",
    "Otro",
]

THREAT_MENU = [
    "Creo que recibí un correo falso, ¿cómo lo sé?",
    "¿Puedo revisar si un enlace es peligroso?",
    "Mi computadora está más lenta, ¿será un virus?",
    "¿Qué hago si descargué un archivo sospechoso?",
    "Otro",
]

CYBERATTACKS_MENU = [
    "¿Qué es el phishing?",
    "¿Qué es el ransomware?",
    "¿Cómo puedo evitar malware?",
    "¿Qué es la ingeniería social?",
]

INCIDENT_TYPES = [
    "Correo sospechoso",
    "Acceso no autorizado",
    "Acoso Cibernético",
    "Víctima de Extorsión", 
    "Víctima de Ciberamenazas",
    "Víctima de fraude",
    "Robo a transeúnte",
    "Otro",
]

CLOSING = (
    "Gracias por cuidar tu seguridad digital con El Agente Bit.\n"
    "Te invito a llenar el formulario de retroalimentación para mejorar nuestro servicio."
)

def quick_menu(*labels: str) -> list[str]:
    return list(labels)
