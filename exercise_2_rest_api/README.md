Tech Test API Project
Este proyecto implementa una API REST para gestionar contactos, con un proceso automatizado para ingerir datos desde un archivo CSV a una base de datos PostgreSQL.
Requisitos
Docker
Docker Compose
Inicio Rápido (Quick Start)
Para levantar el proyecto completo (Base de Datos, API e Ingesta de Datos), sigue estos pasos:
Abre una terminal en la raíz de este proyecto.
Ejecuta el comando correspondiente a tu sistema operativo:
<br>
Para Windows (CMD o PowerShell):
code
Cmd
.\run_ingestion.bat
Para Linux o macOS (Bash/Zsh):
code
Bash
./run_ingestion.sh
(Si obtienes un error de permisos en Linux/macOS, primero ejecuta: chmod +x run_ingestion.sh)
<br>
El script se encargará de todo:
Construirá las imágenes de Docker necesarias.
Levantará la base de datos y la API.
Esperará a que la base de datos esté lista.
Ejecutará el proceso de ingesta de datos.
Una vez finalizado, la API estará disponible y documentada en:
http://localhost:8000/docs