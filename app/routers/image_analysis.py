"""
Image Analysis & Enhancement Router - Task 4
New endpoint untuk combine image analysis + prompt enhancement
TIDAK MENGUBAH existing system, purely additional feature
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from app.services.image_analysis_service import ImageAnalysisService
from app.services.image_wizard_bridge import ImageWizardBridge
from app.services.brief_orchestrator import BriefOrchestratorService
from app.services.multi_provider_image_generator import OpenAIImageService
from app.config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["image-analysis"])


class AnalyzeAndEnhanceRequest(BaseModel):
    """Request model untuk image analysis + enhancement"""
    image_filename: str = "Filename dari uploaded image (dengan extension)"
    user_prompt: str = "User enhancement request"
    api_key: str = "OpenAI API key from user"
    generate_image: Optional[bool] = True  # Whether to generate image after brief


class AnalyzeAndEnhanceResponse(BaseModel):
    """Response model untuk image analysis + enhancement result"""
    status: str
    image_analysis: dict
    enhanced_brief: str
    generated_image_url: Optional[str] = None
    processing_time: float


@router.post("/analyze-and-enhance", response_model=AnalyzeAndEnhanceResponse)
async def analyze_and_enhance(request: AnalyzeAndEnhanceRequest):
    """
    NEW ENDPOINT: Analyze uploaded image + generate enhanced brief + optional image generation
    
    Flow:
    1. Get image URL dari image_id 
    2. Analyze image dengan Vision API
    3. Bridge analysis + user prompt → WizardInput
    4. Generate enhanced brief (existing system)
    5. Optional: Generate final image
    
    TIDAK MENGUBAH existing endpoints!
    """
    import time
    start_time = time.time()
    
    logger.info("🚀 Starting analyze-and-enhance workflow", extra={
        "image_filename": request.image_filename,
        "user_prompt": request.user_prompt[:100] + "..." if len(request.user_prompt) > 100 else request.user_prompt,
        "generate_image": request.generate_image
    })
    
    try:
        # Step 1: Get image path dari filename  
        image_path = f"static/images/uploads/{request.image_filename}"
        logger.debug(f"🖼️ Image path: {image_path}")
        
        # Step 2: Analyze image
        logger.info("👁️ Step 2: Analyzing image with Vision API")
        image_service = ImageAnalysisService()
        image_analysis = await image_service.analyze_product_image_from_file(image_path, request.api_key)
        
        # Step 3: Bridge analysis + prompt ke WizardInput
        logger.info("🌉 Step 3: Bridging analysis with user prompt")
        bridge = ImageWizardBridge()
        wizard_input = bridge.combine_image_and_prompt(image_analysis, request.user_prompt)
        
        # Step 4: Generate enhanced brief (using EXISTING system!)
        logger.info("📝 Step 4: Generating enhanced brief via existing orchestrator")
        orchestrator = BriefOrchestratorService()
        brief_output = await orchestrator.generate_final_brief(wizard_input)
        
        enhanced_brief = brief_output.final_prompt
        
        # Step 5: Optional image generation
        generated_image_url = None
        if request.generate_image:
            logger.info("🎨 Step 5: Generating enhanced image")
            try:
                image_generator = OpenAIImageService()
                image_result = await image_generator.generate_image(
                    brief_prompt=enhanced_brief,
                    user_api_key=request.api_key  # Use API key from user input
                )
                generated_image_url = image_result.image_url
            except Exception as img_error:
                logger.warning(f"⚠️ Image generation failed: {str(img_error)}")
                # Continue without image - brief still successful
        
        processing_time = time.time() - start_time
        
        logger.info("✅ Analyze-and-enhance completed successfully", extra={
            "processing_time": round(processing_time, 2),
            "brief_length": len(enhanced_brief),
            "image_generated": generated_image_url is not None,
            "product_type": image_analysis.get("product_type")
        })
        
        return AnalyzeAndEnhanceResponse(
            status="success",
            image_analysis=image_analysis,
            enhanced_brief=enhanced_brief,
            generated_image_url=generated_image_url,
            processing_time=round(processing_time, 2)
        )
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        logger.error("💥 Analyze-and-enhance workflow failed", extra={
            "error": str(e),
            "error_type": type(e).__name__,
            "processing_time": round(processing_time, 2),
            "image_filename": request.image_filename
        })
        
        raise HTTPException(
            status_code=500,
            detail=f"Analysis and enhancement failed: {str(e)} (Type: {type(e).__name__})"
        )


@router.get("/image-analysis-status/{filename}")
async def get_image_analysis_status(filename: str):
    """
    Get status/preview dari uploaded image
    Helper endpoint untuk frontend
    """
    try:
        import os
        
        # Check if image exists
        image_path = f"static/images/uploads/{filename}"
        
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404,
                detail="Image not found"
            )
        
        # Get file info
        file_size = os.path.getsize(image_path)
        
        return JSONResponse({
            "status": "ready",
            "filename": filename,
            "url": f"/static/images/uploads/{filename}",
            "size_kb": round(file_size / 1024, 1)
        })
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Status check failed: {str(e)}"
        )
