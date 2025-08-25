#!/usr/bin/env python3
"""
Quick API key test - FOCUSED SIMPLE TEST
"""
import requests
import json

API_KEY = "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"

def test_gpt_image_1():
    """Test GPT Image-1 API directly"""
    print("🔥 Testing GPT Image-1 API...")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "OpenAI/1.101.0"
    }
    
    payload = {
        "model": "gpt-image-1",
        "prompt": "Simple test: white bottle product photo on clean background",
        "n": 1,
        "size": "1024x1024",
        "quality": "high"
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API KEY WORKING!")
            print(f"📋 Response keys: {list(result.keys())}")
            if "data" in result:
                print(f"🎯 Image generated successfully!")
                return True
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📝 Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Exception: {e}")
        return False

if __name__ == "__main__":
    test_gpt_image_1()
