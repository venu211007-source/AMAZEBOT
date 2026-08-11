@echo off
cd /d "%~dp0"

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt

echo.
echo Starting AMAZEBOT local LLM backend on http://127.0.0.1:8000
echo Make sure Ollama is running (ollama serve) and the model is pulled.
echo.
uvicorn main:app --host 127.0.0.1 --port 8000

pause
