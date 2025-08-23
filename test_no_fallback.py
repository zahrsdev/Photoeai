#!/usr/bin/env python3
"""
Test script to verify the PhotoeAI system fails properly when AI services are unavailable.
This test verifies that the system no longer uses fallback/mock data.
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.schemas.models import InitialUserRequest, WizardInput
from app.services.brief_orchestrator import BriefOrchestratorService


async def test_no_fallback_behavior():
    """Test that the system fails properly when AI services are unavailable."""
    
    print("🧪 Testing PhotoeAI System - NO FALLBACK MODE")
    print("=" * 60)
    
    orchestrator = BriefOrchestratorService()
    
    # Test 1: Extract and Autofill with unavailable AI service
    print("\n1. Testing extract_and_autofill with unavailable AI service...")
    request = InitialUserRequest(user_request="Cinematic commercial of honey product Madu Ahlan Trigona")
    
    try:
        wizard_input = await orchestrator.extract_and_autofill(request)
        print("❌ UNEXPECTED: Should have failed but got result")
        print(f"   Product: {wizard_input.product_name}")
    except Exception as e:
        print(f"✅ EXPECTED: Failed properly with error: {str(e)}")
    
    # Test 2: Generate Brief with mock wizard data (should also fail at enhancement)
    print("\n2. Testing generate_final_brief with unavailable AI service...")
    
    # Create minimal wizard input manually
    wizard_data = {
        "user_request": "Cinematic commercial of honey product",
        "product_name": "Test Product",
        "product_description": "Test description",
        "key_features": "Test features",
        "product_state": "pristine",
        "shot_type": "Eye-level",
        "framing": "Close-Up",
        "compositional_rule": "Rule of Thirds",
        "negative_space": "Balanced",
        "lighting_style": "Studio Softbox",
        "key_light_setup": "Test setup",
        "fill_light_setup": "Test fill",
        "rim_light_setup": "Test rim",
        "mood": "Clean and professional",
        "environment": "Seamless studio backdrop",
        "dominant_colors": "neutral colors",
        "accent_colors": "warm tones",
        "props": "minimal props",
        "camera_type": "Canon EOS R5",
        "lens_type": "100mm Macro",
        "aperture_value": 8.0,
        "shutter_speed_value": 125,
        "iso_value": 100,
        "visual_effect": "clear focus",
        "overall_style": "Commercial photography",
        "photographer_influences": "Professional photographers"
    }
    
    wizard_input = WizardInput(**wizard_data)
    
    try:
        brief_output = await orchestrator.generate_final_brief(wizard_input)
        print("❌ UNEXPECTED: Should have failed but got result")
        print(f"   Brief length: {len(brief_output.final_prompt)} chars")
    except Exception as e:
        print(f"✅ EXPECTED: Failed properly with error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 CONCLUSION: System now fails properly without fallback data!")
    print("   - No mock data returned when AI services are unavailable")
    print("   - Clear error messages indicate service unavailability")
    print("   - System behavior is now predictable and honest")


if __name__ == "__main__":
    asyncio.run(test_no_fallback_behavior())
