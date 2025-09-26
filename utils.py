# utils.py
import json
import re
from config import REGEX_PATTERNS 

def extract_entities(text):
    """
    Extrae entidades clave como servidores, IPs, incident_id y tiempos del texto.
    """
    entities = {}

    # Expresión regular para encontrar recursos (usa patrón de config)
    server_matches = re.findall(REGEX_PATTERNS['resources'], text, re.IGNORECASE)
    servers = list(set([match[0] if isinstance(match, tuple) else match for match in server_matches]))
    if servers:
        entities['resources'] = servers 

    # Expresión regular para encontrar IPs (usa patrón de config)
    ip_matches = re.findall(REGEX_PATTERNS['ips'], text)
    if ip_matches:
        entities['ips'] = list(set(ip_matches))

    # Expresión regular para encontrar IDs de incidentes (usa patrón de config)
    id_matches = re.findall(REGEX_PATTERNS['incident_id'], text, re.IGNORECASE)
    if id_matches:
        entities['incident_id'] = list(set(id_matches))

    # Expresión regular para encontrar horarios (usa patrón de config)
    time_matches = re.findall(REGEX_PATTERNS['times'], text, re.IGNORECASE)
    if time_matches:
        entities['times'] = list(set(time_matches))

    # Conteo de entidades
    entity_counts = {k: len(v) for k, v in entities.items()}
    
    return entities, entity_counts

def format_as_json(summary_text, original_text, incident_type="N/A", model_metadata={}):
    """
    Formatea el resumen, el texto original y las entidades en una cadena JSON
    y agrega métricas de conteo de palabras.
    """
    extracted_entities, entity_counts = extract_entities(original_text)
    
    # Métricas de conteo
    original_words_count = len(original_text.split())
    summary_words_count = len(summary_text.split())
    
    # Porcentaje de disminución
    if original_words_count > 0:
        reduction_percentage = round((1 - (summary_words_count / original_words_count)) * 100, 2)
    else:
        reduction_percentage = 0
    
    # Estructura de la metadata
    metadata = {
        "model": model_metadata.get('model_name', 'N/A'),
        "min_words": model_metadata.get('min_length', 'N/A'),
        "max_words": model_metadata.get('max_length', 'N/A'),
        "original_words_count": original_words_count,
        "summary_words_count": summary_words_count,
        "reduction_percentage": reduction_percentage,
        "entity_counts": entity_counts
    }
    
    output = {
        "status": "success",
        "incident_type": incident_type,
        "summary": summary_text,
        "entities": extracted_entities,
        "metadata": metadata
    }

    return json.dumps(output, indent=4, ensure_ascii=False)