"""
PhotoeAI Engine Extraction Test Script

This script tests the core functionality of the PhotoeAI engine's first endpoint: POST /extract-and-fill
The goal is to verify the engine's ability to automatically parse a complex, descriptive user request 
and populate the structured WizardInput schema without any manual assistance.

Test Data: Indonesian drink advertisement with detailed visual requirements
"""

import requests
import json
import sys
from typing import Dict, Any

# Configuration
API_ENDPOINT = "http://localhost:8000/extract-and-fill"
TEST_REQUEST = """Realistic Indonesian drink advertisement poster with text "Es Teller Nusantara", a tall glass filled with coconut, avocado, jackfruit, shaved ice, and condensed milk, placed on a rustic wooden surface with droplets of water, a bright tropical green glowing background, floating ice cubes around, and a fresh and vibrant vibe."""

def test_extraction_endpoint() -> None:
    """
    Test the PhotoeAI extraction endpoint with a complex Indonesian drink advertisement request.
    
    This test verifies that the engine's "Analyst LLM" can automatically populate
    all the structured fields based solely on the descriptive user request.
    """
    print("🧪 PhotoeAI Engine - Extraction Endpoint Test")
    print("=" * 60)
    print(f"📝 Test Request: {TEST_REQUEST}")
    print("=" * 60)
    
    # Prepare the payload (ONLY user_request field as per requirements)
    payload = {
        "user_request": TEST_REQUEST
    }
    
    try:
        print("🚀 Sending POST request to extraction endpoint...")
        print(f"📍 Endpoint: {API_ENDPOINT}")
        
        # Send POST request
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # 30 second timeout for AI processing
        )
        
        print(f"📊 Response Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Request successful!")
            print("\n🎯 EXTRACTED DATA - AUTO-POPULATED BY ANALYST LLM:")
            print("=" * 60)
            
            # Parse and pretty-print the JSON response
            extracted_data = response.json()
            print(json.dumps(extracted_data, indent=2, ensure_ascii=False))
            
            print("=" * 60)
            print("🔍 ANALYSIS SUMMARY:")
            print(f"📋 Total fields populated: {len(extracted_data)}")
            
            # Show key fields that were automatically extracted
            key_fields = [
                "product_name", "product_description", "shot_type", 
                "lighting_style", "environment", "dominant_colors", "mood"
            ]
            
            print("\n🎨 Key Visual Elements Detected:")
            for field in key_fields:
                if field in extracted_data and extracted_data[field]:
                    print(f"  • {field}: {extracted_data[field]}")
                    
        else:
            print("❌ Request failed!")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out (30s). The AI might be taking longer to process.")
        
    except requests.exceptions.ConnectionError:
        print("🔌 Connection failed. Make sure the PhotoeAI server is running on localhost:8000")
        print("💡 Tip: Start the server with: uvicorn app.main:app --reload")
        
    except requests.exceptions.RequestException as e:
        print(f"🚨 Request error: {e}")
        
    except json.JSONDecodeError as e:
        print(f"📄 JSON parsing error: {e}")
        print(f"Raw response: {response.text if 'response' in locals() else 'N/A'}")
        
    except Exception as e:
        print(f"💥 Unexpected error: {e}")

def main():
    """Main function to run the extraction test."""
    test_extraction_endpoint()

if __name__ == "__main__":
    main()
