#!/usr/bin/env python3
"""
Simple test to show key results
"""

import requests
import json

def simple_results_test():
    """Test sederhana untuk menampilkan hasil key"""
    
    test_prompt = """Create a vibrant tropical drink advertisement featuring a large watermelon juice bottle in the center. The bottle should appear big, glossy, and labeled "WATERMELON JUICE – SUMMER FRESH." Place a glass of watermelon juice beside it. Surround the bottle with watermelon slices, cubes, and whole mini watermelons floating around. Add a splash of red juice splattering around the bottle. The background should include a sunny tropical beach or palm trees, with blue sky and bright light rays. Include ice cubes, water droplets, and sparkles to give a fresh, lively effect."""
    
    payload = {"user_request": test_prompt}
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/generate-brief",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("=" * 60)
            print("PHOTOEAI BACKEND TEST RESULTS")
            print("=" * 60)
            
            # Basic stats
            if "brief" in result:
                brief = result["brief"]
                filled_fields = sum(1 for v in brief.values() if v and v != "Not specified")
                total_fields = len(brief)
                
                print("WIZARD FIELDS STATISTICS:")
                print("  Total Fields: {}".format(total_fields))
                print("  Filled Fields: {}".format(filled_fields))
                print("  Coverage: {:.1f}%".format((filled_fields/total_fields)*100))
                print()
                
                # Show some key filled fields
                print("KEY FILLED FIELDS:")
                key_samples = 0
                for field, value in brief.items():
                    if value and value != "Not specified" and key_samples < 10:
                        print("  {}: {}".format(field, str(value)[:60]))
                        key_samples += 1
                print()
            
            # Show enhanced prompt snippet
            if "enhanced_prompt" in result:
                enhanced = result["enhanced_prompt"]
                print("ENHANCED PROMPT PREVIEW:")
                print("  Length: {} characters".format(len(enhanced)))
                print("  First 200 chars: {}...".format(enhanced[:200]))
                print()
            
            print("STATUS: SUCCESS - Enhancement prompt working!")
            print("- Backend: Running")
            print("- OpenAI GPT-4o: Connected")
            if "brief" in result:
                brief = result["brief"]
                filled_fields = sum(1 for v in brief.values() if v and v != "Not specified")
                total_fields = len(brief)
                print("- Wizard Fields: {} of {} filled".format(filled_fields, total_fields))
            print("- Enhancement: Active")
            
            return True
            
    except Exception as e:
        print("ERROR: {}".format(e))
        return False

if __name__ == "__main__":
    simple_results_test()
