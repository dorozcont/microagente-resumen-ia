# app.py

from transformers import pipeline
import gradio as gr
from utils import format_as_json
import torch

# --- DETECCIÓN DE GPU Y CARGA DE MODELO ---
# Determina el dispositivo: usa la primera GPU (0) si CUDA está disponible, sino usa CPU (-1)
# Ya confirmamos que torch.cuda.is_available() es True.
device_id = 0 if torch.cuda.is_available() else -1
print(f"DEBUG: El pipeline usará el dispositivo: {'GPU (ID 0)' if device_id == 0 else 'CPU'}")

# Carga el modelo de resumen, forzando el uso del dispositivo detectado.
summarizer = pipeline(
    "summarization", 
    model="facebook/bart-large-cnn",
    device=device_id # <--- MODIFICACIÓN CRÍTICA: Fuerza el uso de la GPU
)

def classify_incident_type(text):
    """
    Clasifica el tipo de incidente basándose en palabras clave en el texto .
    """
    text_lower = text.lower()
    
    if "red" in text_lower or "servidor" in text_lower or "router" in text_lower or "switch" in text_lower:
        return "Redes/Infraestructura"
    if "base de datos" in text_lower or "sql" in text_lower or "postgres" in text_lower or "mongo" in text_lower:
        return "Base de datos"
    if "seguridad" in text_lower or "acceso" in text_lower or "vulnerabilidad" in text_lower or "phishing" in text_lower:
        return "Seguridad"
    if "aplicación" in text_lower or "software" in text_lower or "bug" in text_lower or "código" in text_lower:
        return "Software/Aplicación"
        
    return "General"

def summarize_incident(text_input):
    """
    Toma un texto de incidente, lo clasifica y devuelve un resumen enriquecido en formato JSON.
    """
    if not text_input or len(text_input.split()) < 50:
        return "El texto es demasiado corto para generar un resumen significativo. Por favor, ingrese al menos 50 palabras."
    
    # Parámetros para un resumen más funcional y de alta calidad
    summary = summarizer(
        text_input, 
        max_length=150,    # Longitud máxima del resumen
        min_length=50,     # Longitud mínima del resumen
        do_sample=False,   # Desactiva la aleatoriedad, haciendo la respuesta determinista
        num_beams=4        # Estrategia de búsqueda para una mejor calidad
    )
    
    # Clasifica el tipo de incidente.
    incident_type = classify_incident_type(text_input)
    
    # Formatea la salida como un JSON enriquecido
    return format_as_json(summary[0]['summary_text'], text_input, incident_type)

# Crea y lanza la interfaz de Gradio
iface = gr.Interface(
    fn=summarize_incident, 
    inputs=gr.Textbox(lines=10, label="Texto del incidente"), 
    outputs=gr.Textbox(label="Resumen del incidente (JSON)"),
    title="Microagente de Resumen de Incidentes de TI",
    description="Pegue el texto de un incidente de TI y reciba un resumen conciso y enriquecido en formato JSON."
)

iface.launch(
    server_name="0.0.0.0",
    server_port=7860,
    share=False
)