"""
Test script to demonstrate PhotoeAI backend API with honey product example
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Your honey product request
honey_request = {
    "user_request": """Cinematic commercial of a honey product "Madu Ahlan Trigona". A natural rainforest background with sunlight rays shining through the trees, a waterfall in the distance, and glowing golden honeycombs floating around the bottle. Close-up of the honey bottle standing on a mossy rock, golden honey drops slowly dripping. Dynamic glowing particle effects emphasize freshness and health benefits. Camera smoothly rotates around the bottle with dramatic lighting and lens flare, highlighting the label text "Alami dan Berkhasiat". Transition into slow-motion honey pouring into a spoon with golden sparkles, then zoom out showing the product with tagline: "Madu Ahlan Trigona – Alami, Murni, dan Berkhasiat". Elegant, high contrast, glossy, realistic 3D style, professional advertisement look."""
}

def test_api():
    print("🍯 Testing PhotoeAI Backend with Honey Product")
    print("=" * 60)
    
    # Step 1: Extract and fill wizard data
    print("\n📋 Step 1: Extracting wizard data from user request...")
    try:
        response = requests.post(f"{BASE_URL}/extract-and-fill", json=honey_request)
        if response.status_code == 200:
            wizard_data = response.json()
            print("✅ Successfully extracted wizard data!")
            print(f"   Product Name: {wizard_data.get('product_name', 'N/A')}")
            print(f"   Lighting Style: {wizard_data.get('lighting_style', 'N/A')}")
            print(f"   Environment: {wizard_data.get('environment', 'N/A')}")
            print(f"   Shot Type: {wizard_data.get('shot_type', 'N/A')}")
            print(f"   Camera Type: {wizard_data.get('camera_type', 'N/A')}")
            
            # Show all 69 fields
            print(f"\n📊 Total fields extracted: {len(wizard_data)} fields")
            print("\n🔍 All extracted fields:")
            for key, value in wizard_data.items():
                if value is not None and value != "":
                    print(f"   • {key}: {value}")
        else:
            print(f"❌ Error in extract-and-fill: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error calling extract-and-fill: {e}")
        return
    
    # Step 2: Generate final enhanced brief
    print(f"\n🎨 Step 2: Generating enhanced photography brief...")
    print("   (Using LLM as Creative Director...)")
    try:
        response = requests.post(f"{BASE_URL}/generate-brief", json=wizard_data)
        if response.status_code == 200:
            brief_result = response.json()
            final_prompt = brief_result.get("final_prompt", "")
            
            print("✅ Successfully generated enhanced brief!")
            print(f"   Length: {len(final_prompt)} characters")
            print(f"   Words: {len(final_prompt.split())} words")
            
            print("\n🎯 FINAL ENHANCED PHOTOGRAPHY BRIEF:")
            print("=" * 60)
            print(final_prompt)
            print("=" * 60)
            
            # Save to file
            with open("enhanced_honey_brief.txt", "w", encoding="utf-8") as f:
                f.write("ENHANCED PHOTOGRAPHY BRIEF - MADU AHLAN TRIGONA\n")
                f.write("="*60 + "\n\n")
                f.write(f"Original Request:\n{honey_request['user_request']}\n\n")
                f.write("Enhanced Brief:\n")
                f.write(final_prompt)
            
            print(f"\n💾 Brief saved to: enhanced_honey_brief.txt")
            
        else:
            print(f"❌ Error in generate-brief: {response.status_code}")
            print(f"   Error: {response.text}")
            return
    except Exception as e:
        print(f"❌ Error calling generate-brief: {e}")
        return
    
    print("\n🎉 Test completed successfully!")
    print("   Your cinematic honey commercial brief is ready for use!")

if __name__ == "__main__":
    # Wait a moment for server to be fully ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    test_api()
