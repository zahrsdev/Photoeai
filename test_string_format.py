"""
Test script to verify that AI extraction returns strings instead of arrays
"""
import asyncio
import json
from app.services.ai_client import AIClient
from app.config.settings import settings

async def test_string_format():
    """Test that AI returns strings for fields like key_features, colors, etc."""
    ai_client = AIClient()
    
    test_requests = [
        "madu trigona premium with multiple benefits",
        "leather wallet with card slots and RFID protection"
    ]
    
    for request in test_requests:
        print(f"\n🧪 Testing: {request}")
        
        try:
            result = await ai_client.extract_wizard_data(request)
            
            # Check specific fields that were causing array issues
            problem_fields = [
                'key_features', 'dominant_colors', 'accent_colors', 
                'photographer_influences'
            ]
            
            print("✅ Extraction successful!")
            print(f"  Result type: {type(result)}")
            
            # Print first few keys to understand the structure
            if isinstance(result, dict):
                print(f"  Available keys: {list(result.keys())}")
                
                for field in problem_fields:
                    if field in result:
                        value = result[field]
                        print(f"  {field}: '{value}' (type: {type(value).__name__})")
                        
                        if isinstance(value, list):
                            print(f"  ❌ ERROR: {field} is still a list!")
                        elif isinstance(value, str):
                            print(f"  ✅ {field} is correctly a string")
                        else:
                            print(f"  ⚠️ {field} has unexpected type: {type(value)}")
                    else:
                        print(f"  ⚠️ {field} not found in result")
                        
            else:
                print(f"  Unexpected result type: {type(result)}")
                    
        except Exception as e:
            print(f"❌ Extraction failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_string_format())
