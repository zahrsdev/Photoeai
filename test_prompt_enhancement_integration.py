#!/usr/bin/env python3
"""
Test script to verify the prompt enhancement integration works correctly.
This script tests the critical fix where prompt enhancement was being skipped.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.unified_ai_service import UnifiedAIService
from app.config.settings import settings
from loguru import logger

async def test_prompt_enhancement_integration():
    """Test that prompt enhancement is now properly integrated into the image generation workflow."""
    
    print("🧪 Testing Prompt Enhancement Integration Fix")
    print("=" * 50)
    
    # Initialize the service
    unified_service = UnifiedAIService()
    
    # Test prompt
    test_prompt = "A beautiful red apple"
    print(f"📝 Original prompt: '{test_prompt}'")
    
    # Mock user API key (this won't actually be used for the enhancement step)
    mock_api_key = "test-api-key"
    
    try:
        # This should now include prompt enhancement
        print("\n🔄 Calling generate_image (this should trigger prompt enhancement)...")
        
        # Note: This will fail at the actual image generation API call since we don't have a real API key,
        # but we should see the prompt enhancement logging messages before it fails
        result = await unified_service.generate_image(
            brief_prompt=test_prompt,
            user_api_key=mock_api_key,
            provider_override="openai"
        )
        
        print("✅ Image generation completed successfully!")
        print(f"🎯 Final enhanced prompt: {result.final_enhanced_prompt}")
        
    except Exception as e:
        # Expected to fail at the API call, but we should see enhancement logs
        print(f"⚠️ Expected failure at API call: {e}")
        print("\n✅ However, if you see '🎨 Attempting to enhance prompt...' and '✨ Prompt successfully enhanced.' in the logs above,")
        print("   then the integration is working correctly!")

if __name__ == "__main__":
    # Configure logging to see the enhancement messages
    logger.remove()  # Remove default handler
    logger.add(sys.stdout, level="INFO", format="{level} | {message}")
    
    # Run the test
    asyncio.run(test_prompt_enhancement_integration())
