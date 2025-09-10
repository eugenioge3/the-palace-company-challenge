#!/bin/bash
echo "Ejecutando el script de ingesta de datos..."
docker-compose run --rm ingestor
echo "Ingesta de datos completada."