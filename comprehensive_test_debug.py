#!/usr/bin/env python3
"""
Comprehensive test to diagnose image generation issues and verify complete results.
"""

import asyncio
import json
import os
from app.services.multi_provider_image_generator import MultiProviderImageService, ImageProvider
from app.config.settings import settings

async def test_comprehensive_image_generation():
    """Test complete image generation workflow to identify any issues."""
    
    print("=== COMPREHENSIVE IMAGE GENERATION TEST ===\n")
    
    # Initialize service
    service = MultiProviderImageService()
    
    # Your test prompt
    test_prompt = """A luxurious, cinematic product photography scene featuring the "ELITE LUXURY PERFUME" bottle, captured with a Canon EOS R5 and Canon RF 100mm f/2.8L Macro IS USM lens for ultra-sharp detail and rich textures, framed in a vertical orientation with a tight crop that centers the crystal-clear glass bottle and gold cap, occupying 60% of the frame against a seamless matte black backdrop."""
    
    print(f"📝 Original prompt length: {len(test_prompt)} characters")
    print(f"📝 Original prompt:\n{test_prompt}\n")
    
    # Test 1: Payload Construction
    print("=== TEST 1: PAYLOAD CONSTRUCTION ===")
    payload = service.build_request_payload(
        provider=ImageProvider.OPENAI_DALLE,
        brief_prompt=test_prompt,
        negative_prompt=None,
        model="dall-e-3"
    )
    
    print(f"✅ Payload constructed successfully")
    print(f"📦 Payload keys: {list(payload.keys())}")
    
    # Test JSON serialization
    try:
        json_payload = json.dumps(payload, indent=2, ensure_ascii=False)
        print(f"✅ JSON serialization successful")
        print(f"📄 Final JSON payload:\n{json_payload}\n")
    except Exception as e:
        print(f"❌ JSON serialization failed: {e}")
        return
    
    # Test 2: Check API Key
    print("=== TEST 2: API KEY CHECK ===")
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ No OpenAI API key found in environment variables")
        print("💡 Please set OPENAI_API_KEY environment variable")
        return
    else:
        print("✅ OpenAI API key found in environment variables")
    if openai_key and openai_key.startswith('sk-'):
        print(f"✅ OpenAI API key found (starts with 'sk-')")
        key_preview = f"{openai_key[:10]}...{openai_key[-4:]}"
        print(f"🔑 Key preview: {key_preview}")
    else:
        print(f"❌ No valid OpenAI API key found")
        print(f"💡 Please set OPENAI_API_KEY environment variable")
        return
    
    # Test 3: Check Settings
    print("=== TEST 3: SETTINGS CHECK ===")
    print(f"🔧 Image API Base URL: {settings.IMAGE_API_BASE_URL}")
    print(f"🔧 Image Generation Model: {settings.IMAGE_GENERATION_MODEL}")
    print(f"🔧 Default Provider: {service.detect_provider(settings.IMAGE_API_BASE_URL).value}")
    
    # Test 4: Provider Detection and URL Construction
    print("\n=== TEST 4: PROVIDER & ENDPOINT CHECK ===")
    provider = ImageProvider.OPENAI_DALLE
    base_url = service.api_base_url
    endpoint = f"{base_url.rstrip('/')}{service.get_endpoint_path(provider)}"
    
    print(f"🎯 Provider: {provider.value}")
    print(f"🔗 Base URL: {base_url}")
    print(f"🔗 Full endpoint: {endpoint}")
    
    # Test 5: Headers Construction
    print("\n=== TEST 5: HEADERS CHECK ===")
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json"
    }
    print(f"📋 Headers: {list(headers.keys())}")
    if 'Authorization' in headers:
        auth_preview = f"{headers['Authorization'][:20]}...{headers['Authorization'][-10:]}"
        print(f"🔐 Authorization: {auth_preview}")
    
    # Test 6: Attempt actual image generation (optional)
    print("\n=== TEST 6: ACTUAL GENERATION TEST ===")
    try_generation = input("🤔 Do you want to attempt actual image generation? This will use API credits. (y/n): ")
    
    if try_generation.lower() == 'y':
        try:
            print("🎨 Attempting image generation...")
            result = await service.generate_image(
                brief_prompt=test_prompt,
                user_api_key=openai_key,
                provider_override="openai_dalle"
            )
            
            print(f"✅ Image generation successful!")
            print(f"🖼️ Image URL: {result.image_url}")
            print(f"📝 Final enhanced prompt length: {len(result.final_enhanced_prompt)} characters")
            print(f"📝 Final enhanced prompt preview: {result.final_enhanced_prompt[:200]}...")
            
            if hasattr(result, 'revised_prompt') and result.revised_prompt != result.final_enhanced_prompt:
                print(f"🔄 DALL-E revised prompt: {result.revised_prompt[:200]}...")
            
        except Exception as e:
            print(f"❌ Image generation failed: {e}")
            print(f"💡 Check the logs above for detailed error information")
    
    print("\n=== COMPREHENSIVE TEST COMPLETE ===")
    print("If you're still not getting comprehensive results, the issue might be:")
    print("1. API rate limits or quota exceeded")
    print("2. Prompt enhancement or compression removing important details")  
    print("3. API response parsing issues")
    print("4. Network connectivity problems")

if __name__ == "__main__":
    asyncio.run(test_comprehensive_image_generation())
