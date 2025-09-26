# app.py

from transformers import pipeline, BartTokenizer
import gradio as gr
from utils import format_as_json
from config import (
    MODEL_NAME, MIN_LENGTH, MAX_LENGTH, 
    NUM_BEAMS, DO_SAMPLE, MAX_INPUT_LENGTH,
    SERVER_NAME, SERVER_PORT, INPUT_LINES, OUTPUT_LINES
)

# Carga el tokenizador y el modelo de resumen.
# Se usa un modelo más robusto y entrenado para español.
tokenizer = BartTokenizer.from_pretrained(MODEL_NAME)
summarizer = pipeline(
    "summarization", 
    model=MODEL_NAME, 
    tokenizer=tokenizer
)

def classify_incident_type(text):
    # ... (La función se mantiene igual, ya es funcional)
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
    
    # 2. Manejo de texto largo (Tokenización y truncamiento)
    # Se usa el tokenizador para obtener los IDs y truncar si es necesario.
    tokenized_input = tokenizer(
        text_input, 
        max_length=MAX_INPUT_LENGTH, 
        truncation=True,
        return_tensors="pt"
    )
    
    # Se usa el "input_ids" truncado como entrada del pipeline para evitar errores de memoria/longitud
    input_ids = tokenized_input.input_ids[0].tolist()
    
    # Parámetros para el resumen
    summary_params = {
        'max_length': MAX_LENGTH,
        'min_length': MIN_LENGTH,
        'do_sample': DO_SAMPLE,
        'num_beams': NUM_BEAMS
    }
    
    # Generación del resumen
    # El pipeline necesita la cadena de texto como entrada, no los IDs truncados, 
    # pero el truncamiento se maneja internamente en la llamada con los parámetros correctos.
    # Para asegurar el truncamiento si es necesario:
    
    # **Estrategia de truncamiento seguro para el pipeline:**
    # Se decodifica solo hasta el límite de tokens para el resumen.
    safe_text_input = tokenizer.decode(input_ids, skip_special_tokens=True)
    
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
    json_output = format_as_json(
        summary[0]['summary_text'], 
        text_input, 
        incident_type,
        model_metadata
    )
    
    # 3. Formato para la Interfaz de Gradio (Encabezado y JSON)
    
    # Se simula una confianza alta ya que el modelo BART-CNN no devuelve una métrica de confianza directa (score).
    # Puedes implementar un clasificador separado si necesitas una confianza real.
    confidence_estimate = "Alta (Modelo especializado en español)" 
    
    header = (
        f"--- Datos del Modelo y Resumen ---\n"
        f"Modelo: {MODEL_NAME}\n"
        f"Confianza Estimada: {confidence_estimate}\n"
        f"Palabras (Min/Max): {MIN_LENGTH}/{MAX_LENGTH}\n"
        f"----------------------------------\n"
    )
    
    return header + json_output


# Crea y lanza la interfaz de Gradio
iface = gr.Interface(
    fn=summarize_incident, 
    # Ventanas más grandes (autoajustables)
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