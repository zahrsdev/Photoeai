@echo off
title PhotoEAI Startup
echo 🚀 PhotoEAI Auto-Configuration
echo ==============================

cd /d "%~dp0"

echo 📍 Configuring ports...
python configure_ports.py

echo.
echo 🚀 Starting Backend Server...
start "PhotoEAI Backend" python run.py

timeout /t 3 /nobreak >nul

echo 🎨 Starting Frontend...
start "PhotoEAI Frontend" streamlit run simple_frontend.py

echo.
echo ✅ Both servers starting!
echo 📱 Backend: Check terminal for port info  
echo 🎨 Frontend: Check browser for URL
echo.
pause
