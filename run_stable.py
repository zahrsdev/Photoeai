"""
Stable startup script for the PhotoeAI backend.
This script prevents auto-restart issues and ensures stable operation.
"""

import uvicorn
import os
from app.config.settings import settings

def main():
    """Start the server with stable configuration"""
    print("🚀 Starting PhotoeAI Backend (Stable Mode)...")
    print(f"📍 Host: {settings.host}:{settings.port}")
    print(f"🤖 OpenAI Model: {settings.openai_model}")
    print(f"🔧 Debug Mode: {settings.debug}")
    print("📚 API Documentation available at: http://localhost:8000/docs")
    print("⚡ Stability Mode: Auto-reload DISABLED to prevent restarts")
    print("─" * 60)
    
    # Ensure stable operation by explicitly disabling reload
    config = uvicorn.Config(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,  # Force disable reload for stability
        log_level="info",
        access_log=True,
        workers=1,  # Single worker for stability
    )
    
    server = uvicorn.Server(config)
    
    try:
        server.run()
    except KeyboardInterrupt:
        print("\n🛑 Server shutdown requested")
    except Exception as e:
        print(f"💥 Server error: {e}")
    finally:
        print("👋 PhotoeAI Backend stopped")

if __name__ == "__main__":
    main()
