@echo off
REM PhotoEAI Real-Time Log Monitor
REM Shows backend activity logs in real-time while frontend is running

echo 🔍 PhotoEAI Real-Time Log Monitor
echo =================================
echo.
echo This will show backend activity logs in real-time
echo Keep this window open while using the frontend
echo Press Ctrl+C to stop monitoring
echo.

REM Check if log file exists
if not exist "logs\photoeai_2025-08-23.log" (
    echo ❌ Log file not found. Make sure the backend is running first.
    pause
    exit /b 1
)

echo ✅ Monitoring backend activity logs...
echo =====================================
echo.

REM Use PowerShell to tail the log file (similar to tail -f on Unix)
powershell -Command "Get-Content -Path 'logs\photoeai_2025-08-23.log' -Wait -Tail 20"

pause
