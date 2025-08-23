@echo off
REM PhotoEAI Complete Startup Script for Windows
REM Starts both the FastAPI backend and Streamlit frontend

echo 🚀 PhotoEAI Complete Startup
echo ==========================
echo.

echo 🔍 Checking Python environment...

REM Check if virtual environment exists
if exist ".venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo ⚠️  No virtual environment found. Using system Python.
)

echo.
echo 📋 Installing/updating requirements...
pip install -r requirements.txt

echo.
echo 🚀 Starting services...
echo.

echo 🔧 Starting FastAPI backend server...
start /B python run.py
timeout /t 3 /nobreak >nul

echo    Backend URL: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.

echo 🎨 Starting Streamlit frontend...
echo    Streamlit URL: http://localhost:8501
echo.

echo 🎉 Starting Streamlit... The backend is running in the background.
echo.
echo 📝 Usage:
echo    • Frontend (Streamlit): http://localhost:8501
echo    • Backend API: http://localhost:8000
echo    • API Documentation: http://localhost:8000/docs
echo.
echo 💡 Tips:
echo    • Make sure you have valid API keys for the AI services
echo    • Try the 'Simple Mode' workflow for quick brief generation
echo    • Use 'Advanced Mode' for detailed parameter control
echo.
echo ⏹️  Close this window or press Ctrl+C to stop the frontend
echo    (Backend will continue running in background)
echo.

streamlit run app.py
