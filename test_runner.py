#!/usr/bin/env python3
"""
Script untuk start backend dan test secara terpisah
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_backend():
    """Start backend server dalam subprocess"""
    print("🚀 Starting backend server...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Start backend dengan subprocess
    backend_process = subprocess.Popen(
        [sys.executable, "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=backend_dir
    )
    
    # Tunggu backend start
    print("⏳ Waiting for backend to start...")
    time.sleep(10)
    
    return backend_process

def run_test():
    """Run test script"""
    print("🔍 Running test...")
    
    try:
        # Run test script
        result = subprocess.run(
            [sys.executable, "fixed_test.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print("📊 TEST RESULTS:")
        print("=" * 80)
        print(result.stdout)
        
        if result.stderr:
            print("\n❌ ERRORS:")
            print(result.stderr)
            
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print("❌ Test timeout!")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    print("🎯 PhotoeAI Backend & Test Runner")
    print("=" * 80)
    
    backend_process = None
    
    try:
        # Start backend
        backend_process = start_backend()
        
        # Run test
        test_success = run_test()
        
        if test_success:
            print("\n✅ ALL TESTS PASSED!")
        else:
            print("\n❌ TESTS FAILED!")
            
    finally:
        # Cleanup backend process
        if backend_process:
            print("\n🛑 Stopping backend...")
            backend_process.terminate()
            backend_process.wait(timeout=5)
            print("✅ Backend stopped")

if __name__ == "__main__":
    main()
