# config.py

# Parámetros del Modelo
MODEL_NAME = "facebook/bart-large-cnn" 
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

# Patrones de Expresiones Regulares para Extracción de Entidades
REGEX_PATTERNS = {
    # Nombres de servidores/servicios/recursos
    'resources': r'(\b[A-Z0-9-]{3,}-\b[A-Z0-9-]{3,}|srv-[0-9a-zA-Z-]+|\b(switch|router|servidor|bd|database|hostname|os|apache)-[0-9a-zA-Z-]{2,})', # <-- ¡Ajuste para Hostname, OS y Apache!
    # IPs
    'ips': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
    # IDs de incidentes
    'incident_id': r'(INC-[0-9]{4}|#[0-9]{4})'
}