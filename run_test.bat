@echo off
cd /d "c:\Users\Rekabit\Documents\Ngoding\photoeai-backend"
echo Waiting for backend to start...
timeout /t 5
echo Running test...
python simple_test.py
pause
