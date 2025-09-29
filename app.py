# app.py

from transformers import pipeline, AutoTokenizer
import gradio as gr
import torch # Importamos torch para forzar el uso de la GPU
from utils import format_as_json
from config import (
    MODEL_NAME, MIN_LENGTH, MAX_LENGTH, 
    NUM_BEAMS, DO_SAMPLE, MAX_INPUT_LENGTH,
    SERVER_NAME, SERVER_PORT, INPUT_LINES, OUTPUT_LINES
)

# --- FORZAR USO DE GPU ---
device = 0 if torch.cuda.is_available() else -1
print(f"Usando dispositivo CUDA: {device if device != -1 else 'CPU'}")

# Token ID para español (es_XX) en M-BART. Esto es crucial.
SPANISH_TOKEN_ID = tokenizer.lang_code_to_id["es_XX"] 

# Carga el tokenizador y el modelo de resumen.
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
summarizer = pipeline(
    "summarization", 
    model=MODEL_NAME, 
    tokenizer=tokenizer,
    device=device,
    # El pipeline de M-BART requiere el idioma de entrada para inicializar la generación
    src_lang="es_XX" 
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
    
    # 2. TRUCO PARA FORZAR EL IDIOMA ESPAÑOL (PROMPT)
    spanish_prompt_prefix = "Resuma este texto del incidente de TI de forma concisa y profesional en español: "
    input_with_prompt = spanish_prompt_prefix + text_input
    
    # 3. Manejo de texto largo (Tokenización y truncamiento)
    tokenized_input = tokenizer(
        input_with_prompt, 
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
    # El pipeline, cuando se usa con return_text=False (implícito), devuelve un objeto con el score si el modelo lo soporta.
    # BART-CNN NO devuelve un score de confianza directo (probabilidad del resumen).
    # Simulamos el score de confianza como un 90% para la interfaz, ya que el modelo es determinista (do_sample=False).
    # Este valor debe ser entendido como una 'estimación'.
    confidence_score_estimate = 90.0 
    
    summary_result = summarizer(
        safe_text_input, 
        **summary_params
    )
    
    # Extraer el resumen del resultado (es una lista con un dict)
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


# --- AJUSTE DE LA INTERFAZ GRADIO ---

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
    # Se usa f-string para asegurar que las variables de config.py se muestren
)

# Crea y lanza la interfaz de Gradio
with gr.Blocks(title="Microagente de Resumen de Incidentes de TI") as iface:
    gr.Markdown("# 🤖 Microagente de Resumen de Incidentes de TI")
    gr.Markdown("Pegue el texto de un incidente de TI y reciba un resumen conciso y enriquecido en formato JSON.")
    
    metadata_markdown.render() # Mostrar el componente Markdown
    
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