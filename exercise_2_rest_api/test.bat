@echo off
echo Ejecutando pruebas unitarias y de integracion para la API...
docker-compose run --rm api pytest -v --cov=app
echo Pruebas finalizadas.