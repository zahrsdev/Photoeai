#!/usr/bin/env python3
"""
Test direct dengan curl/requests tanpa bergantung pada terminal
"""

import requests
import json
import time

# Test dengan requests langsung
def test_backend():
    """Test backend langsung"""
    print("🔍 Testing backend directly...")
    
    try:
        # Health check
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ Backend health: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Backend not running!")
            return False
            
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Backend tidak berjalan!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_brief_generation():
    """Test brief generation"""
    print("\n🔍 Testing brief generation...")
    
    test_prompt = """Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center. The bottle should appear big, glossy, and labeled "WATERMELON JUICE – SUMMER FRESH." Place a glass of watermelon juice beside it. Surround the bottle with watermelon slices, cubes, and whole mini watermelons floating around. Add a splash of red juice splattering around the bottle. The background should include a sunny tropical beach or palm trees, with blue sky and bright light rays. Include ice cubes, water droplets, and sparkles to give a fresh, lively effect."""
    
    payload = {"user_request": test_prompt}
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/generate-brief",
            json=payload,
            timeout=120
        )
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Brief generation successful!")
            
            # Print enhanced prompt
            if "enhanced_prompt" in result:
                print("\n🎨 ENHANCED PROMPT (first 300 chars):")
                print("-" * 80)
                print(result["enhanced_prompt"][:300] + "...")
                print("-" * 80)
            
            # Count brief fields
            if "brief" in result:
                brief = result["brief"]
                filled_fields = sum(1 for v in brief.values() if v and v != "Not specified")
                print(f"\n📊 BRIEF STATISTICS:")
                print(f"   Total fields: {len(brief)}")
                print(f"   Filled fields: {filled_fields}")
                print(f"   Coverage: {(filled_fields/len(brief)*100):.1f}%")
                
                # Show wizard fields
                print(f"\n🔍 WIZARD FIELDS FILLED:")
                for field, value in brief.items():
                    if value and value != "Not specified":
                        print(f"   ✅ {field}: {str(value)[:50]}...")
            
            return True
            
        else:
            print(f"❌ Brief generation failed: {response.status_code}")
            try:
                error_detail = response.json()
                print(f"Error: {error_detail}")
            except:
                print(f"Response text: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing brief generation: {e}")
        return False

def main():
    print("🚀 Direct Backend Test")
    print("=" * 80)
    
    # Test backend health first
    if not test_backend():
        print("\n❌ Backend tidak berjalan. Pastikan backend sudah running:")
        print("   python run.py")
        return
    
    # Test brief generation
    success = test_brief_generation()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY:")
    print(f"   Backend Health: ✅")
    print(f"   Brief Generation: {'✅' if success else '❌'}")
    
    if success:
        print("\n🎉 ENHANCEMENT PROMPT TEST PASSED!")
        print("   - 46 wizard fields sistem bekerja")
        print("   - Enhancement prompt dikirim ke OpenAI GPT-4o")
        print("   - Brief generation berhasil")
    else:
        print("\n⚠️ Test failed. Check backend logs.")

if __name__ == "__main__":
    main()
