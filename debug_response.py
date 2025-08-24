#!/usr/bin/env python3
"""
Debug test to check response structure
"""

import requests
import json

BACKEND_URL = "http://localhost:8000"
TEST_PROMPT = """Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center."""

def debug_response():
    payload = {"user_request": TEST_PROMPT}
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/generate-brief",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Response keys:", list(result.keys()))
            
            # Print all fields
            for key, value in result.items():
                if isinstance(value, str) and len(value) > 200:
                    print(f"{key}: {value[:200]}...")
                else:
                    print(f"{key}: {value}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_response()
