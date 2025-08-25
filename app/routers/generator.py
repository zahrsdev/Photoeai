"""
Main Generator Router - Core brief generation endpoints
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from app.services.brief_orchestrator import BriefOrchestratorService
from app.schemas.models import InitialUserRequest, WizardInput, BriefOutput
from app.config.settings import settings

router = APIRouter(prefix="/api/v1", tags=["generator"])


@router.post("/generate-brief", response_model=BriefOutput)
async def generate_brief(request: InitialUserRequest):
    """
    Generate comprehensive photography brief from user request
    """
    try:
        orchestrator = BriefOrchestratorService()
        
        # Extract and autofill wizard input
        wizard_input = await orchestrator.extract_and_autofill(request)
        
        # Generate enhanced brief
        brief_output = await orchestrator.generate_enhanced_brief(wizard_input)
        
        logger.info("✅ Brief generation completed successfully")
        return brief_output
        
    except Exception as e:
        logger.error(f"❌ Brief generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Brief generation failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PhotoEAI Generator"}


@router.post("/wizard-to-brief")
async def wizard_to_brief(wizard_input: WizardInput):
    """
    Generate brief directly from wizard input (bypass extraction)
    """
    try:
        orchestrator = BriefOrchestratorService()
        brief_output = await orchestrator.generate_enhanced_brief(wizard_input)
        
        logger.info("✅ Wizard-to-brief generation completed")
        return brief_output
        
    except Exception as e:
        logger.error(f"❌ Wizard-to-brief failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Wizard-to-brief generation failed: {str(e)}"
        )
