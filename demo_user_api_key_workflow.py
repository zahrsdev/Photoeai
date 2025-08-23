"""
Demo script showing how to use the PhotoeAI backend with user-provided API keys.
This demonstrates the complete workflow from brief generation to image creation.
"""

import requests
import json

# Server configuration
BASE_URL = "http://localhost:8000"

def demo_user_api_key_workflow():
    """Demonstrate the complete workflow with user-provided API keys."""
    
    print("🎯 PhotoeAI Demo: User API Key Workflow")
    print("=" * 50)
    
    # Step 1: Extract and fill wizard data
    print("\n1️⃣ Extracting wizard data from user request...")
    extract_request = {
        "user_request": "I want a stunning photo of a luxury Swiss watch on white marble with dramatic golden hour lighting"
    }
    
    # Note: This would be a real API call in production
    print(f"Request: {json.dumps(extract_request, indent=2)}")
    print("✅ Would extract structured wizard data from user request")
    
    # Step 2: Generate final brief
    print("\n2️⃣ Generating professional photography brief...")
    # Mock wizard data for demo
    wizard_data = {
        "product_name": "Luxury Swiss Watch",
        "shot_type": "Product close-up",
        "lighting_style": "Golden hour dramatic lighting",
        "environment": "White marble surface"
    }
    
    print(f"Wizard Data: {json.dumps(wizard_data, indent=2)}")
    print("✅ Would generate enhanced professional photography brief")
    
    # Step 3: Generate image with user API key
    print("\n3️⃣ Generating image with user-provided API key...")
    image_request = {
        "brief_prompt": "Professional product photography of a luxury Swiss watch on pristine white marble surface, golden hour dramatic side lighting creating warm reflections, shallow depth of field, commercial quality, 85mm lens, f/2.8, award-winning composition",
        "user_api_key": "user-provided-stability-ai-key-here",  # User's own API key
        "negative_prompt": "blurry, low quality, amateur, poor lighting, scratched surface",
        "style_preset": "photorealistic"
    }
    
    print(f"Image Generation Request:")
    # Don't show the full API key in demo
    demo_request = image_request.copy()
    demo_request["user_api_key"] = "user-provided-api-key-***"
    print(json.dumps(demo_request, indent=2))
    print("✅ Would generate high-quality product image using user's API key")
    
    # Step 4: Enhance image
    print("\n4️⃣ Enhancing image with user feedback...")
    enhancement_request = {
        "original_brief_prompt": image_request["brief_prompt"],
        "generation_id": "gen_12345",
        "enhancement_instruction": "Make the lighting warmer and add more contrast to highlight the watch details",
        "user_api_key": "user-provided-stability-ai-key-here",  # Same user's API key
        "seed": 12345
    }
    
    demo_enhancement = enhancement_request.copy()
    demo_enhancement["user_api_key"] = "user-provided-api-key-***"
    print(f"Enhancement Request:")
    print(json.dumps(demo_enhancement, indent=2))
    print("✅ Would enhance image based on user feedback using their API key")
    
    print("\n" + "=" * 50)
    print("🎉 Complete workflow demonstrated!")
    print("\n🔑 Key Benefits of User API Key Approach:")
    print("   • Users have full control over their API usage and costs")
    print("   • No server-side API key storage required")
    print("   • Users can use their preferred image generation service")
    print("   • Scalable architecture without backend API costs")
    print("\n📝 To use in production:")
    print("   1. Start the PhotoeAI backend server")
    print("   2. Users provide their own Stability AI (or compatible) API key")
    print("   3. Make requests to the endpoints with user_api_key included")
    print("   4. Backend processes requests using user's credentials")

if __name__ == "__main__":
    demo_user_api_key_workflow()
