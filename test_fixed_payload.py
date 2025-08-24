#!/usr/bin/env python3
"""
Test GPT Image 1 with correct payload (no response_format)
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG = "org-XKOFJy5SYzXNV9yTQTDTSPx9"

def test_gpt_image_1_correct():
    """Test GPT Image 1 with correct payload"""
    
    print(f"🔍 TESTING GPT IMAGE 1 WITH CORRECT PAYLOAD")
    print(f"=" * 60)
    
    # Correct payload for GPT Image 1
    payload = {
        "model": "gpt-image-1",
        "prompt": "Professional photo of a water bottle on wooden table",
        "n": 1,
        "size": "1024x1024",
        "quality": "high"
        # NO response_format parameter!
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Organization": OPENAI_ORG,
        "Content-Type": "application/json"
    }
    
    print(f"📦 Correct GPT Image 1 payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"\n📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ GPT IMAGE 1 SUCCESS!")
            print(f"🖼️ Image URL: {result['data'][0]['url']}")
            if 'revised_prompt' in result['data'][0]:
                print(f"📝 Revised prompt: {result['data'][0]['revised_prompt']}")
            return True
        else:
            print(f"❌ GPT IMAGE 1 FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_backend_after_fix():
    """Test backend with fixed payload"""
    
    print(f"\n" + "="*60)
    print(f"🔍 TESTING BACKEND AFTER PAYLOAD FIX")
    
    payload = {
        "brief_prompt": "Professional photo of a water bottle",
        "user_api_key": OPENAI_API_KEY,
        "provider": "openai",
        "use_raw_prompt": True
    }
    
    print(f"📦 Backend payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            "http://127.0.0.1:8000/api/v1/generate-image",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"\n📊 Backend Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ BACKEND SUCCESS!")
            print(f"🎯 Model Used: {result.get('model_used')}")
            print(f"🏭 Provider Used: {result.get('provider_used')}")
            print(f"🖼️ Image URL: {result.get('image_url', 'N/A')}")
            return True
        else:
            print(f"❌ BACKEND FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

if __name__ == "__main__":
    print(f"🎯 TESTING FIXED GPT IMAGE 1")
    
    # Test direct API first
    direct_ok = test_gpt_image_1_correct()
    
    if direct_ok:
        # Test backend
        backend_ok = test_backend_after_fix()
        
        print(f"\n" + "="*60)
        print(f"🏁 FINAL RESULTS:")
        print(f"📡 Direct GPT Image 1: {'✅ OK' if direct_ok else '❌ FAILED'}")
        print(f"🔧 Backend Fixed: {'✅ OK' if backend_ok else '❌ FAILED'}")
        
        if direct_ok and backend_ok:
            print(f"\n🎉 SUCCESS! GPT Image 1 working with correct payload!")
        else:
            print(f"\n⚠️ Still needs fixes")
    else:
        print(f"\n❌ Direct API failed, check payload again")
