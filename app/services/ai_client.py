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
