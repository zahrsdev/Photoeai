import requests
import json

def test_honey_api():
    try:
        # Test data
        honey_data = {
            "user_request": "Cinematic commercial of honey product Madu Ahlan Trigona with natural rainforest background, sunlight rays, golden honeycombs, dramatic lighting"
        }
        
        print("🍯 Testing Honey Product with PhotoeAI Backend")
        print("=" * 50)
        
        # Step 1: Extract and fill wizard data
        print("📋 Step 1: Extract and fill...")
        response1 = requests.post("http://localhost:8000/api/v1/extract-and-fill", 
                                json=honey_data, timeout=30)
        
        print(f"Status: {response1.status_code}")
        
        if response1.status_code == 200:
            wizard_data = response1.json()
            print(f"✅ Successfully extracted {len(wizard_data)} fields")
            
            # Show some key extracted fields
            important_fields = ['product_name', 'environment', 'lighting_style', 'shot_type', 'mood']
            for field in important_fields:
                value = wizard_data.get(field, 'Not specified')
                print(f"  {field}: {value}")
            
            # Step 2: Generate enhanced brief
            print("\n🎨 Step 2: Generate enhanced brief...")
            response2 = requests.post("http://localhost:8000/api/v1/generate-brief", 
                                    json=wizard_data, timeout=60)
            
            print(f"Status: {response2.status_code}")
            
            if response2.status_code == 200:
                result = response2.json()
                final_brief = result['final_prompt']
                
                print("✅ Enhanced brief generated successfully!")
                print(f"Length: {len(final_brief)} characters")
                print(f"Word count: {len(final_brief.split())} words")
                
                print("\n" + "="*60)
                print("🎯 FINAL ENHANCED PHOTOGRAPHY BRIEF")
                print("="*60)
                print(final_brief)
                print("="*60)
                
                return True
            else:
                print(f"❌ Error generating brief: {response2.status_code}")
                print(response2.text[:500])
                return False
        else:
            print(f"❌ Error extracting data: {response1.status_code}")
            print(response1.text[:500])
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_honey_api()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
