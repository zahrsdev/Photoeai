#!/usr/bin/env python3
"""
Test GPT Image 1 with correct payload (no response_format)
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def test_gpt_image_1_fixed():
    """Test GPT Image 1 with corrected payload"""
    
    print(f"🎯 TESTING GPT IMAGE 1 WITH FIXED PAYLOAD")
    print(f"=" * 60)
    
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Corrected payload - NO response_format
    payload = {
        "model": "gpt-image-1",
        "prompt": "Professional photo of a water bottle on wooden table",
        "n": 1,
        "size": "1024x1024",
        "quality": "high"
        # NO response_format parameter!
    }
    
    print(f"📦 Fixed Payload:")
    print(f"  model: {payload['model']}")
    print(f"  prompt: {payload['prompt']}")
    print(f"  quality: {payload['quality']}")
    print(f"  ❌ NO response_format (GPT Image 1 doesn't support it)")
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/images/generations",
            json=payload,
            headers=headers,
            timeout=60
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS! GPT Image 1 works with fixed payload!")
            print(f"🖼️ Image URL: {result['data'][0]['url']}")
            
            # Check if there's revised_prompt
            if 'revised_prompt' in result['data'][0]:
                print(f"📝 Revised Prompt: {result['data'][0]['revised_prompt']}")
            
            return True
            
        else:
            print(f"❌ FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_gpt_image_1_fixed()
