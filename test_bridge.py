"""
Test Image-Wizard Bridge Service - Task 3 Validation
Simple test untuk verify bridge functionality
"""
from app.services.image_wizard_bridge import ImageWizardBridge

def test_bridge():
    """Test basic bridge functionality"""
    
    # Sample image analysis result
    sample_analysis = {
        "product_type": "food_beverage",
        "product_name": "Pizza",
        "lighting_style": "natural",
        "background_type": "wooden table",
        "composition_style": "overhead",
        "style_preference": "modern",
        "current_quality": "amateur",
        "improvement_areas": ["lighting", "composition"],
        "dominant_colors": ["red", "yellow", "brown"],
        "camera_angle": "top-down"
    }
    
    # Sample user prompt
    user_prompt = "Make my pizza photo look world-class professional"
    
    # Test bridge
    bridge = ImageWizardBridge()
    wizard_input = bridge.combine_image_and_prompt(sample_analysis, user_prompt)
    
    print("🧪 Bridge Test Results:")
    print(f"Product Name: {wizard_input.product_name}")
    print(f"Product Type: {wizard_input.product_type}")
    print(f"Style Preference: {wizard_input.style_preference}")
    print(f"Lighting Style: {wizard_input.lighting_style}")
    print(f"Enhanced Request: {wizard_input.user_request}")
    print("✅ Bridge test completed!")

if __name__ == "__main__":
    test_bridge()
