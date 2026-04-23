@echo off
echo Starting TrafForesight-AI...
echo.

:: Check for .env file, if not exist copy from example
if not exist .env (
    echo Creating .env from .env.example...
    copy .env.example .env
)

:: Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

:: Start the server
echo Starting Backend Server on http://127.0.0.1:8000
uvicorn app.api:app --reload --port 8000
pause
