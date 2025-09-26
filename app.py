# app.py

from transformers import pipeline, BartTokenizer, BartForConditionalGeneration
import gradio as gr
from utils import format_as_json, preprocess_text, chunk_text
from config import MODEL_CONFIG, APP_CONFIG, INCIDENT_KEYWORDS
import torch
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- INICIALIZACIÓN DEL MODELO ---
def initialize_model():
    """Inicializa el modelo de summarization con la configuración centralizada"""
    device_id = 0 if torch.cuda.is_available() else -1
    logger.info(f"Usando dispositivo: {'GPU' if device_id == 0 else 'CPU'}")
    
    try:
        tokenizer = BartTokenizer.from_pretrained(MODEL_CONFIG["name"])
        model = BartForConditionalGeneration.from_pretrained(MODEL_CONFIG["name"])
        
        if device_id == 0:
            model = model.cuda()
        
        summarizer = pipeline(
            "summarization",
            model=model,
            tokenizer=tokenizer,
            device=device_id
        )
        
        logger.info("Modelo inicializado exitosamente")
        return summarizer
        
    except Exception as e:
        logger.error(f"Error inicializando modelo: {e}")
        raise

# Inicializar modelo al importar
summarizer = initialize_model()

def classify_incident_type(text):
    """
    Clasifica el tipo de incidente usando configuración centralizada
    """
    text_lower = text.lower()
    
    for category, keywords in INCIDENT_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
            
    return "General"

def summarize_incident(text_input):
    """
    Función principal para resumir incidentes
    """
    try:
        if not text_input or len(text_input.strip()) == 0:
            return format_as_json("", "Entrada vacía", "Error", "Texto de entrada vacío")
        
        # Preprocesar texto
        processed_text = preprocess_text(text_input)
        word_count = len(processed_text.split())
        
        # Validar longitud
        if word_count < APP_CONFIG["min_words"]:
            return format_as_json("", processed_text, "General", 
                                f"Texto demasiado corto. Mínimo {APP_CONFIG['min_words']} palabras requeridas.")
        
        # Manejar textos largos
        if word_count > APP_CONFIG["max_words"]:
            chunks = chunk_text(processed_text, APP_CONFIG["chunk_size"])
            processed_text = chunks[0]
            logger.info(f"Texto dividido en {len(chunks)} chunks")
        
        # Crear prompt usando template configurado
        prompt = APP_CONFIG["prompt_template"].format(processed_text)
        
        # Generar resumen con parámetros configurados
        summary = summarizer(
            prompt, 
            max_length=MODEL_CONFIG["max_summary_length"],
            min_length=MODEL_CONFIG["min_summary_length"],
            do_sample=MODEL_CONFIG["do_sample"],
            num_beams=MODEL_CONFIG["num_beams"],
            length_penalty=MODEL_CONFIG["length_penalty"],
            no_repeat_ngram_size=MODEL_CONFIG["no_repeat_ngram_size"]
        )
        
        # Clasificar y formatear resultado
        incident_type = classify_incident_type(processed_text)
        return format_as_json(summary[0]['summary_text'], processed_text, incident_type)
        
    except Exception as e:
        logger.error(f"Error en summarize_incident: {e}")
        return format_as_json("", text_input, "Error", f"Error procesando el texto: {str(e)}")

# Interfaz Gradio
iface = gr.Interface(
    fn=summarize_incident, 
    inputs=gr.Textbox(
        lines=10, 
        label="Texto del incidente",
        placeholder=f"Pegue aquí el texto del incidente... (mínimo {APP_CONFIG['min_words']} palabras)"
    ), 
    outputs=gr.Textbox(label="Resumen del incidente (JSON)"),
    title="Microagente de Resumen de Incidentes de TI",
    description=f"""
    📋 Procesa textos de incidentes de TI y genera resúmenes concisos en español.
    
    **Configuración actual:**
    - Idioma: {APP_CONFIG['language']}
    - Mínimo de palabras: {APP_CONFIG['min_words']}
    - Máximo recomendado: {APP_CONFIG['max_words']} palabras
    - Modelo: {MODEL_CONFIG['name']}
    """
)

if __name__ == "__main__":
    iface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )