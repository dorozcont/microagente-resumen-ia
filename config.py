# config.py
"""
Configuración centralizada del microagente
"""

# Configuración del modelo
MODEL_CONFIG = {
    "name": "facebook/bart-large-cnn",
    "max_input_length": 1024,
    "max_summary_length": 150,
    "min_summary_length": 50,
    "num_beams": 4,
    "length_penalty": 2.0,
    "no_repeat_ngram_size": 3,
    "do_sample": False
}

# Palabras clave para clasificación
INCIDENT_KEYWORDS = {
    "Redes/Infraestructura": [
        "red", "servidor", "router", "switch", "conexión", "network", 
        "server", "conectividad", "ancho de banda", "latencia", "dns", "dhcp"
    ],
    "Base de datos": [
        "base de datos", "sql", "postgres", "mongo", "mysql", "database", 
        "db", "query", "consulta", "índice", "tabla", "transacción", "backup"
    ],
    "Seguridad": [
        "seguridad", "acceso", "vulnerabilidad", "phishing", "malware", 
        "firewall", "security", "autenticación", "autorización", "brecha",
        "intruso", "ataque", "criptografía"
    ],
    "Software/Aplicación": [
        "aplicación", "software", "bug", "código", "app", "programa", 
        "error", "feature", "release", "despliegue", "api", "microservicio"
    ]
}

# Configuración de la aplicación
APP_CONFIG = {
    "min_words": 30,
    "max_words": 2000,
    "chunk_size": 800,
    "language": "es",
    "prompt_template": "Resume el siguiente incidente de TI en español, destacando: problema inicial, acciones tomadas, causa raíz y resultado final:\n\n{}"
}

# Configuración de expresiones regulares para entidades
REGEX_PATTERNS = {
    "servers": [
        r'\b(srv-[0-9a-zA-Z-]+)',
        r'\b([A-Z]{2,}-\d{2,}-\w+)',
        r'\b(\w+-\w+-\d+)'
    ],
    "incident_ids": [
        r'(INC-\d{4,})',
        r'(#\d{4,})',
        r'(incidente\s+[Nn]°?\s*(\d+))'
    ],
    "times": [r'(\d{1,2}:\d{2}\s?(?:a\.m\.|p\.m\.|AM|PM)?)'],
    "dates": [r'(\d{1,2}/\d{1,2}/\d{4}|\d{1,2}-\d{1,2}-\d{4})'],
    "ips": [r'\b(?:\d{1,3}\.){3}\d{1,3}\b'],
    "applications": [r'\b(PostgreSQL|MySQL|MongoDB|Apache|Nginx|Windows|Linux)\b']
}