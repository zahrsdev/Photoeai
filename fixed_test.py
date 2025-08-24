#!/usr/bin/env python3
"""
Simple test script untuk menguji backend enhancement prompt
"""

import requests
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load API key dari file .env
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Set API key dari environment variable
API_KEY = os.getenv("OPENAI_API_KEY")
print(f"Using API Key: {API_KEY[:20]}...")

# Backend URL
BACKEND_URL = "http://localhost:8000"

# Test prompt
TEST_PROMPT = """Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center. The bottle should appear big, glossy, and labeled "WATERMELON JUICE – SUMMER FRESH." Place a glass of watermelon juice beside it. Surround the bottle with watermelon slices, cubes, and whole mini watermelons floating around. Add a splash of red juice splattering around the bottle. The background should include a sunny tropical beach or palm trees, with blue sky and bright light rays. Include ice cubes, water droplets, and sparkles to give a fresh, lively effect."""

def main():
    print("🚀 Testing PhotoeAI Backend Enhancement Prompt")
    print("=" * 80)
    
    # Test backend health
    try:
        response = requests.get(f"{BACKEND_URL}/", timeout=5)
        print(f"✅ Backend health: {response.status_code}")
    except:
        print("❌ Backend tidak berjalan!")
        return
    
    # Test brief generation
    payload = {"user_request": TEST_PROMPT}
    
    headers = {
        "Content-Type": "application/json",
        "X-API-KEY": API_KEY  # Tambahkan API key di header juga
    }
    
    try:
        print("\n🔍 Testing brief generation...")
        print(f"Sending request to: {BACKEND_URL}/api/v1/generate-brief")
        print(f"Using prompt: {TEST_PROMPT[:100]}...")
        
        response = requests.post(
            f"{BACKEND_URL}/api/v1/generate-brief",
            json=payload,
            headers=headers,
            timeout=120  # Tingkatkan timeout
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Brief generation successful!")
            
            # Print enhanced prompt
            if "enhanced_prompt" in result:
                print("\n🎨 ENHANCED PROMPT:")
                print("-" * 80)
                print(result["enhanced_prompt"][:500] + "...")
                print("-" * 80)
            
            # Count brief fields
            if "brief" in result:
                brief = result["brief"]
                filled_fields = sum(1 for v in brief.values() if v and v != "Not specified")
                print(f"\n📊 BRIEF STATISTICS:")
                print(f"   Total fields: {len(brief)}")
                print(f"   Filled fields: {filled_fields}")
                print(f"   Coverage: {(filled_fields/len(brief)*100):.1f}%")
                
                # Show some key fields
                key_fields = ['product_name', 'lighting_style', 'environment', 'camera_type', 'lens_type']
                print(f"\n🔍 KEY FIELDS SAMPLE:")
                for field in key_fields:
                    value = brief.get(field, "Not found")
                    print(f"   {field}: {value}")
            
        else:
            print(f"❌ Brief generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
