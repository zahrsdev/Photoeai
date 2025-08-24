#!/usr/bin/env python3
"""
Test with DALL-E 3 (should work with regular OpenAI accounts)
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def test_dalle3_direct():
    """Test direct DALL-E 3 call"""
    
    print(f"🔍 TESTING DALL-E 3 (Regular OpenAI Account)")
    
    payload = {
        "model": "dall-e-3",
        "prompt": "Professional photo of a water bottle",
        "n": 1,
        "size": "1024x1024",
        "quality": "hd",
        "style": "natural"
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"📦 DALL-E 3 payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 DALL-E 3 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ DALL-E 3 SUCCESS!")
            print(f"🖼️ Image URL: {result['data'][0]['url']}")
            print(f"📝 Revised Prompt: {result['data'][0].get('revised_prompt', 'N/A')}")
        else:
            print(f"❌ DALL-E 3 FAILED!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ DALL-E 3 error: {e}")

def test_backend_with_dalle3():
    """Test backend with DALL-E 3 configuration"""
    
    print(f"\n" + "="*60)
    print(f"🔍 TESTING BACKEND WITH DALL-E 3 MODEL")
    
    # Test backend dengan explicit model dall-e-3
    payload = {
        "brief_prompt": "Professional photo of a water bottle",
        "user_api_key": OPENAI_API_KEY,
        "provider": "openai_dalle",  # Use exact enum value
        "use_raw_prompt": True
    }
    
    print(f"📦 Backend payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/generate-image",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"📊 Backend Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ BACKEND SUCCESS with DALL-E 3!")
            print(f"🎯 Model Used: {result.get('model_used')}")
            print(f"🏭 Provider Used: {result.get('provider_used')}")
            print(f"🖼️ Image URL: {result.get('image_url', 'N/A')}")
        else:
            print(f"❌ BACKEND FAILED!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Backend error: {e}")

if __name__ == "__main__":
    test_dalle3_direct()
    test_backend_with_dalle3()
