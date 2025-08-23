@echo off
echo PhotoEAI Streamlit App Setup and Launch
echo =====================================

echo.
echo 1. Installing requirements...
pip install -r requirements.txt

echo.
echo 2. Launching Streamlit app...
echo.
echo IMPORTANT: Make sure the PhotoEAI backend server is running!
echo You can start it with: python run.py
echo.

streamlit run app.py
