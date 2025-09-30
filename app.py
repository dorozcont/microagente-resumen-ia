# app.py - Versión Futurista (Compatible con Docker)

import json
import time
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

CUSTOM_COLOR = "#C9F70E"  # Verde Limón

# Tema simplificado y compatible
CUSTOM_THEME = gr.themes.Default(
    primary_hue="green",
    neutral_hue="slate"
).set(
    # Configuración básica compatible
    button_primary_background_fill=CUSTOM_COLOR,
    button_primary_text_color="#000000",
    button_primary_border_color=CUSTOM_COLOR,
)

def create_animated_header():
    """Crea un header animado con efecto de partículas digitales"""
    return f"""
    <div class="header-container">
        <div class="digital-particles"></div>
        <div class="header-content">
            <h1 class="main-title">🤖 MICROAGENTE DE ANÁLISIS DE INCIDENTES</h1>
            <div class="subtitle-container">
                <div class="scanning-bar"></div>
                <p class="subtitle">Sistema de Inteligencia Artificial para Análisis y Resumen de Incidentes de TI</p>
            </div>
        </div>
        <div class="status-indicator">
            <div class="pulse-dot"></div>
            <span>SISTEMA ACTIVO</span>
        </div>
    </div>
    """

def create_cyber_card(content, title=None, icon=None, glow_color=CUSTOM_COLOR):
    """Crea una tarjeta con estilo cyberpunk"""
    icon_html = f"<span class='card-icon'>{icon}</span>" if icon else ""
    title_html = f"<h3 class='card-title'>{title}</h3>" if title else ""
    
    return f"""
    <div class="cyber-card" style='--glow-color: {glow_color}'>
        <div class="card-header">
            {icon_html}
            {title_html}
        </div>
        <div class="card-content">
            {content}
        </div>
        <div class="card-glow"></div>
    </div>
    """

def generate_rich_summary_markdown(data):
    """
    Versión mejorada del resumen con elementos visuales futuristas
    """
    icon_map = {
        "Software/Aplicación": "💻", "Redes/Conectividad": "🌐", 
        "Infraestructura/Sistemas": "💾", "Base de datos": "🗄️", 
        "Seguridad": "🔒", "General/Otros": "📜"
    }
    
    summary = data.get('summary', 'Resumen no disponible.')
    incident_type = data.get('incident_type', 'N/A')
    entities = data.get('entities', {})
    metrics = data.get('metadata', {})
    
    confidence = metrics.get('confidence_score', 'N/A')
    original_words = metrics.get('original_words_count', 'N/A')
    summary_words = metrics.get('summary_words_count', 'N/A')
    reduction_percentage = metrics.get('reduction_percentage', 'N/A')
    
    # Header principal con animación
    rich_md = create_cyber_card(
        content=f"""
        <div class="incident-header">
            <div class="type-badge">
                {icon_map.get(incident_type, '📜')} {incident_type}
            </div>
            <div class="confidence-meter">
                <div class="meter-label">CONFIANZA DEL SISTEMA</div>
                <div class="meter-bar">
                    <div class="meter-fill" style="width: {confidence.replace('%', '') if '%' in str(confidence) else '90'}%"></div>
                </div>
                <div class="meter-value">{confidence}</div>
            </div>
        </div>
        """,
        title="ANÁLISIS EJECUTIVO",
        icon="📊"
    )
    
    # Resumen del incidente
    rich_md += create_cyber_card(
        content=f"""
        <div class="summary-content">
            <div class="summary-text">{summary}</div>
        </div>
        """,
        title="RESUMEN DEL INCIDENTE",
        icon="📝"
    )
    
    # Entidades detectadas
    entity_content = ""
    resources = entities.get('resources', [])
    ips = entities.get('ips', [])
    ids = entities.get('incident_id', [])
    
    if resources or ips or ids:
        if resources:
            entity_content += f"""
            <div class="entity-section">
                <h4>💾 RECURSOS/HOSTNAMES</h4>
                <div class="entity-tags">
                    {''.join([f'<span class="entity-tag resource">{str(r)}</span>' for r in resources])}
                </div>
            </div>
            """
        
        if ips:
            entity_content += f"""
            <div class="entity-section">
                <h4>🌐 DIRECCIONES IP</h4>
                <div class="entity-tags">
                    {''.join([f'<span class="entity-tag ip">{str(ip)}</span>' for ip in ips])}
                </div>
            </div>
            """
        
        if ids:
            entity_content += f"""
            <div class="entity-section">
                <h4>🏷️ IDS DE INCIDENTE</h4>
                <div class="entity-tags">
                    {''.join([f'<span class="entity-tag id">{str(i)}</span>' for i in ids])}
                </div>
            </div>
            """
    else:
        entity_content = "<div class='no-entities'>⚠️ No se detectaron entidades clave</div>"
    
    rich_md += create_cyber_card(
        content=entity_content,
        title="ENTIDADES DETECTADAS",
        icon="🔗"
    )
    
    # Métricas de procesamiento
    metrics_content = f"""
    <div class="metrics-grid">
        <div class="metric-item">
            <div class="metric-value">{original_words}</div>
            <div class="metric-label">PALABRAS ORIGINALES</div>
        </div>
        <div class="metric-item">
            <div class="metric-value">{summary_words}</div>
            <div class="metric-label">PALABRAS RESUMEN</div>
        </div>
        <div class="metric-item highlight">
            <div class="metric-value">{reduction_percentage}%</div>
            <div class="metric-label">REDUCCIÓN</div>
        </div>
    </div>
    """
    
    rich_md += create_cyber_card(
        content=metrics_content,
        title="MÉTRICAS DE PROCESAMIENTO",
        icon="📈"
    )
    
    return rich_md

# CSS personalizado para efectos futuristas
CUSTOM_CSS = f"""
<style>
    /* Animaciones y efectos globales */
    @keyframes glow {{
        0%, 100% {{ box-shadow: 0 0 5px {CUSTOM_COLOR}40; }}
        50% {{ box-shadow: 0 0 20px {CUSTOM_COLOR}80, 0 0 30px {CUSTOM_COLOR}40; }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.7; }}
    }}
    
    @keyframes scan {{
        0% {{ transform: translateX(-100%); }}
        100% {{ transform: translateX(400%); }}
    }}
    
    @keyframes float {{
        0%, 100% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-5px); }}
    }}
    
    /* Fondo general oscuro */
    .gradio-container {{
        background: #000000 !important;
        color: #FFFFFF !important;
    }}
    
    /* Header animado */
    .header-container {{
        position: relative;
        padding: 2rem;
        background: linear-gradient(135deg, #000000 0%, #1A1A1A 100%);
        border-bottom: 1px solid {CUSTOM_COLOR}40;
        overflow: hidden;
        margin-bottom: 1rem;
    }}
    
    .digital-particles::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: 
            radial-gradient(circle at 20% 30%, {CUSTOM_COLOR}10 2px, transparent 2px),
            radial-gradient(circle at 80% 70%, {CUSTOM_COLOR}10 1px, transparent 1px);
        background-size: 50px 50px, 30px 30px;
        animation: float 20s infinite linear;
    }}
    
    .main-title {{
        font-family: 'Courier New', monospace;
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(45deg, #FFFFFF, {CUSTOM_COLOR});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }}
    
    .subtitle-container {{
        position: relative;
        overflow: hidden;
        margin-top: 1rem;
    }}
    
    .scanning-bar {{
        position: absolute;
        top: 0;
        left: 0;
        height: 100%;
        width: 20%;
        background: linear-gradient(90deg, transparent, {CUSTOM_COLOR}80, transparent);
        animation: scan 3s infinite linear;
    }}
    
    .subtitle {{
        color: #CCCCCC;
        text-align: center;
        font-size: 1rem;
        margin: 0;
        padding: 0.5rem;
        position: relative;
    }}
    
    .status-indicator {{
        position: absolute;
        top: 1rem;
        right: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: {CUSTOM_COLOR};
        font-family: 'Courier New', monospace;
        font-size: 0.8em;
    }}
    
    .pulse-dot {{
        width: 8px;
        height: 8px;
        background: {CUSTOM_COLOR};
        border-radius: 50%;
        animation: pulse 2s infinite;
    }}
    
    /* Tarjetas cyberpunk */
    .cyber-card {{
        position: relative;
        background: #1A1A1A;
        border: 1px solid {CUSTOM_COLOR}40;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        overflow: hidden;
        transition: all 0.3s ease;
    }}
    
    .cyber-card:hover {{
        border-color: {CUSTOM_COLOR}80;
        transform: translateY(-2px);
        animation: glow 2s infinite;
    }}
    
    .card-glow {{
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--glow-color), transparent);
        opacity: 0;
        transition: opacity 0.3s ease;
    }}
    
    .cyber-card:hover .card-glow {{
        opacity: 1;
    }}
    
    .card-header {{
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid {CUSTOM_COLOR}20;
        padding-bottom: 0.5rem;
    }}
    
    .card-icon {{
        font-size: 1.2em;
    }}
    
    .card-title {{
        color: {CUSTOM_COLOR};
        font-family: 'Courier New', monospace;
        font-size: 1em;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    /* Elementos de contenido */
    .incident-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }}
    
    .type-badge {{
        background: {CUSTOM_COLOR}20;
        border: 1px solid {CUSTOM_COLOR}40;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        color: {CUSTOM_COLOR};
        font-weight: bold;
        font-size: 0.9em;
    }}
    
    .confidence-meter {{
        flex: 1;
        min-width: 200px;
    }}
    
    .meter-label {{
        font-size: 0.8em;
        color: #CCCCCC;
        margin-bottom: 0.25rem;
    }}
    
    .meter-bar {{
        width: 100%;
        height: 6px;
        background: #333333;
        border-radius: 3px;
        overflow: hidden;
    }}
    
    .meter-fill {{
        height: 100%;
        background: linear-gradient(90deg, {CUSTOM_COLOR}80, {CUSTOM_COLOR});
        border-radius: 3px;
        transition: width 1s ease-in-out;
    }}
    
    .meter-value {{
        text-align: right;
        font-size: 0.9em;
        color: {CUSTOM_COLOR};
        margin-top: 0.25rem;
    }}
    
    .summary-content {{
        line-height: 1.6;
        color: #E0E0E0;
    }}
    
    .summary-text {{
        font-size: 0.95em;
    }}
    
    .entity-tags {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.5rem;
    }}
    
    .entity-tag {{
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8em;
        font-family: 'Courier New', monospace;
    }}
    
    .entity-tag.resource {{
        background: {CUSTOM_COLOR}20;
        color: {CUSTOM_COLOR};
        border: 1px solid {CUSTOM_COLOR}40;
    }}
    
    .entity-tag.ip {{
        background: #2196F320;
        color: #2196F3;
        border: 1px solid #2196F340;
    }}
    
    .entity-tag.id {{
        background: #FF980020;
        color: #FF9800;
        border: 1px solid #FF980040;
    }}
    
    .metrics-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 1rem;
        margin-top: 1rem;
    }}
    
    .metric-item {{
        text-align: center;
        padding: 1rem;
        background: #252525;
        border-radius: 6px;
        border: 1px solid #333333;
        transition: all 0.3s ease;
    }}
    
    .metric-item:hover {{
        border-color: {CUSTOM_COLOR}60;
        transform: scale(1.05);
    }}
    
    .metric-item.highlight {{
        background: {CUSTOM_COLOR}15;
        border-color: {CUSTOM_COLOR}40;
    }}
    
    .metric-value {{
        font-size: 1.3em;
        font-weight: bold;
        color: {CUSTOM_COLOR};
        margin-bottom: 0.25rem;
    }}
    
    .metric-label {{
        font-size: 0.75em;
        color: #CCCCCC;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    /* Estilos para componentes de Gradio */
    .panel {{
        background: #1A1A1A !important;
        border: 1px solid #333333 !important;
    }}
    
    .system-stats {{
        font-size: 0.85em;
    }}
    
    .stat-item {{
        margin-bottom: 0.8rem;
        padding-bottom: 0.8rem;
        border-bottom: 1px solid #333333;
    }}
    
    .stat-item:last-child {{
        margin-bottom: 0;
        padding-bottom: 0;
        border-bottom: none;
    }}
    
    .gpu-active {{
        color: {CUSTOM_COLOR};
        font-weight: bold;
    }}
    
    .cpu-active {{
        color: #FF9800;
        font-weight: bold;
    }}
    
    .waiting-message {{
        text-align: center;
        padding: 3rem;
        color: #666666;
        font-style: italic;
    }}
    
    .error-message {{
        text-align: center;
        padding: 2rem;
    }}
    
    /* Ajustes para inputs y outputs */
    textarea, input {{
        background: #1A1A1A !important;
        border: 1px solid #333333 !important;
        color: #FFFFFF !important;
    }}
    
    .tabs {{
        border: 1px solid #333333 !important;
    }}
    
    .tab-nav {{
        background: #1A1A1A !important;
    }}
    
    .tab-nav button {{
        color: #CCCCCC !important;
    }}
    
    .tab-nav button.selected {{
        color: {CUSTOM_COLOR} !important;
        border-bottom: 2px solid {CUSTOM_COLOR} !important;
    }}
</style>
"""

# --- CONFIGURACIÓN DEL MODELO ---
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

translator = pipeline(
    "translation",
    model=TRANSLATION_MODEL_NAME,
    device=device
)

def classify_incident_type(text):
    text_lower = text.lower()
    for category, keywords in INCIDENT_CLASSIFICATIONS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "General/Otros"

def summarize_incident_and_process(text_input):
    if not text_input or len(text_input.split()) < MIN_LENGTH:
        error_msg = f"El texto es demasiado corto para generar un resumen significativo. Por favor, ingrese al menos {MIN_LENGTH} palabras."
        error_card = create_cyber_card(
            content=f"<div class='error-message'><h3>❌ ERROR</h3><p>{error_msg}</p></div>",
            title="ERROR DEL SISTEMA",
            icon="🚨",
            glow_color="#ff4444"
        )
        return json.dumps({"status": "error", "message": error_msg}, indent=4), error_card
    
    # Procesamiento del resumen
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
    
    translation_result = translator(bilingual_summary, max_length=260)
    summary_text_output = translation_result[0]['translation_text']
    
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
    
    data_dict = json.loads(json_output)
    rich_markdown_output = generate_rich_summary_markdown(data_dict)
    
    return json_output, rich_markdown_output

# --- INTERFAZ GRADIO COMPATIBLE ---
with gr.Blocks(theme=CUSTOM_THEME, css=CUSTOM_CSS, title="🤖 CyberAnalyzer - Sistema de Análisis de Incidentes") as iface:
    
    # Header animado
    gr.HTML(create_animated_header())
    
    # Panel de información del sistema
    with gr.Row():
        with gr.Column(scale=3):
            gr.Markdown("### 🎯 INGRESE EL TEXTO DEL INCIDENTE")
            text_input = gr.Textbox(
                lines=INPUT_LINES, 
                label="",
                placeholder=f"📋 Pegue aquí el historial completo del incidente (mínimo {MIN_LENGTH} palabras requeridas)...",
                show_label=False
            )
        with gr.Column(scale=1):
            system_info_html = create_cyber_card(
                content=f"""
                <div class="system-stats">
                    <div class="stat-item">
                        <strong>Modelo de Resumen:</strong><br>
                        <code>{MODEL_NAME.split('/')[-1]}</code>
                    </div>
                    <div class="stat-item">
                        <strong>Modelo de Traducción:</strong><br>
                        <code>{TRANSLATION_MODEL_NAME.split('/')[-1]}</code>
                    </div>
                    <div class="stat-item">
                        <strong>Dispositivo:</strong><br>
                        <span class="{'gpu-active' if device != -1 else 'cpu-active'}">
                            {'⚡ GPU (CUDA)' if device != -1 else '💻 CPU'}
                        </span>
                    </div>
                </div>
                """,
                title="ESTADO DEL SISTEMA",
                icon="🖥️"
            )
            gr.HTML(system_info_html)
    
    # Botón de acción principal
    with gr.Row():
        analyze_btn = gr.Button(
            "🚀 INICIAR ANÁLISIS AUTOMÁTICO", 
            variant="primary", 
            scale=1
        )
    
    # Pestañas de resultados
    with gr.Tabs():
        with gr.TabItem("📊 PANEL DE ANÁLISIS"):
            rich_output_markdown = gr.HTML(
                "<div class='waiting-message'>⏳ El sistema está listo. Ingrese un incidente y haga clic en 'INICIAR ANÁLISIS AUTOMÁTICO'</div>"
            )
        
        with gr.TabItem("⚙️ DATOS TÉCNICOS (JSON)"):
            json_output_textbox = gr.Textbox(
                lines=OUTPUT_LINES, 
                label="SALIDA JSON CRUDA",
                show_label=True
            )
    
    # Conectar el botón
    analyze_btn.click(
        fn=summarize_incident_and_process, 
        inputs=text_input, 
        outputs=[json_output_textbox, rich_output_markdown]
    )

iface.launch(
    server_name=SERVER_NAME,
    server_port=SERVER_PORT,
    share=False
)