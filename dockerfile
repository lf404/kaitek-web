# Usar una imagen ligera de Python
FROM python:3.9-slim

# Directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los requerimientos e instalarlos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del proyecto
COPY . .

# Exponer el puerto 5000
EXPOSE 5000

# Comando para iniciar con Gunicorn (Servidor de producción)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]