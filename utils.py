# utils.py
import json
import re
from config import REGEX_PATTERNS 

def extract_entities(text):
    """
    Extrae entidades clave: recursos (servidores, Hostname, OS) e IPs.
    """
    entities = {}
    
    # 1. Extracción de Recursos (Hostnames, Servidores, OS)
    # Patrón mejorado para capturar nombres después de etiquetas comunes (Hostname: X, OS: Y)
    # y para la detección general de recursos.
    # Usamos re.findall para buscar la expresión en el texto.
    
    # Intenta capturar Hostname/OS/Apache de forma explícita
    explicit_matches = re.findall(r'(Hostname:\s*([a-zA-Z0-9-]+)|OS:\s*([a-zA-Z0-9\s-]+)|(\bntapachedemo\b|\bCentOS\s+9\b))', text, re.IGNORECASE)
    
    # Intenta capturar recursos generales basados en el REGEX_PATTERNS['resources']
    general_resource_matches = re.findall(REGEX_PATTERNS['resources'], text, re.IGNORECASE)

    # Aplanar y consolidar resultados
    all_resources = set()
    
    # Consolidar coincidencias explícitas (captura de grupos 2, 3 o 4)
    for match in explicit_matches:
        if match[1]: all_resources.add(match[1].strip()) # Hostname
        if match[2]: all_resources.add(match[2].strip()) # OS
        if match[3]: all_resources.add(match[3].strip()) # Valores directos
        
    # Consolidar coincidencias generales (aplanando las tuplas del regex de config.py)
    for match in general_resource_matches:
        resource_name = match[0] if isinstance(match, tuple) else match
        # Evitar agregar cadenas vacías o cortas
        if resource_name and len(resource_name.strip()) > 2:
            all_resources.add(resource_name.strip())

    if all_resources:
        entities['resources'] = list(all_resources) 

    # 2. Expresión regular para encontrar IPs (usa patrón de config)
    ip_matches = re.findall(REGEX_PATTERNS['ips'], text)
    if ip_matches:
        entities['ips'] = list(set(ip_matches))

    # 3. Expresión regular para encontrar IDs de incidentes (usa patrón de config)
    id_matches = re.findall(REGEX_PATTERNS['incident_id'], text, re.IGNORECASE)
    if id_matches:
        entities['incident_id'] = list(set(id_matches))

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