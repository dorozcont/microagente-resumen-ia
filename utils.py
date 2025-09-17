# utils.py
import json
import re

def extract_entities(text):
    """
    Extrae entidades clave como IDs, servidores y fechas del texto.
    """
    entities = {}

    # Expresión regular para encontrar nombres de servidores/servicios (ej. "Postgres-DB-01")
    server_matches = re.findall(r'(\b[A-Z0-9-]{3,}-\b[A-Z0-9-]{3,}|srv-[0-9a-zA-Z-]+)', text, re.IGNORECASE)
    if server_matches:
        entities['servers'] = list(set(server_matches))

    # Expresión regular para encontrar IDs de incidentes (ej. "INC-7890", "#4321")
    id_matches = re.findall(r'(INC-[0-9]{4}|#[0-9]{4})', text, re.IGNORECASE)
    if id_matches:
        entities['incident_id'] = list(set(id_matches))

    # Expresión regular para encontrar horarios (ej. "10:30 a.m.", "15:45")
    time_matches = re.findall(r'(\d{1,2}:\d{2}\s?(?:a\.m\.|p\.m\.)?)', text, re.IGNORECASE)
    if time_matches:
        entities['times'] = list(set(time_matches))

    return entities

def format_as_json(summary_text, original_text, incident_type="N/A"):
    """
    Formatea el resumen, el texto original y las entidades en una cadena JSON.
    """
    extracted_entities = extract_entities(original_text)

    output = {
        "original_text": original_text,
        "summary": summary_text,
        "status": "success",
        "incident_type": incident_type,
        "entities": extracted_entities
    }

    return json.dumps(output, indent=4, ensure_ascii=False)