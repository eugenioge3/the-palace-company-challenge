@echo off
echo Construyendo y levantando la base de datos y la API...
docker-compose up --build -d
echo Entorno listo. La API esta disponible en http://localhost:8000
echo Swagger http://localhost:8000/docs