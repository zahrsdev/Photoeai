"""
Image Generator Service for interacting with a text-to-image API.
Handles the logic for image creation and iterative enhancement.
"""
import requests
from typing import Optional
from loguru import logger
from app.config.settings import settings
from app.schemas.models import ImageOutput
from app.services.ai_client import AIClient

class ImageGenerationService:
    """
    Client for interacting with a Text-to-Image generation API.
    """
    def __init__(self):
        # Keep default configuration but allow user API keys to override
        self.default_api_key = getattr(settings, 'IMAGE_API_KEY', None)
        self.api_base_url = settings.IMAGE_API_BASE_URL
        self.model = settings.IMAGE_GENERATION_MODEL
        self.ai_client = AIClient()  # For intelligent prompt enhancement

    async def generate_image(self, brief_prompt: str, user_api_key: str, negative_prompt: Optional[str] = None) -> ImageOutput:
        """
        Generates an image by calling the external text-to-image API.
        Automatically creates a complete enhanced photography brief from the input prompt using AI.
        Uses the user-provided API key for authentication.
        """
        logger.info(f"🎨 Starting image generation with complete prompt enhancement for: '{brief_prompt[:50]}...'")
        
        # STEP 1: AI-powered complete prompt enhancement (creates full detailed brief)
        try:
            enhanced_brief = await self.ai_client.revise_prompt_for_generation(brief_prompt)
            logger.info(f"✨ Complete enhanced brief created by AI: '{enhanced_brief[:100]}...'")
        except Exception as e:
            logger.warning(f"⚠️ AI enhanced brief creation failed, using original: {e}")
            enhanced_brief = brief_prompt
        
        endpoint = f"{self.api_base_url}/text-to-image"
        
        # Use user-provided API key
        headers = {
            "Authorization": f"Bearer {user_api_key}",
            "Content-Type": "application/json"
        }
        
        # Use the AI-enhanced complete brief for generation
        payload = {
            "model": self.model,
            "prompt": enhanced_brief,  # Use AI-enhanced complete brief
            "negative_prompt": negative_prompt,
            "steps": 50,
            "cfg_scale": 7,
            "width": 1024,
            "height": 1024,
            "samples": 1
        }

        logger.info(f"🎨 Sending request to Image Generation API with enhanced brief")

        try:
            # THIS IS A REPRESENTATION. The actual API call will depend on your chosen provider.
            # Replace with the appropriate SDK or requests call.
            response = requests.post(endpoint, headers=headers, json=payload)
            response.raise_for_status() # Fail fast if the API returns an error
            
            api_response = response.json()

            # --- IMPORTANT ---
            # Adapt the following lines to match the actual structure
            # of the response from your image generation API provider.
            image_data = api_response["artifacts"][0]
            
            return ImageOutput(
                image_url=f"data:image/png;base64,{image_data['base64']}", # Example for base64 response
                generation_id=f"gen_{image_data['seed']}", # Create a unique ID
                seed=image_data['seed'],
                revised_prompt=enhanced_brief,  # Now contains AI-enhanced complete brief
                final_enhanced_prompt=enhanced_brief  # Same as enhanced brief for basic generation
            )

        except Exception as e:
            logger.error(f"💥 Critical error in image generation: {e}")
            raise Exception(f"Image generation service failed: {str(e)}")

    async def enhance_image(self, original_prompt: str, instruction: str, user_api_key: str, seed: int) -> ImageOutput:
        """
        Enhances an existing image by intelligently enhancing the prompt itself using AI.
        This creates a superior, more detailed prompt rather than just appending instructions.
        Uses the user-provided API key for authentication.
        """
        logger.info(f"🧠 Using AI-powered intelligent prompt enhancement: '{instruction}'")

        # Use AI-powered intelligent enhancement instead of rule-based
        try:
            enhanced_prompt = await self.ai_client.enhance_prompt_intelligently(original_prompt, instruction)
            logger.info(f"✨ AI-enhanced prompt created: '{enhanced_prompt[:100]}...'")
        except Exception as e:
            logger.warning(f"⚠️ AI enhancement failed, using fallback: {e}")
            # Fallback to rule-based enhancement
            enhanced_prompt = await self._create_enhanced_prompt(original_prompt, instruction)
            logger.info(f"🎨 Fallback enhanced prompt created: '{enhanced_prompt[:100]}...'")

        # Generate image with the enhanced prompt, preserving seed if possible
        return await self.generate_image(brief_prompt=enhanced_prompt, user_api_key=user_api_key)
    
    async def _create_enhanced_prompt(self, original_prompt: str, enhancement_instruction: str) -> str:
        """
        Create an intelligently enhanced prompt by analyzing and improving the original prompt.
        
        Args:
            original_prompt: The original photography prompt
            enhancement_instruction: User's enhancement instruction
            
        Returns:
            A significantly improved and detailed prompt
        """
        # Define enhancement rules based on common photography improvements
        enhancement_patterns = {
            "lighting": [
                "soft lighting", "dramatic lighting", "cinematic lighting", "natural lighting",
                "studio lighting", "golden hour", "rim lighting", "key lighting"
            ],
            "composition": [
                "rule of thirds", "leading lines", "symmetry", "depth of field",
                "bokeh", "shallow focus", "wide angle", "macro", "close-up"
            ],
            "style": [
                "professional", "commercial", "editorial", "lifestyle", "artistic",
                "minimalist", "vintage", "modern", "elegant", "premium"
            ],
            "technical": [
                "high resolution", "sharp focus", "crisp details", "color grading",
                "post-processing", "HDR", "contrast", "saturation", "exposure"
            ],
            "atmosphere": [
                "mood", "ambiance", "atmosphere", "emotion", "feeling",
                "warm", "cool", "bright", "dark", "cozy", "energetic"
            ]
        }
        
        # Analyze the enhancement instruction to determine enhancement type
        instruction_lower = enhancement_instruction.lower()
        enhancement_type = "general"
        
        for category, keywords in enhancement_patterns.items():
            if any(keyword in instruction_lower for keyword in keywords):
                enhancement_type = category
                break
        
        # Create contextual enhancement based on instruction type
        if enhancement_type == "lighting":
            enhancement_prefix = "Create stunning professional lighting with "
            enhancement_details = ", featuring carefully controlled shadows and highlights, dramatic depth, and cinematic quality illumination"
        elif enhancement_type == "composition":
            enhancement_prefix = "Compose with expert-level framing using "
            enhancement_details = ", incorporating professional compositional techniques, perfect balance, and visual hierarchy"
        elif enhancement_type == "style":
            enhancement_prefix = "Elevate to premium commercial style with "
            enhancement_details = ", showcasing sophisticated aesthetic choices, refined color palette, and luxury presentation"
        elif enhancement_type == "technical":
            enhancement_prefix = "Achieve technical excellence with "
            enhancement_details = ", ensuring perfect sharpness, optimal exposure, and professional-grade image quality"
        elif enhancement_type == "atmosphere":
            enhancement_prefix = "Create compelling atmosphere with "
            enhancement_details = ", evoking strong emotional response and captivating visual storytelling"
        else:
            enhancement_prefix = "Enhance with professional refinement: "
            enhancement_details = ", elevating overall quality and visual impact"
        
        # Intelligently merge the original prompt with enhancement
        if "." in original_prompt:
            # If original prompt has sentences, insert enhancement thoughtfully
            sentences = original_prompt.split(".")
            enhanced_sentences = []
            
            for i, sentence in enumerate(sentences):
                enhanced_sentences.append(sentence.strip())
                if i == 0 and sentence.strip():  # After first sentence, add enhancement
                    enhanced_sentences.append(f" {enhancement_prefix}{enhancement_instruction}{enhancement_details}")
            
            enhanced_prompt = ". ".join([s for s in enhanced_sentences if s.strip()]).strip()
        else:
            # Simple enhancement for shorter prompts
            enhanced_prompt = f"{original_prompt.strip()}. {enhancement_prefix}{enhancement_instruction}{enhancement_details}"
        
        # Add professional photography enhancements
        professional_additions = [
            "Professional product photography",
            "Studio quality lighting setup",
            "High-end commercial aesthetic",
            "Sharp focus and perfect clarity",
            "Premium visual presentation",
            "Expert color grading and post-processing"
        ]
        
        # Selectively add professional terms that aren't already in the prompt
        for addition in professional_additions:
            if not any(word.lower() in enhanced_prompt.lower() for word in addition.split()):
                enhanced_prompt += f", {addition.lower()}"
        
        return enhanced_prompt
