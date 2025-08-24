#!/usr/bin/env python3
"""
Test script untuk menguji backend dan frontend dengan enhancement prompt
untuk memastikan sistem bekerja dengan baik dengan GPT Image 1
"""

import os
import requests
import json
import time
from datetime import datetime

# Set API key
API_KEY = "sk-YOUR-API-KEY-HERE"
os.environ["OPENAI_API_KEY"] = API_KEY

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Test prompt
TEST_PROMPT = """Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center. The bottle should appear big, glossy, and labeled "WATERMELON JUICE – SUMMER FRESH." Place a glass of watermelon juice beside it. Surround the bottle with watermelon slices, cubes, and whole mini watermelons floating around. Add a splash of red juice splattering around the bottle. The background should include a sunny tropical beach or palm trees, with blue sky and bright light rays. Include ice cubes, water droplets, and sparkles to give a fresh, lively effect."""

def test_backend_health():
    """Test apakah backend berjalan dengan baik"""
    print("🔍 Testing backend health...")
    try:
        response = requests.get(f"{BACKEND_URL}/")
        print(f"✅ Backend response: {response.status_code}")
        print(f"📄 Response data: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend tidak berjalan! Jalankan server terlebih dahulu.")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_openai_direct():
    """Test koneksi OpenAI secara langsung"""
    print("\n🔍 Testing direct OpenAI connection...")
    try:
        import openai
        
        client = openai.OpenAI(api_key=API_KEY)
        
        # Test dengan simple completion
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Just say 'OpenAI connection working'"}
            ],
            max_tokens=10
        )
        
        print(f"✅ OpenAI direct test successful")
        print(f"📄 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI direct test failed: {e}")
        return False

def test_brief_generation():
    """Test endpoint /api/v1/generate-brief dengan enhancement prompt"""
    print("\n🔍 Testing brief generation with enhancement prompt...")
    
    payload = {
        "user_request": TEST_PROMPT
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"📤 Sending request to: {BACKEND_URL}/api/v1/generate-brief")
        print(f"📋 Payload: {json.dumps(payload, indent=2)}")
        
        start_time = time.time()
        response = requests.post(
            f"{BACKEND_URL}/api/v1/generate-brief",
            json=payload,
            headers=headers,
            timeout=60
        )
        end_time = time.time()
        
        print(f"⏱️ Response time: {end_time - start_time:.2f} seconds")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Brief generation successful!")
            
            # Print enhanced prompt
            if "enhanced_prompt" in result:
                print("\n🎨 ENHANCED PROMPT:")
                print("=" * 80)
                print(result["enhanced_prompt"])
                print("=" * 80)
            
            # Print brief sections
            if "brief" in result:
                brief = result["brief"]
                print("\n📋 GENERATED BRIEF SECTIONS:")
                print("-" * 50)
                
                for section, content in brief.items():
                    if content and content != "Not specified":
                        print(f"\n{section.upper().replace('_', ' ')}:")
                        print(f"  {content}")
            
            return True
        else:
            print(f"❌ Brief generation failed with status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Request timeout (60 seconds)")
        return False
    except Exception as e:
        print(f"❌ Error testing brief generation: {e}")
        return False

def test_image_generation():
    """Test endpoint /api/v1/generate-image dengan GPT Image 1"""
    print("\n🔍 Testing image generation with GPT Image 1...")
    
    # First generate a brief
    brief_payload = {"user_request": TEST_PROMPT}
    
    try:
        brief_response = requests.post(
            f"{BACKEND_URL}/api/v1/generate-brief",
            json=brief_payload,
            timeout=60
        )
        
        if brief_response.status_code != 200:
            print("❌ Failed to generate brief for image test")
            return False
        
        brief_result = brief_response.json()
        enhanced_prompt = brief_result.get("enhanced_prompt", TEST_PROMPT)
        
        # Now test image generation
        image_payload = {
            "prompt": enhanced_prompt,
            "model": "dall-e-3",
            "size": "1024x1024",
            "quality": "standard",
            "style": "vivid"
        }
        
        print(f"📤 Sending image generation request...")
        print(f"🎨 Using enhanced prompt (first 200 chars): {enhanced_prompt[:200]}...")
        
        start_time = time.time()
        image_response = requests.post(
            f"{BACKEND_URL}/api/v1/generate-image",
            json=image_payload,
            timeout=120
        )
        end_time = time.time()
        
        print(f"⏱️ Image generation time: {end_time - start_time:.2f} seconds")
        print(f"📊 Status code: {image_response.status_code}")
        
        if image_response.status_code == 200:
            result = image_response.json()
            print("✅ Image generation successful!")
            
            if "image_url" in result:
                print(f"🖼️ Image URL: {result['image_url']}")
            
            if "revised_prompt" in result:
                print(f"\n📝 Revised prompt by DALL-E:")
                print(f"   {result['revised_prompt'][:200]}...")
            
            return True
        else:
            print(f"❌ Image generation failed with status: {image_response.status_code}")
            print(f"📄 Response: {image_response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing image generation: {e}")
        return False

def main():
    """Main test function"""
    print(f"🚀 PhotoeAI Backend & Frontend Test")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Test 1: Backend Health
    if not test_backend_health():
        print("\n❌ Backend tidak berjalan. Silakan start backend terlebih dahulu:")
        print("   cd photoeai-backend && python run.py")
        return
    
    # Test 2: OpenAI Direct Connection
    if not test_openai_direct():
        print("\n❌ Koneksi OpenAI gagal. Periksa API key.")
        return
    
    # Test 3: Brief Generation with Enhancement
    brief_success = test_brief_generation()
    
    # Test 4: Image Generation with GPT Image 1
    image_success = test_image_generation()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY:")
    print(f"   Backend Health: ✅")
    print(f"   OpenAI Connection: ✅")
    print(f"   Brief Generation: {'✅' if brief_success else '❌'}")
    print(f"   Image Generation: {'✅' if image_success else '❌'}")
    
    if brief_success and image_success:
        print("\n🎉 ALL TESTS PASSED! Sistema enhancement prompt bekerja dengan baik!")
    else:
        print("\n⚠️ Some tests failed. Check logs for details.")

if __name__ == "__main__":
    main()
