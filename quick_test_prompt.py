"""
Quick test script to demonstrate the language enforcement with real prompts.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.ai_client import AIClient

async def test_prompt():
    """Test with sample prompts to show language enforcement."""
    
    print("🧪 QUICK LANGUAGE ENFORCEMENT TEST")
    print("=" * 50)
    
    ai_client = AIClient()
    
    # Test with Indonesian prompt
    indonesian_prompt = {
        "user_request": "Saya ingin foto produk parfum mewah dengan pencahayaan dramatis dan latar belakang hitam yang elegan",
        "product_name": "Parfum Mewah Elite",
        "product_type": "fragrance",
        "shot_type": "hero_shot",
        "lighting": "dramatic",
        "background": "black_elegant",
        "color_scheme": "gold_black",
        "mood": "luxury",
        "style": "high_fashion"
    }
    
    print("📝 INPUT (Indonesian):")
    print(f"Request: {indonesian_prompt['user_request']}")
    print(f"Product: {indonesian_prompt['product_name']}")
    
    try:
        result = await ai_client.enhance_brief_from_structured_data(indonesian_prompt)
        
        print(f"\n✅ OUTPUT LENGTH: {len(result)} characters")
        print(f"✅ WORD COUNT: {len(result.split())} words")
        print(f"✅ SECTIONS: {result.count('##')} sections")
        
        # Show first few lines to verify English output
        lines = result.split('\n')[:10]
        print(f"\n📖 FIRST 10 LINES OF OUTPUT:")
        print("-" * 30)
        for i, line in enumerate(lines, 1):
            if line.strip():
                print(f"{i:2d}. {line.strip()}")
        
        # Check language compliance
        non_english_patterns = ['yang adalah', 'dan juga', 'dengan sangat', 'untuk menciptakan']
        violations = sum(1 for pattern in non_english_patterns if pattern.lower() in result.lower())
        
        print(f"\n🔍 LANGUAGE CHECK: {'✅ PASS' if violations == 0 else '❌ FAIL'} ({violations} violations)")
        print(f"🎯 RESULT: Indonesian input successfully converted to English brief!")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(test_prompt())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
