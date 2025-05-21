@echo off
REM ================================
REM launch_app.bat
REM Lanza Docker Compose, la aplicación FastAPI con uvicorn y la aplicación Angular
REM ================================
REM Cambia al directorio donde está este script
cd /d %~dp0
REM (Opcional) Si usas un entorno virtual llamado "venv", actívalo:
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
) else (
    echo No se encontró un virtualenv en .\venv, usando Python global.
)
REM Asegúrate de tener uvicorn instalado
echo Instalando dependencias (si hace falta)...
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
REM Inicia los servicios de Docker Compose en segundo plano
echo Iniciando Docker Compose...
docker-compose up -d

REM Inicia la aplicación Angular en segundo plano
echo Iniciando aplicación Angular...
start cmd /k "cd C:\Users\Kevin\Desktop\Universidad\2025-1\Analisis de Algoritmos\angular_view\bibliometry_view && ng serve --open"

REM Lanza uvicorn apuntando a tu app
echo Iniciando servidor Uvicorn...
py -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

REM Detiene los contenedores al cerrar la aplicación (opcional)
echo Deteniendo Docker Compose...
docker-compose down
pause