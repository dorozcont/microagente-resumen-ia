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
    INCIDENT_CLASSIFICATIONS, TRANSLATION_MODEL_NAME # <--- ¡Importación completa!
)

# --- CONFIGURACIÓN DE MODELO E INICIO ---
device = 0 if torch.cuda.is_available() else -1
print(f"Usando dispositivo CUDA: {device if device != -1 else 'CPU'}")

# Carga del modelo de RESUMEN (BART-CNN)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
summarizer = pipeline(
    "summarization", 
    model=MODEL_NAME, 
    tokenizer=tokenizer,
    device=device,
    return_text=False 
)

# Carga del modelo de TRADUCCIÓN (Helsinki-NLP/opus-mt-en-es)
translator = pipeline(
    "translation",
    model=TRANSLATION_MODEL_NAME,
    device=device
)
# ----------------------------------------

def classify_incident_type(text):
    """
    Clasifica el tipo de incidente basándose en palabras clave.
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
    icon_map = {
        "Software/Aplicación": "💻", "Redes/Conectividad": "🌐", 
        "Infraestructura/Sistemas": "💾", "Base de datos": "🗄️", 
        "Seguridad": "🔒", "Continuidad de Negocio": "♻️", 
        "General/Otros": "📜"
    }
    
    summary = data['summary']
    incident_type = data['incident_type']
    confidence = data['metadata'].get('confidence_score', 'N/A')
    entities = data['entities']
    metrics = data['metadata']
    
    # --- 1. CABECERA Y RESUMEN CONCISO ---
    # Usamos .get() para la confianza por si no está seteada.
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
    
    # Usamos .get(key, []) para asegurar que no haya un KeyError si la lista está vacía.
    resources = entities.get('resources', [])
    ips = entities.get('ips', [])
    ids = entities.get('incident_id', [])

    if resources or ips or ids:
        if resources:
            entity_md += "### 💾 Recursos/Hostnames\n"
            entity_md += "• " + " • ".join([f"`{r}`" for r in resources]) + "\n\n"

        if ips:
            entity_md += "### 🌐 Direcciones IP\n"
            entity_md += "• " + " • ".join([f"`{ip}`" for ip in ips]) + "\n\n"

        if ids:
            entity_md += "### 🏷️ IDs de Incidente\n"
            entity_md += "• " + " • ".join([f"**{i}**" for i in ids]) + "\n\n"
    else:
        entity_md += "⚠️ No se detectaron entidades clave (recursos, IPs, o IDs de incidente) en el texto.\n\n"
        
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
    Ejecuta el resumen, lo traduce a español puro, clasifica y genera el JSON, 
    devolviendo el JSON crudo y el resumen enriquecido en Markdown.
    """
    if not text_input or len(text_input.split()) < MIN_LENGTH:
        error_msg = f"El texto es demasiado corto para generar un resumen significativo. Por favor, ingrese al menos {MIN_LENGTH} palabras."
        return json.dumps({"status": "error", "message": error_msg}, indent=4), f"## ❌ Error\n{error_msg}"
    
    # 1. Generación de Resumen (BART-CNN)
    spanish_prompt_prefix = "Resuma este texto del incidente de TI de forma concisa, profesional y **exclusivamente en español**: "
    input_with_prompt = spanish_prompt_prefix + text_input
    
    tokenized_input = tokenizer(input_with_prompt, max_length=MAX_INPUT_LENGTH, truncation=True, return_tensors="pt")
    safe_text_input = tokenizer.decode(tokenized_input.input_ids[0], skip_special_tokens=True)
    
    summary_params = {
        'max_length': MAX_LENGTH,
        'min_length': MIN_LENGTH,
        'do_sample': DO_SAMPLE,
        'num_beams': NUM_BEAMS
    }
    
    summary_result = summarizer(safe_text_input, **summary_params)
    bilingual_summary = summary_result[0]['summary_text']
    
    # 2. POST-PROCESAMIENTO DE TRADUCCIÓN (Opus-MT)
    # Usamos un max_length mayor para evitar el truncamiento
    translation_result = translator(bilingual_summary, max_length=260)
    summary_text_output = translation_result[0]['translation_text']
    
    # Clasificación y JSON
    incident_type = classify_incident_type(text_input)
    confidence_score_estimate = 90.0 
    
    model_metadata = {
        'model_name': MODEL_NAME, 
        'translation_model': TRANSLATION_MODEL_NAME, 
        'min_length': MIN_LENGTH, 
        'max_length': MAX_LENGTH
    }
    
    # Llama a format_as_json para generar el JSON completo
    json_output = format_as_json(
        summary_text_output, 
        text_input, 
        incident_type,
        model_metadata,
        confidence=confidence_score_estimate
    )
    
    # Genera la salida enriquecida a partir del diccionario JSON
    data_dict = json.loads(json_output)
    rich_markdown_output = generate_rich_summary_markdown(data_dict)
    
    return json_output, rich_markdown_output


# --- AJUSTE DE LA INTERFAZ GRADIO (Final) ---

with gr.Blocks(theme='soft', title="Microagente de Resumen de Incidentes de TI") as iface:
    
    gr.Markdown("# 🤖 Microagente de Resumen de Incidentes de TI")
    gr.Markdown("Pegue el texto de un incidente de TI y obtenga un resumen conciso y enriquecido en español.")
    
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
    
    with gr.Row():
        text_input = gr.Textbox(
            lines=INPUT_LINES, 
            label=f"Texto Completo del Incidente (Mín. {MIN_LENGTH} palabras)",
            placeholder="Pegue aquí el historial de logs, chats y notas del incidente..."
        )
        
    
    with gr.Tabs():
        with gr.TabItem("✅ Resumen Enriquecido (Recomendado)"): 
            # Output 2 (Markdown)
            rich_output_markdown = gr.Markdown("El resumen enriquecido aparecerá aquí después del procesamiento.", elem_id="rich_output")
            
        with gr.TabItem("⚙️ Salida JSON Cruda"):
            # Output 1 (Raw JSON Textbox)
            json_output_textbox = gr.Textbox(
                lines=OUTPUT_LINES, 
                label="JSON Crudo (Salida del API)", 
                elem_id="json_output"
            )

    # Conexión de la función a los outputs
    gr.Button("Generar Análisis y Resumen", variant="primary").click(
        fn=summarize_incident_and_process, 
        inputs=text_input, 
        outputs=[json_output_textbox, rich_output_markdown] # Asegurar el orden (JSON, Markdown)
    )

    
iface.launch(
    server_name=SERVER_NAME,
    server_port=SERVER_PORT,
    share=False
)