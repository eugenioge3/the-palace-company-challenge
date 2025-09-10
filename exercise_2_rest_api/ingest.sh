#!/bin/bash
echo "Esperando a que la base de datos esté lista..."
sleep 5
echo "Ejecutando el script de ingesta de datos..."
docker-compose run --rm ingestor
echo "Ingesta de datos completada."