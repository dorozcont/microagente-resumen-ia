# config.py

# Parámetros del Modelo
MODEL_NAME = "facebook/bart-large-cnn" 
MAX_INPUT_LENGTH = 1024 
MIN_LENGTH = 100         
MAX_LENGTH = 250         
NUM_BEAMS = 4           
DO_SAMPLE = False       

# Modelo de post-procesamiento para forzar el español
TRANSLATION_MODEL_NAME = "Helsinki-NLP/opus-mt-en-es"

# Configuración de la Interfaz
SERVER_NAME = "0.0.0.0"
SERVER_PORT = 7860
INPUT_LINES = 15
OUTPUT_LINES = 10

# Clasificación de Incidentes (Mantenido)
INCIDENT_CLASSIFICATIONS = {
    "Software/Aplicación": ["aplicación", "software", "bug", "código", "deploy", "rollback"],
    "Redes/Conectividad": ["red", "router", "switch", "conectividad", "latencia", "fibra"],
    "Infraestructura/Sistemas": ["servidor", "cpu", "memoria", "host", "disco", "filesystem"],
    "Base de datos": ["base de datos", "sql", "postgres", "mongo", "deadlock", "query"],
    "Seguridad": ["seguridad", "acceso", "vulnerabilidad", "phishing", "ddos", "firewall", "waf"],
    "General/Otros": []
}

# Patrones de REGEX para utils.py (¡CLAVE!)
REGEX_PATTERNS = {
    # IPv4 con o sin notación CIDR
    'ips': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?:/\d{1,2})?\b',
    # IDs de incidente y tickets comunes
    'incident_id': r'(\bINC-[A-Z0-9]{3,}|SW-[A-Z0-9]{3,}|TICKET-[A-Z0-9]{3,}|#[0-9]{3,})'
}