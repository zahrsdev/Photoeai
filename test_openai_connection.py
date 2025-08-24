#!/usr/bin/env python3
"""
Test OpenAI API connection and available models
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG = "org-XKOFJy5SYzXNV9yTQTDTSPx9"  # From your curl command

def test_openai_connection():
    """Test basic OpenAI API connection"""
    
    print(f"🔍 TESTING OPENAI API CONNECTION")
    print(f"=" * 60)
    print(f"🔑 API Key: {OPENAI_API_KEY[:12]}...")
    print(f"🏢 Organization: {OPENAI_ORG}")
    
    # Test models endpoint
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Organization": OPENAI_ORG,
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n📡 Testing models endpoint...")
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            models_data = response.json()
            models = [model["id"] for model in models_data["data"]]
            
            # Check for image models
            image_models = [m for m in models if any(keyword in m.lower() for keyword in ['dall-e', 'gpt-image', 'image'])]
            
            print(f"✅ Connected successfully!")
            print(f"📊 Total models available: {len(models)}")
            print(f"🖼️ Image models found: {len(image_models)}")
            
            for model in image_models:
                print(f"   - {model}")
            
            # Check specifically for GPT Image 1
            if "gpt-image-1" in models:
                print(f"✅ GPT Image 1 is available!")
                return True, "gpt-image-1"
            elif "dall-e-3" in models:
                print(f"✅ DALL-E 3 is available!")
                return True, "dall-e-3" 
            elif "dall-e-2" in models:
                print(f"✅ DALL-E 2 is available!")
                return True, "dall-e-2"
            else:
                print(f"❌ No image models found!")
                return False, None
                
        else:
            print(f"❌ Connection failed!")
            print(f"Error: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False, None

def test_backend_base_url():
    """Test backend's base URL configuration"""
    
    print(f"\n" + "="*60)
    print(f"🔍 CHECKING BACKEND BASE URL CONFIGURATION")
    
    # Check .env configuration
    from app.config.settings import settings
    
    print(f"📊 Backend Configuration:")
    print(f"   IMAGE_API_BASE_URL: {settings.IMAGE_API_BASE_URL}")
    print(f"   IMAGE_GENERATION_MODEL: {settings.IMAGE_GENERATION_MODEL}")
    
    # Test if backend URL matches OpenAI
    if settings.IMAGE_API_BASE_URL == "https://api.openai.com/v1":
        print(f"✅ Base URL correct for OpenAI!")
        return True
    else:
        print(f"❌ Base URL mismatch!")
        print(f"   Expected: https://api.openai.com/v1")
        print(f"   Current:  {settings.IMAGE_API_BASE_URL}")
        return False

def test_image_generation_direct():
    """Test direct image generation with available model"""
    
    print(f"\n" + "="*60)
    print(f"🔍 TESTING DIRECT IMAGE GENERATION")
    
    connection_ok, available_model = test_openai_connection()
    
    if not connection_ok or not available_model:
        print(f"❌ Cannot test - no image models available")
        return False
    
    print(f"\n🎯 Testing with model: {available_model}")
    
    # Build payload based on available model
    if available_model == "gpt-image-1":
        payload = {
            "model": "gpt-image-1",
            "prompt": "Professional photo of a water bottle",
            "n": 1,
            "size": "1024x1024",
            "quality": "high",
            "response_format": "url"
        }
    else:  # DALL-E models
        payload = {
            "model": available_model,
            "prompt": "Professional photo of a water bottle",
            "n": 1,
            "size": "1024x1024"
        }
        if available_model == "dall-e-3":
            payload.update({
                "quality": "hd",
                "style": "natural"
            })
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Organization": OPENAI_ORG,
        "Content-Type": "application/json"
    }
    
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Direct generation SUCCESS!")
            print(f"🖼️ Image URL: {result['data'][0]['url']}")
            if 'revised_prompt' in result['data'][0]:
                print(f"📝 Revised prompt: {result['data'][0]['revised_prompt']}")
            return True
        else:
            print(f"❌ Direct generation FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Direct generation error: {e}")
        return False

if __name__ == "__main__":
    print(f"🎯 OPENAI API VERIFICATION")
    print(f"=" * 60)
    
    # Test connection and models
    connection_ok, available_model = test_openai_connection()
    
    # Test backend configuration
    config_ok = test_backend_base_url()
    
    # Test direct generation if possible
    if connection_ok and available_model:
        generation_ok = test_image_generation_direct()
    else:
        generation_ok = False
    
    print(f"\n" + "="*60)
    print(f"🏁 VERIFICATION RESULTS:")
    print(f"📡 API Connection: {'✅ OK' if connection_ok else '❌ FAILED'}")
    print(f"🔧 Backend Config: {'✅ OK' if config_ok else '❌ NEEDS FIX'}")
    print(f"🖼️ Image Generation: {'✅ OK' if generation_ok else '❌ FAILED'}")
    
    if available_model:
        print(f"🎯 Recommended model: {available_model}")
    
    if not config_ok:
        print(f"\n🔧 SUGGESTED FIX:")
        print(f"Update .env file:")
        print(f"IMAGE_API_BASE_URL=https://api.openai.com/v1")
        if available_model:
            print(f"IMAGE_GENERATION_MODEL={available_model}")
