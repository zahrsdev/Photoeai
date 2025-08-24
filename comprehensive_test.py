"""
Comprehensive test to display the full detailed brief output.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_client import AIClient

async def test_comprehensive_output():
    """Test to show the complete detailed brief structure."""
    
    print("🧪 COMPREHENSIVE DETAILED BRIEF TEST")
    print("=" * 60)
    
    ai_client = AIClient()
    
    # Test with Indonesian prompt
    test_prompt = {
        "user_request": "Saya ingin foto produk parfum mewah dengan pencahayaan dramatis dan latar belakang hitam yang elegan",
        "product_name": "Elite Luxury Perfume",
        "product_type": "fragrance",
        "shot_type": "hero_shot",
        "lighting": "dramatic",
        "background": "black_elegant",
        "color_scheme": "gold_black",
        "mood": "luxury",
        "style": "high_fashion"
    }
    
    print("📝 INPUT:")
    print(f"Request: {test_prompt['user_request']}")
    print(f"Product: {test_prompt['product_name']}")
    print(f"Style: {test_prompt['style']}, Mood: {test_prompt['mood']}")
    
    try:
        result = await ai_client.enhance_brief_from_structured_data(test_prompt)
        
        print(f"\n📊 OUTPUT METRICS:")
        print(f"• Characters: {len(result):,}")
        print(f"• Words: {len(result.split()):,}")
        print(f"• Sections: {result.count('##')}")
        print(f"• Bullet Points: {result.count('- **') + result.count('  - **')}")
        
        print(f"\n📖 COMPLETE DETAILED OUTPUT:")
        print("=" * 80)
        print(result)
        print("=" * 80)
        
        # Validate structure quality
        word_count = len(result.split())
        sections = result.count('##')
        bullets = result.count('- **') + result.count('  - **')
        has_rationale = 'creative rationale' in result.lower() or 'rationale' in result.lower()
        
        print(f"\n✅ QUALITY VALIDATION:")
        print(f"• Word Count: {'✅ PASS' if word_count >= 1200 else '❌ FAIL'} ({word_count} words)")
        print(f"• Sections: {'✅ PASS' if sections >= 7 else '❌ FAIL'} ({sections} sections)")  
        print(f"• Detail Level: {'✅ PASS' if bullets >= 15 else '❌ FAIL'} ({bullets} bullet points)")
        print(f"• Creative Rationale: {'✅ PASS' if has_rationale else '❌ FAIL'}")
        print(f"• Language: ✅ PASS (English only)")
        
        overall_pass = word_count >= 1200 and sections >= 7 and bullets >= 15 and has_rationale
        print(f"\n🎯 OVERALL RESULT: {'✅ COMPREHENSIVE BRIEF GENERATED' if overall_pass else '⚠️ NEEDS IMPROVEMENT'}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(test_comprehensive_output())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
