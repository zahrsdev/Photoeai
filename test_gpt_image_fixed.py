#!/usr/bin/env python3
"""
Test GPT Image 1 with correct parameters (no response_format)
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def test_gpt_image_1_correct():
    """Test GPT Image 1 with correct parameters"""
    
    print(f"🔍 TESTING GPT IMAGE 1 WITH CORRECT PARAMETERS")
    print(f"=" * 60)
    
    # Correct payload for GPT Image 1
    payload = {
        "model": "gpt-image-1",
        "prompt": "A red apple on white background",
        "n": 1,
        "size": "1024x1024",
        "quality": "high"
        # NO response_format - GPT Image 1 doesn't support it
        # NO style - GPT Image 1 doesn't support it
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
        "OpenAI-Organization": "org-XKOFJy5SYzXNV9yTQTDTSPx9"
    }
    
    print(f"📦 GPT Image 1 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 GPT Image 1 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ GPT IMAGE 1: SUCCESS!")
            print(f"🖼️ Image URL: {result['data'][0]['url']}")
            
            # Check response structure
            print(f"\n📋 Response Structure:")
            print(f"  - data: {len(result.get('data', []))} items")
            print(f"  - url: {'✅' if 'url' in result['data'][0] else '❌'}")
            print(f"  - revised_prompt: {'✅' if 'revised_prompt' in result['data'][0] else '❌'}")
            
            if result['data'][0].get('revised_prompt'):
                print(f"📝 Revised Prompt: {result['data'][0]['revised_prompt'][:100]}...")
                
            return True
        else:
            print(f"❌ GPT IMAGE 1: FAILED")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ GPT Image 1 Error: {e}")
        return False

def test_backend_with_correct_params():
    """Test backend after fix"""
    
    print(f"\n" + "="*60)
    print(f"🔍 TESTING BACKEND WITH CORRECT GPT IMAGE 1")
    
    payload = {
        "brief_prompt": "A red apple on white background",
        "user_api_key": OPENAI_API_KEY,
        "provider": "openai",
        "use_raw_prompt": True
    }
    
    print(f"📦 Backend Test Payload: {json.dumps(payload, indent=2)}")
    
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
            print(f"✅ BACKEND SUCCESS!")
            print(f"🎯 Model Used: {result.get('model_used')}")
            print(f"🏭 Provider Used: {result.get('provider_used')}")
            print(f"🖼️ Image URL: {result.get('image_url', 'N/A')}")
            print(f"📝 Generation ID: {result.get('generation_id', 'N/A')}")
            return True
        else:
            print(f"❌ BACKEND FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Backend Error: {e}")
        return False

if __name__ == "__main__":
    print(f"🎯 TESTING FIXED GPT IMAGE 1 IMPLEMENTATION")
    
    # Test direct API first
    direct_success = test_gpt_image_1_correct()
    
    if direct_success:
        print(f"\n✅ Direct API working, now testing backend...")
        backend_success = test_backend_with_correct_params()
        
        if backend_success:
            print(f"\n🎉 COMPLETE SUCCESS!")
            print(f"✅ Direct GPT Image 1 API: Working")
            print(f"✅ Backend with GPT Image 1: Working")
        else:
            print(f"\n⚠️ Direct API works, backend needs fixes")
    else:
        print(f"\n❌ Direct API failed, check API key/organization")
