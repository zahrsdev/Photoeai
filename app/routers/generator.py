"""
API Router for the PhotoeAI backend.
Defines the REST API endpoints for brief generation functionality.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger
# Models to import (add the new ones)
from app.schemas.models import (
    InitialUserRequest, WizardInput, BriefOutput, 
    ImageGenerationRequest, ImageEnhancementRequest, ImageOutput
)
from app.services.brief_orchestrator import BriefOrchestratorService
# Import the new service
from app.services.image_generator import ImageGenerationService

# Create router instance and orchestrator (existing)
router = APIRouter(prefix="/api/v1", tags=["generator"])
orchestrator = BriefOrchestratorService()

# --- NEW ---
# Initialize the new image generation service
image_service = ImageGenerationService()
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

@router.post("/generate-image", response_model=ImageOutput, tags=["Image Generation"])
async def generate_image(request: ImageGenerationRequest) -> ImageOutput:
    """
    Takes a professionally crafted brief prompt and generates a photorealistic image.
    This is the final step of the PhotoeAI pipeline.
    """
    try:
        if not request.brief_prompt or not request.brief_prompt.strip():
            raise HTTPException(status_code=400, detail="Brief prompt cannot be empty.")
        
        result = await image_service.generate_image(
            brief_prompt=request.brief_prompt,
            negative_prompt=request.negative_prompt
        )
        return result
    except Exception as e:
        logger.error(f"Error in /generate-image endpoint: {e}")
        raise HTTPException(status_code=503, detail=f"Image generation service is unavailable: {str(e)}")

@router.post("/enhance-image", response_model=ImageOutput, tags=["Image Generation"])
async def enhance_image(request: ImageEnhancementRequest) -> ImageOutput:
    """
    Enhances or modifies a previously generated image based on user feedback.
    """
    try:
        if not request.enhancement_instruction or not request.enhancement_instruction.strip():
            raise HTTPException(status_code=400, detail="Enhancement instruction cannot be empty.")

        result = await image_service.enhance_image(
            original_prompt=request.original_brief_prompt,
            instruction=request.enhancement_instruction,
            seed=request.seed
        )
        return result
    except Exception as e:
        logger.error(f"Error in /enhance-image endpoint: {e}")
        raise HTTPException(status_code=503, detail=f"Image enhancement service is unavailable: {str(e)}")

# --- END NEW ENDPOINTS ---
