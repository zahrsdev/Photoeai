#!/usr/bin/env python3
"""
Detailed test untuk melihat enhanced prompt dan wizard fields
"""

import requests
import json

def detailed_test():
    """Test detail untuk melihat enhanced prompt dan wizard fields"""
    print("DETAILED ENHANCEMENT PROMPT TEST")
    print("=" * 100)
    
    test_prompt = """Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center. The bottle should appear big, glossy, and labeled "WATERMELON JUICE – SUMMER FRESH." Place a glass of watermelon juice beside it. Surround the bottle with watermelon slices, cubes, and whole mini watermelons floating around. Add a splash of red juice splattering around the bottle. The background should include a sunny tropical beach or palm trees, with blue sky and bright light rays. Include ice cubes, water droplets, and sparkles to give a fresh, lively effect."""
    
    payload = {"user_request": test_prompt}
    
    try:
        print("ORIGINAL USER REQUEST:")
        print("-" * 80)
        print(test_prompt)
        print("-" * 80)
        
        response = requests.post(
            "http://localhost:8000/api/v1/generate-brief",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Print enhanced prompt
            if "enhanced_prompt" in result:
                print("\nENHANCED PROMPT:")
                print("=" * 100)
                print(result["enhanced_prompt"])
                print("=" * 100)
            
            # Detailed wizard fields analysis
            if "brief" in result:
                brief = result["brief"]
                filled_fields = []
                empty_fields = []
                
                for field, value in brief.items():
                    if value and value != "Not specified":
                        filled_fields.append((field, value))
                    else:
                        empty_fields.append(field)
                
                print("\nWIZARD FIELDS ANALYSIS:")
                print("   Total Fields: {}".format(len(brief)))
                print("   Filled Fields: {}".format(len(filled_fields)))
                print("   Empty Fields: {}".format(len(empty_fields)))
                print("   Coverage: {:.1f}%".format((len(filled_fields)/len(brief)*100)))
                
                print("\nFILLED FIELDS ({}):".format(len(filled_fields)))
                print("-" * 80)
                for field, value in filled_fields:
                    print("   {}: {}...".format(field, str(value)[:80]))
                
                print("\nEMPTY FIELDS ({}):".format(len(empty_fields)))
                print("-" * 80)
                for field in empty_fields:
                    print("   {}".format(field))
                
                # Key sections analysis
                sections = {
                    "Product & Story": ["product_name", "product_description", "key_features", "product_state"],
                    "Composition": ["shot_type", "framing", "compositional_rule", "negative_space"],
                    "Lighting": ["lighting_style", "key_light_setup", "fill_light_setup", "rim_light_setup", "mood"],
                    "Background": ["environment", "dominant_colors", "accent_colors", "props"],
                    "Camera": ["camera_type", "lens_type", "aperture_value", "shutter_speed_value"]
                }
                
                print("\nSECTIONS ANALYSIS:")
                print("-" * 80)
                for section_name, fields in sections.items():
                    filled_count = sum(1 for field in fields if brief.get(field) and brief.get(field) != "Not specified")
                    coverage = (filled_count / len(fields)) * 100
                    print("   {}: {}/{} fields ({:.1f}%)".format(section_name, filled_count, len(fields), coverage))
                
            return True
            
        else:
            print("Test failed: {}".format(response.status_code))
            print("Response: {}".format(response.text))
            return False
            
    except Exception as e:
        print("Error: {}".format(e))
        return False

if __name__ == "__main__":
    detailed_test()
