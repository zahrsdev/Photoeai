"""
Simple port configuration updater
"""
import socket
import re
import os

def find_available_port(start_port=8000, max_attempts=10):
    """Find available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None

def update_file_port(file_path, port):
    """Update port in any file"""
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update API_BASE_URL
        content = re.sub(
            r'API_BASE_URL = "http://localhost:\d+"',
            f'API_BASE_URL = "http://localhost:{port}"',
            content
        )
        
        # Update uvicorn port
        content = re.sub(
            r'port=\d+',
            f'port={port}',
            content
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Updated {file_path} to port {port}")
        return True
        
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def configure_ports():
    """Find available port and update all config files"""
    
    print("🚀 PhotoEAI Port Configuration")
    print("=" * 40)
    
    # Find available port
    port = find_available_port(8000)
    if not port:
        print("❌ No available ports found!")
        return None
    
    print(f"📍 Using port: {port}")
    
    # Files to update
    files = [
        "run.py",
        "app.py", 
        "simple_frontend.py",
        "simple_enhanced_frontend.py"
    ]
    
    # Update all files
    for file_path in files:
        update_file_port(file_path, port)
    
    print("=" * 40)
    print(f"🎯 Configuration complete! Use port {port}")
    print(f"Backend: python run.py")
    print(f"Frontend: streamlit run simple_frontend.py")
    
    return port

if __name__ == "__main__":
    configure_ports()
