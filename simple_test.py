"""
Simple test for the honey product API
"""
import requests
import json

# Test data
honey_request = {
    "user_request": "Cinematic commercial of a honey product 'Madu Ahlan Trigona'. A natural rainforest background with sunlight rays shining through the trees, a waterfall in the distance, and glowing golden honeycombs floating around the bottle. Close-up of the honey bottle standing on a mossy rock, golden honey drops slowly dripping. Dynamic glowing particle effects emphasize freshness and health benefits. Camera smoothly rotates around the bottle with dramatic lighting and lens flare, highlighting the label text 'Alami dan Berkhasiat'. Transition into slow-motion honey pouring into a spoon with golden sparkles, then zoom out showing the product with tagline: 'Madu Ahlan Trigona – Alami, Murni, dan Berkhasiat'. Elegant, high contrast, glossy, realistic 3D style, professional advertisement look."
}

print("🍯 Testing Honey Product API")
print("=" * 50)

# Step 1: Extract and fill
print("📋 Step 1: Extracting wizard data...")
response = requests.post("http://localhost:8000/api/v1/extract-and-fill", json=honey_request)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    wizard_data = response.json()
    print(f"✅ Successfully extracted {len(wizard_data)} fields")
    print(f"Product: {wizard_data.get('product_name')}")
    print(f"Environment: {wizard_data.get('environment')}")
    print(f"Lighting: {wizard_data.get('lighting_style')}")
    
    # Step 2: Generate brief
    print("\n🎨 Step 2: Generating enhanced brief...")
    response2 = requests.post("http://localhost:8000/api/v1/generate-brief", json=wizard_data)
    print(f"Status: {response2.status_code}")
    
    if response2.status_code == 200:
        result = response2.json()
        print("✅ Enhanced brief generated!")
        print(f"Length: {len(result['final_prompt'])} characters")
        print("\n" + "="*60)
        print("ENHANCED PHOTOGRAPHY BRIEF:")
        print("="*60)
        print(result['final_prompt'])
    else:
        print(f"❌ Error: {response2.text}")
else:
    print(f"❌ Error: {response.text}")
