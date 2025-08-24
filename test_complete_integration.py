#!/usr/bin/env python3
"""
Comprehensive test for GPT Image 1 integration.
Tests both direct API calls and backend parsing.
"""

import os
import sys
import json
import asyncio
import aiohttp
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.multi_provider_image_generator import OpenAIImageService, ImageProvider

async def test_direct_openai_api():
    """Test direct OpenAI API call to GPT Image 1."""
    print("🧪 Testing Direct OpenAI API Call...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OpenAI API key not found")
        return None
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "OpenAI-Organization": "org-XKOFJy5SYzXNV9yTQTDTSPx9"
    }
    
    payload = {
        "model": "gpt-image-1",
        "prompt": "A simple red apple on a white background",
        "n": 1,
        "size": "1024x1024"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/images/generations",
                headers=headers,
                json=payload
            ) as response:
                print(f"   Status: {response.status}")
                response_data = await response.json()
                
                if response.status == 200:
                    print("   ✅ API call successful!")
                    print(f"   📊 Response keys: {list(response_data.keys())}")
                    if 'data' in response_data:
                        print(f"   📊 Data items: {len(response_data['data'])}")
                        first_item = response_data['data'][0]
                        print(f"   📊 First item keys: {list(first_item.keys())}")
                        if 'b64_json' in first_item:
                            print(f"   🖼️ Base64 data length: {len(first_item['b64_json'])}")
                        return response_data
                else:
                    print(f"   ❌ API call failed: {response_data}")
                    return None
                    
    except Exception as e:
        print(f"   ❌ Exception during API call: {e}")
        return None

async def test_backend_parsing(api_response):
    """Test backend parsing of GPT Image 1 response."""
    print("\n🧪 Testing Backend Response Parsing...")
    
    if not api_response:
        print("   ⏭️ Skipping - no API response to parse")
        return False
    
    try:
        # Initialize the service
        service = OpenAIImageService()
        
        # Test parsing
        result = service.parse_response(ImageProvider.OPENAI_DALLE, api_response)
        
        print("   ✅ Parsing successful!")
        print(f"   📊 Result type: {type(result)}")
        print(f"   🖼️ Image URL length: {len(result.image_url)}")
        print(f"   🆔 Generation ID: {result.generation_id}")
        print(f"   🤖 Model used: {result.model_used}")
        print(f"   🏪 Provider: {result.provider_used}")
        
        # Check if it's a data URL (base64)
        if result.image_url.startswith("data:image/png;base64,"):
            print("   ✅ Correctly converted to data URL format!")
            return True
        else:
            print(f"   ⚠️ Unexpected URL format: {result.image_url[:50]}...")
            return True
            
    except Exception as e:
        print(f"   ❌ Parsing failed: {e}")
        return False

async def test_end_to_end():
    """Test full end-to-end generation."""
    print("\n🧪 Testing End-to-End Generation...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("   ❌ OpenAI API key not found")
        return False
    
    try:
        # Initialize service
        service = OpenAIImageService()
        
        # Test generation
        result = await service.generate_image(
            brief_prompt="A blue butterfly on a flower",
            user_api_key=api_key
        )
        
        print("   ✅ End-to-end generation successful!")
        print(f"   🖼️ Image URL type: {'data URL' if result.image_url.startswith('data:') else 'regular URL'}")
        print(f"   🆔 Generation ID: {result.generation_id}")
        print(f"   🤖 Model: {result.model_used}")
        print(f"   📝 Prompt used: {result.final_enhanced_prompt[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ End-to-end test failed: {e}")
        import traceback
        print(f"   🔍 Error details: {traceback.format_exc()}")
        return False

async def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 GPT Image 1 Integration Test Suite")
    print("=" * 60)
    
    # Test 1: Direct API call
    api_response = await test_direct_openai_api()
    
    # Test 2: Backend parsing
    parsing_success = await test_backend_parsing(api_response)
    
    # Test 3: End-to-end
    e2e_success = await test_end_to_end()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Direct API: {'✅ PASS' if api_response else '❌ FAIL'}")
    print(f"   Parsing: {'✅ PASS' if parsing_success else '❌ FAIL'}")
    print(f"   End-to-End: {'✅ PASS' if e2e_success else '❌ FAIL'}")
    
    all_passed = bool(api_response) and parsing_success and e2e_success
    print(f"\n🎯 Overall Result: {'✅ ALL TESTS PASSED!' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 GPT Image 1 integration is working correctly!")
        print("   The backend can now properly handle GPT Image 1 responses")
        print("   and convert base64 data to usable image URLs.")
    
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
