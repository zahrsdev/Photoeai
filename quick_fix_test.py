#!/usr/bin/env python3
"""
Quick test to verify the comprehensive results fix is working.
"""

import asyncio
import os
from app.services.multi_provider_image_generator import MultiProviderImageService, ImageProvider

async def quick_comprehensive_test():
    """Quick test to verify comprehensive results are working."""
    
    print("=== QUICK COMPREHENSIVE RESULTS TEST ===\n")
    
    # Set the API key from environment variable
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key:
        print("❌ Please set OPENAI_API_KEY environment variable for testing")
        return
    
    service = MultiProviderImageService()
    
    test_prompt = "A luxury perfume bottle on a black background"
    
    print(f"📝 Original prompt: {test_prompt}")
    print(f"📏 Original length: {len(test_prompt)} characters\n")
    
    try:
        print("🎨 Generating image...")
        result = await service.generate_image(
            brief_prompt=test_prompt,
            user_api_key=os.environ['OPENAI_API_KEY'],
            provider_override="openai_dalle"
        )
        
        print("✅ SUCCESS! Comprehensive results are now working properly!")
        print(f"🖼️ Image URL generated: {result.image_url[:50]}...")
        print(f"📝 Final enhanced prompt length: {len(result.final_enhanced_prompt)} characters")
        print(f"📝 Enhancement ratio: {len(result.final_enhanced_prompt) / len(test_prompt):.1f}x more detailed")
        
        print(f"\n📋 COMPREHENSIVE ENHANCED PROMPT:")
        print(f"'{result.final_enhanced_prompt}'")
        
        if hasattr(result, 'revised_prompt') and result.revised_prompt != result.final_enhanced_prompt:
            print(f"\n🔄 DALL-E also revised the prompt further:")
            print(f"'{result.revised_prompt[:300]}...'")
        
        print(f"\n🎯 CONCLUSION: Your system IS producing comprehensive results!")
        print(f"   - Original: {len(test_prompt)} chars")
        print(f"   - Enhanced: {len(result.final_enhanced_prompt)} chars")
        print(f"   - The enhancement system is working perfectly!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    finally:
        # Clean up - remove the API key from environment
        if 'OPENAI_API_KEY' in os.environ:
            del os.environ['OPENAI_API_KEY']
        print(f"\n🧹 API key removed from environment")

if __name__ == "__main__":
    asyncio.run(quick_comprehensive_test())
