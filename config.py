# config.py

# Parámetros del Modelo
MODEL_NAME = "facebook/bart-large-cnn" 
MAX_INPUT_LENGTH = 1024 # Máxima longitud de tokens (robusta para BART-large)
MIN_LENGTH = 50         # Longitud mínima de palabras para el resumen
MAX_LENGTH = 250        # Longitud máxima de palabras para el resumen
NUM_BEAMS = 4           # Estrategia de búsqueda para mejor calidad
DO_SAMPLE = False       # Desactiva la aleatoriedad

# NUEVO: Modelo de post-procesamiento para forzar el español
TRANSLATION_MODEL_NAME = "Helsinki-NLP/opus-mt-en-es"

# Parámetros de la Interfaz Gradio
SERVER_NAME = "0.0.0.0"
SERVER_PORT = 7860
INPUT_LINES = 15        # Aumentar la ventana de entrada
OUTPUT_LINES = 15       # Aumentar la ventana de salida

# --- CLASIFICACIÓN DE INCIDENTES (Evita el hardcodeo en app.py) ---
INCIDENT_CLASSIFICATIONS = {
    # Priorizamos estas palabras clave para capturar el ejemplo de error de reporte
    "Software/Aplicación": ["aplicación", "software", "bug", "código", "deploy", "apache", "nginx", "java", "script", "micros", "api", "servicio", "módulo", "despliegue", "sintaxis", "rollback", "patch", "reporte", "función", "interfaz de usuario", "devuelve un error"], 
    "Redes/Conectividad": ["red", "router", "switch", "vpn", "firewall", "conectividad", "corte", "enlace"],
    "Infraestructura/Sistemas": ["servidor", "cpu", "memoria", "disco", "os", "centos", "linux", "hardware", "vm", "host", "datacenter", "virtual"],
    "Base de datos": ["base de datos", "sql", "postgres", "mongo", "replication", "query", "bloqueo", "lento", "oracle"],
    "Seguridad": ["seguridad", "acceso", "vulnerabilidad", "phishing", "ransomware", "autenticacion", "filtracion", "malware"],
    "Continuidad de Negocio": ["backup", "respaldo", "dr", "disaster", "replicacion", "recuperacion", "copia"],
}

# Patrones de Expresiones Regulares para Extracción de Entidades
REGEX_PATTERNS = {
    # Solo se dejan IPs e IDs, la extracción de 'resources' usa lógica Key-Value en utils.py
    'ips': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
    'incident_id': r'(INC-[0-9]{4}|#[0-9]{4}|TICKET-[0-9]{4})'
}