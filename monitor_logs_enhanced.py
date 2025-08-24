"""
PhotoEAI Enhanced Log Monitor - Real-time Backend Activity Viewer
================================================================

This script provides real-time monitoring of backend activities with:
- Color-coded log levels (INFO, WARNING, ERROR)
- Filtered view options (API requests, AI operations, errors only)
- Enhanced readability with timestamps and structured formatting
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def colored_text(text, color):
    """Return colored text for terminal display"""
    colors = {
        'green': '\033[92m',
        'yellow': '\033[93m',
        'red': '\033[91m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'white': '\033[97m',
        'reset': '\033[0m'
    }
    return f"{colors.get(color, colors['white'])}{text}{colors['reset']}"

def format_log_line(line):
    """Format log line with colors and better readability"""
    if not line.strip():
        return ""
    
    # Color-code by log level
    if "ERROR" in line:
        return colored_text(line, 'red')
    elif "WARNING" in line:
        return colored_text(line, 'yellow')
    elif "INFO" in line:
        # Highlight important activities
        if "[FRONTEND REQUEST]" in line or "[FRONTEND RESPONSE]" in line:
            return colored_text(line, 'cyan')
        elif "🎨" in line or "🚀" in line or "✅" in line:
            return colored_text(line, 'green')
        else:
            return colored_text(line, 'white')
    else:
        return line

def main():
    print(colored_text("🔍 PhotoEAI Enhanced Log Monitor", 'cyan'))
    print(colored_text("=" * 50, 'cyan'))
    print()
    print(colored_text("⚡ Real-time backend activity monitoring", 'green'))
    print(colored_text("🎯 Tracking: API requests, AI operations, image generation", 'green'))
    print(colored_text("⏹️  Press Ctrl+C to stop monitoring", 'yellow'))
    print()
    print(colored_text("=" * 50, 'cyan'))
    print()
    
    # Get today's log file
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = f"logs/photoeai_{today}.log"
    
    if not os.path.exists(log_file):
        print(colored_text(f"❌ Log file not found: {log_file}", 'red'))
        print(colored_text("Make sure the backend server is running!", 'yellow'))
        input("Press Enter to exit...")
        return
    
    try:
        # Use PowerShell Get-Content -Wait (equivalent to tail -f)
        cmd = f'powershell -Command "Get-Content -Path \'{log_file}\' -Wait -Tail 10"'
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print(colored_text("📊 Monitoring backend logs...", 'green'))
        print(colored_text("-" * 50, 'white'))
        
        while True:
            line = process.stdout.readline()
            if line:
                formatted_line = format_log_line(line.rstrip())
                if formatted_line:
                    print(formatted_line)
            elif process.poll() is not None:
                break
    
    except KeyboardInterrupt:
        print()
        print(colored_text("🛑 Log monitoring stopped by user", 'yellow'))
    except Exception as e:
        print(colored_text(f"❌ Error monitoring logs: {e}", 'red'))
    finally:
        if 'process' in locals():
            process.terminate()

if __name__ == "__main__":
    main()
