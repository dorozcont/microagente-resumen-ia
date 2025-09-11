# Usa una imagen base de Python con PyTorch, que ya incluye CUDA
FROM pytorch/pytorch:2.1.0-cuda11.8-cudnn8-runtime

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia los archivos de requerimientos e instala las dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de tu código al contenedor
COPY . .

# Expone el puerto 7860, que es el que usa Gradio por defecto
EXPOSE 7860

# Comando para ejecutar la aplicación cuando el contenedor se inicie
# CMD ["python", "app.py"]
CMD ["./start.sh"]