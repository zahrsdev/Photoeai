"""
AI Client service for interacting with the OpenAI API.
Handles both extraction and enhancement operations with the LLM.
"""

import json
from typing import Dict, Any, Optional
from openai import OpenAI
from loguru import logger
from app.config.settings import settings


class AIClient:
    """
    Client for interacting with OpenAI's API.
    Handles both extraction            )
            
            enhanced_brief = response.choices[0].message.content.strip()
            
            # CRITICAL POST-PROCESSING: English language validation and cleanup
            enhanced_brief = self._ensure_english_output(enhanced_brief, request_id)
            
            # COMPREHENSIVE QUALITY VALIDATION WITH LANGUAGE COMPLIANCE as Analyst) and enhancement (LLM as Product Photographer) operations.
    """
    
    def __init__(self):
        """Initialize the OpenAI client with API key and official OpenAI base URL from settings."""
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url="https://api.openai.com/v1"  # Use official OpenAI API directly
        )
        self.model = settings.openai_model
    
    def _get_client(self, user_api_key: Optional[str] = None) -> OpenAI:
        """Get OpenAI client with user API key if provided, otherwise use default."""
        if user_api_key and user_api_key.strip():
            return OpenAI(
                api_key=user_api_key.strip(),
                base_url="https://api.openai.com/v1"
            )
        return self.client
    
    async def extract_wizard_data(self, user_request: str) -> Dict[str, Any]:
        """
        Extract structured wizard data from user request using LLM as Analyst.
        
        Args:
            user_request: Raw user request text
            
        Returns:
            Dictionary containing extracted wizard input fields
        """
        request_id = hash(user_request) % 10000  # Simple request tracking
        
        logger.info(f"🔍 Starting wizard data extraction [ID: {request_id}]", extra={
            "request_id": request_id,
            "user_request_length": len(user_request),
            "ai_model": self.model,
            "operation": "extract_wizard_data"
        })
        
        prompt = f"""
        Analyze this product photography request and extract the relevant information for a structured photography brief.
        
        User request: "{user_request}"
        
        CRITICAL: You MUST provide values for these REQUIRED fields (never use null for these):
        - product_name: If unclear, infer from context or use "Product" as fallback
        - shot_type: Choose from [Eye-level, High-angle, Low-angle, Dutch-angle, Top-down flat lay]
        - framing: Choose from [Extreme Close-Up, Close-Up, Medium Shot, Full Shot]
        - lighting_style: Choose from [Studio Softbox, Hard light, Natural window light, Golden hour glow, Cinematic neon]
        - environment: Choose from [Seamless studio backdrop, Textured surface, Natural setting, Indoor setting]
        
        Extract information for ALL 46 fields below (ALL VALUES MUST BE STRINGS, NOT ARRAYS):
        
        # SECTION 1: Main Subject & Story
        product_name: Name of the product (REQUIRED - string, never null)
        product_description: Description of the product (string)
        key_features: Key features to highlight (string, comma-separated if multiple)
        product_state: State of the product (string, default: "pristine")
        
        # SECTION 2: Composition & Framing
        shot_type: Type of shot (REQUIRED - string, choose most appropriate)
        framing: Framing style (REQUIRED - string, choose most appropriate) 
        compositional_rule: Compositional rule (string, default: "Rule of Thirds")
        negative_space: Negative space approach (string, default: "Balanced")
        
        # SECTION 3: Lighting & Atmosphere
        lighting_style: Lighting style (REQUIRED - string, choose most appropriate)
        key_light_setup: Key light setup description (string)
        fill_light_setup: Fill light setup description (string)
        rim_light_setup: Rim light setup description (string)
        mood: Overall mood (string, default: "Clean and professional")
        
        # SECTION 4: Background & Setting
        environment: Environment/background (REQUIRED - string, choose most appropriate)
        dominant_colors: Dominant color palette (string, comma-separated if multiple)
        accent_colors: Accent colors (string, comma-separated if multiple)
        props: Supporting props description (string)
        
        # SECTION 5: Camera & Lens
        camera_type: Camera type (string, default: "Hasselblad X2D 100C")
        lens_type: Lens type (string, default: "85mm f/1.4")
        aperture_value: Aperture f-number (number, default: 2.8)
        shutter_speed_value: Shutter speed denominator (number, default: 125)
        iso_value: ISO value (number, default: 100)
        visual_effect: Visual effect description (string)
        
        # SECTION 6: Style & Post-Production
        overall_style: Overall photographic style (string, default: "Professional product photography")
        photographer_influences: Photographer influences (string, comma-separated if multiple)
        
        # SECTION 7: Advanced Lighting (NEW)
        light_temperature: Light temperature (string, e.g. "warm 3200K", "daylight 5600K")
        shadow_intensity: Shadow intensity (string: "soft", "hard", "medium")
        highlight_control: Highlight control (string: "preserved", "blown", "controlled")
        lighting_direction: Lighting direction (string: "front", "side", "back", "top")
        ambient_lighting: Ambient lighting (string: "studio", "natural", "mixed")
        
        # SECTION 8: Advanced Composition (NEW)
        perspective_angle: Perspective angle (string: "eye-level", "low-angle", "high-angle")
        depth_layers: Depth layers (string describing foreground/midground/background)
        leading_lines: Leading lines (string: "diagonal", "curved", "vertical", "none")
        symmetry_type: Symmetry type (string: "perfect", "asymmetrical", "radial")
        focal_emphasis: Focal emphasis (string: "center", "off-center", "multiple points")
        
        # SECTION 9: Technical Details (NEW)
        focus_mode: Focus mode (string: "manual", "single-point AF", "zone AF")
        metering_mode: Metering mode (string: "matrix", "center-weighted", "spot")
        white_balance: White balance (string: "auto", "daylight", "tungsten", "custom")
        file_format: File format (string: "RAW", "JPEG", "TIFF")
        image_stabilization: Image stabilization (string: "on", "off", "lens-based", "body-based")
        
        # SECTION 10: Brand & Marketing Context (NEW)
        target_audience: Target audience (string: "luxury", "mass market", "professional")
        brand_personality: Brand personality (string: "premium", "friendly", "innovative")
        usage_purpose: Usage purpose (string: "e-commerce", "advertising", "social media")
        seasonal_context: Seasonal context (string: "spring", "summer", "holiday", "evergreen")
        competitive_differentiation: Competitive differentiation (string: unique selling points)
        
        IMPORTANT: 
        - Respond ONLY with valid JSON containing ALL 46 fields
        - ALL text fields must be STRINGS, not arrays
        - Use comma-separated strings for multiple values (e.g. "red, blue, gold" not ["red", "blue", "gold"])
        - NEVER use null for any field - provide intelligent defaults
        - Use reasonable professional photography defaults when information is unclear
        - Make intelligent inferences based on the request context and product type
        """
        
        logger.debug(f"📝 Sending extraction request to AI [ID: {request_id}]", extra={
            "request_id": request_id,
            "prompt_length": len(prompt),
            "temperature": 0.6
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert photography analyst. Extract structured data from user requests and respond only with valid JSON. When requests are vague, make professional inferences and use industry-standard defaults. NEVER leave required fields as null."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6
            )
            
            response_text = response.choices[0].message.content.strip()
            
            logger.debug(f"📥 Received AI response [ID: {request_id}]", extra={
                "request_id": request_id,
                "response_length": len(response_text),
                "tokens_used": response.usage.total_tokens if response.usage else None
            })
            
            # Try to parse the JSON response
            try:
                extracted_data = json.loads(response_text)
                
                logger.info(f"✅ Successfully extracted wizard data [ID: {request_id}]", extra={
                    "request_id": request_id,
                    "extracted_fields": list(extracted_data.keys()),
                    "product_name": extracted_data.get("product_name"),
                    "operation": "extract_wizard_data",
                    "status": "success"
                })
                
                return extracted_data
                
            except json.JSONDecodeError as json_error:
                logger.warning(f"⚠️ JSON parsing failed, attempting recovery [ID: {request_id}]", extra={
                    "request_id": request_id,
                    "json_error": str(json_error),
                    "response_preview": response_text[:200] + "..." if len(response_text) > 200 else response_text
                })
                
                # If JSON parsing fails, try to extract JSON from the response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    extracted_data = json.loads(json_match.group())
                    
                    logger.info(f"✅ Recovered JSON from malformed response [ID: {request_id}]", extra={
                        "request_id": request_id,
                        "extracted_fields": list(extracted_data.keys()),
                        "recovery_method": "regex_extraction"
                    })
                    
                    return extracted_data
                else:
                    logger.error(f"💥 Failed to parse or recover JSON [ID: {request_id}]", extra={
                        "request_id": request_id,
                        "raw_response": response_text,
                        "operation": "extract_wizard_data",
                        "status": "json_parse_failed"
                    })
                    return {}
                    
        except Exception as e:
            logger.error(f"💥 Critical error in wizard data extraction [ID: {request_id}]", extra={
                "request_id": request_id,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "operation": "extract_wizard_data",
                "status": "error"
            })
            raise Exception(f"AI extraction failed: {str(e)}")
    
    async def enhance_brief(self, original_brief: str) -> str:
        """
        Enhance a photography brief using LLM as Product Photographer.
        
        Args:
            original_brief: The original brief text to be enhanced
            
        Returns:
            Enhanced brief text
        """
        request_id = hash(original_brief) % 10000  # Simple request tracking
        
        logger.info(f"🎨 Starting brief enhancement [ID: {request_id}]", extra={
            "request_id": request_id,
            "original_brief_length": len(original_brief),
            "ai_model": self.model,
            "operation": "enhance_brief"
        })
        
        try:
            # Get enhancement instructions from settings
            enhancement_template = settings.enhancement_template
            stopping_power_rules = settings.stopping_power_rules
            anti_anomaly_rules = settings.anti_anomaly_rules
            
            logger.debug(f"📋 Retrieved enhancement templates [ID: {request_id}]", extra={
                "request_id": request_id,
                "has_enhancement_template": bool(enhancement_template),
                "stopping_power_rules_count": len(stopping_power_rules) if stopping_power_rules else 0,
                "anti_anomaly_rules_count": len(anti_anomaly_rules) if anti_anomaly_rules else 0
            })
            
            # Build the enhancement prompt
            system_message = enhancement_template.get("enhancement_instructions", [{}])[0].get("content", "")
            # Add mandatory English enforcement to system message
            system_message = "MANDATORY OUTPUT LANGUAGE: ENGLISH. The entire output brief MUST be written in professional English, regardless of the language of the user's input.\n\n" + system_message
            user_template = enhancement_template.get("enhancement_instructions", [{}, {}])[1].get("content", "")
            
            # Replace the template variable
            user_message = user_template.replace("{{original_brief}}", original_brief)
            
            # Add context about stopping power and anti-anomaly rules
            context_addition = f"""
            
            Additional context to guide your enhancement:
            
            STOPPING POWER ELEMENTS (incorporate selectively):
            {json.dumps(stopping_power_rules, indent=2)}
            
            AVOID THESE ANOMALIES:
            {json.dumps(anti_anomaly_rules, indent=2)}
            
            Focus on enhancing the brief while maintaining photographic realism and avoiding the listed anomalies.
            """
            
            user_message += context_addition
            
            logger.debug(f"📝 Sending enhancement request to AI [ID: {request_id}]", extra={
                "request_id": request_id,
                "prompt_length": len(user_message),
                "temperature": 0.6,
                "max_tokens": 2000
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.6,
                max_tokens=2000
            )
            
            enhanced_brief = response.choices[0].message.content.strip()
            
            # CRITICAL POST-PROCESSING: English language validation and cleanup
            enhanced_brief = self._ensure_english_output(enhanced_brief, request_id)
            
            logger.info(f"✅ Brief enhancement completed successfully [ID: {request_id}]", extra={
                "request_id": request_id,
                "original_length": len(original_brief),
                "enhanced_length": len(enhanced_brief),
                "enhancement_ratio": round(len(enhanced_brief) / len(original_brief), 2) if original_brief else 0,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "operation": "enhance_brief",
                "status": "success"
            })
            
            return enhanced_brief
            
        except Exception as e:
            logger.error(f"💥 Critical error in brief enhancement [ID: {request_id}]", extra={
                "request_id": request_id,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "operation": "enhance_brief",
                "status": "error"
            })
            raise Exception(f"AI enhancement service unavailable: {str(e)}")

    async def enhance_brief_from_structured_data(self, structured_data: dict, user_api_key: Optional[str] = None) -> str:
        """
        CRITICAL REFACTOR: Generate comprehensive photography brief from structured data.
        
        This method implements the fully refactored Product Photographer that generates complete,
        multi-section, detailed photography briefs from JSON input data with ADVANCED ENHANCEMENT.
        
        Args:
            structured_data: Complete WizardInput data in dictionary format
            
        Returns:
            Complete, multi-section photography brief document with professional enhancement
        """
        request_id = hash(str(structured_data)) % 10000  # Simple request tracking
        
        logger.info(f"🎭 ADVANCED: Product Photographer enhanced composition [ID: {request_id}]", extra={
            "request_id": request_id,
            "product_name": structured_data.get("product_name", "Unknown"),
            "ai_model": self.model,
            "operation": "enhance_brief_from_structured_data",
            "refactor_status": "ADVANCED_ENHANCEMENT_ACTIVE"
        })
        
        try:
            # CRITICAL FINAL REFACTOR: ULTRA-DETAILED STRUCTURE ENFORCEMENT
            enhancement_instruction = f"""
🚨🚨🚨 CRITICAL SYSTEM OVERRIDE: COMPREHENSIVE DETAILED BRIEF MANDATORY 🚨🚨🚨

You are an ELITE Product Photographer with 20+ years of world-class product photography experience. You've worked with luxury brands, directed award-winning campaigns, and your images are featured in top-tier publications. ABSOLUTE MANDATORY: NEVER MODIFY THE PRODUCT ITSELF - only enhance photography techniques.

**⚠️⚠️⚠️ ABSOLUTE NON-NEGOTIABLE REQUIREMENTS ⚠️⚠️⚠️**

❌ FORBIDDEN: Writing in Indonesian, Spanish, French, German, or ANY non-English language
✅ MANDATORY: Write 100% in professional English only
❌ FORBIDDEN: Short, basic, or incomplete briefs
✅ MANDATORY: Generate a COMPREHENSIVE, DETAILED brief exactly like this structure with extensive bullet points and sub-details

**🚨 COMPREHENSIVE STRUCTURE ENFORCEMENT:**

Your output MUST follow this exact detailed format with extensive bullet points, sub-categories, and technical specifications:

```markdown
# **[Product Type] Photography Brief: [Product Name]**

---

#### **1. Main Subject: Hero Shot of the [Product Name]**
- **Product Details**: [Detailed physical description with materials, finishes, textures]
- **Product State**: [Condition and presentation approach]
- **Hero Features**: [Key elements to emphasize]
- **Brand Positioning**: [Luxury positioning and target appeal]

---

#### **2. Composition and Framing**
- **Shot Type**: [Specific angle with creative justification]
- **Framing**: [Detailed framing approach with technical reasoning]
- **Compositional Rule**: [Specific rules with placement details]
- **Negative Space**: [Background treatment and focus direction]
- **Visual Hierarchy**: [How elements guide the viewer's eye]
- **Perspective Psychology**: [Why this angle creates desired impact]

---

#### **3. Lighting and Atmosphere**
- **Lighting Style**: [Overall lighting approach and mood]
  - **Key Light**: [Specific equipment model, position, angle, and effect]
  - **Fill Light**: [Equipment, position, power ratio, and purpose]
  - **Rim Light**: [Equipment, positioning, and separation effect]
  - **Background Light**: [If applicable, equipment and effect]
  - **Special Effects**: [Any additional lighting elements]
- **Light Ratios**: [Technical ratios between key, fill, and rim]
- **Color Temperature**: [Kelvin values and color consistency]
- **Overall Mood**: [Atmospheric description and emotional impact]

---

#### **4. Background and Setting**
- **Environment**: [Detailed surface and backdrop description]
- **Color Palette**: [Comprehensive color scheme with psychological impact]
- **Supporting Props**: [Multiple props with detailed descriptions]
  - **[Prop 1]**: [Detailed description and placement reasoning]
  - **[Prop 2]**: [Detailed description and symbolic meaning]
  - **[Prop 3]**: [Detailed description and compositional role]
- **Texture Elements**: [Surface treatments and tactile qualities]
- **Supporting Dynamic Elements**: [Environmental effects like mist, reflections]

---

#### **5. Camera and Lens Simulation**
- **Camera Body**: [Specific professional camera model with technical justification]
- **Lens**: [Exact lens specifications with optical characteristics]
- **Camera Settings**: [Complete exposure triangle with technical reasoning]
  - **Aperture**: [F-stop with depth of field justification]
  - **Shutter Speed**: [Speed with motion control reasoning]
  - **ISO**: [Value with noise/quality balance]
- **Focus Strategy**: [Focus point placement and depth of field control]
- **Visual Effects**: [Bokeh quality, background rendering, focus falloff]

---

#### **6. Stylistic Enhancements**
- **Visual Style References**: [Professional photographer influences]
- **Additional Stopping Power Elements**: [Multiple enhancement strategies]
  - **Emotional Impact**: [How colors, textures, and mood create feeling]
  - **Dynamic Composition**: [Leading lines, visual flow, eye movement]
  - **Dramatic Elements**: [Atmospheric effects and visual interest]
  - **Extreme Realism**: [Texture detail and tactile quality description]
- **Brand Alignment**: [How style supports brand positioning]

---

#### **7. Post-Processing and Color Grading**
- **Color Grading**: [Comprehensive color treatment approach]
- **Retouching Workflow**: [Step-by-step post-production process]
- **Visual Accents**: [Specific enhancement details]
  - **Highlight Treatment**: [How highlights are refined]
  - **Shadow Detail**: [Shadow control and depth]
  - **Texture Enhancement**: [Surface detail amplification]
  - **Reflection Control**: [Reflective surface management]

---

#### **7. ABSOLUTE MANDATORY: PRODUCT LOCK SYSTEM**
- **NEVER CHANGE THE PRODUCT**: The product must appear EXACTLY as it exists in reality. Zero modifications allowed.
- **WARNA PRODUK HARAM DIUBAH**: Original product colors must be preserved 100%. Never change white to black, blue to red, or any color transformation.
- **STRICTLY PROHIBITED**: ubah warna, ganti warna, change colors, recolor, color swap, tint, hue shift, saturation boost on product.
- **ORIGINAL COLORS SACRED**: Product's actual colors from real world must remain untouched and authentic.
- **PHOTOGRAPHY ONLY ENHANCEMENTS**: lighting setup, camera angles, background elements, depth of field, composition rules.
- **VIOLATION PENALTY**: Any attempt to modify the product colors or appearance will result in immediate rejection. PRODUK ASLI HARUS TETAP ASLI.

---

### **Creative Rationale**
[MANDATORY: Comprehensive 150+ word explanation in English of creative choices, technical decisions, brand strategy, and visual storytelling approach. Reference professional photographers and explain why each element serves the overall campaign objective.]
```

**🚨 DETAILED OUTPUT REQUIREMENTS:**
- MINIMUM 1,200 words total
- MINIMUM 8 major sections with extensive bullet points
- MINIMUM 3-5 bullet points per major category
- MINIMUM 150-word Creative Rationale section
- MAXIMUM professional detail in every category
- MANDATORY specific equipment models and technical specifications

**CLIENT FOUNDATION DATA:**
```json
{json.dumps(structured_data, indent=2)}
```

**🚨 EXECUTE COMPREHENSIVE MASTERPIECE IN ENGLISH 🚨**
Generate the most detailed, comprehensive photography brief possible. Every section must be extensively detailed with multiple bullet points, technical specifications, and professional reasoning. This must be a masterpiece-level document that would impress the most demanding luxury brand clients.
"""

            logger.debug(f"📝 ADVANCED: Dispatching Elite Enhancement [ID: {request_id}]", extra={
                "request_id": request_id,
                "instruction_length": len(enhancement_instruction),
                "structured_data_fields": list(structured_data.keys()),
                "product_name": structured_data.get("product_name", "Unknown"),
                "temperature": 0.6,  # Balanced creativity for professional results
                "max_tokens": 4500,   # Expanded for masterpiece output
                "enhancement_level": "ELITE_PROFESSIONAL"
            })

            # OPTIMIZED PARAMETERS FOR CREATIVE EXCELLENCE
            client = self._get_client(user_api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "MANDATORY OUTPUT LANGUAGE: ENGLISH. The entire output brief MUST be written in professional English, regardless of the language of the user's input.\n\nYou are a world-class Product Photographer with elite expertise in luxury product photography. Your job is to enhance PHOTOGRAPHY QUALITY while NEVER MODIFYING THE PRODUCT ITSELF. ABSOLUTE MANDATORY: Never change product colors, shapes, or designs - only enhance lighting, composition, and camera techniques. DETECTION WARNING: NEVER use words like 'ubah', 'gantikan', 'remix', 'alter', 'modify', 'change', 'transform', or 'redesign' when referring to the product - these actions are STRICTLY FORBIDDEN. CRITICAL REQUIREMENTS: 1) Every single word must be ENTIRELY IN ENGLISH, regardless of input language. 2) Generate COMPREHENSIVE, DETAILED briefs with extensive bullet points, technical specifications, and professional equipment details. Your reputation depends on comprehensive English-only masterpiece documents with 1200+ words and extensive technical detail."
                    },
                    {"role": "user", "content": enhancement_instruction}
                ],
                temperature=0.6,     # Balanced creativity for professional results
                max_tokens=4500       # Increased for comprehensive masterpiece output
            )
            
            enhanced_brief = response.choices[0].message.content.strip()
            
            # ADVANCED QUALITY VALIDATION WITH LANGUAGE COMPLIANCE
            word_count = len(enhanced_brief.split())
            section_count = enhanced_brief.count('##')
            technical_terms = sum(1 for term in ['profoto', 'canon', 'sony', 'nikon', 'lighting', 'exposure', 'composition', 'color grading'] 
                                if term.lower() in enhanced_brief.lower())
            
            # SMART LANGUAGE COMPLIANCE CHECK (excluding legitimate technical terms and brand names)
            # Only check for clear non-English patterns in isolation, not technical terms
            non_english_indicators = [
                # Indonesian indicators (clear grammar words)
                'yang adalah', 'yang akan', 'dan juga', 'dengan sangat', 'untuk menciptakan',
                'dari hasil', 'ini akan', 'adalah sebuah', 'akan memberikan', 'atau dapat',
                'pada saat', 'dalam kondisi', 'oleh karena', 'juga dapat', 'dapat memberikan',
                'lebih baik', 'saat ini', 'hanya dengan', 'tidak akan', 'sangat penting',
                # Spanish indicators (clear grammar patterns)
                'el producto', 'la imagen', 'de la', 'con el', 'por favor', 'para el',
                'del producto', 'los usuarios', 'las características', 'una vez', 'uno de',
                'que es', 'muy importante', 'más que', 'son muy', 'está muy',
                'pero también', 'como un', 'todo el', 'bien diseñado',
                # French indicators (clear grammar patterns)
                'le produit', 'du produit', 'avec le', 'pour le', 'les images', 'des éléments',
                'dans le', 'par le', 'sur le', 'qui est', 'que le', 'est très',
                'une belle', 'pas de', 'tout le', 'peut être', 'mais aussi', 'bien fait', 'très belle',
                # German indicators (clear grammar patterns)  
                'der Produkts', 'die Beleuchtung', 'und das', 'mit dem', 'das ist',
                'den Produkts', 'von dem', 'zu dem', 'für das', 'auf dem',
                'ist sehr', 'ein sehr', 'eine sehr', 'auch sehr', 'nur mit',
                'oder auch', 'aber auch', 'wie ein', 'sehr gut'
            ]
            
            # Check for actual language violations (multi-word patterns)
            language_violations = 0
            for indicator in non_english_indicators:
                if indicator.lower() in enhanced_brief.lower():
                    language_violations += 1
            
            has_creative_rationale = 'creative rationale' in enhanced_brief.lower() or 'rationale' in enhanced_brief.lower()
            
            logger.info(f"✅ ADVANCED: Elite enhancement completed [ID: {request_id}]", extra={
                "request_id": request_id,
                "structured_data_size": len(str(structured_data)),
                "enhanced_length": len(enhanced_brief),
                "word_count": word_count,
                "section_count": section_count,
                "technical_depth": technical_terms,
                "language_compliance": "PASS" if language_violations == 0 else "FAIL",
                "language_violations": language_violations,
                "has_creative_rationale": has_creative_rationale,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "operation": "enhance_brief_from_structured_data",
                "status": "ELITE_ENHANCEMENT_SUCCESS",
                "quality_level": "MASTERPIECE" if word_count > 300 and section_count >= 6 and technical_terms >= 3 and language_violations == 0 else "PROFESSIONAL"
            })
            
            # CRITICAL QUALITY ASSURANCE: Ensure comprehensive detailed output
            quality_issues = []
            if word_count < 1200:
                quality_issues.append(f"Word count below comprehensive standard: {word_count} < 1200")
            if section_count < 7:
                quality_issues.append(f"Section count below comprehensive standard: {section_count} < 7")
            if language_violations > 0:
                quality_issues.append(f"CRITICAL: Non-English content detected - {language_violations} violations")
            if not has_creative_rationale:
                quality_issues.append("Missing mandatory Creative Rationale section")
            
            # Check for detailed structure indicators
            bullet_points = enhanced_brief.count('- **') + enhanced_brief.count('  - **')
            if bullet_points < 15:
                quality_issues.append(f"Insufficient detail structure: {bullet_points} bullet points < 15 required")
                
            if quality_issues:
                logger.warning(f"⚠️ COMPREHENSIVE QUALITY ALERT: Enhancement issues detected [ID: {request_id}]", extra={
                    "request_id": request_id,
                    "quality_issues": quality_issues,
                    "word_count": word_count,
                    "section_count": section_count,
                    "bullet_points": bullet_points,
                    "language_violations": language_violations,
                    "expected_word_count": ">=1200",
                    "expected_sections": ">=7",
                    "expected_bullet_points": ">=15",
                    "expected_language": "English only",
                    "recommendation": "Generate more comprehensive detailed brief with extensive bullet points"
                })
            
            # CRITICAL POST-PROCESSING: English language validation and cleanup
            enhanced_brief = self._ensure_english_output(enhanced_brief, request_id)
            
            return enhanced_brief
            
        except Exception as e:
            logger.error(f"💥 CRITICAL ERROR: Elite enhancement system failure [ID: {request_id}]", extra={
                "request_id": request_id,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "operation": "enhance_brief_from_structured_data",
                "status": "ELITE_ENHANCEMENT_ERROR",
                "input_data_size": len(str(structured_data)),
                "product_name": structured_data.get("product_name", "Unknown")
            })
            raise Exception(f"ELITE ENHANCEMENT FAILURE - Product Photographer system unavailable: {str(e)}")

    async def enhance_prompt_intelligently(self, original_prompt: str, enhancement_instruction: str) -> str:
        """
        Intelligently enhance a photography prompt using advanced AI techniques.
        
        This method creates sophisticated prompt enhancements that go beyond simple
        concatenation to produce truly improved, professional photography prompts.
        
        Args:
            original_prompt: The original photography prompt
            enhancement_instruction: User's enhancement instruction
            
        Returns:
            Intelligently enhanced prompt with professional improvements
        """
        request_id = hash(original_prompt + enhancement_instruction) % 10000
        
        logger.info(f"🧠 INTELLIGENT: Advanced prompt enhancement [ID: {request_id}]", extra={
            "request_id": request_id,
            "original_length": len(original_prompt),
            "instruction": enhancement_instruction[:50] + "..." if len(enhancement_instruction) > 50 else enhancement_instruction,
            "operation": "enhance_prompt_intelligently"
        })
        
        try:
            enhancement_instruction = f"""
You are an elite prompt engineer with deep expertise in photography and AI image generation. Your task is to intelligently enhance the original photography prompt by incorporating the user's enhancement request in the most sophisticated way possible.

**ENHANCEMENT PHILOSOPHY:**
- Don't just append or prepend text
- Analyze the original prompt's structure and intent
- Weave the enhancement naturally into the existing narrative
- Elevate technical and artistic language
- Add professional photography terminology where appropriate
- Maintain the core creative vision while amplifying impact

**ORIGINAL PROMPT:**
{original_prompt}

**USER'S ENHANCEMENT REQUEST:**
{enhancement_instruction}

**ENHANCEMENT GUIDELINES:**

1. **INTELLIGENT INTEGRATION**: Seamlessly weave the enhancement into the existing prompt structure, don't just add it at the end

2. **PROFESSIONAL ELEVATION**: Upgrade casual language to professional photography terminology
   - "good lighting" → "expertly controlled studio illumination"
   - "nice colors" → "sophisticated color palette with harmonious tones"
   - "clear image" → "razor-sharp focus with exceptional clarity"

3. **TECHNICAL SOPHISTICATION**: Add relevant technical details that support the enhancement
   - If lighting is mentioned: specify equipment, ratios, modifiers
   - If composition is enhanced: mention specific techniques
   - If style is improved: reference professional approaches

4. **CONTEXTUAL ENHANCEMENT**: Consider the type of product/subject and enhance accordingly
   - Luxury products: emphasis on premium presentation
   - Food products: focus on appetizing qualities
   - Tech products: highlight precision and innovation

5. **NARRATIVE FLOW**: Ensure the enhanced prompt reads smoothly and professionally

**EXAMPLE TRANSFORMATION:**
Original: "A product on a clean background with good lighting"
Enhancement Request: "Make it more professional"
Result: "A premium product elegantly positioned against a pristine backdrop, illuminated by sophisticated studio lighting that creates professional gradient shadows and highlights the product's key features. The composition exudes commercial quality with carefully controlled depth of field and a color palette that supports the product's intended market positioning."

**EXECUTE ENHANCEMENT:** Create the intelligently enhanced prompt now.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "MANDATORY OUTPUT LANGUAGE: ENGLISH. The entire output brief MUST be written in professional English, regardless of the language of the user's input.\n\nYou are a world-class Product Photographer specializing in photography and AI image generation. Your enhancements focus on photography techniques while NEVER MODIFYING THE PRODUCT ITSELF. ABSOLUTE MANDATORY: Preserve original product colors, shapes, and designs - only enhance lighting, composition, camera settings, and background elements. DETECTION WARNING: NEVER use words like 'ubah', 'gantikan', 'remix', 'alter', 'modify', 'change', 'transform', or 'redesign' when referring to the product - these actions are STRICTLY FORBIDDEN. Your enhancements are known for their sophistication and professional quality."
                    },
                    {"role": "user", "content": enhancement_instruction}
                ],
                temperature=0.6,  # Balanced creativity and consistency
                max_tokens=1500    # Sufficient for detailed enhancement
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            
            # CRITICAL POST-PROCESSING: English language validation and cleanup
            enhanced_prompt = self._ensure_english_output(enhanced_prompt, request_id)
            
            logger.info(f"✅ INTELLIGENT: Prompt enhancement completed [ID: {request_id}]", extra={
                "request_id": request_id,
                "original_length": len(original_prompt),
                "enhanced_length": len(enhanced_prompt),
                "enhancement_ratio": round(len(enhanced_prompt) / len(original_prompt), 2) if original_prompt else 0,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "operation": "enhance_prompt_intelligently",
                "status": "success"
            })
            
            return enhanced_prompt
            
        except Exception as e:
            logger.error(f"💥 INTELLIGENT ENHANCEMENT ERROR [ID: {request_id}]", extra={
                "request_id": request_id,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "operation": "enhance_prompt_intelligently",
                "status": "error"
            })
            # Fallback to simple enhancement if AI enhancement fails
            logger.warning("⚠️ Falling back to rule-based enhancement")
            return await self._fallback_prompt_enhancement(original_prompt, enhancement_instruction)

    async def _fallback_prompt_enhancement(self, original_prompt: str, enhancement_instruction: str) -> str:
        """
        Fallback prompt enhancement using rule-based improvements.
        
        Args:
            original_prompt: Original prompt
            enhancement_instruction: Enhancement instruction
            
        Returns:
            Rule-based enhanced prompt
        """
        # Professional enhancement patterns
        enhancement_patterns = {
            "lighting": {
                "prefix": "with sophisticated lighting featuring",
                "suffix": ", creating professional studio-quality illumination"
            },
            "composition": {
                "prefix": "expertly composed using",
                "suffix": ", showcasing masterful framing and visual balance"
            },
            "quality": {
                "prefix": "rendered in premium quality with",
                "suffix": ", exhibiting exceptional detail and professional finish"
            },
            "style": {
                "prefix": "styled with elevated aesthetic featuring",
                "suffix": ", demonstrating refined artistic vision"
            },
            "luxury": {
                "prefix": "presented with luxury appeal including",
                "suffix": ", conveying premium brand sophistication"
            }
        }
        
        # Detect enhancement type
        instruction_lower = enhancement_instruction.lower()
        enhancement_type = "quality"  # default
        
        for pattern_type in enhancement_patterns.keys():
            if pattern_type in instruction_lower:
                enhancement_type = pattern_type
                break
        
        pattern = enhancement_patterns[enhancement_type]
        
        # Create enhanced prompt
        enhanced_prompt = f"{original_prompt.rstrip('.')}, {pattern['prefix']} {enhancement_instruction}{pattern['suffix']}"
        
        return enhanced_prompt

    async def revise_prompt_for_generation(self, original_prompt: str, user_api_key: Optional[str] = None) -> str:
        """
        Create a complete enhanced photography brief from a basic prompt for superior image generation results.
        
        This method transforms simple prompts into comprehensive, professionally-structured photography
        briefs with detailed sections covering all aspects of professional product photography.
        
        Args:
            original_prompt: The basic photography prompt to enhance
            
        Returns:
            Complete enhanced photography brief optimized for image generation
        """
        request_id = hash(original_prompt) % 10000
        
        logger.info(f"✨ ENHANCEMENT: Creating complete enhanced brief [ID: {request_id}]", extra={
            "request_id": request_id,
            "original_length": len(original_prompt),
            "operation": "revise_prompt_for_generation"
        })
        
        try:
            # Use user API key if provided, otherwise fall back to system key
            if user_api_key and user_api_key.strip():
                # Create a temporary client with user's API key
                temp_client = OpenAI(
                    api_key=user_api_key,
                    base_url="https://api.openai.com/v1"  # Use OpenAI directly for user keys
                )
                client_to_use = temp_client
            else:
                # Use system client
                client_to_use = self.client
                
            # This is the new, powerful instruction template.
            enhancement_instruction_template = """
You are an elite-level Product Photographer and world-renowned product photography specialist. Your task is to take the following simple user request and transform it into a comprehensive, fully detailed Product Photography Brief that matches professional industry standards. ABSOLUTE MANDATORY: NEVER MODIFY THE PRODUCT ITSELF - only enhance photography techniques, lighting, and composition.

**CRITICAL INSTRUCTIONS:**
1. **Complete Professional Brief**: Create a full, structured photography brief with all professional sections including Overview, Photography Specifications, Lighting Setup, Composition & Framing, Background & Props, Post-Processing & Color Grading, and Creative Rationale.

2. **Technical Specifications Must Include**:
   - **Camera & Lens**: Specific professional equipment (e.g., "Hasselblad X2D 100C", "85mm f/1.4 lens with creamy bokeh")
   - **Detailed Lighting Setup**: Multiple lights with specific positions, angles, and purposes (Key Light, Fill Light, Back Light, Additional Lighting)
   - **Composition Rules**: Specific framing guidelines (Rule of Thirds, angles, crop specifications)
   - **Props & Background**: Detailed styling elements and background specifications
   - **Post-Processing**: Specific color grading, retouching, and enhancement instructions

3. **Creative Rationale**: Include a detailed explanation of all creative and technical choices made.

4. **Professional Format**: Structure the brief with clear headings, subheadings, and bullet points for easy reading by photography teams.

5. **Comprehensive Detail**: The brief should be thorough enough that any professional photographer could execute the exact vision described.

**User's Request:**
{original_prompt}

Create a complete, comprehensive Product Photography Brief that transforms this simple request into a professional-grade photography direction document:
"""
            # Dynamically format the final instruction
            enhancement_instruction = enhancement_instruction_template.format(original_prompt=original_prompt)

            response = client_to_use.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "MANDATORY OUTPUT LANGUAGE: ENGLISH. The entire output brief MUST be written in professional English, regardless of the language of the user's input.\n\nYou are an elite Product Photographer and world-renowned product photography specialist. You create comprehensive, fully-structured Product Photography Briefs that match professional industry standards. ABSOLUTE MANDATORY: NEVER MODIFY THE PRODUCT ITSELF - only enhance photography techniques, lighting, composition, and camera settings. Your briefs include complete technical specifications, detailed lighting setups, composition guidelines, styling directions, and creative rationales that enable professional photographers to execute award-winning shoots."
                    },
                    {"role": "user", "content": enhancement_instruction}
                ],
                temperature=0.6,  # Balanced for creativity while maintaining structure
                max_tokens=3000   # Sufficient for complete detailed brief
            )
            
            revised_prompt = response.choices[0].message.content.strip()
            
            # CRITICAL POST-PROCESSING: English language validation and cleanup
            revised_prompt = self._ensure_english_output(revised_prompt, request_id)
            
            logger.info(f"✅ ENHANCEMENT: Complete enhanced brief created [ID: {request_id}]", extra={
                "request_id": request_id,
                "original_length": len(original_prompt),
                "enhanced_length": len(revised_prompt),
                "enhancement_ratio": round(len(revised_prompt) / len(original_prompt), 2) if original_prompt else 0,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "operation": "revise_prompt_for_generation",
                "status": "success"
            })
            
            return revised_prompt
            
        except Exception as e:
            logger.error(f"💥 ENHANCED BRIEF CREATION ERROR [ID: {request_id}]", extra={
                "request_id": request_id,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "operation": "revise_prompt_for_generation",
                "status": "error"
            })
            # Return original if enhancement fails
            logger.warning("⚠️ Enhanced brief creation failed, using original prompt")
            return original_prompt
    
    async def generate_text(self, prompt: str, temperature: float = 0.6, max_tokens: int = 2000) -> str:
        """
        Generate text completion using the AI client.
        
        This method provides a simple interface for text generation tasks like prompt compression.
        
        Args:
            prompt: The input prompt for text generation
            temperature: Creativity level (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        request_id = hash(prompt) % 10000
        
        logger.debug(f"📝 TEXT GENERATION: Starting request [ID: {request_id}]", extra={
            "request_id": request_id,
            "prompt_length": len(prompt),
            "temperature": temperature,
            "max_tokens": max_tokens,
            "operation": "generate_text"
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            generated_text = response.choices[0].message.content.strip()
            
            logger.debug(f"✅ TEXT GENERATION: Completed successfully [ID: {request_id}]", extra={
                "request_id": request_id,
                "response_length": len(generated_text),
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "operation": "generate_text",
                "status": "success"
            })
            
            return generated_text
            
        except Exception as e:
            logger.error(f"💥 TEXT GENERATION ERROR [ID: {request_id}]", extra={
                "request_id": request_id,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "operation": "generate_text",
                "status": "error"
            })
            raise Exception(f"Text generation failed: {str(e)}")

    def _ensure_english_output(self, text: str, request_id: int) -> str:
        """
        Post-processing method to ensure output is in English.
        Validates and cleans up any remaining non-English content.
        
        Args:
            text: The text to validate and clean
            request_id: Request ID for logging
            
        Returns:
            Cleaned English-only text
        """
        logger.debug(f"🔍 POST-PROCESS: English validation starting [ID: {request_id}]")
        
        # Smart non-English detection - exclude technical photography terms and brand names
        problematic_patterns = [
            # Indonesian multi-word patterns only
            (r'\byang adalah\b', 'which is'), (r'\bdan juga\b', 'and also'), 
            (r'\bdengan sangat\b', 'with great'), (r'\buntuk menciptakan\b', 'to create'),
            (r'\bdari hasil\b', 'from the results'), (r'\bini akan\b', 'this will'),
            # Spanish multi-word patterns only
            (r'\bel producto\b', 'the product'), (r'\bla imagen\b', 'the image'), 
            (r'\bcon el\b', 'with the'), (r'\bpor favor\b', 'please'),
            (r'\bdel producto\b', 'of the product'), (r'\bque es\b', 'which is'),
            # French multi-word patterns only
            (r'\ble produit\b', 'the product'), (r'\bdu produit\b', 'of the product'), 
            (r'\bavec le\b', 'with the'), (r'\bpour le\b', 'for the'),
            (r'\bdans le\b', 'in the'), (r'\bpar le\b', 'by the'),
            # German multi-word patterns only
            (r'\bder Produkts\b', 'of the product'), (r'\bdie Beleuchtung\b', 'the lighting'),
            (r'\bmit dem\b', 'with the'), (r'\bfür das\b', 'for the')
        ]
        
        # Replace problematic patterns with English equivalents
        cleaned_text = text
        replacements_made = 0
        
        for pattern, replacement in problematic_patterns:
            import re
            matches = re.findall(pattern, cleaned_text, re.IGNORECASE)
            if matches:
                cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.IGNORECASE)
                replacements_made += len(matches)
                
        if replacements_made > 0:
            logger.warning(f"🔧 POST-PROCESS: Made {replacements_made} language corrections [ID: {request_id}]")
        else:
            logger.debug(f"✅ POST-PROCESS: No language corrections needed [ID: {request_id}]")
            
        return cleaned_text

    async def analyze_image(self, image_url: str) -> Dict[str, Any]:
        """
        Analyze uploaded image using OpenAI Vision API.
        Extract product type, style, lighting, composition details.
        
        Args:
            image_url: URL to the uploaded image
            
        Returns:
            Dictionary with structured image analysis data
        """
        request_id = hash(image_url) % 10000
        
        logger.info(f"👁️ Starting image analysis [ID: {request_id}]", extra={
            "request_id": request_id,
            "image_url": image_url,
            "ai_model": self.model,
            "operation": "analyze_image"
        })
        
        try:
            analysis_instruction = """
Analyze this product image and extract detailed photography information.

**REQUIRED OUTPUT FORMAT (JSON only):**
```json
{
    "product_type": "category (e.g., food, electronics, cosmetics, accessories)",
    "product_name": "specific product name or description",
    "lighting_style": "current lighting type (natural, studio, dramatic, soft, etc.)",
    "background_type": "background description (white, wooden, marble, outdoor, etc.)",
    "composition_style": "shot angle (close-up, wide, overhead, side-angle, etc.)", 
    "style_preference": "overall mood/style (modern, vintage, luxury, casual, etc.)",
    "current_quality": "assessment (amateur, professional, commercial, etc.)",
    "improvement_areas": ["list", "of", "areas", "needing", "enhancement"],
    "dominant_colors": ["primary", "colors", "in", "image"],
    "camera_angle": "specific angle description"
}
```

Focus on extracting actionable photography details that can inform brief generation.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_instruction},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                temperature=0.6,  # Standardized temperature
                max_tokens=800
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group(1))
            else:
                # Fallback: try to parse entire response as JSON
                analysis_data = json.loads(analysis_text)
            
            logger.info(f"✅ Image analysis completed [ID: {request_id}]", extra={
                "request_id": request_id,
                "product_type": analysis_data.get("product_type", "unknown"),
                "analysis_fields": list(analysis_data.keys()),
                "operation": "analyze_image",
                "status": "success"
            })
            
            return analysis_data
            
        except json.JSONDecodeError as e:
            logger.error(f"💥 JSON parsing error in image analysis [ID: {request_id}]", extra={
                "request_id": request_id,
                "error": str(e),
                "raw_response": analysis_text[:200] + "..." if 'analysis_text' in locals() else "No response",
                "operation": "analyze_image"
            })
            
            # Return fallback structure
            return {
                "product_type": "unknown",
                "product_name": "Product",
                "lighting_style": "natural",
                "background_type": "neutral",
                "composition_style": "standard",
                "style_preference": "modern",
                "current_quality": "amateur",
                "improvement_areas": ["lighting", "composition"],
                "dominant_colors": ["neutral"],
                "camera_angle": "front"
            }
            
        except Exception as e:
            logger.error(f"💥 Critical error in image analysis [ID: {request_id}]", extra={
                "request_id": request_id,
                "error": str(e),
                "operation": "analyze_image",
                "status": "error"
            })
            raise Exception(f"Image analysis failed: {str(e)}")
