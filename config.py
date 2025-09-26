# config.py

# Parámetros del Modelo
MODEL_NAME = "IIC/bart-large-spanish-xsum" # Mejor modelo para resumen en español y textos largos
MAX_INPUT_LENGTH = 1024 # Máxima longitud de tokens que el modelo puede manejar
MIN_LENGTH = 50         # Longitud mínima de palabras para el resumen
MAX_LENGTH = 150        # Longitud máxima de palabras para el resumen
NUM_BEAMS = 4           # Estrategia de búsqueda para mejor calidad
DO_SAMPLE = False       # Desactiva la aleatoriedad

# Parámetros de la Interfaz Gradio
SERVER_NAME = "0.0.0.0"
SERVER_PORT = 7860
INPUT_LINES = 15        # Aumentar la ventana de entrada
OUTPUT_LINES = 15       # Aumentar la ventana de salida

# Patrones de Expresiones Regulares para Extracción de Entidades
REGEX_PATTERNS = {
    # Nombres de servidores/servicios/recursos (ej. "Postgres-DB-01", "srv-01")
    'resources': r'(\b[A-Z0-9-]{3,}-\b[A-Z0-9-]{3,}|srv-[0-9a-zA-Z-]+|\b(switch|router|servidor|bd|database)-[0-9a-zA-Z-]{2,})',
    # IPs (ej. 192.168.1.1)
    'ips': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
    # IDs de incidentes (ej. "INC-7890", "#4321")
    'incident_id': r'(INC-[0-9]{4}|#[0-9]{4})',
    # Horarios (ej. "10:30 a.m.", "15:45")
    'times': r'(\d{1,2}:\d{2}\s?(?:a\.m\.|p\.m\.)?)'
}