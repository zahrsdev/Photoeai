"""
Enhanced multi-provider service supporting both text and image generation.
Handles the actual API formats for Sumopod, OpenAI, Gemini, and Midjourney.
"""
import requests
import json
from typing import Optional, Dict, Any, Union
from enum import Enum
from loguru import logger
from app.config.settings import settings
from app.schemas.models import ImageOutput
from app.services.ai_client import AIClient

class ProviderType(Enum):
    """Types of AI services supported."""
    TEXT_COMPLETION = "text_completion"
    IMAGE_GENERATION = "image_generation"
    BOTH = "both"

class AIProvider(Enum):
    """Supported AI providers with their capabilities."""
    SUMOPOD = "sumopod"           # Text completion only (no image generation)
    OPENAI = "openai"             # Both text (GPT) and image (DALL-E) ✅ RELIABLE
    GEMINI = "gemini"             # Text + image (Imagen) ⚠️ EXPERIMENTAL - requires special access
    MIDJOURNEY = "midjourney"     # Image generation only ⚠️ REQUIRES API SUBSCRIPTION
    
    @classmethod
    def normalize_provider_name(cls, provider_name: str) -> str:
        """Normalize provider name to handle common variations."""
        if not provider_name:
            return "openai"  # Default provider
            
        # First strip and lowercase, but preserve original for alias lookup
        original_lower = provider_name.lower().strip()
        normalized = original_lower.replace('_', '').replace('-', '')
        
        # Handle common alias mappings
        provider_aliases = {
            "openaidalle": "openai",
            "dalle": "openai", 
            "dalle3": "openai",
            "geminiimagen": "gemini",  # Fixed: handles gemini_imagen correctly
            "imagen": "gemini",
            "sumo": "sumopod",
            "mj": "midjourney",
        }
        
        # Return alias if found, otherwise return the original input
        return provider_aliases.get(normalized, original_lower)

class UnifiedAIService:
    """
    Unified service that handles both text completion and image generation
    across multiple providers using their actual API formats.
    """
    
    # Provider-to-base-URL mapping
    PROVIDER_BASE_URLS = {
        AIProvider.SUMOPOD: "https://ai.sumopod.com/v1",
        AIProvider.OPENAI: "https://api.openai.com/v1",
        AIProvider.GEMINI: "https://generativelanguage.googleapis.com/v1",
        AIProvider.MIDJOURNEY: "https://api.midjourneyapi.io/v2"
    }
    
    def __init__(self):
        # Use OpenAI as default for image generation (most reliable)
        self.api_base_url = settings.IMAGE_API_BASE_URL
        self.default_model = settings.IMAGE_GENERATION_MODEL
        
        # Override default if it's pointing to unsupported providers
        if "openrouter.ai" in self.api_base_url:
            logger.warning("🔄 OpenRouter detected as default - switching to OpenAI for image generation")
            self.api_base_url = "https://api.openai.com/v1"
        elif "sumopod.com" in self.api_base_url:
            logger.warning("🔄 Sumopod may not support image generation - switching to OpenAI")
            self.api_base_url = "https://api.openai.com/v1"
        
    def get_provider_base_url(self, provider: AIProvider) -> str:
        """Get the correct base URL for the specified provider."""
        return self.PROVIDER_BASE_URLS.get(provider, self.api_base_url)
        
    def detect_provider(self, api_base_url: str) -> AIProvider:
        """Auto-detect the provider based on the API URL."""
        url_lower = api_base_url.lower()
        
        if "sumopod" in url_lower:
            return AIProvider.SUMOPOD
        elif "generativelanguage" in url_lower or "gemini" in url_lower:
            return AIProvider.GEMINI
        elif "openai" in url_lower or "api.openai.com" in url_lower:
            return AIProvider.OPENAI
        elif "midjourney" in url_lower:
            return AIProvider.MIDJOURNEY
        else:
            # Default to OpenAI for unknown URLs
            return AIProvider.OPENAI
    
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
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "maxOutputTokens": max_tokens,
                    "temperature": temperature
                }
            }
        
        else:  # Default to OpenAI format
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
            AIProvider.OPENAI: "/chat/completions",         # Standard OpenAI (base URL already has /v1)
            AIProvider.GEMINI: "/models/gemini-pro:generateContent",   # Gemini format
            AIProvider.MIDJOURNEY: "/chat/completions"       # Default to OpenAI-compatible
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
                # Normalize provider name using the new method
                normalized_name = AIProvider.normalize_provider_name(provider_override)
                provider = AIProvider(normalized_name)
                logger.info(f"🎯 Text Provider override: '{provider_override}' → '{provider.value}'")
            except ValueError:
                logger.warning(f"🔄 Unknown provider '{provider_override}' (normalized: '{normalized_name}'), defaulting to OpenAI")
                provider = AIProvider.OPENAI
        else:
            provider = self.detect_provider(self.api_base_url)
        
        # Get provider-specific base URL
        base_url = self.get_provider_base_url(provider)
        
        # Build request for text completion
        endpoint = f"{base_url.rstrip('/')}{self.get_text_completion_endpoint(provider)}"
        if provider == AIProvider.GEMINI:
            endpoint = f"{endpoint}?key={user_api_key}"
            
        payload = self.build_text_completion_payload(provider, prompt, model, max_tokens, temperature)
        
        # Set up headers based on provider
        headers = self._get_headers(provider, user_api_key)
        
        logger.info(f"🤖 Sending text completion request to {provider.value} at {endpoint}")
        
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
        
        if provider == AIProvider.OPENAI:
            # DALL-E image generation
            return {
                "model": model or "dall-e-3",
                "prompt": brief_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "hd",
                "response_format": "url"
            }
        
        elif provider == AIProvider.GEMINI:
            # Gemini does not support image generation through the standard API
            # Google's Imagen is separate and requires Vertex AI access
            # For now, we'll redirect to OpenAI
            logger.warning("🔄 Gemini image generation not supported - switching to OpenAI")
            return {
                "model": model or "dall-e-3",
                "prompt": brief_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "hd",
                "response_format": "url"
            }
        
        elif provider == AIProvider.SUMOPOD:
            # Sumopod image generation (may not be supported - check provider docs)
            # Using OpenAI-compatible format as fallback
            return {
                "model": model or "dall-e-3",
                "prompt": brief_prompt,
                "n": 1,
                "size": "1024x1024",
                "response_format": "url"
            }
        
        elif provider == AIProvider.MIDJOURNEY:
            # Midjourney image generation
            return {
                "prompt": brief_prompt,
                "model": model or "midjourney-v6",
                "aspect_ratio": "1:1",
                "quality": "high"
            }
        
        else:  # Default format
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
            AIProvider.OPENAI: "/images/generations",       # OpenAI (base URL already has /v1)
            AIProvider.GEMINI: "/images/generations",       # Redirect to OpenAI format since Gemini doesn't support image generation
            AIProvider.SUMOPOD: "/images/generations",      # OpenAI-compatible (text-only provider)
            AIProvider.MIDJOURNEY: "/generate"              # Midjourney (requires API access)
        }
        
        return endpoints.get(provider, "/generate")
    
    async def generate_image(self, brief_prompt: str, user_api_key: str, 
                           negative_prompt: Optional[str] = None,
                           provider_override: Optional[str] = None,
                           model: Optional[str] = None) -> ImageOutput:
        """Generate image using the appropriate provider format."""
        
        # --- CRITICAL FIX: Prompt Enhancement Integration ---
        ai_client = AIClient()
        # Import the smart compressor service
        from app.services.prompt_compressor import prompt_compressor
        
        try:
            logger.info("🎨 Attempting to enhance prompt with Creative Director LLM...")
            enhanced_brief = await ai_client.revise_prompt_for_generation(brief_prompt)
            logger.info("✨ Prompt successfully enhanced.")
            
            # CRITICAL: Remove Unicode characters that cause encoding issues
            import re
            # Remove emojis and other problematic Unicode characters
            enhanced_brief = re.sub(r'[^\x00-\x7F]+', '', enhanced_brief)
            
            # NEW STEP: Smart Compression instead of crude truncation
            MAX_PROMPT_LENGTH = 4000  # DALL-E 3 limit
            if len(enhanced_brief) > MAX_PROMPT_LENGTH:
                logger.info(f"📏 Enhanced brief ({len(enhanced_brief)} chars) exceeds API limit. Applying smart compression...")
                
                # Use the smart compressor service
                final_image_prompt = await prompt_compressor.compress_brief_for_generation(enhanced_brief, MAX_PROMPT_LENGTH)
                
                logger.info(f"🎯 Smart compression complete: {len(enhanced_brief)} → {len(final_image_prompt)} chars")
                brief_prompt = final_image_prompt
            else:
                logger.info(f"📏 Enhanced brief within limits ({len(enhanced_brief)} chars), using full version")
                brief_prompt = enhanced_brief
                
        except Exception as e:
            logger.warning(f"⚠️ Prompt enhancement failed: {e}. Falling back to original prompt.")
            # The original brief_prompt will be used automatically.
            pass
        # --- END ENHANCEMENT INTEGRATION ---
        
        # Detect or override provider
        if provider_override:
            try:
                # Normalize provider name using the new method
                normalized_name = AIProvider.normalize_provider_name(provider_override)
                provider = AIProvider(normalized_name)
                logger.info(f"🎯 Image Provider override: '{provider_override}' → '{provider.value}'")
            except ValueError:
                logger.warning(f"🔄 Unknown provider '{provider_override}' (normalized: '{normalized_name}'), defaulting to OpenAI")
                provider = AIProvider.OPENAI
        else:
            provider = self.detect_provider(self.api_base_url)
        
        # Get provider-specific base URL
        base_url = self.get_provider_base_url(provider)
        
        # Safety check: Block unsupported providers for image generation
        if "openrouter.ai" in base_url:
            logger.error(f"❌ OpenRouter does not support image generation - switching to OpenAI")
            provider = AIProvider.OPENAI
            base_url = self.get_provider_base_url(provider)
        elif "sumopod.com" in base_url and provider == AIProvider.SUMOPOD:
            logger.warning(f"⚠️ Sumopod may not support image generation - switching to OpenAI")
            provider = AIProvider.OPENAI
            base_url = self.get_provider_base_url(provider)
        elif provider == AIProvider.GEMINI:
            logger.warning(f"🔄 Gemini does not support image generation - redirecting to OpenAI")
            provider = AIProvider.OPENAI
            base_url = self.get_provider_base_url(provider)
        elif provider == AIProvider.MIDJOURNEY:
            logger.info(f"🎨 Using Midjourney - requires valid API subscription")
        
        # Build request for image generation
        endpoint = f"{base_url.rstrip('/')}{self.get_image_generation_endpoint(provider)}"
            
        payload = self.build_image_generation_payload(provider, brief_prompt, negative_prompt, model)
        
        # Set up headers
        headers = self._get_headers(provider, user_api_key)
        
        # MISSION 1 LOG POINT: Log final prompt being sent to image generation service
        logger.info("Sending final prompt to image generation service.")
        logger.debug(f"Image generation prompt: {brief_prompt}")
        
        logger.info(f"🎨 Sending image generation request to {provider.value} at {endpoint}")
        logger.debug(f"Provider: {provider.value}, Base URL: {base_url}")
        logger.debug(f"Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
            
            # Better error handling
            if not response.ok:
                error_detail = ""
                try:
                    error_response = response.json()
                    error_detail = error_response.get('error', {}).get('message', str(error_response))
                except:
                    error_detail = response.text
                
                logger.error(f"💥 Image generation API error (HTTP {response.status_code}): {error_detail}")
                
                # Provide specific error messages
                if response.status_code == 401:
                    raise Exception("Authentication failed - please check your API key")
                elif response.status_code == 403:
                    raise Exception("Access forbidden - check your API key permissions")
                elif response.status_code == 404:
                    raise Exception(f"Image generation endpoint not found for {provider.value}")
                elif response.status_code == 503:
                    raise Exception(f"Image generation service temporarily unavailable for {provider.value}")
                else:
                    raise Exception(f"Image generation failed (HTTP {response.status_code}): {error_detail}")
            
            api_response = response.json()
            return self._parse_image_response(provider, api_response, brief_prompt)
            
        except Exception as e:
            logger.error(f"💥 Image generation failed for {provider.value}: {e}")
            raise Exception(f"Image generation service failed: {str(e)}")
    
    # HELPER METHODS
    
    def _get_headers(self, provider: AIProvider, api_key: str) -> Dict[str, str]:
        """Get appropriate headers for each provider."""
        
        if provider == AIProvider.GEMINI:
            # Gemini uses API key as query parameter instead of header
            return {
                "Content-Type": "application/json"
            }
        else:
            # Most providers use Bearer token
            return {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
    
    def _parse_text_response(self, provider: AIProvider, response_data: Dict[str, Any]) -> str:
        """Parse text completion response based on provider format."""
        
        try:
            if provider == AIProvider.SUMOPOD:
                # OpenAI-compatible format
                return response_data["choices"][0]["message"]["content"]
            
            elif provider == AIProvider.OPENAI:
                # OpenAI format
                return response_data["choices"][0]["message"]["content"]
            
            elif provider == AIProvider.GEMINI:
                # Gemini format
                if "candidates" in response_data and len(response_data["candidates"]) > 0:
                    candidate = response_data["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        return candidate["content"]["parts"][0].get("text", "")
                return response_data.get("text", "")
            
            elif provider == AIProvider.MIDJOURNEY:
                # Midjourney text format (if supported)
                if "choices" in response_data:
                    return response_data["choices"][0]["message"]["content"]
                else:
                    return response_data.get("text", "")
            
            else:  # Default fallback
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
            if provider == AIProvider.OPENAI:
                image_data = response_data["data"][0]
                return ImageOutput(
                    image_url=image_data["url"],
                    generation_id=f"dalle_{response_data.get('created', 'unknown')}",
                    seed=0,  # DALL-E doesn't use seeds
                    revised_prompt=image_data.get("revised_prompt", original_prompt),
                    final_enhanced_prompt=original_prompt  # MISSION 2: Include final enhanced prompt
                )
            
            elif provider == AIProvider.GEMINI:
                # Since Gemini redirects to OpenAI, use OpenAI response format
                image_data = response_data["data"][0]
                return ImageOutput(
                    image_url=image_data["url"],
                    generation_id=f"gemini_via_dalle_{response_data.get('created', 'unknown')}",
                    seed=0,  # DALL-E doesn't use seeds
                    revised_prompt=image_data.get("revised_prompt", original_prompt),
                    final_enhanced_prompt=original_prompt  # MISSION 2: Include final enhanced prompt
                )
            
            elif provider == AIProvider.SUMOPOD:
                # Sumopod response format
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
                    generation_id=f"sumopod_{response_data.get('id', 'unknown')}",
                    seed=response_data.get('seed', 0),
                    revised_prompt=original_prompt,
                    final_enhanced_prompt=original_prompt  # MISSION 2: Include final enhanced prompt
                )
            
            elif provider == AIProvider.MIDJOURNEY:
                # Midjourney response format
                image_url = response_data.get("image_url") or response_data.get("url", "")
                
                return ImageOutput(
                    image_url=image_url,
                    generation_id=f"midjourney_{response_data.get('id', 'unknown')}",
                    seed=response_data.get('seed', 0),
                    revised_prompt=original_prompt,
                    final_enhanced_prompt=original_prompt  # MISSION 2: Include final enhanced prompt
                )
            
            else:  # Default fallback
                image_url = (response_data.get("image_url") or 
                           response_data.get("url") or 
                           f"data:image/png;base64,{response_data.get('image', '')}")
                
                return ImageOutput(
                    image_url=image_url,
                    generation_id=f"gen_{response_data.get('id', 'unknown')}",
                    seed=response_data.get('seed', 0),
                    revised_prompt=original_prompt,
                    final_enhanced_prompt=original_prompt  # MISSION 2: Include final enhanced prompt
                )
        
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Failed to parse image response from {provider.value}: {e}")
            raise Exception(f"Unable to parse image response from {provider.value}")
    
    async def enhance_image(self, original_prompt: str, instruction: str, 
                          user_api_key: str, seed: int = 0) -> ImageOutput:
        """Enhanced image generation using intelligent prompt enhancement."""
        from app.services.image_generator import ImageGenerationService
        
        logger.info(f"✨ Using intelligent enhancement for: '{instruction}'")
        
        # Use the enhanced image generator service for better enhancement
        enhanced_service = ImageGenerationService()
        return await enhanced_service.enhance_image(
            original_prompt=original_prompt,
            instruction=instruction,
            user_api_key=user_api_key,
            seed=seed
        )
