"""
Direct test of brief generation for Es Teller Nusantara
"""

import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_brief_content():
    """Test and display the actual brief content."""
    
    user_request = """Realistic Indonesian drink advertisement poster with text "Es Teller Nusantara", tall glass filled with coconut, avocado, jackfruit, shaved ice, and condensed milk, placed on rustic wooden surface with droplets of water, bright tropical green glowing background, floating ice cubes around, fresh and vibrant vibe."""
    
    print("🧪 TESTING BRIEF CONTENT GENERATION")
    print("=" * 70)
    
    # Step 1: Extract
    extract_response = client.post("/api/v1/extract-and-fill", json={"user_request": user_request})
    wizard_input = extract_response.json()
    
    print("✅ Extraction completed")
    
    # Step 2: Generate Brief
    brief_response = client.post("/api/v1/generate-brief", json=wizard_input)
    
    print(f"📊 Brief Response Status: {brief_response.status_code}")
    
    if brief_response.status_code == 200:
        brief_data = brief_response.json()
        print(f"📋 Response Keys: {list(brief_data.keys())}")
        
        # Check different possible keys
        for key in ['brief', 'enhanced_brief', 'final_brief', 'content']:
            if key in brief_data and brief_data[key]:
                print(f"✅ Found content in '{key}':")
                print("-" * 50)
                print(brief_data[key][:500] + "..." if len(brief_data[key]) > 500 else brief_data[key])
                print("-" * 50)
                break
        else:
            print("❌ No brief content found")
            print("📄 Full response:")
            print(json.dumps(brief_data, indent=2)[:1000])
    else:
        print(f"❌ Error: {brief_response.text}")

if __name__ == "__main__":
    test_brief_content()
