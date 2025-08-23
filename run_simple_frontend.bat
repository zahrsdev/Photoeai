@echo off
echo PhotoEAI Simple Frontend
echo ========================

echo.
echo Starting simple frontend interface...
echo.
echo Make sure the backend server is running first!
echo You can start it with: python run.py
echo.

streamlit run simple_frontend.py --server.port 8501

pause
