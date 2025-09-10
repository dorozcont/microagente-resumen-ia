#!/bin/bash

# Añade todos los archivos modificados
git add .

# Pregunta por un mensaje de commit
read -p "Ingresa el mensaje de commit: " commit_message

# Realiza el commit
git commit -m "$commit_message"

# Sube los cambios a GitHub, lo que activará el flujo de trabajo de Docker
git push origin master # O el nombre de tu rama principal

echo "Cambios subidos a GitHub. La imagen de Docker se está construyendo."