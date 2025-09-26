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