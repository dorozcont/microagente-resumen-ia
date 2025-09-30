# utils.py
import json
import re
from config import REGEX_PATTERNS 

def extract_entities(text):
    """
    Extrae entidades clave: recursos, IPs e IDs, utilizando patrones flexibles.
    """
    entities = {}
    
    # Conjuntos para acumular coincidencias únicas
    resources = set()
    ips_set = set()
    incident_ids_set = set()

    # 1. Extracción de Key-Value (Hostname, IP, OS, etc.) 
    kv_matches = re.findall(r'(\b(?:Hostname|Host|Server|OS|IP|Usuario|APP|DB|ID|Ticket)\s*:\s*([a-zA-Z0-9.\-/]{2,}))', text, re.IGNORECASE)
    
    # Procesa coincidencias Key-Value
    for match in kv_matches:
        key = match[0].split(':')[0].strip()
        value = match[1].strip()
        
        if key.upper() == 'IP':
            ips_set.add(value)
        elif key.upper() in ['HOSTNAME', 'HOST', 'SERVER', 'OS', 'APP', 'DB']:
            resources.add(value)
        elif key.upper() in ['ID', 'TICKET']:
             incident_ids_set.add(value)
        else:
             resources.add(value)

    # 2. Extracción de RECURSOS GENERALES (¡CLAVE PARA EL TEXTO 2!)
    # Captura nombres técnicos comunes como srv-app-03, router-main-a, FW-EAST-01, API-AUTH-CORE
    # Este regex busca cadenas separadas por guiones o números con prefijos comunes.
    general_resource_matches = re.findall(r'(\b[a-z]{2,5}-[a-z]{2,5}-\d{2,5}|\b[A-Z]{3,}-\b[A-Z0-9-]{2,})', text, re.IGNORECASE)
    resources.update(general_resource_matches)

    # 3. Extracción de IPs (usando patrón de config.py)
    # Se asume que REGEX_PATTERNS['ips'] captura IPv4 válidas.
    ip_matches = re.findall(REGEX_PATTERNS['ips'], text) 
    ips_set.update(ip_matches)

    # 4. Extracción de IDs de incidentes (usando patrón de config.py)
    id_matches = re.findall(REGEX_PATTERNS['incident_id'], text, re.IGNORECASE)
    incident_ids_set.update(id_matches)

    # Llenar el diccionario de salida SOLO si el conjunto no está vacío.
    # El código de app.py debe usar .get(key, []) para evitar KeyErrors.
    if resources: entities['resources'] = [str(r) for r in resources] # Fuerza a STR
    if ips_set: entities['ips'] = [str(ip) for ip in ips_set]        # Fuerza a STR
    if incident_ids_set: entities['incident_id'] = [str(i) for i in incident_ids_set] # Fuerza a STR

    # Conteo de entidades (mantenido)
    entity_counts = {k: len(v) for k, v in entities.items()}
    
    return entities, entity_counts

def format_as_json(summary_text, original_text, incident_type="N/A", model_metadata={}, confidence=None):
    """
    Formatea el resumen, el texto original y las entidades en una cadena JSON
    y agrega métricas de conteo de palabras y confianza. (Mantenido)
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
        "confidence_score": f"{confidence:.2f}%" if confidence is not None else "N/A",
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