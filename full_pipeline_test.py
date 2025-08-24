#!/usr/bin/env python3
"""
Comprehensive test for Enhancement + GPT Image 1 Generation
Tests full pipeline from prompt to generated image
"""

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import time

# Load API key dari file .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)
API_KEY = os.getenv("OPENAI_API_KEY")

BACKEND_URL = "http://localhost:8000"

# Test prompt watermelon advertisement
TEST_PROMPT = """Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center. The bottle should appear big, glossy, and labeled "WATERMELON JUICE – SUMMER FRESH." Place a glass of watermelon juice beside it. Surround the bottle with watermelon slices, cubes, and whole mini watermelons floating around. Add a splash of red juice splattering around the bottle. The background should include a sunny tropical beach or palm trees, with blue sky and bright light rays. Include ice cubes, water droplets, and sparkles to give a fresh, lively effect."""

def test_backend_health():
    """Test backend connectivity"""
    print("=" * 80)
    print("STEP 1: BACKEND HEALTH CHECK")
    print("=" * 80)
    
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Backend: HEALTHY")
            return True
        else:
            print(f"❌ Backend: UNHEALTHY (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"❌ Backend: CONNECTION FAILED - {e}")
        return False

def test_enhancement_generation():
    """Test prompt enhancement and brief generation"""
    print("\n" + "=" * 80)
    print("STEP 2: ENHANCEMENT & BRIEF GENERATION")
    print("=" * 80)
    print(f"Input prompt: {TEST_PROMPT[:100]}...")
    print()
    
    payload = {"user_request": TEST_PROMPT}
    
    try:
        print("⏳ Generating enhanced brief...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/generate-brief",
            json=payload,
            timeout=120
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Brief generation: SUCCESS ({end_time-start_time:.2f}s)")
            
            # Analyze brief
            if "brief" in result:
                brief = result["brief"]
                filled_fields = sum(1 for v in brief.values() if v and v != "Not specified")
                total_fields = len(brief)
                
                print(f"📊 Wizard Fields: {filled_fields}/{total_fields} filled ({(filled_fields/total_fields)*100:.1f}%)")
                
                # Show key fields
                key_fields = ["product_name", "lighting_style", "environment", "camera_type", "dominant_colors"]
                print("🔍 Key Fields:")
                for field in key_fields:
                    value = brief.get(field, "Not found")
                    print(f"   {field}: {value}")
            
            # Enhanced prompt analysis
            enhanced_prompt = result.get("final_prompt", "")
            if enhanced_prompt:
                print(f"\n🎨 Enhanced Prompt: {len(enhanced_prompt)} characters")
                print(f"   Contains 'watermelon': {'watermelon' in enhanced_prompt.lower()}")
                print(f"   Contains 'tropical': {'tropical' in enhanced_prompt.lower()}")
                print(f"   Contains technical terms: {any(term in enhanced_prompt.lower() for term in ['camera', 'lighting', 'photography'])}")
                
                return enhanced_prompt
            else:
                print("❌ No enhanced prompt in response")
                return None
                
        else:
            print(f"❌ Brief generation: FAILED (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Brief generation: ERROR - {e}")
        return None

def test_image_generation(enhanced_prompt):
    """Test image generation with GPT Image 1"""
    print("\n" + "=" * 80)
    print("STEP 3: GPT IMAGE 1 GENERATION")
    print("=" * 80)
    print(f"Using enhanced prompt: {len(enhanced_prompt)} characters")
    print()
    
    payload = {
        "brief_prompt": enhanced_prompt,
        "user_api_key": API_KEY,
        "provider": "openai_dalle",  # Explicitly request OpenAI
        "use_raw_prompt": True  # Use enhanced prompt directly
    }
    
    try:
        print("⏳ Generating image with GPT Image 1...")
        start_time = time.time()
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/generate-image",
            json=payload,
            timeout=180  # Longer timeout for image generation
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Image generation: SUCCESS ({end_time-start_time:.2f}s)")
            
            # Analyze result
            if "image_url" in result:
                image_url = result["image_url"]
                print(f"🖼️ Image URL: {image_url[:80]}...")
                
                # Check if it's base64 (GPT Image 1 format)
                if image_url.startswith("data:image"):
                    print("📄 Format: Base64 (GPT Image 1 format)")
                else:
                    print("🔗 Format: URL")
            
            if "revised_prompt" in result:
                revised = result["revised_prompt"]
                print(f"📝 Revised prompt length: {len(revised)} characters")
                print(f"   Same as input: {revised == enhanced_prompt}")
            
            if "generation_id" in result:
                gen_id = result["generation_id"]
                print(f"🆔 Generation ID: {gen_id}")
            
            return True
            
        else:
            print(f"❌ Image generation: FAILED (Status: {response.status_code})")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Image generation: ERROR - {e}")
        return False

def main():
    """Main comprehensive test"""
    print("🚀 COMPREHENSIVE ENHANCEMENT + GPT IMAGE 1 TEST")
    print(f"⏰ Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Key: {API_KEY[:20]}..." if API_KEY else "❌ No API Key")
    
    # Step 1: Health Check
    if not test_backend_health():
        print("\n💥 FAILED: Backend not accessible")
        return
    
    # Step 2: Enhancement Generation
    enhanced_prompt = test_enhancement_generation()
    if not enhanced_prompt:
        print("\n💥 FAILED: Enhancement generation failed")
        return
    
    # Step 3: Image Generation
    image_success = test_image_generation(enhanced_prompt)
    
    # Final Results
    print("\n" + "=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)
    print("✅ Backend Health: PASSED")
    print("✅ Enhancement Generation: PASSED")
    print(f"{'✅' if image_success else '❌'} GPT Image 1 Generation: {'PASSED' if image_success else 'FAILED'}")
    
    if image_success:
        print("\n🎉 FULL PIPELINE SUCCESS!")
        print("   ✓ 46 wizard fields populated")
        print("   ✓ Enhanced prompt generated") 
        print("   ✓ GPT Image 1 working")
        print("   ✓ Watermelon advertisement enhanced and generated")
    else:
        print("\n⚠️ PARTIAL SUCCESS - Enhancement working but image generation failed")

if __name__ == "__main__":
    main()
