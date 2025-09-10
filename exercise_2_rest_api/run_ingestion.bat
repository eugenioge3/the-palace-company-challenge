@echo off
echo Paso 1: Levantando la base de datos y la API...
REM Construye las imagenes si no existen y levanta los servicios en segundo plano (-d)
docker-compose up --build -d

echo Esperando 10 segundos a que la base de datos se inicie...
REM Comando 'timeout' en Windows (sleep)
timeout /t 10 /nobreak

echo Paso 2: Ejecutando el script de ingesta de datos...
REM 'run --rm' ejecuta el comando del servicio 'ingestor' en un nuevo contenedor
REM y lo elimina (--rm) una vez que el script termina.
docker-compose run --rm ingestor

echo.
echo "¡Proceso completado! La API esta disponible en http://localhost:8000/docs"