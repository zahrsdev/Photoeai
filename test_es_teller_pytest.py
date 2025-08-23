"""
Test the Es Teller Nusantara extraction request using pytest framework
"""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_es_teller_nusantara_extraction():
    """Test PhotoeAI extraction with Es Teller Nusantara request."""
    
    # Your specific test request
    test_request = """Realistic Indonesian drink advertisement poster with text "Es Teller Nusantara", tall glass filled with coconut, avocado, jackfruit, shaved ice, and condensed milk, placed on rustic wooden surface with droplets of water, bright tropical green glowing background, floating ice cubes around, fresh and vibrant vibe."""
    
    # Test payload
    payload = {"user_request": test_request}
    
    print(f"\n🧪 Testing Es Teller Nusantara extraction...")
    print(f"📝 Request: {test_request[:100]}...")
    
    # Send request
    response = client.post("/api/v1/extract-and-fill", json=payload)
    
    print(f"📊 Status: {response.status_code}")
    
    # Assertions
    assert response.status_code == 200
    
    # Parse response
    extracted_data = response.json()
    
    print(f"✅ SUCCESS! Extracted {len(extracted_data)} fields")
    print(f"🥤 Product Name: {extracted_data.get('product_name', 'N/A')}")
    print(f"📸 Shot Type: {extracted_data.get('shot_type', 'N/A')}")
    print(f"💡 Lighting: {extracted_data.get('lighting_style', 'N/A')}")
    print(f"🎨 Colors: {extracted_data.get('dominant_colors', 'N/A')}")
    print(f"🌴 Environment: {extracted_data.get('environment', 'N/A')}")
    print(f"✨ Mood: {extracted_data.get('mood', 'N/A')}")
    
    # Verify key fields are populated
    assert "product_name" in extracted_data
    assert "shot_type" in extracted_data
    assert "lighting_style" in extracted_data
    assert "environment" in extracted_data
    
    # Verify Es Teller is recognized
    assert "Es Teller" in extracted_data["product_name"]
    
    print("\n📋 Full extracted data:")
    print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
    
    # Don't return anything to avoid pytest warning

if __name__ == "__main__":
    # Run the test directly
    test_es_teller_nusantara_extraction()
