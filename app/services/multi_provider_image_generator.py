"""
Enhanced Image Generator Service with multi-provider support.
Supports OpenRouter, Sumopod, Stability AI, OpenAI DALL-E, and other providers.
"""
import requests
from typing import Optional, Dict, Any
from enum import Enum
from loguru import logger
from app.config.settings import settings
from app.schemas.models import ImageOutput

class ImageProvider(Enum):
    """Supported image generation providers."""
    STABILITY_AI = "stability_ai"
    OPENAI_DALLE = "openai_dalle"
    OPENROUTER = "openrouter"
    SUMOPOD = "sumopod"
    MIDJOURNEY = "midjourney"
    GENERIC = "generic"

class MultiProviderImageService:
    """
    Multi-provider image generation service that adapts to different API formats.
    """
    
    def __init__(self):
        self.api_base_url = settings.IMAGE_API_BASE_URL
        self.default_model = settings.IMAGE_GENERATION_MODEL
    
    def detect_provider(self, api_base_url: str) -> ImageProvider:
        """Auto-detect the provider based on the API URL."""
        url_lower = api_base_url.lower()
        
        if "stability" in url_lower or "stabilityai" in url_lower:
            return ImageProvider.STABILITY_AI
        elif "openai" in url_lower or "api.openai.com" in url_lower:
            return ImageProvider.OPENAI_DALLE
        elif "openrouter" in url_lower:
            return ImageProvider.OPENROUTER
        elif "sumopod" in url_lower:
            return ImageProvider.SUMOPOD
        elif "midjourney" in url_lower:
            return ImageProvider.MIDJOURNEY
        else:
            return ImageProvider.GENERIC
    
    def build_request_payload(self, provider: ImageProvider, brief_prompt: str, 
                            negative_prompt: Optional[str] = None, 
                            model: Optional[str] = None) -> Dict[str, Any]:
        """Build request payload based on provider specifications."""
        
        model = model or self.default_model
        
        if provider == ImageProvider.STABILITY_AI:
            return {
                "model": model,
                "prompt": brief_prompt,
                "negative_prompt": negative_prompt,
                "steps": 50,
                "cfg_scale": 7,
                "width": 1024,
                "height": 1024,
                "samples": 1
            }
        
        elif provider == ImageProvider.OPENAI_DALLE:
            return {
                "model": model or "dall-e-3",
                "prompt": brief_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "hd",
                "response_format": "url"
            }
        
        elif provider == ImageProvider.OPENROUTER:
            return {
                "model": model or "stability-ai/stable-diffusion-xl",
                "prompt": brief_prompt,
                "negative_prompt": negative_prompt,
                "steps": 50,
                "cfg_scale": 7,
                "width": 1024,
                "height": 1024,
                "sampler": "DPM++ 2M Karras"
            }
        
        elif provider == ImageProvider.SUMOPOD:
            return {
                "model": model,
                "inputs": brief_prompt,
                "negative_prompt": negative_prompt,
                "guidance_scale": 7,
                "num_inference_steps": 50,
                "width": 1024,
                "height": 1024
            }
        
        elif provider == ImageProvider.MIDJOURNEY:
            return {
                "prompt": brief_prompt,
                "model": model or "midjourney",
                "aspect_ratio": "1:1",
                "quality": "high"
            }
        
        else:  # GENERIC
            # Generic format that works with many providers
            return {
                "prompt": brief_prompt,
                "negative_prompt": negative_prompt,
                "model": model,
                "width": 1024,
                "height": 1024
            }
    
    def get_endpoint_path(self, provider: ImageProvider) -> str:
        """Get the correct endpoint path for each provider."""
        
        endpoints = {
            ImageProvider.STABILITY_AI: "/text-to-image",
            ImageProvider.OPENAI_DALLE: "/images/generations",
            ImageProvider.OPENROUTER: "/api/v1/generate",
            ImageProvider.SUMOPOD: "/v1/generate",
            ImageProvider.MIDJOURNEY: "/generate",
            ImageProvider.GENERIC: "/generate"
        }
        
        return endpoints.get(provider, "/generate")
    
    def parse_response(self, provider: ImageProvider, response_data: Dict[str, Any]) -> ImageOutput:
        """Parse API response based on provider format."""
        
        try:
            if provider == ImageProvider.STABILITY_AI:
                image_data = response_data["artifacts"][0]
                return ImageOutput(
                    image_url=f"data:image/png;base64,{image_data['base64']}",
                    generation_id=f"gen_{image_data.get('seed', 'unknown')}",
                    seed=image_data.get('seed', 0),
                    revised_prompt=response_data.get('prompt', '')
                )
            
            elif provider == ImageProvider.OPENAI_DALLE:
                image_data = response_data["data"][0]
                return ImageOutput(
                    image_url=image_data["url"],
                    generation_id=f"dalle_{image_data.get('id', 'unknown')}",
                    seed=0,  # DALL-E doesn't use seeds
                    revised_prompt=image_data.get("revised_prompt", response_data.get("prompt", ""))
                )
            
            elif provider == ImageProvider.OPENROUTER:
                image_data = response_data["data"][0]
                return ImageOutput(
                    image_url=image_data.get("url") or f"data:image/png;base64,{image_data.get('base64')}",
                    generation_id=f"or_{response_data.get('id', 'unknown')}",
                    seed=image_data.get('seed', 0),
                    revised_prompt=response_data.get('prompt', '')
                )
            
            elif provider == ImageProvider.SUMOPOD:
                # Sumopod typically returns base64 or URL
                image_data = response_data.get("images", [response_data])[0]
                return ImageOutput(
                    image_url=image_data.get("url") or f"data:image/png;base64,{image_data.get('image')}",
                    generation_id=f"sumopod_{response_data.get('job_id', 'unknown')}",
                    seed=response_data.get('seed', 0),
                    revised_prompt=response_data.get('prompt', '')
                )
            
            elif provider == ImageProvider.MIDJOURNEY:
                return ImageOutput(
                    image_url=response_data.get("image_url", ""),
                    generation_id=f"mj_{response_data.get('job_id', 'unknown')}",
                    seed=0,  # Midjourney doesn't typically expose seeds
                    revised_prompt=response_data.get('prompt', '')
                )
            
            else:  # GENERIC
                # Try to handle generic response formats
                image_url = (response_data.get("image_url") or 
                           response_data.get("url") or 
                           response_data.get("data", {}).get("url") or
                           f"data:image/png;base64,{response_data.get('image', '')}")
                
                return ImageOutput(
                    image_url=image_url,
                    generation_id=f"gen_{response_data.get('id', 'unknown')}",
                    seed=response_data.get('seed', 0),
                    revised_prompt=response_data.get('prompt', '')
                )
        
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to parse {provider.value} response: {e}")
            logger.error(f"Response data: {response_data}")
            raise Exception(f"Unable to parse response from {provider.value}: {str(e)}")
    
    async def generate_image(self, brief_prompt: str, user_api_key: str, 
                           negative_prompt: Optional[str] = None,
                           provider_override: Optional[str] = None) -> ImageOutput:
        """
        Generate image using the appropriate provider format.
        
        Args:
            brief_prompt: The enhanced photography brief
            user_api_key: User's API key for the service
            negative_prompt: Optional negative prompt
            provider_override: Optional provider name to override auto-detection
        """
        
        # Detect or override provider
        if provider_override:
            try:
                provider = ImageProvider(provider_override.lower())
            except ValueError:
                provider = ImageProvider.GENERIC
        else:
            provider = self.detect_provider(self.api_base_url)
        
        # Build request
        endpoint = f"{self.api_base_url.rstrip('/')}{self.get_endpoint_path(provider)}"
        payload = self.build_request_payload(provider, brief_prompt, negative_prompt)
        
        # Set up headers (most providers use Bearer token)
        headers = {
            "Authorization": f"Bearer {user_api_key}",
            "Content-Type": "application/json"
        }
        
        # Some providers need special headers
        if provider == ImageProvider.OPENROUTER:
            headers["HTTP-Referer"] = "https://photoeai.app"  # Replace with your domain
            headers["X-Title"] = "PhotoeAI"
        
        logger.info(f"🎨 Sending request to {provider.value} for: '{brief_prompt[:50]}...'")
        logger.info(f"🔗 Endpoint: {endpoint}")
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            api_response = response.json()
            logger.info(f"✅ Received response from {provider.value}")
            
            return self.parse_response(provider, api_response)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"💥 API request failed for {provider.value}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response: {e.response.text}")
            raise Exception(f"Image generation request failed: {str(e)}")
        
        except Exception as e:
            logger.error(f"💥 Unexpected error with {provider.value}: {e}")
            raise Exception(f"Image generation service error: {str(e)}")
    
    async def enhance_image(self, original_prompt: str, instruction: str, 
                          user_api_key: str, seed: int) -> ImageOutput:
        """Enhanced image generation with modified prompt."""
        enhanced_prompt = f"{original_prompt}\n\n---\n**ENHANCEMENT:** {instruction}"
        logger.info(f"✨ Enhancing with: '{instruction}'")
        
        return await self.generate_image(
            brief_prompt=enhanced_prompt,
            user_api_key=user_api_key
        )
