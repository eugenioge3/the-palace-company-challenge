#!/bin/bash
echo "Ejecutando pruebas unitarias y de integración para la API..."
docker-compose run --rm api pytest
echo "Pruebas finalizadas."