FROM python:3.9-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de requerimientos
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto de nuestros archivos
COPY ingest_data.py .
COPY sample.csv .

# 6. Definimos el comando que se ejecutará por defecto cuando se inicie el contenedor
CMD ["python", "ingest_data.py"]