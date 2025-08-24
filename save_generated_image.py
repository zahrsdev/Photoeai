#!/usr/bin/env python3
"""
Script to generate and save image from PhotoeAI backend
Saves the generated image as a PNG file you can view
"""
import requests
import base64
import json
from datetime import datetime
import os

def save_base64_image(base64_data, filename):
    """Save base64 image data to file"""
    try:
        # Remove data:image/png;base64, prefix if present
        if base64_data.startswith('data:image'):
            base64_data = base64_data.split(',')[1]
        
        # Decode base64 data
        image_data = base64.b64decode(base64_data)
        
        # Save to file
        with open(filename, 'wb') as f:
            f.write(image_data)
        
        print(f"✅ Image saved: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return False

def generate_and_save_image():
    """Generate image and save it to disk"""
    backend_url = "http://127.0.0.1:8000"
    
    # Test prompt for watermelon advertisement
    test_prompt = """Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center. The scene should have a bright summer atmosphere with fresh watermelon slices, ice cubes, and tropical leaves in the background. Include marketing text 'FRESH WATERMELON JUICE - 100% Natural' in stylish fonts."""
    
    print("🚀 GENERATE AND SAVE WATERMELON IMAGE")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 75)
    
    try:
        # Step 1: Generate enhanced brief
        print("STEP 1: Generating enhanced brief...")
        brief_response = requests.post(
            f"{backend_url}/api/v1/generate-brief-from-prompt",
            json={
                "user_request": test_prompt
            },
            timeout=60
        )
        
        if brief_response.status_code == 200:
            brief_data = brief_response.json()
            enhanced_prompt = brief_data.get("enhanced_brief", brief_data.get("enhanced_prompt", ""))
            print(f"✅ Enhanced prompt generated: {len(enhanced_prompt)} chars")
        else:
            print(f"❌ Brief generation failed: {brief_response.status_code}")
            return
        
        # Step 2: Generate image using enhanced prompt
        print("\nSTEP 2: Generating image...")
        
        # Get user API key dynamically
        user_api_key = input("Enter your OpenAI API key: ").strip()
        if not user_api_key:
            print("❌ API key is required!")
            return
        
        image_response = requests.post(
            f"{backend_url}/api/v1/generate-image",
            json={
                "brief_prompt": enhanced_prompt,
                "user_api_key": user_api_key,
                "provider": "openai"
            },
            timeout=60
        )
        
        if image_response.status_code == 200:
            image_data = image_response.json()
            image_url = image_data.get("image_url", "")
            
            if image_url.startswith("data:image"):
                # Generate filename with timestamp
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"watermelon_ad_{timestamp}.png"
                
                print(f"✅ Image generated successfully")
                print(f"🖼️ Format: Base64 PNG")
                print(f"📝 Saving to: {filename}")
                
                # Save the image
                if save_base64_image(image_url, filename):
                    print(f"\n🎉 SUCCESS! Your watermelon advertisement image is saved as:")
                    print(f"📂 {os.path.abspath(filename)}")
                    print(f"\n💡 You can now open this PNG file to see your generated image!")
                else:
                    print("❌ Failed to save image")
            else:
                print(f"❌ Unexpected image format: {image_url[:100]}...")
        else:
            print(f"❌ Image generation failed: {image_response.status_code}")
            if image_response.text:
                print(f"Error details: {image_response.text}")
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    generate_and_save_image()
