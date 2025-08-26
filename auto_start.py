"""
Auto-detect available ports and update configuration
"""
import socket
import subprocess
import sys
import os
import time

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

def update_frontend_port(frontend_file, backend_port):
    """Update API_BASE_URL in frontend file"""
    try:
        with open(frontend_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace localhost port in API_BASE_URL
        import re
        pattern = r'API_BASE_URL = "http://localhost:\d+"'
        replacement = f'API_BASE_URL = "http://localhost:{backend_port}"'
        updated_content = re.sub(pattern, replacement, content)
        
        with open(frontend_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated {frontend_file} to use port {backend_port}")
        return True
    except Exception as e:
        print(f"❌ Failed to update {frontend_file}: {e}")
        return False

def update_run_py_port(run_file, port):
    """Update port in run.py"""
    try:
        with open(run_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace port= line
        import re
        pattern = r'port=\d+'
        replacement = f'port={port}'
        updated_content = re.sub(pattern, replacement, content)
        
        with open(run_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ Updated {run_file} to use port {port}")
        return True
    except Exception as e:
        print(f"❌ Failed to update {run_file}: {e}")
        return False

def start_servers():
    """Auto-configure ports and start servers"""
    
    print("🚀 PhotoEAI Auto-Startup")
    print("=" * 50)
    
    # Find available backend port
    backend_port = find_available_port(8000)
    if not backend_port:
        print("❌ No available ports found!")
        return
    
    print(f"📍 Backend will use port: {backend_port}")
    
    # Update run.py with available port
    if not update_run_py_port("run.py", backend_port):
        return
    
    # Update frontend files to match backend port
    frontend_files = [
        "app.py",
        "simple_frontend.py", 
        "simple_enhanced_frontend.py"
    ]
    
    for frontend_file in frontend_files:
        if os.path.exists(frontend_file):
            update_frontend_port(frontend_file, backend_port)
    
    print("=" * 50)
    print("🚀 Starting Backend Server...")
    
    # Start backend in background
    try:
        backend_process = subprocess.Popen(
            [sys.executable, "run.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Wait for backend to start and capture output
        print("⏳ Waiting for backend to initialize...")
        time.sleep(5)
        
        if backend_process.poll() is None:
            print(f"✅ Backend running on http://localhost:{backend_port}")
            print(f"📚 API docs: http://localhost:{backend_port}/docs")
            print("=" * 50)
            
            # Start Streamlit frontend
            print("🎨 Starting Streamlit Frontend...")
            streamlit_process = subprocess.Popen([
                sys.executable, "-m", "streamlit", "run", "simple_frontend.py",
                "--server.port", str(backend_port + 1),
                "--server.headless", "true",
                "--browser.gatherUsageStats", "false"
            ])
            
            print(f"✅ Frontend running on http://localhost:{backend_port + 1}")
            print("=" * 50)
            print("🎯 Both servers are running!")
            print("Press Ctrl+C to stop all servers")
            
            try:
                # Keep both processes running
                backend_process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping servers...")
                backend_process.terminate()
                streamlit_process.terminate()
                print("✅ All servers stopped")
        else:
            # Backend failed, get error output
            output, _ = backend_process.communicate(timeout=5)
            print("❌ Backend failed to start")
            print(f"Error output: {output}")
            
    except Exception as e:
        print(f"❌ Error starting servers: {e}")

if __name__ == "__main__":
    start_servers()
