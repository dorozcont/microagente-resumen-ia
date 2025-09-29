# config.py

# Parámetros del Modelo
MODEL_NAME = "facebook/mbart-large-50-many-to-many-mmt" 
MAX_INPUT_LENGTH = 1024 # Máxima longitud de tokens (robusta para BART-large)
MIN_LENGTH = 50         # Longitud mínima de palabras para el resumen
MAX_LENGTH = 150        # Longitud máxima de palabras para el resumen
NUM_BEAMS = 4           # Estrategia de búsqueda para mejor calidad
DO_SAMPLE = False       # Desactiva la aleatoriedad

# Parámetros de la Interfaz Gradio
SERVER_NAME = "0.0.0.0"
SERVER_PORT = 7860
INPUT_LINES = 15        # Aumentar la ventana de entrada
OUTPUT_LINES = 15       # Aumentar la ventana de salida

# --- CLASIFICACIÓN DE INCIDENTES (Evita el hardcodeo en app.py) ---
INCIDENT_CLASSIFICATIONS = {
    "Redes/Conectividad": ["red", "router", "switch", "vpn", "firewall", "conectividad", "corte"],
    "Infraestructura/Sistemas": ["servidor", "cpu", "memoria", "disco", "os", "centos", "linux", "hardware", "vm", "host"],
    "Base de datos": ["base de datos", "sql", "postgres", "mongo", "replication", "query", "bloqueo", "lento"],
    "Seguridad": ["seguridad", "acceso", "vulnerabilidad", "phishing", "ransomware", "autenticacion", "filtracion"],
    "Software/Aplicación": ["aplicación", "software", "bug", "código", "deploy", "apache", "nginx", "java", "script", "micros", "api"],
    "Continuidad de Negocio": ["backup", "respaldo", "dr", "disaster", "replicacion", "recuperacion"],
}

# Patrones de Expresiones Regulares para Extracción de Entidades
REGEX_PATTERNS = {
    # Solo se dejan IPs e IDs, la extracción de 'resources' usa lógica Key-Value en utils.py
    'ips': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
    'incident_id': r'(INC-[0-9]{4}|#[0-9]{4}|TICKET-[0-9]{4})'
}