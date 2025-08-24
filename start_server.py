#!/usr/bin/env python3
"""
Direct startup script for FastAPI server with auto-reload.
This ensures we start from the correct directory and handles port conflicts.
"""

import os
import sys
import socket
import time
import uvicorn

# Change to the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the current directory to Python path
sys.path.insert(0, script_dir)

def is_port_available(host, port):
    """Check if a port is available for binding."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            return True
    except OSError:
        return False

def find_available_port(host, start_port, max_attempts=10):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        if is_port_available(host, port):
            return port
    return None

if __name__ == "__main__":
    host = "127.0.0.1"
    preferred_port = 8000
    
    print("🚀 Starting PhotoeAI Backend Server (Development Mode)...")
    
    # Check if preferred port is available
    if is_port_available(host, preferred_port):
        port = preferred_port
        print(f"✅ Port {port} is available")
    else:
        print(f"⚠️  Port {preferred_port} is in use, searching for alternative...")
        # Wait a moment in case port is being released
        time.sleep(2)
        
        # Try preferred port one more time
        if is_port_available(host, preferred_port):
            port = preferred_port
            print(f"✅ Port {port} is now available")
        else:
            # Find alternative port
            port = find_available_port(host, preferred_port + 1)
            if port:
                print(f"✅ Using alternative port {port}")
            else:
                print(f"❌ No available ports found in range {preferred_port+1}-{preferred_port+10}")
                sys.exit(1)
    
    print(f"🌐 Server will start on http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 ReDoc Documentation: http://{host}:{port}/redoc")
    print("⚡ Stable mode: Auto-reload DISABLED to prevent restarts")
    
    try:
        # Start the FastAPI server without reload for stability
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=False,  # Disabled for stability
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        sys.exit(1)
