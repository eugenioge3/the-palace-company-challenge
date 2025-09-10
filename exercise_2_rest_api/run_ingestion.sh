#!/bin/bash

# Este script automatiza el proceso de construcción y ejecución de la ingesta de datos.

echo "Paso 1: Levantando la base de datos y la API..."
# Construye las imágenes si no existen y levanta los servicios en segundo plano (-d)
docker-compose up --build -d

# pausa para asegurar que la base de datos esté completamente lista para aceptar conexiones
echo "Esperando 10 segundos a que la base de datos se inicie..."
sleep 10

echo "Paso 2: Ejecutando el script de ingesta de datos..."
# 'run --rm' ejecuta el comando del servicio 'ingestor' en un nuevo contenedor
# y lo elimina (--rm) una vez que el script termina.
docker-compose run --rm ingestor

echo "Proceso completado! La API está disponible en http://localhost:8000/docs"