# app.py

import json
import torch
from transformers import pipeline, AutoTokenizer
import gradio as gr

# Importaciones modulares
from utils import format_as_json
from config import (
    MODEL_NAME, MIN_LENGTH, MAX_LENGTH, 
    NUM_BEAMS, DO_SAMPLE, MAX_INPUT_LENGTH,
    SERVER_NAME, SERVER_PORT,
    INCIDENT_CLASSIFICATIONS, TRANSLATION_MODEL_NAME
)
from ui_config import (
    CUSTOM_THEME, CUSTOM_CSS, create_animated_header,
    generate_rich_summary_markdown, create_system_info_card
)

# --- CONFIGURACIÓN DEL MODELO ---
def setup_models():
    """Configura y retorna los modelos cargados"""
    device = 0 if torch.cuda.is_available() else -1
    print(f"Usando dispositivo: {'GPU (CUDA)' if device != -1 else 'CPU'}")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    summarizer = pipeline(
        "summarization", 
        model=MODEL_NAME, 
        tokenizer=tokenizer,
        device=device,
        return_text=False 
    )
    
    translator = pipeline(
        "translation",
        model=TRANSLATION_MODEL_NAME,
        device=device
    )
    
    return device, tokenizer, summarizer, translator

# --- LÓGICA DE PROCESAMIENTO ---
def classify_incident_type(text):
    """Clasifica el tipo de incidente basándose en palabras clave"""
    text_lower = text.lower()
    for category, keywords in INCIDENT_CLASSIFICATIONS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "General/Otros"

def create_error_response(error_msg):
    """Crea una respuesta de error estandarizada"""
    from ui_config import create_cyber_card
    error_output = json.dumps({"status": "error", "message": error_msg}, indent=4)
    error_card = create_cyber_card(
        content=f"<div class='error-message'><h3>❌ ERROR</h3><p>{error_msg}</p></div>",
        title="ERROR DEL SISTEMA",
        icon="🚨",
        glow_color="#ff4444"
    )
    return error_output, error_card

def summarize_incident_and_process(text_input, tokenizer, summarizer, translator):
    """
    Procesa el texto del incidente: resume, traduce y genera salidas
    """
    if not text_input or len(text_input.split()) < MIN_LENGTH:
        error_msg = f"El texto es demasiado corto. Mínimo {MIN_LENGTH} palabras requeridas."
        return create_error_response(error_msg)
    
    try:
        # 1. Generación de Resumen
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
        
        # 2. Traducción a español
        translation_result = translator(bilingual_summary, max_length=260)
        summary_text_output = translation_result[0]['translation_text']
        
        # 3. Clasificación y formateo
        incident_type = classify_incident_type(text_input)
        confidence_score_estimate = 90.0 
        
        model_metadata = {
            'model_name': MODEL_NAME, 
            'translation_model': TRANSLATION_MODEL_NAME, 
            'min_length': MIN_LENGTH, 
            'max_length': MAX_LENGTH
        }
        
        json_output = format_as_json(
            summary_text_output, 
            text_input, 
            incident_type,
            model_metadata,
            confidence=confidence_score_estimate
        )
        
        # 4. Generar salida visual
        data_dict = json.loads(json_output)
        rich_markdown_output = generate_rich_summary_markdown(data_dict)
        
        return json_output, rich_markdown_output
        
    except Exception as e:
        error_msg = f"Error en el procesamiento: {str(e)}"
        return create_error_response(error_msg)

# --- CONFIGURACIÓN DE LA INTERFAZ ---
def create_interface(device, tokenizer, summarizer, translator):
    """Crea y configura la interfaz de Gradio"""
    
    with gr.Blocks(theme=CUSTOM_THEME, css=CUSTOM_CSS, 
                  title="🤖 CyberAnalyzer - Sistema de Análisis de Incidentes") as iface:
        
        # Header animado
        gr.HTML(create_animated_header())
        
        # Panel principal
        with gr.Row():
            with gr.Column(scale=3):
                gr.Markdown("### 🎯 INGRESE EL TEXTO DEL INCIDENTE")
                text_input = gr.Textbox(
                    lines=10, 
                    label="",
                    placeholder=f"📋 Pegue aquí el historial completo del incidente (mínimo {MIN_LENGTH} palabras requeridas)...",
                    show_label=False
                )
            with gr.Column(scale=1):
                system_info = create_system_info_card(device, MODEL_NAME, TRANSLATION_MODEL_NAME)
                gr.HTML(system_info)
        
        # Botón de acción
        with gr.Row():
            analyze_btn = gr.Button(
                "🚀 INICIAR ANÁLISIS AUTOMÁTICO", 
                variant="primary", 
                scale=1
            )
        
        # Pestañas de resultados
        with gr.Tabs():
            with gr.TabItem("📊 PANEL DE ANÁLISIS"):
                rich_output = gr.HTML(
                    "<div class='waiting-message'>⏳ El sistema está listo. Ingrese un incidente y haga clic en 'INICIAR ANÁLISIS AUTOMÁTICO'</div>"
                )
            
            with gr.TabItem("⚙️ DATOS TÉCNICOS (JSON)"):
                json_output = gr.Textbox(
                    lines=10, 
                    label="SALIDA JSON CRUDA",
                    show_label=True
                )
        
        # Conectar el botón con la función de procesamiento
        analyze_btn.click(
            fn=lambda text: summarize_incident_and_process(text, tokenizer, summarizer, translator),
            inputs=text_input,
            outputs=[json_output, rich_output]
        )
    
    return iface

# --- INICIALIZACIÓN ---
def main():
    """Función principal de la aplicación"""
    print("🚀 Iniciando Microagente de Resumen de Incidentes...")
    
    # Configurar modelos
    device, tokenizer, summarizer, translator = setup_models()
    
    # Crear interfaz
    iface = create_interface(device, tokenizer, summarizer, translator)
    
    # Lanzar aplicación
    print(f"🌐 Servidor iniciado en: {SERVER_NAME}:{SERVER_PORT}")
    iface.launch(
        server_name=SERVER_NAME,
        server_port=SERVER_PORT,
        share=False
    )

if __name__ == "__main__":
    main()