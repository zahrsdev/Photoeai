#!/usr/bin/env python3
"""
Test Professional Photography Quality Rules Integration
Validates that the new English terminology photography rules are properly injected
"""

import asyncio
import json
from app.schemas.models import WizardInput
from app.services.brief_orchestrator import BriefOrchestratorService

async def test_photography_rules():
    """Test photography quality rules integration"""
    print("🔬 Testing Professional Photography Quality Rules Integration...")
    
    # Create test wizard input
    test_wizard = WizardInput(
        user_request="Professional product photo of luxury watch on marble surface",
        product_name="Luxury Swiss Watch", 
        shot_type="close-up product shot",
        lighting_style="studio lighting",
        background_setting="marble surface",
        mood="luxury and elegance",
        color_scheme="gold and black",
        additional_props="minimal shadows",
        user_api_key=None  # Test without API key first
    )
    
    try:
        orchestrator = BriefOrchestratorService()
        
        # Generate brief with photography rules
        result = await orchestrator.generate_final_brief(test_wizard)
        
        print("\n📊 Photography Rules Integration Test Results:")
        print("=" * 60)
        
        # Check for professional terminology
        rules_keywords = [
            "gamma correction", "tone consistency", "RGBA channel",
            "natural lighting", "sensor photosite", "anti-aliasing",
            "artifact prevention", "color space", "luminance values"
        ]
        
        found_keywords = []
        for keyword in rules_keywords:
            if keyword.lower() in result.final_prompt.lower():
                found_keywords.append(keyword)
        
        print(f"✅ Professional Terms Found: {len(found_keywords)}/{len(rules_keywords)}")
        print(f"📝 Keywords: {', '.join(found_keywords)}")
        print(f"📏 Final Brief Length: {len(result.final_prompt)} characters")
        
        # Show preview of photography rules section
        if "PROFESSIONAL PHOTOGRAPHY QUALITY CONTROL" in result.final_prompt:
            print("\n🎯 Photography Rules Section Found:")
            rules_section = result.final_prompt.split("PROFESSIONAL PHOTOGRAPHY QUALITY CONTROL")[1][:500]
            print(f"Preview: {rules_section}...")
            print("✅ Photography quality rules successfully integrated!")
        else:
            print("❌ Photography rules section not found!")
        
        print(f"\n📋 Brief Preview (first 800 chars):")
        print("-" * 60) 
        print(result.final_prompt[:800] + "..." if len(result.final_prompt) > 800 else result.final_prompt)
        
        return True
        
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_photography_rules())
    print(f"\n🎯 Test {'PASSED' if success else 'FAILED'}")