# app.py

from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import gradio as gr
import torch
from utils import format_as_json
from config import (
    MODEL_NAME, MIN_LENGTH, MAX_LENGTH, 
    NUM_BEAMS, DO_SAMPLE, MAX_INPUT_LENGTH,
    SERVER_NAME, SERVER_PORT, INPUT_LINES, OUTPUT_LINES,
    INCIDENT_CLASSIFICATIONS 
)

# --- FORZAR USO DE GPU ---
device = 0 if torch.cuda.is_available() else -1

# Carga el tokenizador. Esto debe hacerse antes del pipeline para obtener el token de idioma.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# --- CONFIGURACIÓN DE LENGUAJE PARA M-BART ---
# Token de idioma para M-BART (es_XX = español)
SPANISH_TOKEN_ID = tokenizer.lang_code_to_id["es_XX"]
tokenizer.src_lang = "es_XX" 

summarizer = pipeline(
    "summarization", 
    model=MODEL_NAME, 
    tokenizer=tokenizer,
    device=device, # Usa la GPU si está disponible
    return_text=False 
)

def classify_incident_type(text):
    """
    Clasifica el tipo de incidente usando el diccionario de configuracion (sin hardcodeo if/elif)
    """
    text_lower = text.lower()
    
    # Itera sobre las categorías definidas en config.py
    for category, keywords in INCIDENT_CLASSIFICATIONS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
            
    return "General/Otros"


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
    # Se pasa el texto sin el 'prompt' ya que M-BART usa el token de idioma
    tokenized_input = tokenizer(
        text_input, 
        max_length=MAX_INPUT_LENGTH, 
        truncation=True, 
        return_tensors="pt"
    )
    safe_text_input = tokenizer.decode(tokenized_input.input_ids[0], skip_special_tokens=True)
    
    # Parámetros para el resumen
    summary_params = {
        'max_length': MAX_LENGTH,
        'min_length': MIN_LENGTH,
        'do_sample': DO_SAMPLE,
        'num_beams': NUM_BEAMS
    }
    
    # Generación del resumen
    # Se mantiene la confianza como estimación (90%)
    confidence_score_estimate = 90.0 
    
    summary_result = summarizer(
        safe_text_input, 
        # Fuerza el inicio de la generación con el token de español
        forced_bos_token_id=SPANISH_TOKEN_ID, 
        **summary_params
    )
    
    summary_text_output = summary_result[0]['summary_text']
    
    # Clasifica el tipo de incidente
    incident_type = classify_incident_type(text_input)
    
    # Prepara metadata para el JSON
    model_metadata = {
        'model_name': MODEL_NAME,
        'min_length': MIN_LENGTH,
        'max_length': MAX_LENGTH
    }
    
    # Formatea la salida como un JSON enriquecido, pasando la confianza
    json_output = format_as_json(
        summary_text_output, 
        text_input, 
        incident_type,
        model_metadata,
        confidence=confidence_score_estimate
    )
    
    return json_output


# --- AJUSTE DE LA INTERFAZ GRADIO (Metadata como componente separado) ---

# Se crea el componente de Markdown para mostrar la metadata
metadata_markdown = gr.Markdown(
    f"""
    ## 🧠 Metadata del Microagente
    | Parámetro | Valor |
    | :--- | :--- |
    | **Modelo** | `{MODEL_NAME}` |
    | **Min/Max Palabras** | `{MIN_LENGTH}/{MAX_LENGTH}` |
    | **Dispositivo** | `{'GPU (CUDA)' if device != -1 else 'CPU'}` |
    | **Confianza Est.** | `90%` |
    """,
)

# Crea y lanza la interfaz de Gradio
with gr.Blocks(title="Microagente de Resumen de Incidentes de TI") as iface:
    gr.Markdown("# 🤖 Microagente de Resumen de Incidentes de TI")
    gr.Markdown("Pegue el texto de un incidente de TI y reciba un resumen conciso y enriquecido en formato JSON.")
    
    metadata_markdown.render() 
    
    text_input = gr.Textbox(lines=INPUT_LINES, label=f"Texto del incidente (mínimo {MIN_LENGTH} palabras)")
    json_output = gr.Textbox(lines=OUTPUT_LINES, label="Resumen del incidente (JSON)")
    
    gr.Button("Generar Resumen").click(
        fn=summarize_incident, 
        inputs=text_input, 
        outputs=json_output
    )


iface.launch(
    server_name=SERVER_NAME,
    server_port=SERVER_PORT,
    share=False
)