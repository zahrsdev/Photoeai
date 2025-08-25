"""
🎯 TASK 3: Test 2-Step Flow Implementation
FOKUS: Test GPT-4o Vision → DALL-E 3 flow
JANGAN OVER ENGINEER!
"""

import asyncio
import sys
import os
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.multi_provider_image_generator import OpenAIImageService

async def test_task3_flow():
    """
    🎯 TASK 3: Simple flow test
    """
    
    logger.info("🎯 TASK 3 START: Testing 2-step flow implementation")
    
    # Initialize service
    service = OpenAIImageService()
    
    # Test data
    test_prompt = "Professional product photography of a water bottle with mountain backdrop, golden hour lighting"
    test_api_key = "sk-test-key-replace-with-real-key"  # Boss ganti dengan key asli
    
    print("\n" + "="*60)
    print("🎯 TASK 3: 2-STEP FLOW TEST")
    print("="*60)
    
    # TEST 1: No image (text-only flow)
    print("\n📝 TEST 1: Text-only flow (no image)")
    print("-" * 40)
    
    try:
        result1 = await service.generate_image(
            brief_prompt=test_prompt,
            user_api_key=test_api_key,
            uploaded_image_base64=None  # No image
        )
        
        print("✅ TEST 1 RESULT:")
        print(f"  - Image URL: {result1.image_url[:50]}..." if result1.image_url else "  - No image URL")
        print(f"  - Model Used: {result1.model_used}")
        print(f"  - Provider: {result1.provider_used}")
        print(f"  - Generation ID: {result1.generation_id}")
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
    
    # TEST 2: Base64 image processing
    print("\n📸 TEST 2: Base64 image conversion")
    print("-" * 40)
    
    try:
        # Test base64 conversion (dummy path - Boss ganti dengan path asli)
        test_image_path = "test_image.jpg"  # Boss ganti dengan image path asli
        
        if os.path.exists(test_image_path):
            base64_img = service.load_image_as_base64(test_image_path)
            validated_img = service.validate_and_resize_image(base64_img)
            
            print("✅ TEST 2 RESULT:")
            print(f"  - Base64 length: {len(base64_img)} chars")
            print(f"  - Validated length: {len(validated_img)} chars")
            
            # TEST 3: Full 2-step flow with image
            print("\n🎨 TEST 3: Full 2-step flow (Vision + DALL-E 3)")
            print("-" * 40)
            
            result3 = await service.generate_image(
                brief_prompt=test_prompt,
                user_api_key=test_api_key,
                uploaded_image_base64=validated_img  # With image
            )
            
            print("✅ TEST 3 RESULT:")
            print(f"  - Image URL: {result3.image_url[:50]}..." if result3.image_url else "  - No image URL")
            print(f"  - Enhanced Prompt Length: {len(result3.final_enhanced_prompt)} chars")
            print(f"  - Revised Prompt: {result3.revised_prompt[:100]}...")
            
        else:
            print(f"⚠️  TEST 2 SKIPPED: Image file not found: {test_image_path}")
            print("   Boss, ganti test_image_path dengan path image yang ada!")
    
    except Exception as e:
        print(f"❌ TEST 2/3 FAILED: {e}")
    
    print("\n" + "="*60)
    print("🎯 TASK 3 COMPLETE: Flow test finished")
    print("="*60)

if __name__ == "__main__":
    print("🎯 TASK 3: Starting flow test...")
    print("⚠️  BOSS: Ganti test_api_key dengan OpenAI API key asli!")
    print("⚠️  BOSS: Ganti test_image_path dengan path image yang ada!")
    
    asyncio.run(test_task3_flow())
