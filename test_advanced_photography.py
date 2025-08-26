#!/usr/bin/env python3
"""
Test Professional Photography Rules with User API Key
Validates that photography rules work with dynamic API key system
"""

import asyncio
import os
from app.schemas.models import WizardInput
from app.services.brief_orchestrator import BriefOrchestratorService

async def test_with_user_api_key():
    """Test photography rules with user's API key"""
    print("🔑 Testing Photography Rules with User API Key...")
    
    # Check if user has API key in environment
    user_api_key = os.getenv('OPENAI_API_KEY')
    if not user_api_key:
        print("⚠️  No OPENAI_API_KEY found in environment. Testing without API key...")
        user_api_key = None
    else:
        print("✅ User API key found, testing dynamic API key system")
    
    # Create test wizard with complex photography requirements
    test_wizard = WizardInput(
        user_request="Create professional beauty shot of skincare serum with natural lighting, clear logo visibility, and premium feel",
        product_name="Premium Anti-Aging Serum",
        shot_type="beauty product hero shot",
        lighting_style="natural window light",
        background_setting="clean white marble",
        mood="fresh and natural",
        color_scheme="soft gold and white",
        additional_props="water droplets for freshness",
        user_api_key=user_api_key
    )
    
    try:
        orchestrator = BriefOrchestratorService()
        result = await orchestrator.generate_final_brief(test_wizard)
        
        print("\n📊 Professional Photography Analysis:")
        print("=" * 60)
        
        # Check specific photography terminology integration
        advanced_terms = [
            "gamma correction", "luminance values", "color temperature",
            "sensor photosite", "sub-pixel precision", "anti-aliasing",
            "light ray casting", "ambient occlusion", "natural depth of field",
            "compression artifacts", "bokeh characteristics"
        ]
        
        found_advanced = [term for term in advanced_terms if term.lower() in result.final_prompt.lower()]
        
        print(f"🎯 Advanced Photography Terms: {len(found_advanced)}/{len(advanced_terms)}")
        print(f"📝 Terms Found: {', '.join(found_advanced)}")
        
        # Check for specific user requirements integration
        user_requirements = ["logo visibility", "natural lighting", "premium feel"]
        found_requirements = [req for req in user_requirements if req.lower() in result.final_prompt.lower()]
        
        print(f"✅ User Requirements Integrated: {len(found_requirements)}/{len(user_requirements)}")
        print(f"📋 Requirements: {', '.join(found_requirements)}")
        
        # Analyze brief structure
        sections = result.final_prompt.count('##')
        words = len(result.final_prompt.split())
        
        print(f"📏 Brief Structure:")
        print(f"   - Total Sections: {sections}")
        print(f"   - Word Count: {words}")
        print(f"   - Character Count: {len(result.final_prompt)}")
        
        # Show photography rules section
        if "PROFESSIONAL PHOTOGRAPHY QUALITY CONTROL" in result.final_prompt:
            print(f"\n🎨 Photography Quality Section:")
            rules_start = result.final_prompt.find("PROFESSIONAL PHOTOGRAPHY QUALITY CONTROL")
            rules_section = result.final_prompt[rules_start:rules_start + 1000]
            print("-" * 50)
            print(rules_section + "...")
            
        return True
        
    except Exception as e:
        print(f"❌ Test Failed: {str(e)}")
        return False

async def test_multiple_scenarios():
    """Test multiple photography scenarios"""
    scenarios = [
        {
            "name": "Tech Product",
            "wizard": WizardInput(
                user_request="Professional tech product shot of smartphone with clean reflections",
                product_name="Premium Smartphone",
                shot_type="tech product photography",
                lighting_style="studio lighting",
                background_setting="gradient background",
                mood="modern and sleek",
                color_scheme="black and silver",
                additional_props="minimal shadows"
            )
        },
        {
            "name": "Food Product", 
            "wizard": WizardInput(
                user_request="Appetizing food photography of artisan chocolate with natural textures",
                product_name="Artisan Dark Chocolate",
                shot_type="food photography",
                lighting_style="natural daylight",
                background_setting="rustic wooden surface",
                mood="artisanal and warm",
                color_scheme="rich brown and gold",
                additional_props="coffee beans as props"
            )
        }
    ]
    
    orchestrator = BriefOrchestratorService()
    
    for scenario in scenarios:
        print(f"\n🎬 Testing {scenario['name']} Scenario...")
        try:
            result = await orchestrator.generate_final_brief(scenario['wizard'])
            
            # Quick validation
            has_rules = "PROFESSIONAL PHOTOGRAPHY QUALITY CONTROL" in result.final_prompt
            rules_count = sum(1 for term in ["gamma correction", "natural lighting", "color space"] 
                            if term.lower() in result.final_prompt.lower())
            
            print(f"   ✅ Rules Integrated: {'Yes' if has_rules else 'No'}")
            print(f"   🎯 Key Terms Found: {rules_count}/3")
            print(f"   📏 Brief Length: {len(result.final_prompt)} chars")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")

if __name__ == "__main__":
    async def main():
        print("🎯 Starting Comprehensive Photography Rules Testing...\n")
        
        # Test 1: User API key integration
        success1 = await test_with_user_api_key()
        
        # Test 2: Multiple scenarios
        await test_multiple_scenarios()
        
        print(f"\n🎊 Tests Complete! Primary test {'PASSED' if success1 else 'FAILED'}")
    
    asyncio.run(main())