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
    Handles both extraction (LLM as Analyst) and enhancement (LLM as Creative Director) operations.
    """
    
    def __init__(self):
        """Initialize the OpenAI client with API key and custom base URL from settings."""
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.sumopod_api_base_url
        )
        self.model = settings.openai_model
    
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
        
        Extract information for ALL fields below (ALL VALUES MUST BE STRINGS, NOT ARRAYS):
        
        product_name: Name of the product (REQUIRED - string, never null)
        product_description: Description of the product (string)
        key_features: Key features to highlight (string, comma-separated if multiple)
        product_state: State of the product (string, default: "pristine")
        shot_type: Type of shot (REQUIRED - string, choose most appropriate)
        framing: Framing style (REQUIRED - string, choose most appropriate) 
        compositional_rule: Compositional rule (string, default: "Rule of Thirds")
        negative_space: Negative space approach (string, default: "Balanced")
        lighting_style: Lighting style (REQUIRED - string, choose most appropriate)
        key_light_setup: Key light setup description (string)
        fill_light_setup: Fill light setup description (string)
        rim_light_setup: Rim light setup description (string)
        mood: Overall mood (string, default: "Clean and professional")
        environment: Environment/background (REQUIRED - string, choose most appropriate)
        dominant_colors: Dominant color palette (string, comma-separated if multiple)
        accent_colors: Accent colors (string, comma-separated if multiple)
        props: Supporting props description (string)
        camera_type: Camera type (string, default: "Canon EOS R5")
        lens_type: Lens type (string, default: "50mm f/1.8")
        aperture_value: Aperture f-number (number, default: 2.8)
        shutter_speed_value: Shutter speed denominator (number, default: 125)
        iso_value: ISO value (number, default: 100)
        visual_effect: Visual effect description (string)
        overall_style: Overall photographic style (string, default: "Professional product photography")
        photographer_influences: Photographer influences (string, comma-separated if multiple)
        
        IMPORTANT: 
        - Respond ONLY with valid JSON
        - ALL text fields must be STRINGS, not arrays
        - Use comma-separated strings for multiple values (e.g. "red, blue, gold" not ["red", "blue", "gold"])
        - NEVER use null for required fields (product_name, shot_type, framing, lighting_style, environment)
        - Use reasonable professional photography defaults when information is unclear
        - Make intelligent inferences based on the request context
        """
        
        logger.debug(f"📝 Sending extraction request to AI [ID: {request_id}]", extra={
            "request_id": request_id,
            "prompt_length": len(prompt),
            "temperature": 0.3
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert photography analyst. Extract structured data from user requests and respond only with valid JSON. When requests are vague, make professional inferences and use industry-standard defaults. NEVER leave required fields as null."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
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
        Enhance a photography brief using LLM as Creative Director.
        
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
                "temperature": 0.7,
                "max_tokens": 2000
            })
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            enhanced_brief = response.choices[0].message.content.strip()
            
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

    async def enhance_brief_from_structured_data(self, structured_data: dict) -> str:
        """
        CRITICAL REFACTOR: Generate comprehensive photography brief from structured data.
        
        This method implements the fully refactored Creative Director that generates complete,
        multi-section, detailed photography briefs from JSON input data with ADVANCED ENHANCEMENT.
        
        Args:
            structured_data: Complete WizardInput data in dictionary format
            
        Returns:
            Complete, multi-section photography brief document with professional enhancement
        """
        request_id = hash(str(structured_data)) % 10000  # Simple request tracking
        
        logger.info(f"🎭 ADVANCED: Creative Director enhanced composition [ID: {request_id}]", extra={
            "request_id": request_id,
            "product_name": structured_data.get("product_name", "Unknown"),
            "ai_model": self.model,
            "operation": "enhance_brief_from_structured_data",
            "refactor_status": "ADVANCED_ENHANCEMENT_ACTIVE"
        })
        
        try:
            # ADVANCED ENHANCEMENT INSTRUCTION WITH DEEPER CREATIVE INTELLIGENCE
            enhancement_instruction = f"""
You are an ELITE Creative Director with 20+ years of world-class product photography experience. You've worked with luxury brands, directed award-winning campaigns, and your images are featured in top-tier publications. Your mission: Transform the structured JSON data into a MASTERPIECE photography brief that would be worthy of a $100,000 commercial shoot.

**ELITE ENHANCEMENT MANDATES:**

1. **VISIONARY DOCUMENT CREATION**: Generate a comprehensive, structured Markdown document that reads like a professional creative brief from the world's top agencies. This is premium commercial photography direction.

2. **SACRED DATA FOUNDATION**: The JSON below contains the client's core vision. Treat every detail as sacred input that must be elevated to professional excellence. Build upon, never replace.

3. **EXPERT CREATIVE AMPLIFICATION**: For any basic or missing elements, apply world-class expertise:
   - Transform simple descriptions into vivid, cinematic language
   - Specify professional-grade equipment with technical justification
   - Create sophisticated lighting scenarios with precise positioning
   - Design compelling color stories with psychological impact
   - Develop sophisticated post-processing workflows

4. **LUXURY NARRATIVE STYLE**: Write with the sophistication of luxury brand guidelines. Every sentence should convey expertise, precision, and creative vision.

5. **ADVANCED SECTION ARCHITECTURE** (Each section must be rich and detailed):

   ## **1. Creative Vision & Main Subject**
   ↳ Comprehensive product narrative, hero feature storytelling, aspirational positioning strategy, brand elevation approach

   ## **2. Advanced Composition & Framing Strategy**  
   ↳ Sophisticated compositional techniques, psychological framing impact, visual hierarchy design, negative space mastery

   ## **3. Professional Lighting Design & Atmosphere Creation**
   ↳ Complete lighting ecosystem: key, fill, rim, background lighting with specific equipment models, power ratios, modifier specifications, atmospheric mood crafting

   ## **4. Environmental Design & Setting Architecture**
   ↳ Location/studio environment with creative rationale, sophisticated color psychology, curated prop ecosystem, spatial relationship orchestration

   ## **5. Technical Excellence & Camera Systems**
   ↳ Professional camera selection with creative justification, premium lens choice with optical characteristics, exposure triangle mastery, technical precision

   ## **6. Visual Effects & Artistic Enhancement**
   ↳ Creative enhancement strategies, artistic influences integration, visual effects applications, style differentiation techniques

   ## **7. Post-Production Mastery**
   ↳ Advanced color science, professional retouching workflow, brand-consistent finishing, final polish techniques

**PROFESSIONAL EXCELLENCE EXAMPLE:**
Transform "good lighting" into: "Establish primary illumination through a Profoto D2 1000W strobe firing through a 180cm Para Softbox positioned at 45 degrees camera left, creating beautifully graduated light that sculpts the product's form while maintaining crisp edge definition. Complement with a Profoto B10X LED panel at 30% power as fill light, positioned camera right and elevated 20 degrees to lift shadows strategically without compromising the dramatic 3:1 lighting ratio. Add dimensional separation using a Profoto B1X with 20-degree grid as rim light, creating a subtle glow around the product's silhouette."

**ENHANCEMENT PSYCHOLOGY**: Think like you're briefing Annie Leibovitz, Peter Lindbergh, or Mario Testino. Every detail should justify a premium budget.

**CLIENT FOUNDATION DATA:**
```json
{json.dumps(structured_data, indent=2)}
```

**EXECUTE MASTERY**: Create a brief so compelling that it would win creative awards. Make every word count, every technical detail purposeful, every creative choice defensible. This is your masterpiece.
"""

            logger.debug(f"📝 ADVANCED: Dispatching Elite Enhancement [ID: {request_id}]", extra={
                "request_id": request_id,
                "instruction_length": len(enhancement_instruction),
                "structured_data_fields": list(structured_data.keys()),
                "product_name": structured_data.get("product_name", "Unknown"),
                "temperature": 0.85,  # Optimized for creative excellence
                "max_tokens": 4500,   # Expanded for masterpiece output
                "enhancement_level": "ELITE_PROFESSIONAL"
            })

            # OPTIMIZED PARAMETERS FOR CREATIVE EXCELLENCE
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a world-renowned Creative Director with elite-level expertise in luxury product photography. Your briefs are legendary in the industry for their precision, creativity, and commercial success. Every response must be a comprehensive masterpiece document."
                    },
                    {"role": "user", "content": enhancement_instruction}
                ],
                temperature=0.85,     # Optimized for creative but controlled enhancement
                max_tokens=4500       # Increased for comprehensive masterpiece output
            )
            
            enhanced_brief = response.choices[0].message.content.strip()
            
            # ADVANCED QUALITY VALIDATION
            word_count = len(enhanced_brief.split())
            section_count = enhanced_brief.count('##')
            technical_terms = sum(1 for term in ['profoto', 'canon', 'sony', 'nikon', 'lighting', 'exposure', 'composition', 'color grading'] 
                                if term.lower() in enhanced_brief.lower())
            
            logger.info(f"✅ ADVANCED: Elite enhancement completed [ID: {request_id}]", extra={
                "request_id": request_id,
                "structured_data_size": len(str(structured_data)),
                "enhanced_length": len(enhanced_brief),
                "word_count": word_count,
                "section_count": section_count,
                "technical_depth": technical_terms,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "operation": "enhance_brief_from_structured_data",
                "status": "ELITE_ENHANCEMENT_SUCCESS",
                "quality_level": "MASTERPIECE" if word_count > 300 and section_count >= 6 and technical_terms >= 3 else "PROFESSIONAL"
            })
            
            # QUALITY ASSURANCE: Ensure elite-level output
            if word_count < 250 or section_count < 5:
                logger.warning(f"⚠️ QUALITY ALERT: Enhancement below elite standards [ID: {request_id}]", extra={
                    "request_id": request_id,
                    "word_count": word_count,
                    "section_count": section_count,
                    "expected_word_count": ">300",
                    "expected_sections": ">=7",
                    "recommendation": "Consider re-enhancement with stronger creative direction"
                })
            
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
            raise Exception(f"ELITE ENHANCEMENT FAILURE - Creative Director system unavailable: {str(e)}")

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
Original: "A bottle of perfume on a white background with soft lighting"
Enhancement Request: "Make it more luxurious"
Result: "An exquisite luxury perfume bottle elegantly positioned against a pristine seamless backdrop, illuminated by sophisticated softbox lighting that creates gentle gradient shadows and highlights the bottle's premium crystal facets. The composition exudes refined elegance with carefully controlled depth of field and a color palette that speaks to exclusivity and sophistication."

**EXECUTE ENHANCEMENT:** Create the intelligently enhanced prompt now.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert prompt engineer specializing in photography and AI image generation. Your enhancements are known for their sophistication and professional quality."
                    },
                    {"role": "user", "content": enhancement_instruction}
                ],
                temperature=0.75,  # Balanced for creativity and consistency
                max_tokens=1500    # Sufficient for detailed enhancement
            )
            
            enhanced_prompt = response.choices[0].message.content.strip()
            
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

    async def revise_prompt_for_generation(self, original_prompt: str) -> str:
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
            # This is the new, powerful instruction template.
            enhancement_instruction_template = """
You are an elite-level AI Creative Director and a world-renowned product photographer. Your task is to take the following foundational prompt, which was extracted from a simple user request, and expand it into a complete, narrative, and highly detailed Product Photography Brief in Markdown format.

**CRITICAL INSTRUCTIONS:**
1.  **Full Creative Expansion**: Your primary task is to be creative. For every detail that is missing, incomplete, or too simple in the original prompt, you MUST use your expert knowledge of photography and art direction to dynamically infer, invent, and add the best possible professional choices. You must fill out every section of a professional brief.
2.  **Mandatory Inferred Details**: Your final brief MUST include specific, professional choices for:
    -   **Camera & Lens**: (e.g., "Shot on: Canon EOS R5", "Lens: 100mm Macro f/2.8"). Do not be generic.
    -   **Precise Lighting Setup**: (e.g., "Key Light: A single, large softbox at a 45-degree angle...").
    -   **Detailed Composition & Framing**: (e.g., "Compositional Rule: Rule of Thirds, with the product placed slightly off-center...").
    -   **Creative Background & Props**.
    -   **Professional Post-Processing & Color Grading notes**.
3.  **Justify Your Choices**: You MUST include a "Creative Rationale" section at the end, explaining why you made the creative and technical choices you did.
4.  **No Mock Data**: Do NOT use any external examples. Your entire response must be a unique, creative expansion based ONLY on the foundational prompt provided below and your own expertise.

**Foundational Prompt:**
{original_prompt}

Now, generate the full, enhanced, and complete photography brief.
"""
            # Dynamically format the final instruction
            enhancement_instruction = enhancement_instruction_template.format(original_prompt=original_prompt)

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an elite Creative Director and world-renowned product photographer. You create comprehensive photography briefs that result in award-winning images. You respond with complete, detailed briefs structured exactly as requested."
                    },
                    {"role": "user", "content": enhancement_instruction}
                ],
                temperature=0.7,  # Balanced for creativity while maintaining structure
                max_tokens=3000   # Sufficient for complete detailed brief
            )
            
            revised_prompt = response.choices[0].message.content.strip()
            
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
    
    async def generate_text(self, prompt: str, temperature: float = 0.5, max_tokens: int = 2000) -> str:
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
