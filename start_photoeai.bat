@echo off
echo 🚀 PhotoEAI Auto-Startup
echo ========================

cd /d "%~dp0"

echo 📍 Auto-detecting available ports...
python auto_start.py

pause
