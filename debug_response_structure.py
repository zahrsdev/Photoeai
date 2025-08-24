#!/usr/bin/env python3
"""
Debug GPT Image 1 response structure
"""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_ORG = "org-XKOFJy5SYzXNV9yTQTDTSPx9"

def debug_gpt_image_response():
    """Debug exact response structure from GPT Image 1"""
    
    payload = {
        "model": "gpt-image-1",
        "prompt": "Simple photo of a water bottle",
        "n": 1,
        "size": "1024x1024",
        "quality": "high"
    }
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Organization": OPENAI_ORG,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ GPT Image 1 Response Structure:")
            print(f"📊 Full response:")
            print(json.dumps(result, indent=2))
            
            print(f"\n🔍 Response Analysis:")
            print(f"   Top-level keys: {list(result.keys())}")
            
            if 'data' in result:
                print(f"   Data length: {len(result['data'])}")
                if result['data']:
                    print(f"   First item keys: {list(result['data'][0].keys())}")
                    
                    item = result['data'][0]
                    if 'url' in item:
                        print(f"   ✅ URL found: {item['url'][:50]}...")
                    if 'revised_prompt' in item:
                        print(f"   ✅ Revised prompt found: {item['revised_prompt'][:50]}...")
                    if 'b64_json' in item:
                        print(f"   ✅ Base64 found: {len(item['b64_json'])} chars")
            
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_gpt_image_response()
