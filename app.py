# app.py

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import gradio as gr
from utils import format_as_json
from config import (
    MODEL_NAME, MIN_LENGTH, MAX_LENGTH, 
    NUM_BEAMS, DO_SAMPLE, MAX_INPUT_LENGTH,
    SERVER_NAME, SERVER_PORT, INPUT_LINES, OUTPUT_LINES
)

# Carga el tokenizador y el modelo de resumen.
# Usamos AutoTokenizer para cargar el tokenizador correcto para el modelo estable.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
summarizer = pipeline(
    "summarization", 
    model=MODEL_NAME, 
    tokenizer=tokenizer
)

def classify_incident_type(text):
    # Función de clasificación (se mantiene igual)
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
    if not text_input:
        return "El texto de entrada está vacío."
    
    # 1. Validación de longitud mínima (en palabras)
    if len(text_input.split()) < MIN_LENGTH:
        return f"El texto es demasiado corto para generar un resumen significativo. Por favor, ingrese al menos {MIN_LENGTH} palabras."
    
    # 2. TRUCO PARA FORZAR EL IDIOMA ESPAÑOL (PROMPT)
    # Esto agrega un prefix en español al texto de entrada, lo que instruye al modelo a responder en el mismo idioma.
    spanish_prompt_prefix = "Resuma este texto del incidente de TI de forma concisa y profesional en español: "
    input_with_prompt = spanish_prompt_prefix + text_input
    
    # 3. Manejo de texto largo (Tokenización y truncamiento)
    tokenized_input = tokenizer(
        input_with_prompt, 
        max_length=MAX_INPUT_LENGTH, 
        truncation=True, # Trunca si excede los 1024 tokens
        return_tensors="pt"
    )
    
    # Decodificamos el input truncado para pasarlo al pipeline
    safe_text_input = tokenizer.decode(tokenized_input.input_ids[0], skip_special_tokens=True)
    
    # Parámetros para el resumen
    summary_params = {
        'max_length': MAX_LENGTH,
        'min_length': MIN_LENGTH,
        'do_sample': DO_SAMPLE,
        'num_beams': NUM_BEAMS
    }
    
    # Generación del resumen
    summary = summarizer(
        safe_text_input, 
        **summary_params
    )
    
    # Clasifica el tipo de incidente
    incident_type = classify_incident_type(text_input)
    
    # Prepara metadata para el JSON
    model_metadata = {
        'model_name': MODEL_NAME,
        'min_length': MIN_LENGTH,
        'max_length': MAX_LENGTH
    }
    
    # Formatea la salida como un JSON enriquecido
    summary_text_output = summary[0]['summary_text']
    
    json_output = format_as_json(
        summary_text_output, 
        text_input, 
        incident_type,
        model_metadata
    )
    
    # 4. Formato para la Interfaz de Gradio (Encabezado y JSON)
    # Se añade la información del encabezado solicitada.
    confidence_estimate = "Media/Alta (Modelo estable en inglés con instrucción en español)" 
    
    header = (
        f"--- Datos del Modelo y Resumen ---\n"
        f"Modelo: {MODEL_NAME}\n"
        f"Confianza Estimada: {confidence_estimate}\n"
        f"Palabras (Min/Max Recomendadas): {MIN_LENGTH}/{MAX_LENGTH}\n"
        f"----------------------------------\n"
    )
    
    return header + json_output


# Crea y lanza la interfaz de Gradio
iface = gr.Interface(
    fn=summarize_incident, 
    # Ventanas más grandes (autoajustables) usando valores de config.py
    inputs=gr.Textbox(lines=INPUT_LINES, label=f"Texto del incidente (mínimo {MIN_LENGTH} palabras)"), 
    outputs=gr.Textbox(lines=OUTPUT_LINES, label="Resumen del incidente (JSON)"),
    title="Microagente de Resumen de Incidentes de TI",
    description="Pegue el texto de un incidente de TI y reciba un resumen conciso y enriquecido en formato JSON."
)

iface.launch(
    server_name=SERVER_NAME,
    server_port=SERVER_PORT,
    share=False
)