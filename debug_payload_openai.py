#!/usr/bin/env python3
"""
Debug script to see exact payload being sent to OpenAI API
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Test configuration
API_BASE = "http://127.0.0.1:8000"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def debug_request_to_openai():
    """Debug the exact request being sent to OpenAI"""
    
    # Simple test prompt
    test_prompt = "Professional photo of a water bottle"
    
    print(f"🔍 DEBUGGING OPENAI REQUEST")
    print(f"📝 Test prompt: {test_prompt}")
    print(f"🔑 API Key: {OPENAI_API_KEY[:12]}...")
    
    # Test payload that should work with GPT Image 1
    payload = {
        "brief_prompt": test_prompt,
        "user_api_key": OPENAI_API_KEY,
        "provider": "openai",
        "use_raw_prompt": True  # Use prompt as-is to avoid complex processing
    }
    
    print(f"\n⚡ Sending request...")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/generate-image",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS!")
            print(f"🎯 Model Used: {result.get('model_used')}")
            print(f"🏭 Provider Used: {result.get('provider_used')}")
            print(f"🖼️ Image URL: {result.get('image_url', 'N/A')}")
            
        else:
            print(f"❌ FAILED!")
            print(f"Error details: {response.text}")
            
            # Try to get more detailed error from server logs
            print(f"\n🔍 Let's check what exact payload was sent to OpenAI...")
            
    except Exception as e:
        print(f"❌ Request error: {e}")

def test_direct_openai_call():
    """Test direct call to OpenAI API for comparison"""
    
    print(f"\n" + "="*60)
    print(f"🔍 TESTING DIRECT OPENAI API CALL")
    
    # Test what works with GPT Image 1
    payload = {
        "model": "gpt-image-1",
        "prompt": "Professional photo of a water bottle",
        "n": 1,
        "size": "1024x1024",
        "quality": "high"
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    print(f"📦 Direct OpenAI payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Direct OpenAI Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ DIRECT OPENAI SUCCESS!")
            print(f"🖼️ Image URL: {result['data'][0]['url']}")
        else:
            print(f"❌ DIRECT OPENAI FAILED!")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Direct OpenAI error: {e}")

if __name__ == "__main__":
    debug_request_to_openai()
    test_direct_openai_call()
