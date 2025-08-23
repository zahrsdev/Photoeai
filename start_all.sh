#!/bin/bash

# PhotoEAI Complete Startup Script
# Starts both the FastAPI backend and Streamlit frontend

echo "🚀 PhotoEAI Complete Startup"
echo "=========================="
echo ""

# Check if running on Windows (Git Bash or WSL)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    PYTHON_CMD="python"
    VENV_ACTIVATE=".venv/Scripts/activate"
else
    PYTHON_CMD="python3"
    VENV_ACTIVATE=".venv/bin/activate"
fi

echo "🔍 Checking Python environment..."

# Activate virtual environment if it exists
if [ -f "$VENV_ACTIVATE" ]; then
    echo "📦 Activating virtual environment..."
    source "$VENV_ACTIVATE"
else
    echo "⚠️  No virtual environment found. Using system Python."
fi

echo ""
echo "📋 Installing/updating requirements..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting services..."
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup INT TERM

# Start the backend server in the background
echo "🔧 Starting FastAPI backend server..."
$PYTHON_CMD run.py &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Backend URL: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"

# Wait a moment for the backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if kill -0 $BACKEND_PID 2>/dev/null; then
    echo "✅ Backend server is running"
else
    echo "❌ Backend server failed to start"
    exit 1
fi

echo ""
echo "🎨 Starting Streamlit frontend..."
streamlit run app.py &
STREAMLIT_PID=$!
echo "   Streamlit PID: $STREAMLIT_PID"
echo "   Streamlit URL: http://localhost:8501"

echo ""
echo "🎉 Both services are starting up!"
echo ""
echo "📝 Usage:"
echo "   • Frontend (Streamlit): http://localhost:8501"
echo "   • Backend API: http://localhost:8000"
echo "   • API Documentation: http://localhost:8000/docs"
echo ""
echo "💡 Tips:"
echo "   • Make sure you have valid API keys for the AI services"
echo "   • Try the 'Simple Mode' workflow for quick brief generation"
echo "   • Use 'Advanced Mode' for detailed parameter control"
echo ""
echo "⏹️  Press Ctrl+C to stop both services"
echo ""

# Wait for either process to exit
wait
