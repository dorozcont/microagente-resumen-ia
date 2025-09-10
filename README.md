Resumen de incidentes 📑


Descripción: Cuando ocurre un incidente complejo, como una interrupción del servicio, los equipos de TI pueden generar muchos mensajes y logs. Un microagente puede procesar todo este texto y generar un resumen conciso para los líderes o para los informes de post-mortem.

Funcionamiento:

Entrada: Un bloque de texto que contiene las notas de un incidente, las líneas de tiempo, los comandos ejecutados y los mensajes de chat entre los técnicos.

Agente de IA: El agente usa un modelo de resumen de texto para extraer los puntos clave, como el problema inicial, las acciones tomadas, la causa raíz y el resultado final.

Resultado: Un párrafo de texto que resume el incidente. Por ejemplo: "A las 10:30 am, el servidor web 'srv-01' dejó de responder debido a un alto uso de la CPU. El equipo reinició el servicio y se restauró la funcionalidad a las 10:45 am. Causa raíz identificada: bucle infinito en el script de análisis de datos."
