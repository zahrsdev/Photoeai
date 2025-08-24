@echo off
REM PhotoEAI Complete System Monitor
REM Starts backend, frontend, and log monitoring all at once

echo 🚀 PhotoEAI Complete System Monitor
echo ===================================
echo.
echo This will start:
echo  1. Backend API server
echo  2. Frontend Streamlit app
echo  3. Real-time log monitoring
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not available. Please install Python first.
    pause
    exit /b 1
)

echo 📦 Installing/updating requirements...
pip install -r requirements.txt

echo.
echo 🚀 Starting PhotoEAI system...
echo.

REM Start backend in background
echo 🔧 Starting backend server...
start "PhotoEAI Backend" cmd /k "python run.py"

REM Wait for backend to start
echo ⏳ Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

REM Start frontend in background
echo 🎨 Starting frontend interface...
start "PhotoEAI Frontend" cmd /k "streamlit run simple_frontend.py --server.port 8501"

REM Wait for frontend to start
echo ⏳ Waiting for frontend to initialize...
timeout /t 3 /nobreak >nul

REM Start enhanced log monitor
echo 📊 Starting enhanced log monitoring...
python monitor_logs_enhanced.py

pause
