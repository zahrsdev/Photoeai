"""
🚀 BREAKTHROUGH Enhanced Image Generator Service for OpenAI GPT Image 1.
NOW WITH IMAGE EDIT API FOR PERFECT SHAPE PRESERVATION!
Optimized for single provider (OpenAI) for reliability and performance.
"""
from typing import Optional, Dict, Any
from enum import Enum
from loguru import logger
import requests
import re
import base64
import os
import uuid
import io
from PIL import Image
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
        
        NOTE: This is for GENERATION API (text-to-image) with 4000 char limits
        """
        normalized = prompt
        original_length = len(normalized)
        
        logger.info(f"🎯 Normalizing prompt for GENERATION API: {original_length} chars")
        
        # FOCUSED FIX: UNIVERSAL PRODUCT PRESERVATION FOR ANY PRODUCT TYPE
        # Generic preservation rules that work for shoes, bottles, cosmetics, etc.
        preservation_content = """You must photograph this EXACT product as it exists. DO NOT change the product shape, DO NOT redesign any components, DO NOT alter proportions or design elements. This is professional product photography of an existing product - capture it EXACTLY as shown in the reference image. Your job is professional lighting and composition ONLY, not product design changes. Maintain original dimensions, design features, and visual characteristics EXACTLY as they appear."""
        
        logger.info("🔒 PRESERVATION: Direct shape preservation protocol injected")
        logger.info("🔒 FOCUSED MODE: Documentary photography - no product modifications")

        # Remove ALL markdown formatting that might confuse image AI
        normalized = re.sub(r'^#+\s+', '', normalized, flags=re.MULTILINE)  # Remove headers
        normalized = re.sub(r'\*\*(.*?)\*\*', r'\1', normalized)  # Remove bold
        normalized = re.sub(r'\*(.*?)\*', r'\1', normalized)  # Remove italic
        normalized = re.sub(r'`(.*?)`', r'\1', normalized)  # Remove code blocks
        normalized = re.sub(r'```.*?```', '', normalized, flags=re.DOTALL)  # Remove code blocks
        normalized = re.sub(r'^\s*[-*+]\s+', '', normalized, flags=re.MULTILINE)  # Remove bullets
        normalized = re.sub(r'^\s*\d+\.\s+', '', normalized, flags=re.MULTILINE)  # Remove numbers
        normalized = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', normalized)  # Remove links [text](url)
        normalized = re.sub(r'>\s*', '', normalized, flags=re.MULTILINE)  # Remove blockquotes
        normalized = re.sub(r'^\s*\|.*\|.*$', '', normalized, flags=re.MULTILINE)  # Remove table rows
        normalized = re.sub(r'^[-\s|:]+$', '', normalized, flags=re.MULTILINE)  # Remove table separators
        normalized = re.sub(r'---+', '', normalized)  # Remove horizontal rules
        normalized = re.sub(r'~~(.*?)~~', r'\1', normalized)  # Remove strikethrough
        
        # CRITICAL: Re-inject product preservation rules at the beginning
        if preservation_content:
            normalized = preservation_content + " " + normalized
            logger.info(f"🔒 PRESERVATION INJECTION: Added {len(preservation_content)} chars of protection rules")
            logger.info(f"🔒 PRESERVATION PREVIEW: {preservation_content[:100]}...")
        else:
            logger.error("🚨 CRITICAL ERROR: NO PRESERVATION RULES INJECTED - PRODUCT AT RISK!")
        
        logger.info(f"🔒 FINAL PROMPT PREVIEW: {normalized[:200]}...")
        
        
        # Ensure natural photography language
        if 'photograph' not in normalized.lower() and 'photography' not in normalized.lower():
            if 'ultra-realistic' in normalized.lower():
                # Already has realistic descriptor
                pass
            else:
                normalized = f"Realistic photograph of {normalized.lstrip('A ').lstrip('An ')}"
        
        # Clean up multiple spaces and formatting  
        normalized = ' '.join(normalized.split())
        
        # Final cleanup - remove any remaining markdown artifacts
        normalized = re.sub(r'\\+', '', normalized)  # Remove escaped characters
        normalized = re.sub(r'\|+', '', normalized)  # Remove remaining pipe characters
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize spaces
        
        # 🚀 GPT IMAGE-1 PROCESSING: No compression needed (high capacity model)
        # GPT Image-1 can handle full comprehensive briefs without compression
        
        final_length = len(normalized)
        logger.info(f"� GPT IMAGE-1 Processing complete: {original_length} → {final_length} chars (NO COMPRESSION)")
        
        return normalized
    
    def _normalize_for_edit_api(self, prompt: str) -> str:
        """
        🚀 BREAKTHROUGH: NO COMPRESSION for GPT Image-1 Edit API (32,000 char limit)
        
        This function does MINIMAL processing for Edit API:
        - NO compression (32K character limit)
        - Clean markdown only
        - Preserve ALL technical details
        - Full preservation instructions
        """
        normalized = prompt
        original_length = len(normalized)
        
        logger.info(f"🚀 BREAKTHROUGH: Processing for Edit API (NO COMPRESSION): {original_length} chars")
        
        # ONLY remove markdown formatting - NO COMPRESSION
        normalized = re.sub(r'^#+\s+', '', normalized, flags=re.MULTILINE)  # Remove headers
        normalized = re.sub(r'\*\*(.*?)\*\*', r'\1', normalized)  # Remove bold
        normalized = re.sub(r'\*(.*?)\*', r'\1', normalized)  # Remove italic
        normalized = re.sub(r'`(.*?)`', r'\1', normalized)  # Remove code blocks
        normalized = re.sub(r'```.*?```', '', normalized, flags=re.DOTALL)  # Remove code blocks
        normalized = re.sub(r'^\s*[-*+]\s+', '', normalized, flags=re.MULTILINE)  # Remove bullets
        normalized = re.sub(r'^\s*\d+\.\s+', '', normalized, flags=re.MULTILINE)  # Remove numbers
        normalized = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', normalized)  # Remove links
        
        # Clean up spaces ONLY
        normalized = ' '.join(normalized.split())
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize spaces
        
        final_length = len(normalized)
        logger.info(f"🚀 BREAKTHROUGH: Edit API processing complete: {original_length} → {final_length} chars (NO COMPRESSION)")
        
        return normalized
        
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
            
            # Step 2: If STILL too long, prioritize PRODUCT PRESERVATION + technical + visual
            if len(normalized) > target_length:
                # TOP PRIORITY: PURE ENGLISH PRODUCT PRESERVATION (NEVER filter out)
                product_preservation_priority = [
                    'CRITICAL PRODUCT PRESERVATION PROTOCOL', 'ABSOLUTELY FORBIDDEN', 'FORBIDDEN TERRITORY',
                    'NEVER CHANGE', 'NEVER ALTER', 'NEVER MODIFY', 'ZERO MODIFICATIONS', 
                    'EXACTLY AS IT EXISTS', 'PRODUCT COLORS ARE SACRED', 'SACRED AND UNTOUCHABLE',
                    'white stays white', 'black stays black', 'red stays red', 'blue stays blue',
                    'STRICTLY PROHIBITED', 'IMMEDIATE REJECTION', 'FORBIDDEN FROM CHANGING',
                    'preserve original', 'authentic', 'unchanged', 'natural colors', 'true colors',
                    'original appearance', 'exact shape', 'original design', 'as-is condition',
                    'photography techniques only', 'lighting setup only', 'background only',
                    'camera angles only', 'depth of field only', 'composition only',
                    'VIOLATION', 'PENALTY', 'RESTRICTION', 'PROTOCOL', 'MANDATORY'
                ]
                
                # CRITICAL: Rule-based restrictions (NEVER remove)
                rule_restrictions = [
                    'poor quality', 'low resolution', 'blurry', 'out of focus', 'watermark',
                    'disfigured', 'deformed', 'mutated', 'extra limbs', 'bad hands',
                    'overexposed', 'underexposed', 'harsh shadows', 'unnatural colors',
                    'floating', 'levitating', 'unrealistic', 'impossible', 'melted',
                    'cluttered', 'messy', 'distracting', 'negative prompt', 'avoid',
                    'forbidden', 'restriction', 'rule', 'must not', 'should not'
                ]
                
                # PRIORITY: Keep technical specs that affect HD quality (COMPLETE sentences only)
                technical_priority = [
                    'Hasselblad medium format camera', 'Phase One XF IQ4 digital back', '15-stop dynamic range sensor',
                    '85mm f/1.4 lens with creamy bokeh', '35mm f/1.4 environmental portrait', '50mm f/1.2 prime', 'tilt-shift lens',
                    'Rembrandt lighting', 'Loop lighting', 'Butterfly lighting', 'Split lighting', 'Clamshell lighting',
                    'large octabox softbox', 'silver beauty dish with grid', 'parabolic umbrella reflector', 'profoto strobe 500 Ws',
                    'golden hour warm directional light', 'daylight 5600K cool tone', 'tungsten 3200K warm glow',
                    'Kodak Portra 400 film grain', 'Kodak Ektar 100 saturated colors', 'medium format raw files',
                    'shallow depth of field', 'creamy bokeh background', 'rule of thirds composition', 'leading lines',
                    'professional color grading', 'high dynamic range HDR tonal compression', 'clean white background'
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
                
                # Categorize by importance (PRODUCT PRESERVATION = TOP PRIORITY)
                critical_sentences = []
                important_sentences = []
                
                for sentence in sentences:
                    has_product_preservation = any(preserve.lower() in sentence.lower() for preserve in product_preservation_priority)
                    has_rule_restriction = any(rule.lower() in sentence.lower() for rule in rule_restrictions)
                    has_technical = any(tech.lower() in sentence.lower() for tech in technical_priority)
                    has_visual = any(visual.lower() in sentence.lower() for visual in visual_priority)
                    
                    if has_product_preservation or has_rule_restriction:
                        # ABSOLUTE TOP PRIORITY - product preservation & restrictions NEVER get filtered
                        critical_sentences.insert(0, sentence)  # Insert at beginning
                    elif has_technical or has_visual:
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
    
    def _save_base64_to_file(self, base64_data: str, file_extension: str = "png") -> str:
        """
        Save base64 image data to static file and return URL.
        
        Args:
            base64_data: Base64 encoded image data
            file_extension: File extension (default: png)
            
        Returns:
            HTTP URL to the saved image file
        """
        # Generate unique filename
        file_id = str(uuid.uuid4())[:8]
        filename = f"img_{file_id}.{file_extension}"
        filepath = os.path.join("static", "images", filename)
        
        # Create directory if not exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Decode and save base64 data
        image_bytes = base64.b64decode(base64_data)
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Return HTTP URL
        base_url = f"http://{settings.host}:{settings.port}"
        image_url = f"{base_url}/static/images/{filename}"
        
        logger.info(f"💾 Saved image: {filepath} → {image_url}")
        return image_url
    
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
            # GPT Image 1 image generation format with HIGH quality
            normalized_prompt = self._normalize_for_chatgpt_quality(brief_prompt)
            
            # FORCE TECHNICAL PRESERVATION constraints at prompt end
            technical_constraints = " Technical photography specification: maintain exact product shape, color accuracy, and proportions as shown. Documentary photography mode with zero artistic modifications to the product itself. Natural product representation only."
            final_prompt = normalized_prompt + technical_constraints
            
            # 🎯 GPT IMAGE 1 API payload (uses images endpoint) with HIGH quality
            return {
                "model": "gpt-image-1",
                "prompt": final_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "high"  # HIGH quality setting (updated from 'hd')
                # Note: GPT Image-1 doesn't support "style" parameter - removed
            }
        else:  # Always fallback to GPT Image 1 format
            normalized_prompt = self._normalize_for_chatgpt_quality(brief_prompt)
            
            # FORCE TECHNICAL PRESERVATION constraints at prompt end
            technical_constraints = " Technical photography specification: maintain exact product shape, color accuracy, and proportions as shown. Documentary photography mode with zero artistic modifications to the product itself. Natural product representation only."
            final_prompt = normalized_prompt + technical_constraints
            
            return {
                "model": "gpt-image-1",
                "prompt": final_prompt,
                "n": 1,
                "size": "1024x1024",
                "quality": "high"  # HIGH quality setting (updated from 'hd')
                # Note: GPT Image-1 doesn't support "style" parameter - removed
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
                        # GPT Image 1 format - save base64 to file and return URL
                        base64_data = image_data["b64_json"]
                        image_url = self._save_base64_to_file(base64_data)
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
                    # GPT Image 1 format - save base64 to file and return URL
                    base64_data = image_data["b64_json"]
                    image_url = self._save_base64_to_file(base64_data)
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
                           provider_override: Optional[str] = None,
                           uploaded_image_base64: Optional[str] = None,
                           progress_callback = None) -> ImageOutput:
        """
        🎯 BOSS PROPER PIPELINE: Image Analysis → Wizard → Brief → Generation
        
        Args:
            brief_prompt: User input prompt
            user_api_key: User's API key for the service
            negative_prompt: Optional negative prompt
            provider_override: Optional provider name override
            uploaded_image_base64: Base64 encoded uploaded image for full pipeline
        """
        
        # If image uploaded, run FULL PIPELINE (background processing)
        if uploaded_image_base64:
            if progress_callback:
                await progress_callback("Analisis image sedang berlangsung")
            logger.info("🎯 BOSS PIPELINE: Running full analysis pipeline")
            
            # Import services for pipeline
            from app.services.image_analysis_service import ImageAnalysisService
            from app.services.image_wizard_bridge import ImageWizardBridge  
            from app.services.brief_orchestrator import BriefOrchestratorService
            import tempfile
            import base64
            from pathlib import Path
            
            # STEP 1: Vision API analyze image (BACKGROUND)
            if progress_callback:
                await progress_callback("Sedang ekstrak dari image")
            image_service = ImageAnalysisService()
            
            # Convert base64 to temp file for analysis
            image_data = base64.b64decode(uploaded_image_base64)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_file.write(image_data)
                temp_path = tmp_file.name
            
            try:
                # Analyze image
                logger.info("🔍 PIPELINE STEP 1: Analyzing uploaded image...")
                image_analysis = await image_service.analyze_product_image_from_file(temp_path, user_api_key)
                
                if progress_callback:
                    await progress_callback("Prompt dari image berhasil di ekstrak")
                
                # STEP 2: Bridge analysis + prompt → wizard fields (BACKGROUND)  
                if progress_callback:
                    await progress_callback("Sedang mengisi 48 wizard fields dari image analysis dan prompt user")
                logger.info("🌉 PIPELINE STEP 2: Bridging image analysis with user prompt...")
                bridge = ImageWizardBridge()
                wizard_input = bridge.combine_image_and_prompt(image_analysis, brief_prompt)
                
                if progress_callback:
                    await progress_callback("Prompt dari user dan image berhasil di isi di 48 wizard fields")
                
                # STEP 3: Generate comprehensive brief from wizard (BACKGROUND)
                if progress_callback:
                    await progress_callback("Enhance brief sudah digenerate")
                logger.info("📝 PIPELINE STEP 3: Generating comprehensive brief from wizard data...")
                orchestrator = BriefOrchestratorService()
                brief_output = await orchestrator.generate_final_brief(wizard_input)
                
                if progress_callback:
                    await progress_callback("Enhance full brief dikirim ke OpenAI")
                
                # Use enhanced brief for generation
                brief_prompt = brief_output.final_prompt
                
            finally:
                # Clean up temp file
                Path(temp_path).unlink(missing_ok=True)
        
        # STEP 4: Generate image with existing logic (BACKGROUND)
        if progress_callback:
            await progress_callback("Full brief sudah dikirim ke OpenAI")
        logger.info("🎨 PIPELINE FINAL: Generating image...")
        
        # Always use OpenAI provider for GPT Image 1
        provider = ImageProvider.OPENAI_GPT_IMAGE
        
        # Accept various provider override names but always map to OpenAI
        if provider_override:
            logger.info(f"Provider override '{provider_override}' requested, using OpenAI GPT Image 1")
        
        # Build request
        endpoint = f"{self.api_base_url.rstrip('/')}{self.get_endpoint_path(provider)}"
        payload = self.build_request_payload(provider, brief_prompt, negative_prompt)
        
        # Set up headers (GPT Image 1 compatible with OpenAI 1.101.0)
        headers = {
            "Authorization": f"Bearer {user_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "OpenAI/1.101.0"  # OpenAI 1.101.0 user agent
        }
        
        # Add any provider-specific headers if needed
        # (OpenRouter headers removed since it's no longer supported)
        
        logger.info(f"🎨 Sending request to {provider.value} for: '{brief_prompt[:50]}...'")
        logger.info(f"🔗 Endpoint: {endpoint}")
        
        try:
            response = requests.post(endpoint, headers=headers, json=payload, timeout=300)
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
    
    async def generate_with_breakthrough_edit(
        self, 
        brief_prompt: str, 
        user_api_key: str,
        uploaded_image_base64: str,
        progress_callback = None
    ) -> ImageOutput:
        """
        🚀 BREAKTHROUGH: GPT Image-1 Edit API for PERFECT Shape Preservation
        
        This uses the IMAGE EDIT API instead of text-to-image generation:
        1. Upload original product image directly to GPT Image-1
        2. Use 'input_fidelity=high' to preserve original features  
        3. Apply professional photography enhancement prompts
        4. RESULT: Enhanced image with PRESERVED original shape!
        """
        if progress_callback:
            await progress_callback("🚀 BREAKTHROUGH: Initializing GPT Image-1 Edit API...")
        
        logger.info("🔥 BREAKTHROUGH MODE: Using GPT Image-1 Edit API for shape preservation")
        
        try:
            # Import image editing service
            import tempfile
            from pathlib import Path
            from app.services.image_analysis_service import ImageAnalysisService
            from app.services.image_wizard_bridge import ImageWizardBridge  
            from app.services.brief_orchestrator import BriefOrchestratorService
            
            # STEP 1: Get analysis for enhanced prompting (OPTIONAL - for context)
            if progress_callback:
                await progress_callback("🔍 Analyzing product for preservation context...")
            
            # Quick analysis for prompt enhancement
            image_data = base64.b64decode(uploaded_image_base64)
            
            # TASK 2: RESIZE IMAGE FOR EDIT API (max 4MB, recommended 1024x1024)
            from PIL import Image
            import io
            
            image_pil = Image.open(io.BytesIO(image_data))
            
            # Resize if too big (Edit API limit)
            max_size = 1024
            if image_pil.width > max_size or image_pil.height > max_size:
                if progress_callback:
                    await progress_callback(f"📏 Resizing image from {image_pil.width}x{image_pil.height} to max {max_size}px...")
                
                image_pil.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert back to bytes
                buffer = io.BytesIO()
                image_pil.save(buffer, format='PNG', optimize=True)
                image_data = buffer.getvalue()
                
                # Update base64 for later use
                uploaded_image_base64 = base64.b64encode(image_data).decode('utf-8')
            
            image_service = ImageAnalysisService()
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_file.write(image_data)
                temp_path = tmp_file.name
            
            try:
                # Get analysis for context (but we don't need full pipeline)
                analysis = await image_service.analyze_product_image_from_file(temp_path, user_api_key)
                analysis_text = analysis.get('analysis', '')
            except Exception as e:
                logger.warning(f"Analysis failed, proceeding without context: {e}")
                analysis_text = ""
            finally:
                Path(temp_path).unlink(missing_ok=True)
            
            # STEP 2: Enhance brief prompt first (CRITICAL FOR FULL PHOTOGRAPHY BRIEF)
            if progress_callback:
                await progress_callback("🎯 Enhancing prompt to full photography brief...")
            
            # Use correct brief orchestrator pipeline (STEP 1: InitialUserRequest)
            from app.schemas.models import InitialUserRequest
            initial_request = InitialUserRequest(user_request=brief_prompt)
            
            # Create brief orchestrator instance
            brief_orchestrator = BriefOrchestratorService()
            
            # STEP 2: Extract to WizardInput
            wizard_input = await brief_orchestrator.extract_and_autofill(initial_request)
            
            # STEP 3: Generate final enhanced brief  
            brief_result = await brief_orchestrator.generate_final_brief(wizard_input)
            enhanced_brief = brief_result.final_prompt
            
            # STEP 3: Build preservation-focused edit prompt with ENHANCED brief
            if progress_callback:
                await progress_callback("🎯 Building shape preservation prompt...")
            
            edit_prompt = self._build_edit_preservation_prompt(enhanced_brief, analysis_text)
            
            # STEP 4: Prepare image for GPT Image-1 Edit API
            if progress_callback:
                await progress_callback("🖼️ Preparing image for Edit API...")
            
            # Convert to proper format for API
            image = Image.open(io.BytesIO(image_data))
            
            # FIX: Resize image if too large to avoid 413 Payload Too Large
            max_size = (1024, 1024)  # OpenAI Edit API recommended max size
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                logger.info(f"🔧 Resizing image from {image.size} to fit {max_size}")
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
                if progress_callback:
                    await progress_callback("📏 Resized image for optimal API payload size...")
            
            # Convert to PNG for best compatibility 
            png_buffer = io.BytesIO()
            if image.mode == 'RGBA':
                image.save(png_buffer, format='PNG')
            else:
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                image.save(png_buffer, format='PNG')
            
            png_buffer.seek(0)
            
            # STEP 4: Call GPT Image-1 Edit API
            if progress_callback:
                await progress_callback("🚀 Calling GPT Image-1 Edit API with HIGH fidelity...")
            
            logger.info(f"🎯 Edit API call with preservation prompt: {edit_prompt[:200]}...")
            
            # Build edit request (multipart form data)
            import requests
            
            endpoint = f"{self.api_base_url.rstrip('/')}/images/edits"
            
            headers = {
                "Authorization": f"Bearer {user_api_key}",
                "User-Agent": "OpenAI/1.101.0"
            }
            
            files = {
                'image': ('image.png', png_buffer, 'image/png')
            }
            
            data = {
                'model': 'gpt-image-1',
                'prompt': edit_prompt,
                'input_fidelity': 'high', 
                'quality': 'high',
                'n': 1,
                'output_format': 'png'
            }
            
            if progress_callback:
                await progress_callback("⚡ Processing with GPT Image-1 Edit API...")
            
            response = requests.post(endpoint, headers=headers, files=files, data=data, timeout=300)
            response.raise_for_status()
            
            api_response = response.json()
            logger.info("✅ BREAKTHROUGH SUCCESS: GPT Image-1 Edit API completed!")
            
            # STEP 5: Process response
            if progress_callback:
                await progress_callback("🎉 BREAKTHROUGH: Shape preserved! Processing result...")
            
            image_base64 = api_response['data'][0]['b64_json']
            
            # FIX: Save base64 to file like normal flow
            image_url = self._save_base64_to_file(image_base64)
            
            return ImageOutput(
                image_url=image_url,
                generation_id=str(uuid.uuid4()),
                seed=42,  # Default seed for Edit API
                revised_prompt=enhanced_brief,
                final_enhanced_prompt=enhanced_brief,
                model_used="gpt-image-1",
                provider_used="gpt-image-1-edit-breakthrough"
            )
            
        except Exception as e:
            logger.error(f"💥 BREAKTHROUGH Edit API failed: {e}")
            if progress_callback:
                await progress_callback(f"❌ Edit API Error: {str(e)}")
            raise Exception(f"GPT Image-1 Edit API failed: {str(e)}")
    
    def _build_edit_preservation_prompt(self, user_prompt: str, analysis_text: str = "") -> str:
        """
        🚀 BREAKTHROUGH: Build FULL DETAILED prompt for GPT Image-1 Edit API (32,000 chars max)
        
        CRITICAL: NO COMPRESSION! GPT Image-1 Edit API supports up to 32,000 characters
        - VISUAL INPUT advantage (AI can see the original image)
        - FULL preservation commands without compression
        - Complete professional photography specifications
        - Detailed technical requirements
        """
        
        # Extract FULL product details if available (NO TRUNCATION)
        product_context = ""
        if analysis_text:
            product_context = f"PRODUCT ANALYSIS CONTEXT:\n{analysis_text}\n\n"
        
        # BUILD COMPREHENSIVE PRESERVATION PROMPT (NO COMPRESSION)
        preservation_prompt = f"""CRITICAL VISUAL PRESERVATION PROTOCOL FOR GPT IMAGE-1 EDIT API:

You are analyzing the EXACT original product image that I have uploaded. Your task is PROFESSIONAL PHOTOGRAPHY ENHANCEMENT ONLY while maintaining 100% visual fidelity to the input image.

ABSOLUTE PRESERVATION MANDATES:
- MAINTAIN exact bottle/container shape, size, dimensions, and proportions from the input image
- PRESERVE all original colors EXACTLY as they appear in the input image - no color modifications
- KEEP all labels, text, graphics, logos, and branding elements IDENTICAL to input image
- DO NOT modify caps, lids, handles, spouts, or any physical product features
- MAINTAIN exact product positioning, orientation, and angle shown in input image
- PRESERVE product surface textures, materials, and finishes exactly as shown
- KEEP all product details like ridges, grooves, embossing, or raised elements unchanged
- MAINTAIN original lighting reflections and highlights on the product surface
- DO NOT redesign, reshape, recolor, or alter ANY aspect of the physical product
- NEVER ADD TEXT, LABELS, STICKERS, OR ANY ADDITIONAL ELEMENTS TO THE PRODUCT
- DO NOT SUGGEST OR APPLY ANY TEXTUAL ADDITIONS, BRAND MODIFICATIONS, OR EXTRA GRAPHICS ON THE PRODUCT

PHOTOGRAPHY ENHANCEMENT SPECIFICATIONS:
- Apply professional commercial studio lighting with soft, even illumination
- Use controlled shadow placement with proper fill lighting ratios
- Implement premium commercial photography aesthetics with clean composition
- Apply proper depth of field control with sharp product focus
- Use Hasselblad medium format camera quality standards
- Implement Phase One digital back image quality and dynamic range
- Add professional lighting patterns: Rembrandt, Loop, or Butterfly lighting for dimensionality
- Apply subtle professional color grading for luxury commercial photography look
- Create clean, professional background that complements without distracting
- Use world-class product photography techniques: proper exposure, contrast, and clarity
- Apply professional retouching for dust removal and surface perfection
- Implement commercial photography composition rules and visual hierarchy
- Add professional studio lighting setup with key light, fill light, and rim light
- Use controlled reflector placement for highlight and shadow management
- Apply professional product photography post-processing workflow

TECHNICAL PHOTOGRAPHY SPECIFICATIONS:
- Hasselblad H6D-100c medium format camera body
- Phase One XF IQ4 150MP digital back with 15-stop dynamic range
- Carl Zeiss Distagon T* 50mm f/3.5 lens for product photography
- Professional studio lighting: Profoto Pro-10 2400 AirTTL power pack
- Key light: Large octabox softbox 120cm with honeycomb grid
- Fill light: Silver beauty dish 55cm with 40-degree grid
- Rim light: Strip softbox 30x120cm for edge separation
- Background light: 7-inch reflector with 20-degree honeycomb grid
- Light stands: Avenger C-Stand with boom arm and sandbags
- Trigger system: Profoto Air Remote TTL-C wireless trigger
- Camera settings: ISO 64 base sensitivity, f/8.0 aperture, 1/125s shutter
- Color temperature: Daylight balanced 5500K with ±50K tolerance
- White balance: Custom grey card calibration for accurate color
- File format: 16-bit TIFF RAW files with Adobe RGB color space
- Focus: Single-point autofocus with focus peaking confirmation
- Metering: Spot metering on product highlight areas
- Exposure compensation: ±1/3 stop bracketing for HDR processing

LIGHTING SETUP DETAILS:
- Main key light positioned at 45-degree angle from camera axis
- Light height: 2 meters above subject with 30-degree downward angle
- Fill light at camera position with 2:1 lighting ratio to key light
- Rim light positioned opposite to key light for edge separation
- Background gradient from pure white center to light grey edges
- Light modifiers: Softboxes with inner and outer diffusion panels
- Power settings: Key light 100%, fill light 50%, rim light 75%
- Color gels: None - pure daylight balanced light sources only
- Reflector cards: White foam core boards for shadow fill control
- Flag cards: Black foam core for selective light blocking

POST-PROCESSING WORKFLOW:
- RAW file processing in Phase One Capture One Pro
- Lens correction: Distortion, vignetting, and chromatic aberration removal
- Color grading: Professional product photography color palette
- Gamma correction & tone consistency: Apply proper gamma correction (power 1/2.2) for consistent tone mapping across all image elements, maintain uniform luminance values and color temperature throughout composition, ensure balanced exposure with natural dynamic range distribution
- Contrast enhancement: Subtle S-curve for dimensional depth
- Sharpening: Output sharpening optimized for print and digital display
- Noise reduction: Minimal processing to preserve fine detail texture
- Color balance: Neutral whites with accurate product color reproduction
- Shadow/highlight recovery: Maintain full tonal range and detail
- Local adjustments: Selective masking for optimal product presentation
- Output format: 350 DPI high-resolution TIFF and JPEG files optimized for professional printing and commercial use

{product_context}

USER ENHANCEMENT REQUEST: {user_prompt}

FINAL CRITICAL PRESERVATION REMINDER:
This is PROFESSIONAL PRODUCT PHOTOGRAPHY ENHANCEMENT using the input image as your complete visual reference. The GPT Image-1 Edit API has full access to see the original uploaded image. Your role is to apply ONLY photographic improvements - lighting quality, composition refinement, background enhancement, and technical camera excellence - while preserving EVERY SINGLE DETAIL of the actual product exactly as shown in the input image. The product's shape, colors, textures, labels, and design elements must remain 100% visually identical to the input image. Any deviation from the original product appearance is strictly forbidden. This is documentary-style product photography with professional enhancement, not creative reinterpretation."""

        logger.info(f"🚀 BREAKTHROUGH: Full prompt built - {len(preservation_prompt)} characters (Max 32,000 allowed)")
        
        return preservation_prompt
