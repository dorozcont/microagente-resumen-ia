# utils.py
import json
import re
from datetime import datetime
from config import REGEX_PATTERNS

def preprocess_text(text):
    """Preprocesa el texto para mejorar la calidad del resumen"""
    text = text.strip()
    text = ' '.join(text.split())  # Normalizar espacios
    return text

def chunk_text(text, max_tokens=800):
    """Divide texto muy largo en chunks manejables"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        word_tokens = len(word) // 4 + 1  # Estimación mejorada
        
        if current_length + word_tokens > max_tokens:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = word_tokens
        else:
            current_chunk.append(word)
            current_length += word_tokens
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

def extract_entities(text):
    """Extrae entidades usando patrones configurados"""
    entities = {
        'servers': [], 'incident_ids': [], 'times': [],
        'dates': [], 'ips': [], 'applications': []
    }

    # Extracción usando patrones configurados
    for entity_type, patterns in REGEX_PATTERNS.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    # Para grupos de captura, tomar el primer grupo no vacío
                    valid_matches = [m for m in match if m and str(m).strip()]
                    if valid_matches:
                        entities[entity_type].extend(valid_matches)
                else:
                    entities[entity_type].append(match)

    # Eliminar duplicados y vacíos
    for key in entities:
        entities[key] = list(set([item for item in entities[key] if item and str(item).strip()]))
    
    return entities

def format_as_json(summary_text, original_text, incident_type="N/A", error_message=None):
    """Formatea la respuesta en JSON"""
    extracted_entities = extract_entities(original_text)
    
    metadata = {
        "processed_at": datetime.now().isoformat(),
        "original_word_count": len(original_text.split()),
        "summary_word_count": len(summary_text.split()) if summary_text else 0,
        "entities_count": {key: len(value) for key, value in extracted_entities.items()}
    }

    output = {
        "status": "error" if error_message else "success",
        "incident_type": incident_type,
        "summary": summary_text,
        "original_text_preview": original_text[:500] + "..." if len(original_text) > 500 else original_text,
        "entities": extracted_entities,
        "metadata": metadata
    }
    
    if error_message:
        output["error_message"] = error_message

    return json.dumps(output, indent=2, ensure_ascii=False)