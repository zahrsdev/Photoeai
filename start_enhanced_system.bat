@echo off
echo Starting PhotoeAI Enhanced System...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\activate
    echo Then: pip install -r requirements.txt
    pause
    exit /b
)

echo Activating virtual environment...
call .venv\Scripts\activate

echo.
echo Starting FastAPI Backend Server...
start "PhotoeAI Backend" cmd /k "python app.py"

echo Waiting for backend to start...
timeout /t 5 /nobreak

echo.
echo Starting Enhanced Frontend...
start "PhotoeAI Enhanced Frontend" cmd /k "streamlit run enhanced_frontend.py --server.port 8501 --server.headless false"

echo.
echo ========================================
echo PhotoeAI Enhanced System Started!
echo ========================================
echo Backend API: http://localhost:8000
echo Enhanced Frontend: http://localhost:8501
echo.
echo Both applications are running in separate windows.
echo Close this window when you're done.
echo ========================================

pause
