"""
Simple test: Compare hasil backend vs raw prompt ke OpenAI
"""

import requests
import json

def simple_test():
    print("🔍 SIMPLE COMPARISON TEST")
    print("=" * 60)
    
    api_key = "sk-YOUR-API-KEY-HERE"
    
    # Prompt yang sama dengan ChatGPT Image
    prompt = """Ultra-realistic commercial product photography of a banana and raisin flavored milk drink bottle splashing in creamy milk. The bottle is glossy with detailed branding, surrounded by floating fresh bananas, banana slices, and raisins frozen mid-air. Milk splash is dynamic, high-speed, and hyper-detailed with droplets suspended in motion. Background is a smooth golden-yellow gradient, enhancing freshness and energy. Studio lighting with soft reflections highlights the glossy surface of the bottle and realistic textures of fruits. Shot in high-resolution, cinematic style, with sharp focus, vibrant colors, and perfect clarity."""
    
    print(f"📝 Testing prompt: {len(prompt)} chars")
    print(f"   {prompt[:100]}...")
    
    # Test 1: Enhanced mode (Default)
    print(f"\n🤖 TEST 1: ENHANCED MODE")
    payload1 = {
        "brief_prompt": prompt,
        "user_api_key": api_key,
        "provider": "openai"
    }
    
    try:
        response1 = requests.post(
            "http://localhost:8000/api/v1/generate-image",
            json=payload1,
            timeout=60
        )
        
        if response1.status_code == 200:
            result1 = response1.json()
            enhanced_prompt = result1.get('final_enhanced_prompt', '')
            api_prompt = result1.get('revised_prompt', '')
            
            print(f"✅ Enhanced Mode Success")
            print(f"   Enhanced: {len(enhanced_prompt)} chars")
            print(f"   API sent: {len(api_prompt)} chars") 
            print(f"   Image: {result1.get('image_url', 'N/A')[:60]}...")
            
        else:
            print(f"❌ Enhanced failed: {response1.status_code}")
            return
            
    except Exception as e:
        print(f"💥 Enhanced error: {e}")
        return
    
    # Test 2: RAW mode (Should match ChatGPT exactly)
    print(f"\n🔧 TEST 2: RAW MODE (Same as ChatGPT)")
    payload2 = {
        "brief_prompt": prompt,
        "user_api_key": api_key,
        "provider": "openai",
        "use_raw_prompt": True
    }
    
    try:
        response2 = requests.post(
            "http://localhost:8000/api/v1/generate-image",
            json=payload2,
            timeout=60
        )
        
        if response2.status_code == 200:
            result2 = response2.json()
            raw_api_prompt = result2.get('revised_prompt', '')
            
            print(f"✅ Raw Mode Success")
            print(f"   Input: {len(prompt)} chars")
            print(f"   API sent: {len(raw_api_prompt)} chars")
            print(f"   Image: {result2.get('image_url', 'N/A')[:60]}...")
            
            # Compare raw vs enhanced
            print(f"\n📊 COMPARISON:")
            print(f"   Enhanced API: {len(api_prompt)} chars")
            print(f"   Raw API:      {len(raw_api_prompt)} chars")
            
            if len(api_prompt) > len(raw_api_prompt) * 2:
                print("⚠️ Enhanced menggunakan prompt yang jauh lebih panjang!")
                print("   Ini bisa jadi penyebab hasil berbeda")
            else:
                print("✅ Prompt lengths reasonable")
                
        else:
            print(f"❌ Raw failed: {response2.status_code}")
            
    except Exception as e:
        print(f"💥 Raw error: {e}")

if __name__ == "__main__":
    simple_test()
