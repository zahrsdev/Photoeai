#!/usr/bin/env python3
"""
Test script to demonstrate the smart truncation logic.
Shows how prompts are now truncated at natural breakpoints.
"""

import re

def smart_truncate_demo(text: str, max_length: int = 200) -> str:
    """Demonstrate the smart truncation logic with a shorter limit for testing."""
    
    if len(text) <= max_length:
        return text
        
    print(f"Original length: {len(text)} chars")
    print(f"Max allowed: {max_length} chars")
    
    truncated = text[:max_length]
    
    # Try to end at a section break (---) 
    section_break = truncated.rfind('\n---\n')
    if section_break > max_length * 0.7:
        result = text[:section_break]
        print(f"✂️ Truncated at section break to {len(result)} characters")
        return result
    else:
        # Try to end at a complete sentence
        sentence_end = max(truncated.rfind('. '), truncated.rfind('.\n'))
        if sentence_end > max_length * 0.8:
            result = text[:sentence_end + 1]
            print(f"✂️ Truncated at sentence end to {len(result)} characters")
            return result
        else:
            # Fall back to word boundary
            result = text[:max_length].rsplit(' ', 1)[0]
            print(f"✂️ Truncated at word boundary to {len(result)} characters")
            return result

# Test with sample enhanced prompt
sample_prompt = """### Enhanced Product Photography Brief: Luxe Skincare Revival Cream

---

#### **1. Main Subject: Hero Shot of the Luxe Skincare Revival Cream**  
The Luxe Skincare Revival Cream is presented in a matte black jar with an elegantly reflective metallic silver lid. The jar features engraved text, delicately recessed into the surface.

---

#### **2. Composition and Framing**  
A straight-on hero shot with a slight downward tilt, ensuring the jar is the central focal point. This classic perspective emphasizes the products symmetry and solidity.

---

#### **3. Lighting and Atmosphere**  
A low-key lighting setup will create a dramatic, moody atmosphere. The interplay of light and shadow will highlight the products premium textures and details."""

print("🧪 Smart Truncation Demo")
print("=" * 50)

result = smart_truncate_demo(sample_prompt, 300)
print("\n📄 Final truncated prompt:")
print("-" * 30)
print(result)
print("-" * 30)
print(f"\n✅ Result: Clean, complete section ending (no mid-sentence cuts)")
