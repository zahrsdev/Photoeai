#!/usr/bin/env python3
"""
Debug GPT Image 1 API call
"""

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load API key
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv("OPENAI_API_KEY")

def test_direct_openai_image():
    """Test direct OpenAI API call to check format"""
    print("Testing direct OpenAI Images API...")
    
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Test with simple payload first
    simple_payload = {
        "model": "dall-e-3",
        "prompt": "A vibrant tropical watermelon juice bottle advertisement",
        "n": 1,
        "size": "1024x1024",
        "quality": "standard"
    }
    
    try:
        print("Sending request to OpenAI...")
        response = requests.post(url, headers=headers, json=simple_payload, timeout=60)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Direct OpenAI call successful!")
            print(f"Response keys: {list(result.keys())}")
            if "data" in result:
                print(f"Image data keys: {list(result['data'][0].keys())}")
        else:
            print(f"❌ Direct OpenAI call failed")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_backend_image_api():
    """Test backend image API with debug info"""
    print("\nTesting backend image API...")
    
    BACKEND_URL = "http://localhost:8000"
    
    payload = {
        "brief_prompt": "A vibrant tropical watermelon juice bottle advertisement",
        "user_api_key": API_KEY,
        "provider": "openai_dalle",
        "use_raw_prompt": True
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/generate-image",
            json=payload,
            timeout=60
        )
        
        print(f"Backend Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Backend Error: {e}")

if __name__ == "__main__":
    test_direct_openai_image()
    test_backend_image_api()
