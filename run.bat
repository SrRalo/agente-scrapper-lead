@echo off
echo ========================================
echo   Lead Pipeline - Scraper de Negocios
echo ========================================
echo.

if not exist "venv" (
    echo [1/4] Creando entorno virtual...
    python -m venv venv
) else (
    echo [1/4] Entorno virtual encontrado.
)

echo [2/4] Instalando dependencias...
call venv\Scripts\activate.bat
pip install -r requirements.txt -q

if not exist ".env" (
    echo [!] Archivo .env no encontrado. Copia .env.example a .env y agrega tu SERPAPI_KEY
    echo [!] Copiando .env.example a .env...
    copy .env.example .env
)

echo [3/4] Inicializando base de datos...
python -c "import asyncio; from backend.models import init_db; asyncio.run(init_db())"

echo [4/4] Iniciando servidor en http://localhost:8000
echo.
echo Abre http://localhost:8000 en tu navegador
echo Presiona Ctrl+C para detener
echo.
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
