@echo off
echo Starting PhotoeAI Backend on port 8001...
cd /d "C:\Users\Rekabit\Documents\Ngoding\photoeai-backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
pause
