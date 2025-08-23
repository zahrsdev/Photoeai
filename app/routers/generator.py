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
from app.services.unified_ai_service import UnifiedAIService

# Create router instance and orchestrator (existing)
router = APIRouter(prefix="/api/v1", tags=["generator"])
orchestrator = BriefOrchestratorService()

# --- NEW ---
# Initialize both image generation services
image_service = ImageGenerationService()  # Keep for backward compatibility
unified_ai_service = UnifiedAIService()  # Unified service for both text and image generation
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
        if not request.user_request or not request.user_request.strip():
            raise HTTPException(
                status_code=400, 
                detail="User request cannot be empty"
            )
        
        wizard_input = await orchestrator.extract_and_autofill(request)
        return wizard_input
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in extract_and_fill endpoint: {e}")
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
        # Basic validation - ensure at least product name or user request exists
        if not wizard_input.product_name and not wizard_input.user_request:
            raise HTTPException(
                status_code=400,
                detail="Either product_name or user_request must be provided"
            )
        
        brief_output = await orchestrator.generate_final_brief(wizard_input)
        
        if not brief_output.final_prompt or not brief_output.final_prompt.strip():
            raise HTTPException(
                status_code=500,
                detail="Generated brief is empty. Please try again."
            )
        
        return brief_output
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in generate_brief endpoint: {e}")
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

@router.post("/generate-text-advanced", response_model=TextOutput)
async def generate_text_advanced(request: TextGenerationRequest) -> TextOutput:
    """
    Advanced text generation with full provider control.
    Supports all the provider endpoints: Sumopod, OpenAI, Gemini, Midjourney.
    """
    logger.info(f"🤖 Advanced text generation with provider: {request.provider}")
    
    try:
        # Use unified AI service for text generation
        generated_text = await unified_ai_service.generate_text(
            prompt=request.prompt,
            user_api_key=request.user_api_key,
            provider_override=request.provider,
            model=request.model
        )
        
        # Return structured response
        return TextOutput(
            generated_text=generated_text,
            provider_used=request.provider or "auto_detected",
            model_used=request.model or "default",
            generation_metadata={
                "max_tokens": request.max_tokens,
                "temperature": request.temperature,
                "service": "unified_ai_service",
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
        
        # Use unified AI service for text generation
        generated_text = await unified_ai_service.generate_text(
            prompt=text_prompt,
            user_api_key=request.user_api_key,
            provider_override=getattr(request, 'provider', None),
            model=getattr(request, 'model', None)
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
    Takes a professionally crafted brief prompt and generates a photorealistic image.
    This is the final step of the PhotoeAI pipeline.
    Requires the user to provide their own API key for the image generation service.
    Supports multiple providers: OpenAI DALL-E, Gemini, Sumopod, Midjourney.
    """
    try:
        if not request.brief_prompt or not request.brief_prompt.strip():
            raise HTTPException(status_code=400, detail="Brief prompt cannot be empty.")
        
        if not request.user_api_key or not request.user_api_key.strip():
            raise HTTPException(status_code=400, detail="User API key is required for image generation.")
        
        # Use multi-provider service for better compatibility
        result = await unified_ai_service.generate_image(
            brief_prompt=request.brief_prompt,
            user_api_key=request.user_api_key,
            negative_prompt=request.negative_prompt,
            provider_override=request.provider
        )
        return result
    except Exception as e:
        logger.error(f"Error in /generate-image endpoint: {e}")
        raise HTTPException(status_code=503, detail=f"Image generation service is unavailable: {str(e)}")

@router.post("/enhance-image", response_model=ImageOutput, tags=["Image Generation"])
async def enhance_image(request: ImageEnhancementRequest) -> ImageOutput:
    """
    Enhances or modifies a previously generated image based on user feedback.
    Requires the user to provide their own API key for the image generation service.
    Supports multiple providers: OpenAI DALL-E, Gemini, Sumopod, Midjourney.
    """
    try:
        if not request.enhancement_instruction or not request.enhancement_instruction.strip():
            raise HTTPException(status_code=400, detail="Enhancement instruction cannot be empty.")

        if not request.user_api_key or not request.user_api_key.strip():
            raise HTTPException(status_code=400, detail="User API key is required for image enhancement.")

        # Use multi-provider service for better compatibility
        result = await unified_ai_service.enhance_image(
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
