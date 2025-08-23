"""
Image Generator Service for interacting with a text-to-image API.
Handles the logic for image creation and iterative enhancement.
"""
import requests
from typing import Optional
from loguru import logger
from app.config.settings import settings
from app.schemas.models import ImageOutput

class ImageGenerationService:
    """
    Client for interacting with a Text-to-Image generation API.
    """
    def __init__(self):
        self.api_key = settings.IMAGE_API_KEY
        self.api_base_url = settings.IMAGE_API_BASE_URL
        self.model = settings.IMAGE_GENERATION_MODEL

    async def generate_image(self, brief_prompt: str, negative_prompt: Optional[str] = None) -> ImageOutput:
        """
        Generates an image by calling the external text-to-image API.
        """
        endpoint = f"{self.api_base_url}/text-to-image"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "prompt": brief_prompt,
            "negative_prompt": negative_prompt,
            "steps": 50,
            "cfg_scale": 7,
            "width": 1024,
            "height": 1024,
            "samples": 1
        }

        logger.info(f"🎨 Sending request to Image Generation API for product: '{brief_prompt[:50]}...'")

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
                revised_prompt=brief_prompt
            )

        except Exception as e:
            logger.error(f"💥 Critical error in image generation: {e}")
            raise Exception(f"Image generation service failed: {str(e)}")

    async def enhance_image(self, original_prompt: str, instruction: str, seed: int) -> ImageOutput:
        """
        Enhances an existing image by modifying the prompt and reusing the seed.
        """
        # Smartly merge the original brief with the new instruction
        enhanced_prompt = f"{original_prompt}\n\n---\n**CRITICAL ENHANCEMENT:** {instruction}"
        
        logger.info(f"✨ Enhancing image with instruction: '{instruction}'")

        # Reuse the logic from generate_image, but with the modified prompt and original seed
        # This is a simplified example. A real implementation might use image-to-image.
        return await self.generate_image(brief_prompt=enhanced_prompt) # Add seed to payload if API supports it
