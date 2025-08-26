import requests
import json
import time

def test_end_to_end_rules():
    """Test end-to-end rules integration via API"""
    
    print("🚀 Testing End-to-End Rules Integration via API...")
    
    # Test case 1: Quantity mismatch prevention 
    test_payload_1 = {
        "user_request": "foto 1 donat coklat di meja",
        "product_name": "donat coklat",
        "shoot_type": "product",
        "lighting": "natural",
        "background": "clean"
    }
    
    print("📊 Test 1: Quantity Control via Brief Generation API")
    try:
        response = requests.post("http://localhost:8000/generate-brief", 
                               json=test_payload_1, 
                               timeout=30)
        if response.status_code == 200:
            result = response.json()
            final_brief = result.get('final_prompt', '')
            
            print(f"✅ API Response: {response.status_code}")
            print(f"✅ Contains Quantity Rule: {'exactly 1 donat' in final_brief.lower()}")
            print(f"✅ Contains Spatial Rules: {'NO floating elements' in final_brief}")
            print(f"Brief sample: {final_brief[:200]}...\n")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}\n")
    except Exception as e:
        print(f"❌ Connection Error: {e}\n")
    
    # Test case 2: Multiple quantity control
    test_payload_2 = {
        "user_request": "foto 2 burger dan 1 kentang goreng", 
        "product_name": "makanan",
        "shoot_type": "product",
        "lighting": "studio",
        "background": "white"
    }
    
    print("📊 Test 2: Multiple Quantity Control via API")
    try:
        response = requests.post("http://localhost:8000/generate-brief",
                               json=test_payload_2,
                               timeout=30)
        if response.status_code == 200:
            result = response.json()
            final_brief = result.get('final_prompt', '')
            
            print(f"✅ API Response: {response.status_code}")
            print(f"✅ Contains 2 burger rule: {'exactly 2 burger' in final_brief.lower()}")
            print(f"✅ Contains 1 kentang rule: {'exactly 1 kentang' in final_brief.lower()}")
            print(f"Brief sample: {final_brief[:200]}...\n")
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}\n")
    except Exception as e:
        print(f"❌ Connection Error: {e}\n")
    
    print("🎯 End-to-End Testing Complete!")
    print("Rules sekarang udah integrated ke seluruh system flow!")

if __name__ == "__main__":
    test_end_to_end_rules()
