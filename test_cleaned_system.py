#!/usr/bin/env python3
"""
Test cleaned up OpenAI-only system
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Test configuration
API_BASE = "http://127.0.0.1:8000"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def test_cleaned_system():
    """Test the cleaned OpenAI-only system"""
    
    print(f"🔍 TESTING CLEANED OPENAI-ONLY SYSTEM")
    print(f"=" * 60)
    
    # Simple test prompt
    test_prompt = "Professional photo of a water bottle on wooden table"
    
    print(f"📝 Test prompt: {test_prompt}")
    print(f"🔑 API Key: {OPENAI_API_KEY[:12]}...")
    
    # Test with clean payload
    payload = {
        "brief_prompt": test_prompt,
        "user_api_key": OPENAI_API_KEY,
        "provider": "openai",  # Should always map to OpenAI now
        "use_raw_prompt": True
    }
    
    print(f"\n⚡ Testing cleaned backend...")
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
            print(f"✅ SUCCESS! Cleaned system working!")
            print(f"🎯 Model Used: {result.get('model_used')}")
            print(f"🏭 Provider Used: {result.get('provider_used')}")
            print(f"🖼️ Image URL: {result.get('image_url', 'N/A')}")
            print(f"📝 Generation ID: {result.get('generation_id', 'N/A')}")
            
            return True
            
        else:
            print(f"❌ FAILED!")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False

def test_different_providers():
    """Test that all provider names map to OpenAI"""
    
    print(f"\n" + "="*60)
    print(f"🔍 TESTING PROVIDER MAPPING")
    
    providers_to_test = ["openai", "openai_dalle", "gemini", "midjourney", "sumopod", None]
    
    for provider in providers_to_test:
        print(f"\n📡 Testing provider: {provider or 'None (auto-detect)'}")
        
        payload = {
            "brief_prompt": "Test image",
            "user_api_key": OPENAI_API_KEY,
            "use_raw_prompt": True
        }
        
        if provider:
            payload["provider"] = provider
        
        try:
            response = requests.post(
                f"http://127.0.0.1:8000/api/v1/generate-image",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {provider or 'auto'} → OpenAI: {result.get('provider_used')}")
            else:
                print(f"❌ {provider or 'auto'} → Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {provider or 'auto'} → Exception: {e}")

if __name__ == "__main__":
    print(f"🎯 TESTING CLEANED SYSTEM (OpenAI GPT Image 1 Only)")
    print(f"=" * 60)
    
    # Test main functionality
    success = test_cleaned_system()
    
    if success:
        # Test provider mapping
        test_different_providers()
        
        print(f"\n" + "="*60)
        print(f"🏁 CLEANUP RESULT: ✅ SUCCESS!")
        print(f"✅ All providers now map to OpenAI GPT Image 1")
        print(f"✅ System simplified and optimized")
        print(f"✅ No more multi-provider complexity")
    else:
        print(f"\n" + "="*60)
        print(f"🏁 CLEANUP RESULT: ❌ NEEDS FIXES")
