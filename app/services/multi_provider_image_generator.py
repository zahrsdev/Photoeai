"""
Enhanced Image Generator Service for OpenAI GPT Image 1.
Optimized for single provider (OpenAI) for reliability and performance.
"""
from typing import Optional, Dict, Any
from enum import Enum
from loguru import logger
import requests
import re
from app.config.settings import settings
from app.schemas.models import ImageOutput

class ImageProvider(Enum):
    """Supported image generation providers."""
    OPENAI_DALLE = "openai_dalle"
    OPENAI_GPT_IMAGE = "openai_gpt_image"

class OpenAIImageService:
    """
    OpenAI GPT Image 1 generation service optimized for single provider reliability.
    """
    
    def __init__(self):
        self.api_base_url = settings.IMAGE_API_BASE_URL
        self.default_model = settings.IMAGE_GENERATION_MODEL
    
    def detect_provider(self, api_base_url: str) -> ImageProvider:
        """Auto-detect the provider based on the API URL. Always returns OpenAI."""
        # Simplified: Always use OpenAI for GPT Image 1
        return ImageProvider.OPENAI_GPT_IMAGE
    
    def _normalize_for_chatgpt_quality(self, prompt: str) -> str:
        """
        🎯 SMART DALL-E OPTIMIZATION: Balance comprehensive brief with DALL-E limits
        
        This function processes prompts to match ChatGPT Image's natural,
        realistic photography output while preserving technical specs for HD quality.
        """
        normalized = prompt
        original_length = len(normalized)
        
        logger.info(f"🎯 Normalizing prompt: {original_length} chars")
        
        # Remove excessive markdown formatting that might confuse image AI
        normalized = re.sub(r'^#+\s+', '', normalized, flags=re.MULTILINE)  # Remove headers
        normalized = re.sub(r'\*\*(.*?)\*\*', r'\1', normalized)  # Remove bold
        normalized = re.sub(r'\*(.*?)\*', r'\1', normalized)  # Remove italic
        normalized = re.sub(r'`(.*?)`', r'\1', normalized)  # Remove code blocks
        normalized = re.sub(r'^\s*[-*+]\s+', '', normalized, flags=re.MULTILINE)  # Remove bullets
        normalized = re.sub(r'^\s*\d+\.\s+', '', normalized, flags=re.MULTILINE)  # Remove numbers
        
        
        # Ensure natural photography language
        if 'photograph' not in normalized.lower() and 'photography' not in normalized.lower():
            if 'ultra-realistic' in normalized.lower():
                # Already has realistic descriptor
                pass
            else:
                normalized = f"Realistic photograph of {normalized.lstrip('A ').lstrip('An ')}"
        
        # Clean up multiple spaces and formatting
        normalized = ' '.join(normalized.split())
        
        # 🎯 DYNAMIC DALL-E OPTIMIZATION: Adjust based on actual prompt length
        # DALL-E 3 works best with 1500-3500 characters
        target_length = min(3500, max(1500, len(normalized)))
        
        if len(normalized) > target_length:
            logger.info(f"⚡ Optimizing: {len(normalized)} → target ~{target_length} chars")
            
            # Step 1: SMART COMPRESSION - Preserve sentence boundaries and technical specs
            # Compress headers and redundant text while keeping complete sentences
            normalized = re.sub(r'Professional Product Photography Brief:\s*', '', normalized)
            normalized = re.sub(r'Campaign Overview\s*', '', normalized)
            normalized = re.sub(r'Visual Composition & Artistic Direction\s*', '', normalized)
            normalized = re.sub(r'Primary Subject & Product Placement\s*', '', normalized)
            normalized = re.sub(r'Environmental Context & Location Aesthetics\s*', '', normalized)
            normalized = re.sub(r'Lighting Design & Atmospheric Conditions\s*', '', normalized)
            normalized = re.sub(r'Technical Camera Specifications\s*', '', normalized)
            normalized = re.sub(r'Brand Integration & Product Presentation\s*', '', normalized)
            
            # CAREFULLY compress repetitive phrases without breaking sentences
            normalized = re.sub(r'This comprehensive photography brief outlines the creative and technical specifications for capturing ', 'Capturing ', normalized)
            normalized = re.sub(r'designed to showcase the brand\'s commitment to ', 'showcasing ', normalized)
            normalized = re.sub(r'The central focus features a large ', 'Large ', normalized)
            normalized = re.sub(r'positioned strategically to emerge ', 'emerging ', normalized)
            
            # Step 2: If STILL too long, prioritize technical + visual (keep HD specs)
            if len(normalized) > target_length:
                # PRIORITY: Keep technical specs that affect HD quality (COMPLETE sentences only)
                technical_priority = [
                    'Canon EOS R5', 'f/1.8', 'f/5.6', '50mm', 'lens',
                    'ISO', 'shutter speed', 'aperture', 'depth of field', 'focus point',
                    'post-production', 'sharpening', 'color grading', 'enhancement',
                    'broadcast quality', 'resolution', 'large-format', 'printing'
                ]
                
                # PRIORITY: Keep visual elements
                visual_priority = [
                    'bottle', 'water', 'mountain', 'lake', 'golden hour', 'sunlight',
                    'crystal-clear', 'reflections', 'natural light', 'cinematic', 
                    'composition', 'rule of thirds', 'lighting', 'backdrop'
                ]
                
                # SMART sentence splitting - handle technical specs properly
                # Don't split on periods that are part of technical specs (f/5.6, ISO 200.0, etc.)
                
                # Replace technical periods with temporary placeholders
                temp_normalized = normalized
                temp_normalized = re.sub(r'f/(\d+)\.(\d+)', r'f/\1DOTPLACEHOLDER\2', temp_normalized)  # f/5.6 → f/5DOTPLACEHOLDER6
                temp_normalized = re.sub(r'(\d+)\.(\d+)mm', r'\1DOTPLACEHOLDER\2mm', temp_normalized)  # 50.0mm → 50DOTPLACEHOLDER0mm
                temp_normalized = re.sub(r'ISO (\d+)\.(\d+)', r'ISO \1DOTPLACEHOLDER\2', temp_normalized)  # ISO 200.0 → ISO 200DOTPLACEHOLDER0
                temp_normalized = re.sub(r'(\d+)\.(\d+)s', r'\1DOTPLACEHOLDER\2s', temp_normalized)  # 1.5s → 1DOTPLACEHOLDER5s
                temp_normalized = re.sub(r'1/(\d+)\.(\d+)s', r'1/\1DOTPLACEHOLDER\2s', temp_normalized)  # 1/125.0s → 1/125DOTPLACEHOLDER0s
                
                # Now safely split by sentences
                sentences = [s.strip() for s in temp_normalized.split('.') if s.strip()]
                
                # Restore the periods in technical specs
                sentences = [s.replace('DOTPLACEHOLDER', '.') for s in sentences]
                
                # Categorize by importance (technical + visual = highest priority)
                critical_sentences = []
                important_sentences = []
                
                for sentence in sentences:
                    has_technical = any(tech.lower() in sentence.lower() for tech in technical_priority)
                    has_visual = any(visual.lower() in sentence.lower() for visual in visual_priority)
                    
                    if has_technical or has_visual:
                        critical_sentences.append(sentence)
                    elif len(sentence) > 30:  # Keep meaningful sentences
                        important_sentences.append(sentence)
                
                # Build result: Critical first, ensure complete sentences
                result_sentences = []
                
                # Add critical sentences (technical + visual) with completeness check
                for sentence in critical_sentences[:12]:  # Max 12 critical
                    # Ensure sentence is reasonably complete (has subject + verb or detailed description)
                    if len(sentence) > 20 and ('Canon' in sentence or 'f/' in sentence or 'ISO' in sentence or 
                                             any(visual.lower() in sentence.lower() for visual in visual_priority)):
                        result_sentences.append(sentence)
                    elif len(sentence) > 40:  # Longer sentences are more likely complete
                        result_sentences.append(sentence)
                
                # Fill remaining space with important sentences
                current_length = len('. '.join(result_sentences))
                
                for sentence in important_sentences:
                    if current_length + len(sentence) + 2 < target_length - 200:  # Leave more buffer
                        if len(sentence) > 25:  # Only add substantial sentences
                            result_sentences.append(sentence)
                            current_length += len(sentence) + 2
                    else:
                        break
                
                # Properly reconstruct with periods
                if result_sentences:
                    normalized = '. '.join(result_sentences)
                    # Ensure proper ending
                    if not normalized.endswith('.') and not normalized.endswith('!') and not normalized.endswith('?'):
                        normalized += '.'
        
        # Final cleanup
        normalized = re.sub(r'\s+', ' ', normalized)  # Multiple spaces
        normalized = re.sub(r'\.\s*\.', '.', normalized)  # Double periods
        
        final_length = len(normalized)
        logger.info(f"✅ Normalization complete: {original_length} → {final_length} chars ({final_length/original_length*100:.1f}%)")
        
        return normalized.strip()
    
    def _extract_enhancement_ratio(self, brief_content: str) -> str:
        """Extract enhancement ratio information for display"""
        import re
        
        # Look for enhancement patterns in the brief
        enhancement_patterns = [
            r'(\d+)x enhanced',
            r'(\d+)x expansion',
            r'expanded (\d+)x',
            r'enhanced by (\d+)x',
            r'(\d+)-fold enhancement'
        ]
        
        for pattern in enhancement_patterns:
            match = re.search(pattern, brief_content, re.IGNORECASE)
            if match:
                ratio = match.group(1)
                return f"{ratio}x enhancement"
        
        # Fallback: estimate based on length
        if len(brief_content) > 3000:
            return "10x+ enhancement"
        elif len(brief_content) > 2000:
            return "8x enhancement"
        elif len(brief_content) > 1000:
            return "6x enhancement"
        else:
            return "4x enhancement"
    
    def build_request_payload(self, provider: ImageProvider, brief_prompt: str, 
                            negative_prompt: Optional[str] = None, 
                            model: Optional[str] = None) -> Dict[str, Any]:
        """Build request payload based on provider specifications."""
        
        model = model or self.default_model
        
        if provider == ImageProvider.OPENAI_GPT_IMAGE:
            # GPT Image 1 image generation format
            normalized_prompt = self._normalize_for_chatgpt_quality(brief_prompt)
            
            # 🎯 GPT IMAGE 1 API payload (uses images endpoint)
            return {
                "model": "gpt-image-1",
                "prompt": normalized_prompt,
                "n": 1,
                "size": "1024x1024"
            }
        else:  # Always fallback to GPT Image 1 format
            normalized_prompt = self._normalize_for_chatgpt_quality(brief_prompt)
            return {
                "model": "gpt-image-1",
                "prompt": normalized_prompt,
                "n": 1,
                "size": "1024x1024"
            }
    
    def get_endpoint_path(self, provider: ImageProvider) -> str:
        """Get the correct endpoint path for image generation."""
        if provider == ImageProvider.OPENAI_GPT_IMAGE:
            return "/images/generations"  # GPT Image 1 uses images endpoint
        return "/chat/completions"  # Default for other providers
    
    def parse_response(self, provider: ImageProvider, response_data: Dict[str, Any]) -> ImageOutput:
        """Parse API response based on provider format."""
        
        try:
            if provider == ImageProvider.OPENAI_GPT_IMAGE:
                # GPT Image 1 response format (image generation API format)
                if "data" in response_data and response_data["data"]:
                    image_data = response_data["data"][0]
                    
                    # Handle different response formats
                    if "url" in image_data:
                        image_url = image_data["url"]
                    elif "b64_json" in image_data:
                        # GPT Image 1 format - convert base64 to data URL
                        base64_data = image_data["b64_json"]
                        image_url = f"data:image/png;base64,{base64_data}"
                    else:
                        raise KeyError("No 'url' or 'b64_json' found in response")
                    
                    revised_prompt = image_data.get("revised_prompt", "")
                    generation_id = f"gpt_image_{abs(hash(image_url)) % 100000}"
                    
                    return ImageOutput(
                        image_url=image_url,
                        generation_id=generation_id,
                        seed=0,  # GPT Image 1 doesn't use seeds
                        revised_prompt=revised_prompt,
                        final_enhanced_prompt=revised_prompt,
                        model_used="GPT-Image-1",
                        provider_used="OpenAI GPT Image 1"
                    )
                else:
                    raise KeyError("No 'data' found in GPT Image 1 response")
            
            else:  # Always fallback to OpenAI format
                # Handle as OpenAI response format
                image_data = response_data["data"][0]
                revised_prompt = image_data.get("revised_prompt", "")
                
                # Handle different response formats
                if "url" in image_data:
                    image_url = image_data["url"]
                elif "b64_json" in image_data:
                    # GPT Image 1 format - convert base64 to data URL
                    base64_data = image_data["b64_json"]
                    image_url = f"data:image/png;base64,{base64_data}"
                else:
                    raise KeyError("No 'url' or 'b64_json' found in response")
                
                generation_id = f"openai_{abs(hash(image_url)) % 100000}"
                
                return ImageOutput(
                    image_url=image_url,
                    generation_id=generation_id,
                    seed=0,
                    revised_prompt=revised_prompt,
                    final_enhanced_prompt=revised_prompt,
                    model_used="OpenAI Image Model",
                    provider_used="OpenAI Image API"
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
        
        # Always use OpenAI provider for GPT Image 1
        provider = ImageProvider.OPENAI_GPT_IMAGE
        
        # Accept various provider override names but always map to OpenAI
        if provider_override:
            logger.info(f"Provider override '{provider_override}' requested, using OpenAI GPT Image 1")
        
        # Build request
        endpoint = f"{self.api_base_url.rstrip('/')}{self.get_endpoint_path(provider)}"
        payload = self.build_request_payload(provider, brief_prompt, negative_prompt)
        
        # Set up headers (ChatGPT Image compatible)
        headers = {
            "Authorization": f"Bearer {user_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenAI-ChatGPT/1.0"
        }
        
        # Add any provider-specific headers if needed
        # (OpenRouter headers removed since it's no longer supported)
        
        logger.info(f"🎨 Sending request to {provider.value} for: '{brief_prompt[:50]}...'")
        logger.info(f"🔗 Endpoint: {endpoint}")
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=120)
            response.raise_for_status()
            
            api_response = response.json()
            logger.info(f"✅ Received response from {provider.value}")
            
            # 🔍 DEBUG: Log response structure for better ID extraction
            logger.debug(f"📋 API Response structure: {list(api_response.keys())}")
            if "data" in api_response and api_response["data"]:
                logger.debug(f"📋 Image data keys: {list(api_response['data'][0].keys())}")
            
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
