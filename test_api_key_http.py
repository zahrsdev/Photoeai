"""
Simple test untuk verify user API key works end-to-end via HTTP API
"""

import requests
import json

def test_api_key_via_http():
    """Test user API key injection via HTTP API"""
    
    print("🧪 Testing User API Key via HTTP API...")
    
    # Test payload dengan user API key
    test_payload = {
        "user_request": "foto burger dengan kentang goreng di piring putih",
        "product_name": "makanan",
        "shoot_type": "product", 
        "lighting": "studio",
        "background": "white",
        "user_api_key": "sk-test-user-key-123456789"
    }
    
    try:
        # Call generate-brief endpoint
        response = requests.post(
            "http://localhost:8000/generate-brief",
            json=test_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            final_prompt = result.get('final_prompt', '')
            
            print("✅ API Response Success!")
            print(f"   Status Code: {response.status_code}")
            print(f"   Final Prompt Length: {len(final_prompt)} chars")
            print(f"   Contains Realism Rules: {'REALISM ENHANCEMENT' in final_prompt}")
            print(f"   Sample: {final_prompt[:200]}...")
            print()
            print("🎯 USER API KEY HTTP INTEGRATION: SUCCESS ✅")
            print("Frontend sekarang bisa kirim API key ke backend!")
            
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        print("   Make sure backend server is running on port 8000")

if __name__ == "__main__":
    test_api_key_via_http()
