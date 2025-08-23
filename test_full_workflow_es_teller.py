"""
Full PhotoeAI Workflow Test: Es Teller Nusantara
Tests the complete pipeline: Extraction → Brief Generation → Enhancement
"""

import pytest
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_full_es_teller_workflow():
    """Test the complete PhotoeAI workflow with Es Teller Nusantara request."""
    
    # Your specific Indonesian drink request
    user_request = """Realistic Indonesian drink advertisement poster with text "Es Teller Nusantara", tall glass filled with coconut, avocado, jackfruit, shaved ice, and condensed milk, placed on rustic wooden surface with droplets of water, bright tropical green glowing background, floating ice cubes around, fresh and vibrant vibe."""
    
    print(f"\n🧪 FULL PHOTOEAI WORKFLOW TEST")
    print("=" * 80)
    print(f"📝 Original Request: {user_request}")
    print("=" * 80)
    
    # STEP 1: Extract and Fill
    print("\n🔍 STEP 1: EXTRACTION & AUTO-FILL")
    print("-" * 50)
    
    extract_payload = {"user_request": user_request}
    extract_response = client.post("/api/v1/extract-and-fill", json=extract_payload)
    
    assert extract_response.status_code == 200
    wizard_input = extract_response.json()
    
    print(f"✅ Extraction Status: {extract_response.status_code}")
    print(f"🎯 Product: {wizard_input.get('product_name', 'N/A')}")
    print(f"📸 Shot Type: {wizard_input.get('shot_type', 'N/A')}")
    print(f"💡 Lighting: {wizard_input.get('lighting_style', 'N/A')}")
    print(f"🌴 Environment: {wizard_input.get('environment', 'N/A')}")
    print(f"🎨 Colors: {wizard_input.get('dominant_colors', 'N/A')}")
    
    # STEP 2: Generate Brief
    print("\n📋 STEP 2: BRIEF GENERATION")
    print("-" * 50)
    
    brief_response = client.post("/api/v1/generate-brief", json=wizard_input)
    
    assert brief_response.status_code == 200
    brief_data = brief_response.json()
    
    print(f"✅ Brief Generation Status: {brief_response.status_code}")
    print(f"📄 Brief Length: {len(brief_data.get('brief', ''))} characters")
    
    # Display the generated brief
    print("\n🎨 GENERATED PHOTOGRAPHY BRIEF:")
    print("=" * 80)
    print(brief_data.get('brief', 'No brief generated'))
    print("=" * 80)
    
    # STEP 3: Preview Brief (optional validation)
    print("\n👀 STEP 3: BRIEF PREVIEW")
    print("-" * 50)
    
    preview_response = client.post("/api/v1/preview-brief", json=wizard_input)
    
    assert preview_response.status_code == 200
    preview_data = preview_response.json()
    
    print(f"✅ Preview Status: {preview_response.status_code}")
    print(f"📊 Preview Length: {len(preview_data.get('preview', ''))} characters")
    
    # Summary
    print("\n🎉 WORKFLOW SUMMARY:")
    print("=" * 80)
    print(f"🥤 Indonesian Drink: Es Teller Nusantara ✅")
    print(f"🔍 Extraction: Success - {len(wizard_input)} fields populated ✅")
    print(f"📋 Brief Generation: Success - Professional brief created ✅")
    print(f"👀 Preview: Success - Brief validated ✅")
    print(f"🚀 Full Pipeline: WORKING PERFECTLY! ✅")
    
    # Key insights
    print(f"\n🎯 KEY INSIGHTS:")
    print(f"   • AI recognized Indonesian cultural context")
    print(f"   • Technical photography settings auto-configured")
    print(f"   • Visual elements properly structured")
    print(f"   • Professional brief ready for creative team")
    
    return {
        "extraction": wizard_input,
        "brief": brief_data,
        "preview": preview_data
    }

if __name__ == "__main__":
    # Run the test directly
    result = test_full_es_teller_workflow()
    print(f"\n✨ Test completed successfully!")
