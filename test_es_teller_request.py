"""
Test script for the specific Indonesian drink advertisement request
"""

import requests
import json

def test_es_teller_nusantara():
    """Test the PhotoeAI engine with the Es Teller Nusantara request."""
    
    # Your specific test request
    test_request = """Realistic Indonesian drink advertisement poster with text "Es Teller Nusantara", tall glass filled with coconut, avocado, jackfruit, shaved ice, and condensed milk, placed on rustic wooden surface with droplets of water, bright tropical green glowing background, floating ice cubes around, fresh and vibrant vibe."""
    
    print("🧪 PhotoeAI Engine - Es Teller Nusantara Test")
    print("=" * 70)
    print(f"📝 Request: {test_request}")
    print("=" * 70)
    
    # Prepare payload
    payload = {"user_request": test_request}
    
    try:
        print("🚀 Sending request to PhotoeAI extraction endpoint...")
        
        response = requests.post(
            "http://localhost:8000/extract-and-fill",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS! PhotoeAI extracted the following data:")
            print("=" * 70)
            
            extracted_data = response.json()
            print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            
            print("=" * 70)
            print("🎯 Key Extraction Results:")
            print(f"   🥤 Product Name: {extracted_data.get('product_name', 'N/A')}")
            print(f"   📸 Shot Type: {extracted_data.get('shot_type', 'N/A')}")
            print(f"   💡 Lighting: {extracted_data.get('lighting_style', 'N/A')}")
            print(f"   🎨 Colors: {extracted_data.get('dominant_colors', 'N/A')}")
            print(f"   🌴 Environment: {extracted_data.get('environment', 'N/A')}")
            print(f"   ✨ Mood: {extracted_data.get('mood', 'N/A')}")
            
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("🔌 Connection failed. Make sure the PhotoeAI server is running.")
    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 30 seconds.")
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_es_teller_nusantara()
