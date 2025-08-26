"""
Simple startup script for the PhotoeAI backend.
Run this file to start the development server.
"""

import uvicorn
from app.config.settings import settings

if __name__ == "__main__":
    print("🚀 Starting PhotoeAI Backend...")
    print(f"📍 Host: {settings.host}:{settings.port}")
    print(f"🤖 OpenAI Model: {settings.openai_model}")
    print(f"🔧 Debug Mode: {settings.debug}")
    print("📚 API Documentation available at: http://localhost:{settings.port}/docs")
    print("─" * 50)
    
    # ⚡ STABILITY FIX: Disable auto-reload to prevent server restarts
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=False,  # Disabled to prevent automatic restarts
        log_level="info" if not settings.debug else "debug"
    )
