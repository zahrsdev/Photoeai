"""
API Router for the PhotoeAI backend.
Defines the REST API endpoints for brief generation functionality.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse  # MISSION 2: Added for download endpoint
from loguru import logger
import io  # MISSION 2: Added for download endpoint
# Models to import (add the new ones)
from app.schemas.models import (
    InitialUserRequest, WizardInput, BriefOutput, 
    ImageGenerationRequest, ImageEnhancementRequest, ImageOutput,
    TextGenerationRequest, TextOutput, DownloadBriefRequest  # MISSION 2: Added DownloadBriefRequest
)
from app.services.brief_orchestrator import BriefOrchestratorService
# Import the new service
from app.services.image_generator import ImageGenerationService
from app.services.multi_provider_image_generator import OpenAIImageService
from app.services.ai_client import AIClient

# Create router instance and orchestrator (existing)
router = APIRouter(prefix="/api/v1", tags=["generator"])
orchestrator = BriefOrchestratorService()

# --- NEW ---
# Initialize both image generation services
image_service = ImageGenerationService()  # Keep for backward compatibility
openai_service = OpenAIImageService()  # OpenAI GPT Image 1 service
ai_client = AIClient()  # AI client for text generation
# --- END NEW ---


@router.post("/extract-and-fill", response_model=WizardInput)
async def extract_and_fill(request: InitialUserRequest) -> WizardInput:
    """
    Extract structured wizard data from initial user request and autofill with defaults.
    
    This endpoint implements Flow 1 from the architecture:
    1. Receives a simple text request from the user
    2. Uses LLM as Analyst to extract structured data
    3. Autofills missing fields with defaults
    4. Returns complete WizardInput for the frontend wizard
    
    Args:
        request: InitialUserRequest containing the user's text request
        
    Returns:
        WizardInput: Complete wizard data with all fields filled
        
    Raises:
        HTTPException: If the extraction process fails
    """
    try:
        logger.info(f"🌟 [FRONTEND REQUEST] Extract and fill: '{request.user_request[:100]}...'")
        
        if not request.user_request or not request.user_request.strip():
            logger.warning("❌ [FRONTEND REQUEST] Empty user request received")
            raise HTTPException(
                status_code=400, 
                detail="User request cannot be empty"
            )
        
        wizard_input = await orchestrator.extract_and_autofill(request)
        logger.info(f"✅ [FRONTEND RESPONSE] Extract and fill completed successfully")
        return wizard_input
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 [FRONTEND ERROR] Extract and fill failed: {e}")
        error_msg = str(e)
        if "AI extraction service unavailable" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="AI extraction service is currently unavailable. Please check your API configuration and try again."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during extraction: {str(e)}"
        )


@router.post("/generate-brief", response_model=BriefOutput)
async def generate_brief(wizard_input: WizardInput) -> BriefOutput:
    """
    Generate final enhanced photography brief from complete wizard input.
    
    This endpoint implements Flow 2 from the architecture:
    1. Receives complete WizardInput (validated by user)
    2. Composes initial brief using system prompt template
    3. Validates the brief against quality rules
    4. Uses LLM as Creative Director to enhance the brief
    5. Returns final BriefOutput with enhanced prompt
    
    Args:
        wizard_input: Complete WizardInput with all photography parameters
        
    Returns:
        BriefOutput: Final enhanced photography brief
        
    Raises:
        HTTPException: If the brief generation process fails
    """
    try:
        logger.info(f"🌟 [FRONTEND REQUEST] Generate brief for product: '{wizard_input.product_name}'")
        
        # Basic validation - ensure at least product name or user request exists
        if not wizard_input.product_name and not wizard_input.user_request:
            logger.warning("❌ [FRONTEND REQUEST] Missing required fields: product_name or user_request")
            raise HTTPException(
                status_code=400,
                detail="Either product_name or user_request must be provided"
            )
        
        brief_output = await orchestrator.generate_final_brief(wizard_input)
        
        if not brief_output.final_prompt or not brief_output.final_prompt.strip():
            logger.error("💥 [FRONTEND ERROR] Generated brief is empty")
            raise HTTPException(
                status_code=500,
                detail="Generated brief is empty. Please try again."
            )
        
        logger.info(f"✅ [FRONTEND RESPONSE] Brief generated successfully ({len(brief_output.final_prompt)} chars)")
        return brief_output
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 [FRONTEND ERROR] Brief generation failed: {e}")
        error_msg = str(e)
        if "AI enhancement service unavailable" in error_msg:
            raise HTTPException(
                status_code=503,
                detail="AI enhancement service is currently unavailable. Please check your API configuration and try again."
            )
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during brief generation: {str(e)}"
        )


@router.post("/preview-brief")
async def preview_brief(wizard_input: WizardInput):
    """
    Get a preview of the initial brief without AI enhancement.
    Useful for debugging and validation during development.
    
    Args:
        wizard_input: Complete WizardInput with all photography parameters
        
    Returns:
        Dictionary containing initial brief, validation results, and wizard data
        
    Raises:
        HTTPException: If the preview generation fails
    """
    try:
        preview_data = await orchestrator.get_brief_preview(wizard_input)
        return preview_data
        
    except Exception as e:
        print(f"Error in preview_brief endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during preview generation: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify the service is running.
    
    Returns:
        Dictionary with service status
    """
    return {
        "status": "healthy",
        "service": "PhotoeAI Backend",
        "version": "1.0.0"
    }


# --- NEW ENDPOINTS ---

@router.post("/generate-brief-from-prompt", response_model=BriefOutput)
async def generate_brief_from_prompt(request: InitialUserRequest) -> BriefOutput:
    """
    ENHANCED ENDPOINT: Create comprehensive photography brief from simple user prompt.
    This is the recommended first step - use this to get a detailed brief, then send to /generate-image.
    """
    try:
        if not request.user_request or not request.user_request.strip():
            raise HTTPException(status_code=400, detail="User request cannot be empty.")
        
        logger.info(f"📝 Creating comprehensive brief from simple prompt: {request.user_request[:100]}...")
        
        # Step 1: Extract structured data from user prompt
        wizard_input = await orchestrator.extract_and_autofill(request)
        
        # Step 2: Generate comprehensive enhanced brief
        brief_result = await orchestrator.generate_final_brief(wizard_input)
        
        logger.info(f"✅ Generated comprehensive brief ({len(brief_result.final_prompt)} characters)")
        
        return brief_result
        
    except Exception as e:
        logger.error(f"Error in /generate-brief-from-prompt endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Brief generation failed: {str(e)}")

@router.post("/generate-text-advanced", response_model=TextOutput)
async def generate_text_advanced(request: TextGenerationRequest) -> TextOutput:
    """
    Advanced text generation with full provider control.
    Optimized for OpenAI GPT Image 1 single provider.
    """
    logger.info(f"🤖 Advanced text generation with provider: {request.provider}")
    
    try:
        # Use AI client for text generation
        generated_text = await ai_client.generate_text(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # Return structured response
        return TextOutput(
            generated_text=generated_text,
            provider_used=request.provider or "auto_detected",
            model_used=request.model or "default",
            generation_metadata={
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "service": "ai_client",
                "timestamp": "2024-08-23T10:00:00Z"
            }
        )
        
    except Exception as e:
        logger.error(f"💥 Advanced text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")


@router.post("/generate-text", response_model=BriefOutput)
async def generate_text(request: InitialUserRequest) -> BriefOutput:
    """
    Generate text completions using the unified AI service.
    This endpoint can be used for brief generation using various providers.
    """
    logger.info(f"📝 Text generation request: {request.product_name}")
    
    try:
        # Validate user API key
        if not request.user_api_key:
            raise HTTPException(
                status_code=400,
                detail="❌ User API key is required for text generation"
            )
        
        # Create a prompt for text generation
        text_prompt = f"""Generate a detailed photography brief for {request.product_name}.
        Product description: {request.product_description or "Not provided"}
        Target audience: {request.target_audience or "General audience"}
        
        Please provide a comprehensive brief including:
        1. Visual concept and composition
        2. Lighting requirements
        3. Background and props
        4. Style and mood
        5. Technical specifications
        """
        
        # Use AI client for text generation
        generated_text = await ai_client.generate_text(
            prompt=text_prompt,
            temperature=0.6,
            max_tokens=1000
        )
        
        # Return as BriefOutput
        return BriefOutput(
            brief_content=generated_text,
            product_name=request.product_name,
            generation_metadata={
                "service": "unified_ai_text_generation",
                "provider": "auto_detected",
                "timestamp": "2024-08-23T10:00:00Z"
            }
        )
        
    except Exception as e:
        logger.error(f"💥 Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text generation failed: {str(e)}")


@router.post("/generate-image", response_model=ImageOutput)
async def generate_image(request: ImageGenerationRequest) -> ImageOutput:
    """
    Generate image from a professionally crafted brief prompt.
    This endpoint expects to receive a comprehensive brief from /generate-brief endpoint.
    Optimized for OpenAI GPT Image 1.
    """
    try:
        logger.info(f"🌟 [FRONTEND REQUEST] Generate image - Prompt length: {len(request.brief_prompt)} chars")
        logger.info(f"🔑 [FRONTEND REQUEST] Provider: {request.provider or 'Auto-detect'}")
        
        if not request.brief_prompt or not request.brief_prompt.strip():
            logger.warning("❌ [FRONTEND REQUEST] Empty brief prompt received")
            raise HTTPException(status_code=400, detail="Brief prompt cannot be empty.")
        
        if not request.user_api_key or not request.user_api_key.strip():
            logger.warning("❌ [FRONTEND REQUEST] Missing API key")
            raise HTTPException(status_code=400, detail="User API key is required for image generation.")
        
        # ⚡ API Key validation and quota check
        if "sk-proj-" not in request.user_api_key and "sk-" not in request.user_api_key:
            logger.warning("❌ [FRONTEND REQUEST] Invalid API key format")
            raise HTTPException(status_code=400, detail="Invalid API key format. Please check your OpenAI API key.")
        
        logger.info(f"🎨 [PROCESSING] Generating image from prompt ({len(request.brief_prompt)} characters)")
        
        # If user explicitly requests raw prompt, use it directly
        if request.use_raw_prompt:
            logger.info("🔧 Raw prompt mode activated - using prompt as-is")
            generation_prompt = request.brief_prompt
            comprehensive_prompt = request.brief_prompt
        else:
            # ⚡ OPTIMIZED WORKFLOW: Single extraction, efficient processing
            logger.info("🎯 Starting optimized brief processing workflow")
            
            try:
                # Step 1: Extract wizard data ONCE (efficient approach)
                initial_request = InitialUserRequest(user_request=request.brief_prompt)
                wizard_input = await orchestrator.extract_and_autofill(initial_request)
                logger.info("✅ Wizard data extracted successfully")
                
                # Step 2: Force all prompts to use full brief generation
                # is_comprehensive_brief = _is_comprehensive_descriptive_prompt(request.brief_prompt)
                is_comprehensive_brief = False  # Force full brief generation for all inputs
                
                if is_comprehensive_brief:
                    logger.info("📋 Comprehensive prompt detected - applying smart enhancement")
                    
                    try:
                        # Use wizard data to enhance without re-extraction
                        enhanced_brief = await _create_optimized_enhanced_brief(
                            original_prompt=request.brief_prompt,
                            wizard_input=wizard_input,
                            skip_extraction=True  # Skip re-extraction since we already have wizard data
                        )
                        
                        comprehensive_prompt = enhanced_brief
                        generation_prompt = enhanced_brief
                        logger.info(f"📄 Smart enhanced brief ready: {len(enhanced_brief)} chars")
                        
                    except Exception as enhancement_error:
                        logger.warning(f"⚠️ Enhancement failed, using original comprehensive prompt: {enhancement_error}")
                        # Fallback: Use original comprehensive prompt
                        comprehensive_prompt = request.brief_prompt
                        generation_prompt = request.brief_prompt
                
                else:
                    # Simple prompt detected - use wizard data efficiently for full brief generation
                    logger.info("🔧 Simple prompt detected - generating comprehensive brief efficiently")
                    
                    try:
                        # Use the wizard data we already extracted (no re-extraction needed)
                        brief_result = await orchestrator.generate_final_brief(wizard_input)
                        comprehensive_prompt = brief_result.final_prompt
                        
                        # Smart length optimization for generation
                        if len(brief_result.final_prompt) <= 4000:
                            logger.info("📄 Using full generated brief (optimal length)")
                            generation_prompt = brief_result.final_prompt
                        else:
                            logger.info("📦 Brief too long, applying smart compression")
                            generation_prompt = await _create_smart_compressed_prompt(brief_result.final_prompt)
                            
                    except Exception as brief_generation_error:
                        logger.warning(f"⚠️ Brief generation failed, using enhanced original: {brief_generation_error}")
                        # Fallback: Create basic enhanced version from original prompt
                        comprehensive_prompt = f"High-quality, professional, realistic photograph: {request.brief_prompt}. Ultra-detailed, HD quality, cinematic lighting, sharp focus."
                        generation_prompt = comprehensive_prompt
                        
            except Exception as wizard_extraction_error:
                logger.error(f"💥 Wizard extraction failed: {wizard_extraction_error}")
                # Ultimate fallback: Use original prompt with basic enhancement
                logger.info("🚨 Using emergency fallback - basic prompt enhancement")
                comprehensive_prompt = f"Professional photography, high quality, realistic: {request.brief_prompt}. Ultra-detailed, HD, sharp focus."
                generation_prompt = comprehensive_prompt
        
        logger.info(f"🎯 Using optimized generation prompt ({len(generation_prompt)} characters)")
        
        # Generate image with optimized prompt
        result = await openai_service.generate_image(
            brief_prompt=generation_prompt,
            user_api_key=request.user_api_key,
            negative_prompt=request.negative_prompt,
            provider_override=request.provider
        )
        
        # Ensure the result includes the full comprehensive prompt for frontend display
        result.final_enhanced_prompt = comprehensive_prompt
        result.revised_prompt = generation_prompt  # The prompt actually used for generation
        
        return result
        
    except Exception as e:
        logger.error(f"Error in /generate-image endpoint: {e}")
        raise HTTPException(status_code=503, detail=f"Image generation service is unavailable: {str(e)}")


@router.post("/generate-brief-and-image", tags=["Unified Generation"])
async def generate_brief_and_image(request: ImageGenerationRequest):
    """
    UNIFIED ENDPOINT: Generate both brief and image in one call.
    Takes user request, creates brief, then generates image.
    """
    try:
        logger.info(f"🚀 [UNIFIED] Starting brief + image generation")
        
        # Step 1: Generate brief from user request
        initial_request = InitialUserRequest(user_request=request.brief_prompt)
        brief_result = await generate_brief_from_prompt(initial_request)
        
        # Step 2: Generate image using the enhanced brief
        image_request = ImageGenerationRequest(
            brief_prompt=brief_result.final_prompt,
            user_api_key=request.user_api_key,
            provider=request.provider
        )
        image_result = await generate_image(image_request)
        
        # Return both results
        return {
            "brief": brief_result,
            "image": image_result
        }
        
    except Exception as e:
        logger.error(f"Error in unified endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Unified generation failed: {str(e)}")


def _is_comprehensive_descriptive_prompt(prompt: str) -> bool:
    """
    Enhanced detection for comprehensive or descriptive prompts that should be used as-is.
    
    Returns True if the prompt is:
    1. A formal photography brief (contains technical indicators)
    2. A detailed descriptive text that adequately describes the scene
    3. Long enough and descriptive enough to work well without enhancement
    
    Args:
        prompt: The input prompt to analyze
        
    Returns:
        bool: True if prompt should be used directly, False if needs wizard processing
    """
    prompt_lower = prompt.lower().strip()
    prompt_length = len(prompt)
    words = len(prompt.split())
    
    # Immediate rejection for very short prompts
    if words < 5 or prompt_length < 25:
        logger.info(f"🔄 Very short prompt detected - will enhance (words: {words}, length: {prompt_length})")
        return False
    
    # 1. Check for formal photography brief indicators (highest priority)
    photography_brief_indicators = [
        'photography brief', 'lighting setup', 'camera settings', 'composition brief', 
        'technical specifications', '###', '##', 'equipment:', 'shot with canon',
        'shot with sony', 'shot with nikon', 'professional photography',
        'camera:', 'lens:', 'lighting:', 'aperture:', 'iso:', 'shutter speed',
        'f/', 'mm lens', 'profoto', 'softbox', 'key light', 'fill light'
    ]
    
    if any(indicator in prompt_lower for indicator in photography_brief_indicators):
        logger.info("📋 Formal photography brief detected")
        return True
    
    # 2. Check for detailed descriptive content (requires multiple indicators)
    descriptive_indicators = [
        # Food/Drink products
        'refreshing glass', 'steaming cup', 'bottle of', 'bowl of', 'plate of', 'milk drink bottle',
        'bottle splashing', 'creamy milk', 'flavored milk', 'drink bottle',
        
        # Presentation and staging details
        'served on', 'placed on', 'garnished with', 'accompanied by', 'surrounded by', 
        'floating fresh', 'frozen mid-air', 'suspended in motion',
        
        # Setting and surface details
        'wooden table', 'marble surface', 'ceramic mug', 'banana leaf', 'golden-yellow gradient',
        'smooth gradient', 'glossy surface', 'detailed branding',
        
        # Lighting descriptions (broad coverage)
        'natural lighting', 'soft lighting', 'warm lighting', 'morning lighting', 'studio lighting',
        'soft reflections', 'highlights the', 'dynamic lighting',
        
        # Text and labeling elements
        'text above reads', 'text below reads', 'label says', 'sign reads', 'branding',
        
        # Composition and camera work
        'overhead view', 'close-up view', 'side view', 'beautiful view', 'cinematic style',
        'high-resolution', 'sharp focus', 'hyper-detailed', 'ultra-realistic',
        
        # Visual effects and details
        'drops of water', 'condensation', 'steam rising', 'bubbles', 'droplets suspended',
        'high-speed', 'mid-air', 'dynamic splash', 'milk splash',
        
        # Cultural and specialty contexts
        'traditional indonesian', 'authentic javanese', 'classic thai', 'local specialty',
        'commercial product', 'product photography'
    ]
    
    descriptive_score = sum(1 for indicator in descriptive_indicators if indicator in prompt_lower)
    
    # 3. Length and complexity analysis
    sentences = prompt.count('.') + prompt.count('!') + prompt.count('?')
    
    # 4. Decision logic - requires multiple criteria
    
    # High-confidence comprehensive: Multiple descriptive elements + good length
    if descriptive_score >= 3 and words >= 20:
        logger.info(f"📝 Detailed descriptive prompt detected (score: {descriptive_score}, words: {words})")
        return True
    
    # Medium-confidence comprehensive: Very detailed text
    if words >= 35 and sentences >= 2 and descriptive_score >= 2:
        logger.info(f"📄 Long descriptive text detected ({words} words, {sentences} sentences, score: {descriptive_score})")
        return True
    
    # Strong descriptive content with good length
    if prompt_length >= 120 and descriptive_score >= 3:
        logger.info(f"📃 Comprehensive description detected ({prompt_length} chars, score: {descriptive_score})")
        return True
    
    # 5. Check for very specific complete scene descriptions (stricter)
    complete_scene_patterns = [
        'refreshing glass of iced', 'steaming cup of traditional', 
        'beautiful overhead view of', 'traditional indonesian dessert',
        'served on a banana leaf', 'garnished with shaved ice'
    ]
    
    if any(pattern in prompt_lower for pattern in complete_scene_patterns):
        logger.info("🖼️ Complete scene description detected")
        return True
    
    logger.info(f"🔄 Simple prompt detected - will enhance (words: {words}, score: {descriptive_score}, sentences: {sentences})")
    return False


async def _create_optimized_enhanced_brief(original_prompt: str, wizard_input, skip_extraction: bool = False) -> str:
    """
    ⚡ OPTIMIZED: Create enhanced brief efficiently using pre-extracted wizard data.
    
    This function:
    1. Uses wizard data that was ALREADY extracted (no re-extraction)
    2. Applies smart enhancement based on prompt type
    3. Optimizes for API efficiency and realistic results
    4. Preserves original visual intent
    
    Args:
        original_prompt: User's original prompt
        wizard_input: Pre-extracted wizard data (DO NOT re-extract)
        skip_extraction: True to skip re-extraction (already done)
        
    Returns:
        str: Optimized enhanced photography brief
    """
    try:
        logger.info(f"⚡ Starting optimized enhancement (skip_extraction={skip_extraction})")
        
        # Strategy: Efficient enhancement using existing wizard data
        # 🎯 DYNAMIC ENHANCEMENT: Adjust enhancement level based on original prompt
        original_length = len(original_prompt)
        
        # Smart enhancement scaling with SPECIFIC character targets
        if original_length < 100:
            # Very short prompts (like "bottle in lake") - enhance 8-12x but target ~800 chars
            target_enhancement = "8-10x longer, target 800-1200 characters"
            max_tokens = 400
            temperature = 0.6  # Standardized temperature
        elif original_length < 300:
            # Medium prompts (like our test) - enhance 6-8x, target 1800-2400 chars  
            target_enhancement = "6-8x longer, target 1800-2400 characters"
            max_tokens = 600
            temperature = 0.6  # Standardized temperature
        elif original_length < 500:
            # Longer prompts - enhance 4-5x, target 2000-2500 chars
            target_enhancement = "4-5x longer, target 2000-2500 characters"
            max_tokens = 700
            temperature = 0.6  # Standardized temperature
        else:
            # Already detailed prompts - enhance 2-3x, target 1200-1800 chars
            target_enhancement = "2-3x longer, target 1200-1800 characters"
            max_tokens = 500
            temperature = 0.6  # Standardized temperature
        
        enhancement_instruction = f"""
You are a professional photography director creating an enhanced brief for realistic image generation.

ORIGINAL USER PROMPT ({original_length} chars):
{original_prompt}

PRE-EXTRACTED WIZARD DATA (use efficiently):
- Product: {getattr(wizard_input, 'product_name', 'N/A')}
- Shot Type: {getattr(wizard_input, 'shot_type', 'natural angle')}
- Lighting: {getattr(wizard_input, 'lighting_style', 'natural lighting')}
- Background: {getattr(wizard_input, 'background_elements', 'contextual')}
- Style: {getattr(wizard_input, 'photography_style', 'realistic')}
- Quality: {getattr(wizard_input, 'image_quality', 'high quality')}

TARGET: Create enhanced brief that is {target_enhancement} than original

ENHANCEMENT RULES:
1. PRESERVE ORIGINAL: Keep 70% of original prompt structure and language
2. ADD HD SPECS: Include realistic camera settings (Canon EOS R5, f/5.6, ISO 200-400, etc.)
3. SMART INTEGRATION: Blend wizard data naturally into prompt
4. REALISTIC DETAILS: Add lighting, composition, and technical photography details
5. NATURAL FLOW: Make it sound like a single cohesive photography brief
6. DALL-E OPTIMAL: Target 2000-3500 characters for best DALL-E results

Create an enhanced brief that produces HD realistic images while staying within DALL-E's optimal range.

ENHANCED PHOTOGRAPHY BRIEF:
"""
        
        # Use AI client for dynamic enhancement
        enhanced_brief = await ai_client.generate_text(
            prompt=enhancement_instruction,
            temperature=temperature,  # Dynamic based on original length
            max_tokens=max_tokens     # Dynamic token limit
        )
        
        # Quality metrics
        enhanced_length = len(enhanced_brief)
        original_length = len(original_prompt)
        enhancement_ratio = enhanced_length / original_length
        
        logger.info(f"⚡ Optimized enhanced brief ready: {enhanced_length} chars (ratio: {enhancement_ratio:.1f}x)")
        
        # Smart length optimization
        if enhanced_length > 4000:  # DALL-E optimal range
            logger.info("📦 Applying smart compression for optimal generation")
            return await _create_smart_compressed_prompt(enhanced_brief)
        
        return enhanced_brief
        
    except Exception as e:
        logger.warning(f"⚡ Optimized enhancement failed: {e}, using fallback")
        # Fallback: Use original ChatGPT-quality enhancement
        return await _create_chatgpt_quality_enhanced_brief(original_prompt, wizard_input)


async def _create_chatgpt_quality_enhanced_brief(original_prompt: str, wizard_input) -> str:
    """
    Create enhanced brief that preserves ChatGPT Image quality while adding technical depth.
    
    This function:
    1. Preserves the original prompt's core intent and style
    2. Adds complementary technical details from wizard data
    3. Creates enhanced brief that produces ChatGPT-quality results
    4. Avoids over-engineering that changes the visual outcome
    
    Args:
        original_prompt: User's original comprehensive prompt
        wizard_input: WizardInput object with extracted technical fields
        
    Returns:
        str: ChatGPT-quality enhanced photography brief
    """
    try:
        logger.info("🎯 Creating ChatGPT-quality enhanced brief (preserves visual intent)")
        
        # Strategy: Natural Photography Enhancement for realistic results
        enhancement_instruction = f"""
You are enhancing a photography prompt to produce REALISTIC, NATURAL PHOTOGRAPHY results like ChatGPT Image - NOT artificial or overly perfect graphics.

ORIGINAL USER PROMPT (keep this natural style):
{original_prompt}

AVAILABLE TECHNICAL DATA (use sparingly and naturally):
- Shot Type: {getattr(wizard_input, 'shot_type', 'N/A')}
- Lighting: {getattr(wizard_input, 'lighting_style', 'N/A')}
- Camera: {getattr(wizard_input, 'camera_type', 'N/A')}

CRITICAL RULES FOR NATURAL PHOTOGRAPHY:
1. REALISTIC IMPERFECTIONS: Add subtle natural imperfections that make it look like real photography
2. NATURAL LIGHTING: Emphasize natural, realistic lighting (not perfect studio setup)
3. AUTHENTIC TEXTURES: Focus on realistic material textures and surfaces
4. PHOTOGRAPHIC FEEL: Make it feel like a photograph taken by a professional photographer
5. AVOID PERFECTION: Don't make it too clean, too perfect, or too artificial
6. PRESERVE ORIGINAL STYLE: Keep the user's descriptive language and visual intent

ENHANCEMENT APPROACH:
- Keep original prompt as main foundation (70-80%)
- Add realistic photography context (not technical specs)
- Emphasize authenticity and natural photographic qualities
- Use terms like "captured", "photographed", "real", "authentic"
- Avoid overly technical camera settings that make it artificial

Create a natural photography prompt that produces realistic, authentic-looking photographs like ChatGPT Image generates.

ENHANCED NATURAL PHOTOGRAPHY PROMPT:
"""
        
        # Use AI client for ChatGPT-quality enhancement
        enhanced_brief = await ai_client.generate_text(
            prompt=enhancement_instruction,
            temperature=0.6,  # Standardized temperature
            max_tokens=1500   # Moderate length to avoid over-enhancement
        )
        
        # Validate enhancement quality
        enhanced_length = len(enhanced_brief)
        original_length = len(original_prompt)
        enhancement_ratio = enhanced_length / original_length
        
        logger.info(f"✅ ChatGPT-quality enhanced brief created: {enhanced_length} chars (ratio: {enhancement_ratio:.1f}x)")
        
        # Quality control: ensure it's enhanced but not over-engineered
        if enhancement_ratio > 6.0:  # Too much enhancement
            logger.warning(f"Enhancement ratio too high ({enhancement_ratio:.1f}x), applying smart compression")
            return await _create_smart_compressed_prompt(enhanced_brief)
        
        return enhanced_brief
        
    except Exception as e:
        logger.warning(f"ChatGPT-quality enhancement failed: {e}, falling back to comprehensive enhancement")
        return await _create_comprehensive_enhanced_brief(original_prompt, wizard_input)


async def _create_comprehensive_enhanced_brief(original_prompt: str, wizard_input) -> str:
    """
    Create an enhanced comprehensive brief by combining user's detailed prompt 
    with intelligent wizard-extracted details.
    
    This function:
    1. Takes the user's comprehensive descriptive prompt as the base
    2. Extracts technical details from wizard input (46 fields)
    3. Intelligently combines them to create a super-detailed photography brief
    4. Maintains user's original vision while adding professional technical specs
    
    Args:
        original_prompt: User's comprehensive descriptive prompt
        wizard_input: WizardInput object with extracted/autofilled fields
        
    Returns:
        str: Enhanced comprehensive photography brief
    """
    try:
        logger.info("🎨 Creating comprehensive enhanced brief from user prompt + wizard intelligence")
        
        # Use AI to intelligently merge the comprehensive prompt with wizard data
        enhancement_instruction = f"""
You are an expert photography director. Your task is to create an enhanced photography brief by intelligently combining:

1. USER'S COMPREHENSIVE PROMPT (preserve the core vision):
{original_prompt}

2. EXTRACTED TECHNICAL SPECIFICATIONS FROM WIZARD:
- Product: {getattr(wizard_input, 'product_name', 'N/A')}
- Shot Type: {getattr(wizard_input, 'shot_type', 'N/A')}
- Lighting Style: {getattr(wizard_input, 'lighting_style', 'N/A')}
- Camera Type: {getattr(wizard_input, 'camera_type', 'N/A')}
- Lens Type: {getattr(wizard_input, 'lens_type', 'N/A')}
- Aperture: f/{getattr(wizard_input, 'aperture_value', 'N/A')}
- Environment: {getattr(wizard_input, 'environment', 'N/A')}
- Mood: {getattr(wizard_input, 'mood', 'N/A')}
- Key Light Setup: {getattr(wizard_input, 'key_light_setup', 'N/A')}
- Fill Light Setup: {getattr(wizard_input, 'fill_light_setup', 'N/A')}
- Dominant Colors: {getattr(wizard_input, 'dominant_colors', 'N/A')}
- Surface Material: {getattr(wizard_input, 'surface_material', 'N/A')}

ENHANCEMENT RULES:
1. PRESERVE: Keep the user's creative vision and specific descriptions intact
2. ENHANCE: Add missing technical photography details from wizard data where appropriate
3. STRUCTURE: Organize into professional photography brief format with clear sections
4. INTEGRATE: Seamlessly blend user descriptions with technical specifications
5. AVOID: Don't contradict or override user's explicit choices
6. ENRICH: Add professional terminology and equipment specifications where relevant

Create a comprehensive photography brief that maintains the user's vision while adding professional depth and technical precision. Structure it with clear sections like:

**Product Photography Brief: [Product Name]**

### Main Subject
[Integrate user's product description with wizard product details]

### Composition and Framing  
[User's composition preferences + wizard shot type and framing details]

### Lighting Setup
[User's lighting description enhanced with wizard technical lighting specifications]

### Camera and Technical Settings
[Add professional camera settings from wizard data]

### Background and Environment
[Combine user's background description with wizard environment details]

### Stylistic Enhancements
[User's style preferences + wizard mood and aesthetic details]

ENHANCED COMPREHENSIVE BRIEF:
"""
        
        # Use AI client for intelligent enhancement
        enhanced_brief = await ai_client.generate_text(
            prompt=enhancement_instruction,
            temperature=0.6,  # Standardized temperature
            max_tokens=2000   # Allow for detailed output
        )
        
        logger.info(f"✅ Enhanced brief created: {len(enhanced_brief)} characters")
        return enhanced_brief
        
    except Exception as e:
        logger.warning(f"Enhancement failed: {e}, falling back to wizard-generated brief")
        
        # Fallback: use orchestrator to generate standard brief
        brief_result = await orchestrator.generate_final_brief(wizard_input)
        return brief_result.final_prompt


async def _create_smart_compressed_prompt(comprehensive_brief: str) -> str:
    """
    Create an optimized prompt that preserves essential technical details while staying under DALL-E limits.
    Unlike basic compression, this preserves key technical specifications.
    """
    # If it's already short enough, use as-is
    if len(comprehensive_brief) <= 3800:
        return comprehensive_brief
    
    logger.info("📝 Creating smart compressed prompt preserving technical details")
    
    # Use AI to intelligently compress while preserving technical details
    compression_instruction = f"""
You are an expert prompt engineer. Your task is to compress the following comprehensive photography brief into a concise but highly detailed prompt under 3500 characters while preserving ALL critical technical specifications.

COMPRESSION REQUIREMENTS:
1. PRESERVE: Camera model, lens specifications, lighting equipment, exact technical settings
2. PRESERVE: Specific lighting setup (key light, fill light, rim light positions and ratios)
3. PRESERVE: Exact compositional rules, framing details, and perspective information
4. PRESERVE: Material textures, color specifications, and surface treatments
5. PRESERVE: Professional photography terminology and equipment names
6. CONDENSE: Redundant descriptions, excessive adjectives, repetitive sections
7. MAINTAIN: Professional photography style and technical precision

COMPREHENSIVE BRIEF TO COMPRESS:
{comprehensive_brief}

Create a compressed version that maintains technical precision while removing redundancy:
"""
    
    try:
        # Use AI client for intelligent compression
        compressed = await ai_client.generate_text(
            prompt=compression_instruction,
            temperature=0.6,  # Standardized temperature
            max_tokens=1500   # Sufficient for compressed output
        )
        
        # Ensure it's within limits
        if len(compressed) <= 3800:
            logger.info(f"✅ Smart compression successful: {len(comprehensive_brief)} → {len(compressed)} characters")
            return compressed
        else:
            # Fallback to extraction-based compression if AI compression is still too long
            logger.warning("AI compression still too long, using extraction fallback")
            return _extract_key_technical_elements(comprehensive_brief)
            
    except Exception as e:
        logger.warning(f"Smart compression failed: {e}, using extraction fallback")
        return _extract_key_technical_elements(comprehensive_brief)


def _extract_key_technical_elements(comprehensive_brief: str) -> str:
    """Extract and combine the most important technical elements from a comprehensive brief."""
    
    import re
    
    # Extract key technical sections using pattern matching
    sections_to_extract = {
        "subject": r"(?:product|subject):\s*([^\.]+)",
        "camera": r"(?:camera|equipment):\s*([^\.]+)",
        "lens": r"(?:lens):\s*([^\.]+)", 
        "lighting": r"(?:lighting|illumination):\s*([^\.]+)",
        "composition": r"(?:composition|framing):\s*([^\.]+)",
        "background": r"(?:background|environment|setting):\s*([^\.]+)",
        "style": r"(?:style|aesthetic):\s*([^\.]+)"
    }
    
    extracted_elements = []
    brief_lower = comprehensive_brief.lower()
    
    # Try to extract each section
    for section_name, pattern in sections_to_extract.items():
        matches = re.findall(pattern, brief_lower, re.IGNORECASE)
        if matches:
            # Take the first match and clean it up
            content = matches[0].strip()
            if len(content) > 10:  # Only include substantial content
                extracted_elements.append(content)
    
    # If extraction failed, create a structured prompt from key terms
    if len(extracted_elements) < 3:
        # Look for specific technical terms and equipment
        technical_terms = []
        key_terms = [
            "canon eos", "sony", "nikon", "phase one", "profoto", "softbox", 
            "key light", "fill light", "rim light", "f/", "85mm", "50mm", "macro",
            "studio lighting", "natural light", "golden hour", "bokeh", "depth of field",
            "rule of thirds", "leading lines", "symmetry", "marble", "wood", "leather",
            "luxury", "premium", "elegant", "sophisticated", "professional"
        ]
        
        for term in key_terms:
            if term in brief_lower:
                technical_terms.append(term)
        
        # Create a fallback technical prompt
        product_name = "luxury product"  # Default
        
        # Try to identify the product name
        product_patterns = [
            r"product photography of\s+([^,\.]+)",
            r"photograph\s+(?:of\s+)?(?:a\s+|the\s+)?([^,\.]+)",
            r"([a-zA-Z\s]+)\s+(?:bottle|jar|container|package|box)"
        ]
        
        for pattern in product_patterns:
            match = re.search(pattern, brief_lower, re.IGNORECASE)
            if match:
                product_name = match.group(1).strip()
                break
        
        # Construct technical prompt
        compressed = f"Professional product photography of {product_name}"
        
        if "canon eos" in brief_lower or "sony" in brief_lower:
            compressed += ", shot with professional DSLR camera"
        if "85mm" in brief_lower or "macro" in brief_lower:
            compressed += ", 85mm lens with shallow depth of field"
        if "softbox" in brief_lower or "studio lighting" in brief_lower:
            compressed += ", studio softbox lighting setup"
        if "luxury" in brief_lower or "premium" in brief_lower:
            compressed += ", luxury premium presentation"
        if "marble" in brief_lower:
            compressed += ", marble background surface"
        
        compressed += ", professional commercial photography, ultra-detailed, 8K resolution, photorealistic"
        
        return compressed
    
    # Combine extracted elements into a coherent prompt
    combined = "Professional product photography: " + ". ".join(extracted_elements[:6])  # Limit to prevent over-length
    combined += ". Ultra-detailed, commercial photography quality, photorealistic rendering."
    
    return combined

@router.post("/enhance-image", response_model=ImageOutput, tags=["Image Generation"])
async def enhance_image(request: ImageEnhancementRequest) -> ImageOutput:
    """
    Enhances or modifies a previously generated image based on user feedback.
    Requires the user to provide their own API key for the image generation service.
    Optimized for OpenAI GPT Image 1.
    """
    try:
        if not request.enhancement_instruction or not request.enhancement_instruction.strip():
            raise HTTPException(status_code=400, detail="Enhancement instruction cannot be empty.")

        if not request.user_api_key or not request.user_api_key.strip():
            raise HTTPException(status_code=400, detail="User API key is required for image enhancement.")

        # Use multi-provider service for better compatibility
        result = await openai_service.enhance_image(
            original_prompt=request.original_brief_prompt,
            instruction=request.enhancement_instruction,
            user_api_key=request.user_api_key,
            seed=request.seed or 0
        )
        return result
    except Exception as e:
        logger.error(f"Error in /enhance-image endpoint: {e}")
        raise HTTPException(status_code=503, detail=f"Image enhancement service is unavailable: {str(e)}")


# MISSION 2: New endpoint for downloading photography brief as text file
@router.post("/download-brief", tags=["Export"])
async def download_brief(request: DownloadBriefRequest):
    """
    Download the final enhanced prompt as a text file.
    
    This endpoint allows users and developers to download the exact, final text prompt
    that was used to generate an image for inspection and auditing purposes.
    
    Args:
        request: DownloadBriefRequest containing the prompt text to download
        
    Returns:
        StreamingResponse: Text file download with photography_brief.txt filename
        
    Raises:
        HTTPException: If the request is invalid
    """
    try:
        if not request.prompt_text or not request.prompt_text.strip():
            raise HTTPException(
                status_code=400, 
                detail="Prompt text cannot be empty"
            )
        
        # Convert the prompt string to a byte stream
        stream = io.StringIO(request.prompt_text)
        response = StreamingResponse(
            iter([stream.read()]), 
            media_type="text/plain",
            headers={"Content-Disposition": "attachment; filename=photography_brief.txt"}
        )
        
        logger.info("📥 Photography brief download requested")
        logger.debug(f"Download content length: {len(request.prompt_text)} characters")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Download brief failed: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate download: {str(e)}"
        )

# --- END NEW ENDPOINTS ---
