#!/usr/bin/env python3
"""
Test OpenAI API directly to check available models and base URL
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def test_openai_models():
    """Test OpenAI models endpoint"""
    
    print(f"🔍 TESTING OPENAI API MODELS ENDPOINT")
    print(f"=" * 60)
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Organization": "org-XKOFJy5SYzXNV9yTQTDTSPx9"  # Your org ID
    }
    
    try:
        response = requests.get(
            "https://api.openai.com/v1/models",
            headers=headers,
            timeout=30
        )
        
        print(f"📊 Models API Status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            
            print(f"✅ API Connection: SUCCESS")
            print(f"🎯 Total Models: {len(models.get('data', []))}")
            
            # Look for image generation models
            image_models = []
            for model in models.get('data', []):
                model_id = model.get('id', '')
                if any(keyword in model_id.lower() for keyword in ['image', 'dall', 'gpt-image']):
                    image_models.append(model_id)
            
            if image_models:
                print(f"\n🖼️ AVAILABLE IMAGE MODELS:")
                for model in image_models:
                    print(f"  ✅ {model}")
            else:
                print(f"\n❌ No image models found in list")
                
            # Show first 10 models for reference
            print(f"\n📋 FIRST 10 MODELS (sample):")
            for i, model in enumerate(models.get('data', [])[:10]):
                print(f"  {i+1}. {model.get('id')}")
                
        else:
            print(f"❌ API Connection: FAILED")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ API Test Error: {e}")

def test_image_generation_direct():
    """Test image generation directly"""
    
    print(f"\n" + "="*60)
    print(f"🔍 TESTING IMAGE GENERATION DIRECTLY")
    
    # Try with different models
    models_to_test = ["dall-e-3", "gpt-image-1"]
    
    for model in models_to_test:
        print(f"\n🎯 Testing model: {model}")
        
        payload = {
            "model": model,
            "prompt": "A simple red apple on white background",
            "n": 1,
            "size": "1024x1024",
            "quality": "standard"
        }
        
        if model == "gpt-image-1":
            payload["response_format"] = "url"
            payload["quality"] = "high"
        elif model == "dall-e-3":
            payload["style"] = "natural"
            payload["quality"] = "hd"
        
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
            "OpenAI-Organization": "org-XKOFJy5SYzXNV9yTQTDTSPx9"
        }
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/images/generations",
                json=payload,
                headers=headers,
                timeout=60
            )
            
            print(f"  📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ {model}: SUCCESS!")
                print(f"  🖼️ Image URL: {result['data'][0]['url']}")
                if result['data'][0].get('revised_prompt'):
                    print(f"  📝 Revised: {result['data'][0]['revised_prompt'][:100]}...")
            else:
                print(f"  ❌ {model}: FAILED")
                print(f"  Error: {response.text}")
                
        except Exception as e:
            print(f"  ❌ {model}: Exception - {e}")

if __name__ == "__main__":
    print(f"🎯 OPENAI API CONNECTION TEST")
    print(f"🔑 API Key: {OPENAI_API_KEY[:12]}...")
    print(f"🌐 Base URL: https://api.openai.com/v1")
    print(f"🏢 Organization: org-XKOFJy5SYzXNV9yTQTDTSPx9")
    
    test_openai_models()
    test_image_generation_direct()
