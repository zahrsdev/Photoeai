"""
Image-Wizard Bridge Service - Task 3
Convert image analysis results ke WizardInput format
Combine user prompt + image analysis untuk existing wizard flow
"""
from typing import Dict, Any
from loguru import logger
from app.schemas.models import WizardInput


class ImageWizardBridge:
    """
    Bridge service untuk convert image analysis ke WizardInput format
    Combine user prompt dengan image analysis data
    """
    
    def __init__(self):
        pass
    
    def combine_image_and_prompt(
        self, 
        image_analysis: Dict[str, Any], 
        user_prompt: str
    ) -> WizardInput:
        """
        Combine image analysis dengan user prompt jadi WizardInput
        
        Args:
            image_analysis: Result dari ImageAnalysisService
            user_prompt: User input prompt text
            
        Returns:
            WizardInput object siap untuk existing brief generation flow
        """
        logger.info("🌉 Bridging image analysis with user prompt", extra={
            "user_prompt_length": len(user_prompt),
            "operation": "combine_image_and_prompt"
        })
        
        # Input validation
        if image_analysis is None:
            logger.warning("⚠️ Bridge service received None image_analysis", extra={
                "fallback_used": True,
                "user_prompt_preserved": True
            })
            image_analysis = {}
        
        if not isinstance(image_analysis, dict):
            logger.warning("⚠️ Bridge service received invalid image_analysis type", extra={
                "received_type": type(image_analysis).__name__,
                "fallback_used": True,
                "user_prompt_preserved": True
            })
            image_analysis = {}
        
        logger.info("✅ Input validation passed", extra={
            "product_type": image_analysis.get("product_type"),
            "analysis_keys": list(image_analysis.keys())
        })
        
        # DEBUG: Log full image analysis result
        logger.debug("🔍 DEBUG: Full image analysis result", extra={
            "image_analysis": image_analysis
        })
        
        try:
            # Extract product name dari analysis atau user prompt
            product_name = self._extract_product_name(image_analysis, user_prompt)
            
            # Combine user prompt dengan improvement suggestions dari image
            enhanced_user_request = self._enhance_user_request(image_analysis, user_prompt)
            
            # Map image analysis ke WizardInput fields
            wizard_input = WizardInput(
                product_name=product_name,
                user_request=enhanced_user_request,
                product_type=image_analysis.get("product_type"),
                style_preference=image_analysis.get("style_preference"),
                lighting_style=image_analysis.get("lighting_style"),
                shot_type=image_analysis.get("composition_style"),  
                framing=image_analysis.get("camera_angle"),         
                environment=image_analysis.get("background_type"),
                dominant_colors=self._format_color_list(image_analysis.get("dominant_colors")),
                accent_colors="complementary background tones",  # Keep background neutral
                camera_type="Canon EOS R5",  # Default professional camera
                lens_type="50mm f/1.8",      # Default lens
                aperture_value=2.8,          # Default aperture
                shutter_speed_value=125,     # Default shutter
                iso_value=100               # Default ISO
            )
            
            logger.info("✅ Image-wizard bridge completed", extra={
                "product_name": wizard_input.product_name,
                "product_type": wizard_input.product_type,
                "style_preference": wizard_input.style_preference,
                "enhanced_request_length": len(wizard_input.user_request)
            })
            
            return wizard_input
            
        except KeyError as e:
            logger.error(f"💥 Bridge service - Missing required data: {str(e)}", extra={
                "error_type": "KeyError",
                "missing_key": str(e),
                "available_keys": list(image_analysis.keys()) if isinstance(image_analysis, dict) else "N/A",
                "user_prompt_length": len(user_prompt),
                "fallback_used": True
            })
            
        except AttributeError as e:
            logger.error(f"💥 Bridge service - Model attribute error: {str(e)}", extra={
                "error_type": "AttributeError", 
                "error_detail": str(e),
                "user_prompt_length": len(user_prompt),
                "fallback_used": True
            })
            
        except Exception as e:
            logger.error(f"💥 Bridge service - Unexpected error: {str(e)}", extra={
                "error_type": type(e).__name__,
                "error_detail": str(e),
                "image_analysis_type": type(image_analysis).__name__ if image_analysis else "None",
                "user_prompt_length": len(user_prompt),
                "fallback_used": True
            })
            
        # Enhanced fallback WizardInput with better defaults
        logger.info("🔄 Using enhanced fallback WizardInput", extra={
            "fallback_reason": "Bridge service error recovery",
            "user_prompt_preserved": True
        })
        
        return WizardInput(
            product_name="Product",
            user_request=user_prompt,
            product_type="other",
            style_preference="modern",
            lighting_style="natural",
            camera_type="Canon EOS R5",
            lens_type="50mm f/1.8",
            aperture_value=2.8,
            shutter_speed_value=125,
            iso_value=100
        )
    
    def _extract_product_name(self, image_analysis: Dict[str, Any], user_prompt: str) -> str:
        """Extract product name dari analysis atau user prompt"""
        
        # Priority 1: Product name dari image analysis
        if image_analysis.get("product_name") and image_analysis["product_name"] != "Product":
            return image_analysis["product_name"]
        
        # Priority 2: Extract dari user prompt
        prompt_lower = user_prompt.lower()
        
        # Common product keywords
        product_keywords = [
            "pizza", "burger", "coffee", "cake", "bread", "pasta",
            "phone", "laptop", "headphone", "camera", "watch",
            "perfume", "lipstick", "cream", "serum", "shampoo",
            "shirt", "shoes", "bag", "jacket", "dress",
            "ring", "necklace", "bracelet", "earring"
        ]
        
        for keyword in product_keywords:
            if keyword in prompt_lower:
                return keyword.title()
        
        # Priority 3: Use product type as fallback
        product_type = image_analysis.get("product_type", "other")
        if product_type != "other":
            return product_type.replace("_", " ").title()
        
        # Final fallback
        return "Product"
    
    def _enhance_user_request(self, image_analysis: Dict[str, Any], user_prompt: str) -> str:
        """Enhance user prompt dengan insights dari image analysis"""
        
        improvement_areas = image_analysis.get("improvement_areas", [])
        current_quality = image_analysis.get("current_quality", "amateur")
        
        # Base user request
        enhanced_request = user_prompt
        
        # Add context dari image analysis
        context_additions = []
        
        # Add quality improvement context
        if current_quality in ["amateur", "basic"]:
            context_additions.append("upgrade to professional quality")
        
        # Add specific improvement areas
        if "lighting" in improvement_areas:
            context_additions.append("improve lighting setup")
        
        if "composition" in improvement_areas:
            context_additions.append("enhance composition and framing")
        
        if "background" in improvement_areas:
            context_additions.append("optimize background treatment")
        
        # Combine dengan user prompt
        if context_additions:
            enhanced_request += f". Focus on: {', '.join(context_additions)}"
        
        # Add current style context
        current_style = image_analysis.get("style_preference", "modern")
        enhanced_request += f". Maintain {current_style} aesthetic"
        
        logger.debug("🔧 Enhanced user request", extra={
            "original_length": len(user_prompt),
            "enhanced_length": len(enhanced_request),
            "improvements_added": len(context_additions)
        })
        
        return enhanced_request
    
    def _format_color_list(self, color_data) -> str:
        """Format color data from image analysis into readable string"""
        if not color_data:
            return "natural product colors"
        
        if isinstance(color_data, list):
            if len(color_data) > 0:
                return ", ".join(color_data)
            else:
                return "natural product colors"
        
        if isinstance(color_data, str):
            return color_data
        
        return "natural product colors"
