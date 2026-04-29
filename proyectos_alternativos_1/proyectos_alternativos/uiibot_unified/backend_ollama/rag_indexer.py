#!/usr/bin/env python3
"""
rag_indexer.py — Indexador de documentos de Ciberseguridad México
Alimenta la base vectorial ChromaDB que usa Agente Bit para contexto RAG.

Uso:
    python rag_indexer.py          # Indexa todos los documentos predefinidos
    python rag_indexer.py --reset  # Borra y reindexa desde cero
    python rag_indexer.py --stats  # Muestra estadísticas de la colección

Dependencias:
    pip install chromadb sentence-transformers requests beautifulsoup4 pypdf
"""

import argparse
import sys
import logging
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
CHROMA_DB_PATH  = Path(__file__).parent / "chroma_db"
COLLECTION_NAME = "ciberseg_mexico"
EMBED_MODEL     = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Base de conocimiento: Ciberseguridad México 2024-2025
# ---------------------------------------------------------------------------
KNOWLEDGE_BASE = [
    # ── CERT-MX / UNAM-CERT ────────────────────────────────────────────────
    {
        "id": "certmx_phishing_sat_2024",
        "text": (
            "ALERTA CERT-MX 2024 — Phishing SAT: Campaña masiva de correos electrónicos "
            "falsos que suplantan al Servicio de Administración Tributaria (SAT). Los mensajes "
            "alertan sobre 'adeudos fiscales' o 'devoluciones de impuestos' con ligas a sitios "
            "falsos que roban RFC, CURP y datos bancarios. "
            "ACCIONES: No haga clic en enlaces del correo. Ingrese directamente a sat.gob.mx. "
            "Reporte a cert@unam.mx o al SAT: sat.gob.mx/portal/public/tramites/atiende-phishing."
        ),
        "source": "CERT-MX UNAM 2024",
        "category": "phishing",
    },
    {
        "id": "certmx_phishing_imss_2024",
        "text": (
            "ALERTA CERT-MX 2024 — Phishing IMSS: Mensajes SMS y correos fraudulentos que "
            "suplantan al IMSS ofreciendo 'verificación de semanas cotizadas' o 'trámites AFORE'. "
            "Solicitan NSS, CURP y datos personales. El IMSS nunca solicita datos por mensaje. "
            "Ingrese solo en imss.gob.mx. Reporte al IMSS: 800-623-2323."
        ),
        "source": "CERT-MX UNAM 2024",
        "category": "phishing",
    },
    {
        "id": "certmx_ransomware_pymes_2024",
        "text": (
            "ALERTA CERT-MX 2024 — Ransomware en PYMES mexicanas: Se detectó aumento del 67% "
            "en ataques de ransomware a pequeñas y medianas empresas en México. Variantes activas: "
            "LockBit 3.0, BlackCat/ALPHV, Cl0p. Sectores más afectados: manufactura, comercio, salud. "
            "MEDIDAS PREVENTIVAS: Realizar respaldos offline diarios, aplicar parches de Windows, "
            "capacitar empleados en reconocimiento de phishing, implementar MFA en accesos remotos. "
            "Ante incidente: desconectar equipos afectados de la red, NO pagar rescate, "
            "reportar a CERT-MX: cert@unam.mx."
        ),
        "source": "CERT-MX UNAM 2024",
        "category": "ransomware",
    },
    {
        "id": "certmx_vishing_bancario_2024",
        "text": (
            "ALERTA CERT-MX 2024 — Vishing bancario: Llamadas telefónicas donde atacantes se "
            "identifican como empleados de BBVA, Banamex, Santander, HSBC o Banorte. Argumentan "
            "cargos no reconocidos para obtener NIP, tokens o acceso a banca en línea. "
            "RECUERDE: Los bancos NUNCA solicitan NIP, contraseñas ni tokens por teléfono. "
            "Cuelgue y llame al número oficial de su banco. Reporte a CONDUSEF: 800-999-8080."
        ),
        "source": "CERT-MX UNAM 2024",
        "category": "vishing",
    },

    # ── CONDUSEF ────────────────────────────────────────────────────────────
    {
        "id": "condusef_fraude_digital_stats_2024",
        "text": (
            "CONDUSEF 2024 — Estadísticas de fraude digital México: Las reclamaciones por fraude "
            "digital aumentaron 40% en 2023 vs 2022. Se registraron 11.6 millones de quejas ante "
            "instituciones financieras. Monto promedio defraudado: $8,200 MXN por víctima. "
            "Principales modalidades: cargo no reconocido (45%), transferencia no autorizada (30%), "
            "disposición de efectivo falsa (15%). "
            "Contacto CONDUSEF: 800-999-8080 | condusef.gob.mx | SIPRES para quejas formales."
        ),
        "source": "CONDUSEF 2024",
        "category": "fraude_financiero",
    },
    {
        "id": "condusef_smishing_2024",
        "text": (
            "CONDUSEF — Smishing (fraude por SMS): Mensajes de texto falsos que notifican "
            "'movimiento inusual en tu cuenta' o 'tu tarjeta fue bloqueada'. Incluyen ligas "
            "acortadas que llevan a sitios clonados de bancos. Al ingresar credenciales, "
            "los datos son robados en tiempo real. "
            "PROTECCIÓN: No ingrese datos bancarios desde un SMS. Borre el mensaje. "
            "Verifique movimientos en la app oficial de su banco. Reporte: CONDUSEF 800-999-8080."
        ),
        "source": "CONDUSEF 2024",
        "category": "smishing",
    },
    {
        "id": "condusef_derechos_usuarios_banca",
        "text": (
            "CONDUSEF — Derechos del usuario de banca digital en México: Ante un fraude bancario "
            "digital, usted tiene derecho a: 1) Presentar reclamación ante su banco (plazo 45 días). "
            "2) Si el banco rechaza, recurrir a CONDUSEF gratuitamente. 3) El banco debe responder "
            "en 45 días hábiles. 4) Para cargos no reconocidos por tarjeta: el banco debe realizar "
            "investigación y dar respuesta. 5) Puede solicitar BURO DE ENTIDADES FINANCIERAS. "
            "SIPRES (sistema de quejas): condusef.gob.mx/SIPRES."
        ),
        "source": "CONDUSEF",
        "category": "derechos_usuario",
    },

    # ── INAI / LFPDPPP ──────────────────────────────────────────────────────
    {
        "id": "inai_derechos_arco",
        "text": (
            "INAI — Derechos ARCO (Acceso, Rectificación, Cancelación, Oposición): "
            "En México, la Ley Federal de Protección de Datos Personales en Posesión de "
            "Particulares (LFPDPPP) te otorga 4 derechos fundamentales sobre tus datos personales. "
            "ACCESO: Conocer qué datos tiene una empresa de ti. "
            "RECTIFICACIÓN: Corregir datos incorrectos. "
            "CANCELACIÓN: Solicitar eliminación de tus datos. "
            "OPOSICIÓN: Oponerte al uso de tus datos. "
            "Ejercer derechos: envía solicitud escrita al responsable del tratamiento. "
            "Si no atienden, presenta queja en inai.org.mx o llama 800-835-4324."
        ),
        "source": "INAI / LFPDPPP",
        "category": "privacidad",
    },
    {
        "id": "inai_aviso_privacidad",
        "text": (
            "INAI — Aviso de Privacidad obligatorio en México: Toda empresa que recopile datos "
            "personales DEBE tener un Aviso de Privacidad visible. Debe incluir: identidad del "
            "responsable, finalidades del tratamiento, mecanismo para ejercer derechos ARCO, "
            "transferencias a terceros, y cómo revocar consentimiento. "
            "Sanción por incumplimiento: hasta 32 millones de pesos (LFPDPPP). "
            "Para verificar cumplimiento o presentar denuncias: inai.org.mx."
        ),
        "source": "INAI / LFPDPPP",
        "category": "privacidad",
    },
    {
        "id": "inai_brecha_seguridad",
        "text": (
            "INAI — Brechas de seguridad de datos personales en México: Las empresas tienen "
            "OBLIGACIÓN de notificar al INAI y a los titulares cuando ocurra una brecha que "
            "vulnere datos personales. La notificación debe hacerse en cuanto se conozca el "
            "incidente. Debe informar: naturaleza del incidente, datos comprometidos, acciones "
            "correctivas. Incumplir es sancionable con multas de hasta $32 MDP. "
            "Reportar brecha: inai.org.mx → 'Notificación de Vulneraciones'."
        ),
        "source": "INAI",
        "category": "privacidad",
    },

    # ── POLICÍA CIBERNÉTICA ──────────────────────────────────────────────────
    {
        "id": "policia_cibernetica_contacto",
        "text": (
            "Policía Cibernética México — Contacto y denuncias: La Policía Cibernética de la "
            "Secretaría de Seguridad y Protección Ciudadana atiende delitos informáticos. "
            "CONTACTO: Línea de emergencia 088 (24/7). "
            "Correo: division.cientifica@sspc.gob.mx. "
            "Delitos que atiende: hackeo, sextorsión, grooming, acoso +digital, fraude en línea, "
            "robo de identidad digital, pornografía infantil en internet. "
            "También puedes denunciar en el Ministerio Público de tu entidad."
        ),
        "source": "Policía Cibernética SSPC",
        "category": "denuncia",
    },
    {
        "id": "policia_cibernetica_sextorsion",
        "text": (
            "Sextorsión en México: Delito donde criminales amenazan con difundir imágenes o "
            "videos íntimos para extorsionar económicamente a la víctima. "
            "¿QUÉ HACER? 1) NO pague ni negocie con el extorsionador. 2) Conserve evidencia "
            "(capturas de pantalla con fecha/hora). 3) Bloquee al agresor en todas las plataformas. "
            "4) Denuncie a Policía Cibernética: 088 o division.cientifica@sspc.gob.mx. "
            "5) Reporte el perfil del agresor a la red social. "
            "APOYO PSICOLÓGICO: CAVI 55 5200-9632 (CDMX)."
        ),
        "source": "Policía Cibernética SSPC",
        "category": "sextorsion",
    },

    # ── BUENAS PRÁCTICAS GENERALES ───────────────────────────────────────────
    {
        "id": "bp_contrasenas_seguras",
        "text": (
            "Buenas prácticas — Contraseñas seguras: Una contraseña robusta debe tener mínimo "
            "12 caracteres, combinar mayúsculas, minúsculas, números y símbolos. "
            "NUNCA reutilice contraseñas entre servicios distintos. "
            "Use un gestor de contraseñas (Bitwarden es gratuito y de código abierto). "
            "Active autenticación de dos factores (2FA/MFA) en correo, banco y redes sociales. "
            "Cambie contraseñas si sospecha que fueron comprometidas. "
            "Verifique si su correo fue filtrado en: haveibeenpwned.com."
        ),
        "source": "Buenas Prácticas Ciberseguridad",
        "category": "prevencion",
    },
    {
        "id": "bp_wifi_publica",
        "text": (
            "Buenas prácticas — Redes Wi-Fi públicas: Las redes Wi-Fi públicas (cafés, aeropuertos, "
            "centros comerciales) son inseguras. Riesgos: ataques Man-in-the-Middle, redes falsas "
            "('evil twin'), captura de tráfico no cifrado. "
            "MEDIDAS: Evite ingresar a banca en línea en Wi-Fi pública. Use VPN si es necesario. "
            "Desactive 'conectar automáticamente' en su celular. "
            "Verifique el nombre exacto de la red con el establecimiento antes de conectarse. "
            "Prefiera datos móviles para operaciones sensibles."
        ),
        "source": "Buenas Prácticas Ciberseguridad",
        "category": "prevencion",
    },
    {
        "id": "bp_actualizaciones_seguridad",
        "text": (
            "Buenas prácticas — Actualizaciones de seguridad: Mantener el sistema operativo y "
            "aplicaciones actualizados es la medida preventiva más efectiva. El 60% de los "
            "ciberataques explotan vulnerabilidades con parche disponible. "
            "ACCIONES: Active actualizaciones automáticas en Windows/macOS/Android/iOS. "
            "Actualice el router doméstico (firmware). Elimine aplicaciones que ya no reciben "
            "actualizaciones de seguridad. En empresas: implemente política de parcheo mensual."
        ),
        "source": "Buenas Prácticas Ciberseguridad",
        "category": "prevencion",
    },

    # ── ESTADÍSTICAS MÉXICO ──────────────────────────────────────────────────
    {
        "id": "stats_ciberataques_mexico_2024",
        "text": (
            "Ciberseguridad en México — Estadísticas 2024: México es el segundo país más "
            "atacado de Latinoamérica (Kaspersky 2024). Se registran más de 200 millones de "
            "intentos de ciberataque anuales. Sectores más vulnerables: gobierno (35%), "
            "servicios financieros (25%), salud (15%), manufactura (10%). "
            "Costo promedio de una brecha de seguridad en México: $2.76 millones USD (IBM 2024). "
            "Principal vector de ataque: phishing (68% de los incidentes). "
            "México carece de una Ley Nacional de Ciberseguridad específica (en debate legislativo 2024)."
        ),
        "source": "Kaspersky / IBM Security 2024",
        "category": "estadisticas",
    },
    {
        "id": "stats_delitos_informaticos_mexico",
        "text": (
            "Delitos informáticos en México — Marco legal: El Código Penal Federal tipifica "
            "delitos informáticos en los artículos 211-bis. Delitos reconocidos: acceso ilícito "
            "a sistemas (211-bis1), modificación/destrucción de datos (211-bis2), fraude informático. "
            "Penas: de 3 meses a 9 años de prisión según gravedad. "
            "El Convenio de Budapest (cibercrimen internacional) aún no ha sido ratificado por México. "
            "Para denuncias de delitos informáticos: FGR (Fiscalía General), Policía Cibernética (088)."
        ),
        "source": "Código Penal Federal México",
        "category": "marco_legal",
    },
]


# ---------------------------------------------------------------------------
# Funciones principales
# ---------------------------------------------------------------------------

def get_collection():
    """Inicializa cliente ChromaDB y retorna la colección."""
    import chromadb
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    return client, client.get_or_create_collection(COLLECTION_NAME)


def get_embedder():
    """Carga el modelo de embeddings multilingüe."""
    from sentence_transformers import SentenceTransformer
    logger.info(f"Cargando embedder: {EMBED_MODEL}")
    return SentenceTransformer(EMBED_MODEL)


def index_all(reset: bool = False):
    """Indexa todos los documentos del KNOWLEDGE_BASE."""
    client, collection = get_collection()

    if reset:
        logger.warning("Reseteando colección...")
        client.delete_collection(COLLECTION_NAME)
        _, collection = get_collection()

    embedder = get_embedder()
    new_count = 0
    skip_count = 0

    for doc in KNOWLEDGE_BASE:
        doc_id = doc["id"]

        # Verificar si ya existe
        existing = collection.get(ids=[doc_id])
        if existing["ids"]:
            logger.info(f"  SKIP (ya existe): {doc_id}")
            skip_count += 1
            continue

        embedding = embedder.encode(doc["text"]).tolist()
        collection.add(
            documents=[doc["text"]],
            embeddings=[embedding],
            metadatas=[{
                "source":   doc.get("source", ""),
                "category": doc.get("category", "general"),
            }],
            ids=[doc_id],
        )
        logger.info(f"  ✅ Indexado: {doc_id}")
        new_count += 1

    logger.info(f"\n📚 Resultado: {new_count} nuevos | {skip_count} omitidos")
    logger.info(f"📊 Total en colección: {collection.count()}")


def show_stats():
    """Muestra estadísticas de la colección."""
    _, collection = get_collection()
    count = collection.count()
    print(f"\n{'='*50}")
    print(f"  Colección: {COLLECTION_NAME}")
    print(f"  Documentos indexados: {count}")
    print(f"  Ruta DB: {CHROMA_DB_PATH}")
    print(f"{'='*50}\n")

    if count > 0:
        sample = collection.get(limit=3)
        print("Muestra de documentos:")
        for i, (doc_id, meta) in enumerate(zip(sample["ids"], sample["metadatas"])):
            print(f"  [{i+1}] ID: {doc_id} | Fuente: {meta.get('source','?')} | Cat: {meta.get('category','?')}")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Indexador RAG — Ciberseguridad México")
    parser.add_argument("--reset", action="store_true", help="Borra y reindexa desde cero")
    parser.add_argument("--stats", action="store_true", help="Muestra estadísticas de la colección")
    args = parser.parse_args()

    if args.stats:
        show_stats()
        sys.exit(0)

    logger.info("🚀 Iniciando indexación de documentos de Ciberseguridad México...")
    index_all(reset=args.reset)
    logger.info("✅ Indexación completada.")
