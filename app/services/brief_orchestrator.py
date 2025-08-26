"""
Brief Orchestrator Service - Main service that orchestrates the entire workflow.
Coordinates between AI Client and Prompt Composer Service for end-to-end brief generation.
Enhanced with structured logging and self-healing architecture.
"""

from typing import Dict, Any
from loguru import logger
from app.schemas.models import InitialUserRequest, WizardInput, BriefOutput
from app.services.ai_client import AIClient
from app.services.prompt_composer import PromptComposerService


class BriefOrchestratorService:
    """
    Main orchestrator service that coordinates the entire brief generation workflow.
    Handles both extraction/autofill and final brief generation flows with logging.
    """
    
    def __init__(self):
        """Initialize the orchestrator with required services."""
        self.ai_client = AIClient()
        self.prompt_composer = PromptComposerService()
        logger.info("BriefOrchestratorService initialized with self-healing architecture")
    
    async def extract_and_autofill(self, request: InitialUserRequest) -> WizardInput:
        """
        Extract wizard data from user request with self-healing validation feedback loop.
        
        This implements Flow 1 with self-healing architecture:
        1. Receive InitialUserRequest
        2. Use AIClient to extract structured data (LLM as Analyst) with retry logic
        3. Validate extracted data and provide feedback for corrections
        4. Autofill missing fields with defaults
        5. Return complete WizardInput
        
        Args:
            request: Initial user request containing raw text
            
        Returns:
            Complete WizardInput object with all fields filled
        """
        MAX_RETRIES = 2
        extracted_data = None
        validation_errors = []
        request_id = id(request)  # Simple request tracking
        
        logger.info(f"🎬 Starting extraction workflow [ID: {request_id}]", extra={
            "request_id": request_id,
            "user_request_length": len(request.user_request),
            "workflow": "extract_and_autofill"
        })
        
        # Self-healing retry loop
        for attempt in range(MAX_RETRIES):
            try:
                # Prepare the request for AI Client
                if attempt == 0:
                    # First attempt - standard extraction
                    logger.info(f"🔍 Attempt {attempt + 1}/{MAX_RETRIES}: Initial extraction [ID: {request_id}]")
                    extracted_data = await self.ai_client.extract_wizard_data(request.user_request)
                else:
                    # Retry attempt - include validation errors as feedback
                    error_feedback = "; ".join(validation_errors)
                    retry_instruction = (
                        f"Your previous attempt to extract data failed with the following errors: {error_feedback}. "
                        f"Please analyze these errors, correct your process, and provide a new, valid JSON output "
                        f"based on the original user request: '{request.user_request}'"
                    )
                    logger.warning(f"⚠️ Attempt {attempt + 1}/{MAX_RETRIES}: Retry with error feedback [ID: {request_id}]", extra={
                        "request_id": request_id,
                        "validation_errors": validation_errors,
                        "error_feedback": error_feedback
                    })
                    extracted_data = await self.ai_client.extract_wizard_data(retry_instruction)
                
                # Debug: Log raw extracted data
                logger.debug(f"🔍 Raw extracted data [ID: {request_id}]", extra={
                    "request_id": request_id,
                    "extracted_fields": list(extracted_data.keys()) if extracted_data else [],
                    "data_size": len(str(extracted_data)) if extracted_data else 0
                })
                
                # Ensure user_request is preserved
                extracted_data["user_request"] = request.user_request
                
                # Validate the extracted data
                validation_errors = self.prompt_composer.validate_extracted_data(extracted_data)
                
                if not validation_errors:
                    # Success! Data is valid
                    logger.info(f"✅ Extraction valid on attempt {attempt + 1} [ID: {request_id}]", extra={
                        "request_id": request_id,
                        "attempt": attempt + 1,
                        "product_name": extracted_data.get("product_name", "Unknown")
                    })
                    break
                else:
                    logger.warning(f"❌ Validation failed on attempt {attempt + 1} [ID: {request_id}]", extra={
                        "request_id": request_id,
                        "attempt": attempt + 1,
                        "validation_errors": validation_errors
                    })
                    if attempt == MAX_RETRIES - 1:
                        # Final attempt failed
                        error_msg = f"Failed to extract valid data after {MAX_RETRIES} attempts"
                        logger.error(f"💥 Self-healing failed [ID: {request_id}]", extra={
                            "request_id": request_id,
                            "max_retries": MAX_RETRIES,
                            "final_errors": validation_errors
                        })
                        raise Exception(f"{error_msg}. Final errors: {validation_errors}")
                    
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    # Final attempt failed with exception
                    error_msg = f"AI extraction service failed after {MAX_RETRIES} attempts: {str(e)}"
                    logger.error(f"💥 Critical extraction failure [ID: {request_id}]", extra={
                        "request_id": request_id,
                        "max_retries": MAX_RETRIES,
                        "final_exception": str(e),
                        "exception_type": type(e).__name__
                    })
                    raise Exception(error_msg)
                else:
                    logger.warning(f"⚠️ Attempt {attempt + 1} failed with exception [ID: {request_id}]", extra={
                        "request_id": request_id,
                        "attempt": attempt + 1,
                        "exception": str(e),
                        "retrying": True
                    })
                    continue
        
        # Step 2: Autofill missing fields with defaults
        logger.info(f"🔧 Autofilling missing fields with defaults [ID: {request_id}]")
        wizard_input = self.prompt_composer.autofill_wizard_input(extracted_data)
        
        logger.info(f"🎉 Extraction workflow completed successfully [ID: {request_id}]", extra={
            "request_id": request_id,
            "product_name": wizard_input.product_name,
            "shot_type": wizard_input.shot_type,
            "lighting_style": wizard_input.lighting_style,
            "workflow": "extract_and_autofill",
            "status": "success"
        })
        
        return wizard_input
    
    async def generate_final_brief(self, wizard_input: WizardInput) -> BriefOutput:
        """
        Generate the final enhanced photography brief from wizard input.
        
        This implements Flow 2 from the architecture guide:
        1. Receive complete WizardInput
        2. Compose initial brief using template
        3. Validate the brief
        4. Enhance the brief using AI Client (LLM as Product Photographer)
        5. Return final BriefOutput
        
        Args:
            wizard_input: Complete wizard input data
            
        Returns:
            BriefOutput containing the final enhanced prompt
        """
        request_id = id(wizard_input)  # Simple request tracking
        
        logger.info(f"🎨 Starting final brief generation workflow [ID: {request_id}]", extra={
            "request_id": request_id,
            "product_name": wizard_input.product_name,
            "shot_type": wizard_input.shot_type,
            "workflow": "generate_final_brief"
        })
        
        try:
            # Step 1: Compose initial brief using system prompt template
            logger.info(f"📝 Composing initial brief from wizard input [ID: {request_id}]")
            initial_brief = self.prompt_composer.compose_initial_brief(wizard_input)
            
            logger.debug(f"📊 Initial brief metrics [ID: {request_id}]", extra={
                "request_id": request_id,
                "initial_brief_length": len(initial_brief),
                "product_name": wizard_input.product_name
            })
            
            # Step 2: Validate the brief against quality rules
            logger.info(f"✅ Validating composed brief [ID: {request_id}]")
            validation_result = self.prompt_composer.validate_brief(initial_brief, wizard_input)
            
            if not validation_result["is_valid"]:
                logger.warning(f"⚠️ Brief validation failed [ID: {request_id}]", extra={
                    "request_id": request_id,
                    "validation_errors": validation_result['errors']
                })
                # Continue with warnings, but log errors
                for error in validation_result["errors"]:
                    logger.warning(f"❌ Validation error: {error} [ID: {request_id}]")
            else:
                logger.info(f"✅ Brief validation passed [ID: {request_id}]")
            
            if validation_result["warnings"]:
                for warning in validation_result["warnings"]:
                    logger.warning(f"⚠️ Validation warning: {warning} [ID: {request_id}]")
            
            # CRITICAL REFACTOR LOG POINT: Log structured WizardInput data before enhancement
            logger.info(f"🎯 MISSION CRITICAL: Sending structured data to Product Photographer [ID: {request_id}]", extra={
                "request_id": request_id,
                "operation": "PRE_PRODUCT_PHOTOGRAPHER_DATA_DISPATCH",
                "structured_data_fields": list(wizard_input.model_dump().keys()),
                "product_name": wizard_input.product_name,
                "user_request_preview": wizard_input.user_request[:100] + "..." if len(wizard_input.user_request) > 100 else wizard_input.user_request,
                "refactor_phase": "STRUCTURED_DATA_TO_PRODUCT_PHOTOGRAPHER"
            })
            logger.debug("🔍 MISSION DEBUG: Pre-enhancement structured data", extra={
                "full_structured_data": wizard_input.model_dump()
            })
            
            # CRITICAL CHANGE: Send structured data to refactored Product Photographer
            logger.info(f"🚀 CRITICAL REFACTOR: Calling refactored Product Photographer with structured data [ID: {request_id}]")
            
            # Add professional photography quality rules with proper English terminology
            professional_photography_rules = """
PROFESSIONAL PHOTOGRAPHY QUALITY CONTROL:

## GAMMA CORRECTION & TONE CONSISTENCY
- Apply proper gamma correction (power 1/2.2) for consistent tone mapping across all image elements
- Maintain uniform luminance values and color temperature throughout composition
- Ensure balanced exposure with natural dynamic range distribution

## COLOR SPACE & CHANNEL MANAGEMENT  
- Standardized RGBA channel consistency with proper color space workflow
- Accurate color reproduction with natural saturation levels
- Prevent color banding and maintain smooth gradients

## NATURAL LIGHTING PHYSICS
- Implement realistic light ray casting with proper directional shadows
- Natural light falloff and ambient occlusion integration
- Consistent light temperature and atmospheric perspective
- Proper surface material interaction with light sources

## SENSOR PHOTOSITE PRECISION (Logo & Text Clarity)
- Sharp edge definition for all text elements and logo components
- Sub-pixel precision rendering for crisp typography
- Anti-aliasing optimization for readability at all scales
- Maintain vector-like sharpness for brand elements

## PREVIEW QUALITY & ARTIFACT PREVENTION
- Eliminate compression artifacts and digital noise
- Prevent haloing, ghosting, or composite seam visibility
- Natural depth of field with proper bokeh characteristics
- Avoid artificial post-processing appearance

## REALISM INTEGRATION
- All elements must appear naturally integrated and realistic
- Objects in motion should have proper physics and natural movement blur
- Ensure cohesive environmental lighting and proper shadow casting
- Avoid artificial or composite appearance with seamless element integration
"""
            
            enhanced_brief = await self.ai_client.enhance_brief_from_structured_data(
                wizard_input.model_dump(), 
                user_api_key=wizard_input.user_api_key
            )
            
            # Combine with professional photography rules
            final_brief = professional_photography_rules + enhanced_brief
            
            # CRITICAL REFACTOR LOG POINT: Validate and log enhanced output
            word_count = len(enhanced_brief.split())
            section_count = enhanced_brief.count('##')
            logger.info(f"📊 MISSION VALIDATION: Enhanced brief analysis [ID: {request_id}]", extra={
                "request_id": request_id,
                "enhanced_brief_length": len(enhanced_brief),
                "word_count": word_count,
                "section_count": section_count,
                "refactor_success": word_count > 200 and section_count >= 5,
                "operation": "POST_PRODUCT_PHOTOGRAPHER_VALIDATION"
            })
            logger.info(f"📝 ENHANCED BRIEF PREVIEW [ID: {request_id}]: {enhanced_brief[:800]}{'...' if len(enhanced_brief) > 800 else ''}")
            
            logger.debug(f"📈 Enhanced brief metrics [ID: {request_id}]", extra={
                "request_id": request_id,
                "enhanced_brief_length": len(enhanced_brief),
                "enhancement_ratio": round(len(enhanced_brief) / len(initial_brief), 2) if initial_brief else 0
            })
            
            # Step 4: Create and return final output
            logger.info(f"🎉 Brief generation completed successfully [ID: {request_id}]", extra={
                "request_id": request_id,
                "product_name": wizard_input.product_name,
                "final_brief_length": len(enhanced_brief),
                "workflow": "generate_final_brief",
                "status": "success"
            })
            
            return BriefOutput(final_prompt=final_brief)
            
        except Exception as e:
            logger.error(f"💥 Critical error in generate_final_brief [ID: {request_id}]", extra={
                "request_id": request_id,
                "product_name": wizard_input.product_name,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "workflow": "generate_final_brief",
                "status": "error"
            })
            raise Exception(f"Failed to generate final brief: {str(e)}")
    
    async def get_brief_preview(self, wizard_input: WizardInput) -> Dict[str, Any]:
        """
        Get a preview of the initial brief without AI enhancement.
        Useful for debugging and validation purposes.
        
        Args:
            wizard_input: Complete wizard input data
            
        Returns:
            Dictionary containing initial brief and validation results
        """
        try:
            # Compose initial brief
            initial_brief = self.prompt_composer.compose_initial_brief(wizard_input)
            
            # Validate the brief
            validation_result = self.prompt_composer.validate_brief(initial_brief, wizard_input)
            
            return {
                "initial_brief": initial_brief,
                "validation": validation_result,
                "wizard_data": wizard_input.model_dump()
            }
            
        except Exception as e:
            print(f"Error in get_brief_preview: {e}")
            return {
                "error": str(e),
                "initial_brief": None,
                "validation": {"is_valid": False, "errors": [str(e)], "warnings": []},
                "wizard_data": wizard_input.model_dump() if wizard_input else None
            }
