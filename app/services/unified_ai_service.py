"""
Enhanced multi-provider service supporting both text and image generation.
Handles the actual API formats shown by the user for Sumopod, OpenRouter, OpenAI, and Gemini.
"""
import requests
import json
from typing import Optional, Dict, Any, Union
from enum import Enum
from loguru import logger
from app.config.settings import settings
from app.schemas.models import ImageOutput

class ProviderType(Enum):
    """Types of AI services supported."""
    TEXT_COMPLETION = "text_completion"
    IMAGE_GENERATION = "image_generation"
    BOTH = "both"

class AIProvider(Enum):
    """Supported AI providers with their capabilities."""
    SUMOPOD = "sumopod"           # Both text and image
    OPENROUTER = "openrouter"     # Both text and image  
    OPENAI = "openai"             # Both text (GPT) and image (DALL-E)
    GEMINI = "gemini"             # Text completion
    STABILITY_AI = "stability_ai"  # Image generation only
    MIDJOURNEY = "midjourney"     # Image generation only
    GENERIC = "generic"           # Fallback

class UnifiedAIService:
    """
    Unified service that handles both text completion and image generation
    across multiple providers using their actual API formats.
    """
    
    def __init__(self):
        self.api_base_url = settings.IMAGE_API_BASE_URL
        self.default_model = settings.IMAGE_GENERATION_MODEL
        
    def detect_provider(self, api_base_url: str) -> AIProvider:
        """Auto-detect the provider based on the API URL."""
        url_lower = api_base_url.lower()
        
        if "sumopod" in url_lower:
            return AIProvider.SUMOPOD
        elif "openrouter" in url_lower:
            return AIProvider.OPENROUTER
        elif "openai" in url_lower or "api.openai.com" in url_lower:
            return AIProvider.OPENAI
        elif "gemini" in url_lower or "generativeai" in url_lower:
            return AIProvider.GEMINI
        elif "stability" in url_lower or "stabilityai" in url_lower:
            return AIProvider.STABILITY_AI
        elif "midjourney" in url_lower:
            return AIProvider.MIDJOURNEY
        else:
            return AIProvider.GENERIC
    
    # TEXT COMPLETION METHODS (for brief generation)
    
    def build_text_completion_payload(self, provider: AIProvider, prompt: str, 
                                    model: Optional[str] = None,
                                    max_tokens: int = 150,
                                    temperature: float = 0.7) -> Dict[str, Any]:
        """Build text completion payload based on provider specifications."""
        
        if provider == AIProvider.SUMOPOD:
            # Using OpenAI-compatible format for Sumopod
            return {
                "model": model or "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        
        elif provider == AIProvider.OPENROUTER:
            # Using OpenRouter chat completions format
            return {
                "model": model or "openai/gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False  # We'll handle non-streaming for simplicity
            }
        
        elif provider == AIProvider.OPENAI:
            # Using OpenAI chat completions format
            return {
                "model": model or "gpt-4o",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
        
        elif provider == AIProvider.GEMINI:
            # Gemini uses different format
            return {
                "model": model or "gemini-2.5-flash",
                "contents": prompt
            }
        
        else:  # GENERIC
            return {
                "model": model or "gpt-4",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
    
    def get_text_completion_endpoint(self, provider: AIProvider) -> str:
        """Get the correct text completion endpoint for each provider."""
        
        endpoints = {
            AIProvider.SUMOPOD: "/chat/completions",        # OpenAI-compatible
            AIProvider.OPENROUTER: "/api/v1/chat/completions",  # As shown in your example
            AIProvider.OPENAI: "/v1/chat/completions",      # Standard OpenAI
            AIProvider.GEMINI: "/models/generate_content",   # Gemini format
            AIProvider.GENERIC: "/chat/completions"
        }
        
        return endpoints.get(provider, "/chat/completions")
    
    async def generate_text(self, prompt: str, user_api_key: str, 
                          provider_override: Optional[str] = None,
                          model: Optional[str] = None,
                          max_tokens: int = 150,
                          temperature: float = 0.7) -> str:
        """
        Generate text completion using the appropriate provider format.
        This can be used for brief generation and enhancement.
        """
        
        # Detect or override provider
        if provider_override:
            try:
                provider = AIProvider(provider_override.lower())
            except ValueError:
                provider = AIProvider.GENERIC
        else:
            provider = self.detect_provider(self.api_base_url)
        
        # Build request for text completion
        endpoint = f"{self.api_base_url.rstrip('/')}{self.get_text_completion_endpoint(provider)}"
        payload = self.build_text_completion_payload(provider, prompt, model, max_tokens, temperature)
        
        # Set up headers based on provider
        headers = self._get_headers(provider, user_api_key)
        
        logger.info(f"🤖 Sending text completion request to {provider.value}")
        
        try:
            if provider == AIProvider.GEMINI:
                # Gemini might use different client pattern
                # For now, we'll use requests but this could be enhanced
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            else:
                # Most providers use standard REST
                response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
            
            response.raise_for_status()
            api_response = response.json()
            
            return self._parse_text_response(provider, api_response)
            
        except Exception as e:
            logger.error(f"💥 Text completion failed for {provider.value}: {e}")
            raise Exception(f"Text completion service failed: {str(e)}")
    
    # IMAGE GENERATION METHODS (existing functionality enhanced)
    
    def build_image_generation_payload(self, provider: AIProvider, brief_prompt: str, 
                                     negative_prompt: Optional[str] = None,
                                     model: Optional[str] = None) -> Dict[str, Any]:
        """Build image generation payload based on provider specifications."""
        
        if provider == AIProvider.STABILITY_AI:
            return {
                "model": model or "stable-diffusion-xl-1024-v1-0",
                "prompt": brief_prompt,
                "negative_prompt": negative_prompt,
                "steps": 50,
                "cfg_scale": 7,
                "width": 1024,
                "height": 1024,
                "samples": 1
            }
        
        elif provider == AIProvider.OPENAI:
            # DALL-E image generation
            return {
                "model": model or "dall-e-3",
                "prompt": brief_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "hd",
                "response_format": "url"
            }
        
        elif provider == AIProvider.OPENROUTER:
            # OpenRouter image generation (if they support it)
            return {
                "model": model or "stability-ai/stable-diffusion-xl",
                "prompt": brief_prompt,
                "negative_prompt": negative_prompt,
                "steps": 50,
                "cfg_scale": 7,
                "width": 1024,
                "height": 1024
            }
        
        elif provider == AIProvider.SUMOPOD:
            # Sumopod image generation (if they support it)  
            return {
                "model": model or "stable-diffusion-xl",
                "prompt": brief_prompt,
                "negative_prompt": negative_prompt,
                "guidance_scale": 7,
                "num_inference_steps": 50,
                "width": 1024,
                "height": 1024
            }
        
        else:  # GENERIC
            return {
                "prompt": brief_prompt,
                "negative_prompt": negative_prompt,
                "model": model,
                "width": 1024,
                "height": 1024
            }
    
    def get_image_generation_endpoint(self, provider: AIProvider) -> str:
        """Get the correct image generation endpoint for each provider."""
        
        endpoints = {
            AIProvider.STABILITY_AI: "/text-to-image",
            AIProvider.OPENAI: "/v1/images/generations",
            AIProvider.OPENROUTER: "/api/v1/generate",  # May vary
            AIProvider.SUMOPOD: "/v1/images/generate",  # Hypothetical
            AIProvider.MIDJOURNEY: "/generate",
            AIProvider.GENERIC: "/generate"
        }
        
        return endpoints.get(provider, "/generate")
    
    async def generate_image(self, brief_prompt: str, user_api_key: str, 
                           negative_prompt: Optional[str] = None,
                           provider_override: Optional[str] = None,
                           model: Optional[str] = None) -> ImageOutput:
        """Generate image using the appropriate provider format."""
        
        # Detect or override provider
        if provider_override:
            try:
                provider = AIProvider(provider_override.lower())
            except ValueError:
                provider = AIProvider.GENERIC
        else:
            provider = self.detect_provider(self.api_base_url)
        
        # Build request for image generation
        endpoint = f"{self.api_base_url.rstrip('/')}{self.get_image_generation_endpoint(provider)}"
        payload = self.build_image_generation_payload(provider, brief_prompt, negative_prompt, model)
        
        # Set up headers
        headers = self._get_headers(provider, user_api_key)
        
        logger.info(f"🎨 Sending image generation request to {provider.value}")
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            api_response = response.json()
            return self._parse_image_response(provider, api_response, brief_prompt)
            
        except Exception as e:
            logger.error(f"💥 Image generation failed for {provider.value}: {e}")
            raise Exception(f"Image generation service failed: {str(e)}")
    
    # HELPER METHODS
    
    def _get_headers(self, provider: AIProvider, api_key: str) -> Dict[str, str]:
        """Get appropriate headers for each provider."""
        
        base_headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        if provider == AIProvider.OPENROUTER:
            # OpenRouter specific headers as shown in your example
            base_headers.update({
                "HTTP-Referer": "https://photoeai.app",  # Your domain
                "X-Title": "PhotoeAI"
            })
        elif provider == AIProvider.OPENAI:
            # OpenAI specific headers if needed
            # Could add Organization and Project headers here
            pass
        elif provider == AIProvider.GEMINI:
            # Gemini might use different auth format
            base_headers["Authorization"] = f"Bearer {api_key}"
        
        return base_headers
    
    def _parse_text_response(self, provider: AIProvider, response_data: Dict[str, Any]) -> str:
        """Parse text completion response based on provider format."""
        
        try:
            if provider == AIProvider.SUMOPOD:
                # OpenAI-compatible format
                return response_data["choices"][0]["message"]["content"]
            
            elif provider == AIProvider.OPENROUTER:
                # OpenRouter format (similar to OpenAI)
                return response_data["choices"][0]["message"]["content"]
            
            elif provider == AIProvider.OPENAI:
                # OpenAI format
                return response_data["choices"][0]["message"]["content"]
            
            elif provider == AIProvider.GEMINI:
                # Gemini format
                return response_data.get("text", "")
            
            else:  # GENERIC
                # Try common patterns
                if "choices" in response_data:
                    return response_data["choices"][0]["message"]["content"]
                elif "text" in response_data:
                    return response_data["text"]
                else:
                    return str(response_data)
        
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to parse text response from {provider.value}: {e}")
            raise Exception(f"Unable to parse text response from {provider.value}")
    
    def _parse_image_response(self, provider: AIProvider, response_data: Dict[str, Any], 
                            original_prompt: str) -> ImageOutput:
        """Parse image generation response based on provider format."""
        
        try:
            if provider == AIProvider.STABILITY_AI:
                image_data = response_data["artifacts"][0]
                return ImageOutput(
                    image_url=f"data:image/png;base64,{image_data['base64']}",
                    generation_id=f"gen_{image_data.get('seed', 'unknown')}",
                    seed=image_data.get('seed', 0),
                    revised_prompt=original_prompt
                )
            
            elif provider == AIProvider.OPENAI:
                image_data = response_data["data"][0]
                return ImageOutput(
                    image_url=image_data["url"],
                    generation_id=f"dalle_{response_data.get('created', 'unknown')}",
                    seed=0,  # DALL-E doesn't use seeds
                    revised_prompt=image_data.get("revised_prompt", original_prompt)
                )
            
            elif provider in [AIProvider.OPENROUTER, AIProvider.SUMOPOD]:
                # Try common response patterns
                if "data" in response_data:
                    image_data = response_data["data"][0]
                    image_url = image_data.get("url") or f"data:image/png;base64,{image_data.get('base64', '')}"
                elif "images" in response_data:
                    image_data = response_data["images"][0]
                    image_url = image_data.get("url") or f"data:image/png;base64,{image_data.get('image', '')}"
                else:
                    image_url = response_data.get("image_url", "")
                
                return ImageOutput(
                    image_url=image_url,
                    generation_id=f"{provider.value}_{response_data.get('id', 'unknown')}",
                    seed=response_data.get('seed', 0),
                    revised_prompt=original_prompt
                )
            
            else:  # GENERIC
                image_url = (response_data.get("image_url") or 
                           response_data.get("url") or 
                           f"data:image/png;base64,{response_data.get('image', '')}")
                
                return ImageOutput(
                    image_url=image_url,
                    generation_id=f"gen_{response_data.get('id', 'unknown')}",
                    seed=response_data.get('seed', 0),
                    revised_prompt=original_prompt
                )
        
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to parse image response from {provider.value}: {e}")
            raise Exception(f"Unable to parse image response from {provider.value}")
    
    async def enhance_image(self, original_prompt: str, instruction: str, 
                          user_api_key: str, seed: int = 0) -> ImageOutput:
        """Enhanced image generation with modified prompt."""
        enhanced_prompt = f"{original_prompt}\n\n---\n**ENHANCEMENT:** {instruction}"
        logger.info(f"✨ Enhancing with: '{instruction}'")
        
        return await self.generate_image(
            brief_prompt=enhanced_prompt,
            user_api_key=user_api_key
        )
