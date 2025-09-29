# app.py

import json
from transformers import pipeline, AutoTokenizer
import gradio as gr
import torch
from utils import format_as_json
from config import (
    MODEL_NAME, MIN_LENGTH, MAX_LENGTH, 
    NUM_BEAMS, DO_SAMPLE, MAX_INPUT_LENGTH,
    SERVER_NAME, SERVER_PORT, INPUT_LINES, OUTPUT_LINES,
    INCIDENT_CLASSIFICATIONS, TRANSLATION_MODEL_NAME
)

# --- CONFIGURACIÓN DE MODELO E INICIO ---
# Modelo estable: facebook/bart-large-cnn (Estabilidad garantizada)
device = 0 if torch.cuda.is_available() else -1
print(f"Usando dispositivo CUDA: {device if device != -1 else 'CPU'}")

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
summarizer = pipeline(
    "summarization", 
    model=MODEL_NAME, 
    tokenizer=tokenizer,
    device=device,
    return_text=False 
)

# Carga del modelo de TRADUCCIÓN (Helsinki-NLP/opus-mt-en-es)
# Se crea un nuevo pipeline para la traducción
translator = pipeline(
    "translation",
    model=TRANSLATION_MODEL_NAME,
    device=device
)
# ----------------------------------------

def classify_incident_type(text):
    """
    Clasifica el tipo de incidente usando el diccionario de configuracion.
    """
    text_lower = text.lower()
    
    for category, keywords in INCIDENT_CLASSIFICATIONS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
            
    return "General/Otros"

def generate_rich_summary_markdown(data):
    """
    Procesa el diccionario de salida y genera un resumen atractivo en Markdown.
    """
    # Íconos para las categorías (añade atractivo visual)
    icon_map = {
        "Software/Aplicación": "💻", "Redes/Conectividad": "🌐", 
        "Infraestructura/Sistemas": "💾", "Base de datos": "🗄️", 
        "Seguridad": "🔒", "Continuidad de Negocio": "♻️", 
        "General/Otros": "📜"
    }
    
    summary = data['summary']
    incident_type = data['incident_type']
    confidence = data['metadata']['confidence_score']
    entities = data['entities']
    metrics = data['metadata']
    
    # --- 1. CABECERA Y RESUMEN CONCISO ---
    rich_md = f"""
    <div style='border: 1px solid #10B981; border-radius: 8px; padding: 15px; background-color: #ECFDF5;'>
        <h3 style='margin-top: 0; color: #065F46;'>{icon_map.get(incident_type, '📜')} Incidente Clasificado como: <span style='color: #047857;'>{incident_type}</span></h3>
        <p><strong>Confianza Estimada:</strong> <span style='color: #059669;'>{confidence}</span></p>
    </div>
    
    ---
    
    ## 📝 Resumen Ejecutivo
    
    {summary}
    
    ---
    """
    
    # --- 2. ENTIDADES CLAVE ---
    entity_md = "## 🔗 Entidades Detectadas\n"
    
    resources = entities.get('resources', [])
    if resources:
        entity_md += "### 💾 Recursos/Hostnames\n"
        entity_md += "• " + " • ".join([f"`{r}`" for r in resources]) + "\n\n"

    ips = entities.get('ips', [])
    if ips:
        entity_md += "### 🌐 Direcciones IP\n"
        entity_md += "• " + " • ".join([f"`{ip}`" for ip in ips]) + "\n\n"

    ids = entities.get('incident_id', [])
    if ids:
        entity_md += "### 🏷️ IDs de Incidente\n"
        entity_md += "• " + " • ".join([f"**{i}**" for i in ids]) + "\n\n"
        
    rich_md += entity_md
    
    # --- 3. MÉTRICAS DE EFICIENCIA (Tabla) ---
    rich_md += """
    ---
    ## 📈 Métricas de Procesamiento
    
    | Métrica | Valor |
    | :--- | :--- |
    | Palabras Originales | {original_words_count} |
    | Palabras del Resumen | {summary_words_count} |
    | **Reducción (%)** | **{reduction_percentage}%** |
    """.format(**metrics)
    
    return rich_md

def summarize_incident_and_process(text_input):
    """
    Ejecuta el resumen, clasificación y genera el JSON, devolviendo el JSON crudo 
    y el resumen enriquecido en Markdown.
    """
    if not text_input:
        # Devuelve dos outputs: uno para el JSON, otro para el Markdown
        return json.dumps({"status": "error", "message": "El texto de entrada está vacío."}, indent=4), "## ❌ Error\nEl texto de entrada está vacío."
    
    if len(text_input.split()) < MIN_LENGTH:
        error_msg = f"El texto es demasiado corto para generar un resumen significativo. Por favor, ingrese al menos {MIN_LENGTH} palabras."
        return json.dumps({"status": "error", "message": error_msg}, indent=4), f"## ❌ Error\n{error_msg}"

    # TRUCO DE INSTRUCCIÓN EN ESPAÑOL (Mantenido para guiar el resumen de BART-CNN)
    spanish_prompt_prefix = "Resuma este texto del incidente de TI de forma concisa, profesional y **exclusivamente en español**: "
    input_with_prompt = spanish_prompt_prefix + text_input
    
    # 1. Generación de Resumen (Puede ser bilingüe)
    tokenized_input = tokenizer(input_with_prompt, max_length=MAX_INPUT_LENGTH, truncation=True, return_tensors="pt")
    safe_text_input = tokenizer.decode(tokenized_input.input_ids[0], skip_special_tokens=True)
    
    summary_params = {
        'max_length': MAX_LENGTH,
        'min_length': MIN_LENGTH,
        'do_sample': DO_SAMPLE,
        'num_beams': NUM_BEAMS
    }
    
    confidence_score_estimate = 90.0 
    
    summary_result = summarizer(safe_text_input, **summary_params)
    bilingual_summary = summary_result[0]['summary_text']
    
    # 2. POST-PROCESAMIENTO DE TRADUCCIÓN (Para forzar el español puro)
    # Asume que la mayoría del texto es español con frases en inglés incrustadas
    # Se utiliza el modelo de EN->ES para limpiar frases en inglés como "The incident occurred..."
    translation_result = translator(bilingual_summary, max_length=260)
    summary_text_output = translation_result[0]['translation_text']

    incident_type = classify_incident_type(text_input)
    
    model_metadata = {
        'model_name': MODEL_NAME,
        'translation_model': TRANSLATION_MODEL_NAME,
        'min_length': MIN_LENGTH,
        'max_length': MAX_LENGTH
    }
    
    # Genera la salida JSON cruda
    json_output = format_as_json(
        summary_text_output, 
        text_input, 
        incident_type,
        model_metadata,
        confidence=confidence_score_estimate
    )
    
    # Genera la salida enriquecida a partir del JSON
    data_dict = json.loads(json_output)
    rich_markdown_output = generate_rich_summary_markdown(data_dict)
    
    # Devuelve la tupla (JSON crudo, Markdown enriquecido)
    return json_output, rich_markdown_output


# --- AJUSTE DE LA INTERFAZ GRADIO (Final) ---

# Usamos la sintaxis de tema compatible y la estructura de bloques
with gr.Blocks(theme='soft', title="Microagente de Resumen de Incidentes de TI") as iface:
    
    gr.Markdown("# 🤖 Microagente de Resumen de Incidentes de TI")
    gr.Markdown("Pegue el texto de un incidente de TI y obtenga un resumen conciso y enriquecido en español.")
    
    # Metadata del Modelo
    metadata_markdown = gr.Markdown(
        f"""
        <div style='background-color: #F3F4F6; padding: 10px; border-radius: 5px;'>
            | Parámetro | Valor |
            | :--- | :--- |
            | **Modelo de Resumen** | `{MODEL_NAME}` |
            | **Modelo de Traducción** | `{TRANSLATION_MODEL_NAME}` |
            | **Dispositivo** | `{'GPU (CUDA)' if device != -1 else 'CPU'}` |
        </div>
        """,
    )
    
    # Área de entrada
    with gr.Row():
        text_input = gr.Textbox(
            lines=INPUT_LINES, 
            label=f"Texto Completo del Incidente (Mín. {MIN_LENGTH} palabras)",
            placeholder="Pegue aquí el historial de logs, chats y notas del incidente..."
        )
        
    
    # Contenedores para las salidas (inicializados)
    with gr.Tabs():
        with gr.TabItem("✅ Resumen Enriquecido (Recomendado)"):
            rich_output_markdown = gr.Markdown("El resumen enriquecido aparecerá aquí después del procesamiento.", elem_id="rich_output")
            
        with gr.TabItem("⚙️ Salida JSON Cruda"):
            json_output_textbox = gr.Textbox(
                lines=OUTPUT_LINES, 
                label="JSON Crudo (Salida del API)", 
                elem_id="json_output"
            )

    # Botón y conexión de la lógica a los componentes de salida
    gr.Button("Generar Análisis y Resumen", variant="primary").click(
        fn=summarize_incident_and_process, 
        inputs=text_input, 
        # Conectamos directamente la tupla de salida (JSON, Markdown) a los componentes
        outputs=[json_output_textbox, rich_output_markdown] 
    )

    
iface.launch(
    server_name=SERVER_NAME,
    server_port=SERVER_PORT,
    share=False
)