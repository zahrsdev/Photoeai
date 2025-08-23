#!/usr/bin/env python3
"""
Simple run script for PhotoeAI server without auto-reload
"""

from app.main import app
import uvicorn

if __name__ == "__main__":
    print("🚀 Starting PhotoeAI Server (No Auto-Reload)...")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=False,
        log_level="info"
    )
