# utils.py
import json
import re
from config import REGEX_PATTERNS 

def extract_entities(text):
    """
    Extrae entidades clave: recursos, IPs e IDs, utilizando patrones flexibles.
    """
    entities = {}
    
    # 1. Extracción de Key-Value (Hostname, IP, OS, etc.)
    # Patrón: (Key: Value) - Captura claves comunes seguidas de dos puntos y el valor.
    # Mejora la detección de 'Hostname: X' y 'IP: Y' de forma genérica.
    kv_matches = re.findall(r'(\b(?:Hostname|Host|Server|OS|IP|Usuario|APP|DB)\s*:\s*([a-zA-Z0-9.\-/]{3,}))', text, re.IGNORECASE)
    
    # 2. Extracción de IPs
    ip_matches = re.findall(REGEX_PATTERNS['ips'], text) # Usa el patrón simple y robusto de config.py
    
    # Consolidación de recursos (hostnames, OS, etc.)
    resources = set()
    ips_set = set(ip_matches)

    for match in kv_matches:
        key = match[0].split(':')[0].strip()
        value = match[1].strip()
        
        if key.upper() == 'IP':
            ips_set.add(value)
        elif key.upper() in ['HOSTNAME', 'HOST', 'SERVER', 'OS', 'APP', 'DB']:
            resources.add(value)
        else:
             # Incluir el valor como recurso si no es IP
             resources.add(value)
             
    # 3. Extracción de IDs de incidentes (usa patrón de config)
    id_matches = re.findall(REGEX_PATTERNS['incident_id'], text, re.IGNORECASE)

    # Llenar el diccionario de salida
    if resources: entities['resources'] = list(resources) 
    if ips_set: entities['ips'] = list(ips_set)
    if id_matches: entities['incident_id'] = list(set(id_matches))

    # Conteo de entidades
    entity_counts = {k: len(v) for k, v in entities.items()}
    
    return entities, entity_counts

def format_as_json(summary_text, original_text, incident_type="N/A", model_metadata={}, confidence=None):
    """
    Formatea el resumen, el texto original y las entidades en una cadena JSON
    y agrega métricas de conteo de palabras y confianza.
    """
    extracted_entities, entity_counts = extract_entities(original_text)
    
    # Métricas de conteo
    original_words_count = len(original_text.split())
    summary_words_count = len(summary_text.split())
    
    # Porcentaje de disminución
    reduction_percentage = round((1 - (summary_words_count / original_words_count)) * 100, 2) if original_words_count > 0 else 0
    
    # Estructura de la metadata
    metadata = {
        "model": model_metadata.get('model_name', 'N/A'),
        "min_words": model_metadata.get('min_length', 'N/A'),
        "max_words": model_metadata.get('max_length', 'N/A'),
        "confidence_score": f"{confidence:.2f}%" if confidence is not None else "N/A", # Agregando la confianza
        "original_words_count": original_words_count,
        "summary_words_count": summary_words_count,
        "reduction_percentage": reduction_percentage,
        "entity_counts": entity_counts
    }
    
    output = {
        "status": "success",
        "incident_type": incident_type,
        "summary": summary_text,
        "entities": extracted_entities, # Ya no incluye 'times' porque no se extrajo
        "metadata": metadata
    }

    return json.dumps(output, indent=4, ensure_ascii=False)