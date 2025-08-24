"""
Image Analysis Service - Task 2
Service untuk handle image analysis menggunakan OpenAI Vision API
"""
from typing import Dict, Any
from loguru import logger
from app.services.ai_client import AIClient


class ImageAnalysisService:
    """
    Service untuk analisis gambar produk menggunakan Vision API
    Extract informasi produk, lighting, style, dan composition
    """
    
    def __init__(self):
        self.ai_client = AIClient()
    
    async def analyze_product_image_from_file(self, image_path: str, api_key: str = None) -> Dict[str, Any]:
        """
        Analyze product image dari file path dengan base64 encoding
        
        Args:
            image_path: Path ke image file
            api_key: OpenAI API key (optional, uses settings if not provided)
            
        Returns:
            Dict dengan analysis results siap untuk wizard integration
        """
        logger.info(f"🖼️ Starting product image analysis for file: {image_path}")
        
        try:
            # Read file and convert to base64
            import base64
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Call Vision API through AIClient with base64
            if api_key:
                # Create temporary client with user API key
                from openai import OpenAI
                temp_client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
                analysis_result = await self._analyze_with_custom_client_base64(temp_client, image_data)
            else:
                # Use default client - call method to be added
                analysis_result = await self.ai_client.analyze_image_base64(image_data)
            
            # Validate dan normalize data
            validated_result = self._validate_analysis_result(analysis_result)
            
            logger.info(f"✅ Image analysis completed successfully", extra={
                "product_type": validated_result.get("product_type"),
                "style_preference": validated_result.get("style_preference"),
                "lighting_style": validated_result.get("lighting_style")
            })
            
            return validated_result
            
        except Exception as e:
            logger.error(f"💥 Image analysis service error: {str(e)}")
            
            # Return safe fallback
            return self._get_fallback_analysis()

    async def analyze_product_image(self, image_url: str, api_key: str = None) -> Dict[str, Any]:
        """
        Analyze product image dan return structured data
        
        Args:
            image_url: Full URL ke uploaded image
            api_key: OpenAI API key (optional, uses settings if not provided)
            
        Returns:
            Dict dengan analysis results siap untuk wizard integration
        """
        logger.info(f"🖼️ Starting product image analysis for: {image_url}")
        
        try:
            # Call Vision API through AIClient
            if api_key:
                # Create temporary client with user API key
                from openai import OpenAI
                temp_client = OpenAI(api_key=api_key, base_url="https://api.openai.com/v1")
                analysis_result = await self._analyze_with_custom_client(temp_client, image_url)
            else:
                # Use default client
                analysis_result = await self.ai_client.analyze_image(image_url)
            
            # Validate dan normalize data
            validated_result = self._validate_analysis_result(analysis_result)
            
            logger.info(f"✅ Image analysis completed successfully", extra={
                "product_type": validated_result.get("product_type"),
                "style_preference": validated_result.get("style_preference"),
                "lighting_style": validated_result.get("lighting_style")
            })
            
            return validated_result
            
        except Exception as e:
            logger.error(f"💥 Image analysis service error: {str(e)}")
            
            # Return safe fallback
            return self._get_fallback_analysis()
    
    async def _analyze_with_custom_client(self, client, image_url: str) -> Dict[str, Any]:
        """
        Analyze image using custom OpenAI client (with user API key)
        """
        request_id = hash(image_url) % 10000
        
        logger.info(f"👁️ Starting image analysis with custom client [ID: {request_id}]")
        
        analysis_instruction = """
Analyze this product image with professional commercial photography expertise and extract technical information.

**REQUIRED OUTPUT FORMAT (JSON only):**
```json
{
    "product_type": "category (e.g., food, electronics, cosmetics, accessories)",
    "product_name": "specific product name or description",
    "lighting_style": "professional lighting pattern (Rembrandt lighting, butterfly lighting, split lighting, clamshell setup, rim lighting, high-key, low-key, golden hour directional, etc.)",
    "background_type": "professional backdrop (seamless white studio backdrop, black velvet, marble surface, wooden texture, environmental context, etc.)",
    "composition_style": "professional shot technique (macro close-up with shallow DOF, environmental wide shot, top-down flat lay, Dutch angle dynamic, eye-level hero shot, etc.)", 
    "style_preference": "photography aesthetic (luxury commercial, editorial fashion, minimalist product, vintage film, ultra-modern digital, award-winning commercial, etc.)",
    "current_quality": "professional assessment (amateur snapshot, prosumer DSLR, professional commercial, award-winning photography, etc.)",
    "improvement_areas": ["specific", "technical", "photography", "enhancements"],
    "dominant_colors": ["precise", "professional", "product", "color", "descriptions"],
    "camera_angle": "technical angle with professional context"
}
```

CRITICAL: For 'dominant_colors', use professional color accuracy terminology (e.g., "deep burgundy red", "warm champagne gold", "matte charcoal black"). Identify ONLY the actual colors of the PRODUCT itself, not background or environment. Focus on authentic product appearance with precision.
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",  # Use consistent model
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": analysis_instruction},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            import re
            import json
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group(1))
            else:
                analysis_data = json.loads(analysis_text)
            
            logger.info(f"✅ Custom client image analysis completed [ID: {request_id}]")
            return analysis_data
            
        except Exception as e:
            logger.error(f"💥 Custom client analysis error: {str(e)}")
            # Return fallback
            return {
                "product_type": "unknown",
                "product_name": "Product", 
                "lighting_style": "natural",
                "background_type": "neutral",
                "composition_style": "standard",
                "style_preference": "modern",
                "current_quality": "amateur",
                "improvement_areas": ["lighting", "composition"],
                "dominant_colors": ["natural product tone"],
                "camera_angle": "front"
            }
    
    async def _analyze_with_custom_client_base64(self, client, image_data: str) -> Dict[str, Any]:
        """Analyze image dengan custom OpenAI client menggunakan base64 data"""
        request_id = hash(image_data[:100]) % 10000
        
        logger.info(f"👁️ Starting image analysis with custom client base64 [ID: {request_id}]")
        
        analysis_instruction = """
Analyze this product image and extract structured data for photography brief generation.

Return ONLY valid JSON with these exact fields:
```json
{
    "product_type": "category (e.g., food, electronics, cosmetics, accessories)",
    "product_name": "specific product name or description", 
    "lighting_style": "current lighting type (natural, studio, dramatic, soft, etc.)",
    "background_type": "background description (white, wooden, marble, outdoor, etc.)",
    "composition_style": "shot angle (close-up, wide, overhead, side-angle, etc.)", 
    "style_preference": "overall mood/style (modern, vintage, luxury, casual, etc.)",
    "current_quality": "assessment (amateur, professional, commercial, etc.)",
    "improvement_areas": ["list", "of", "areas", "needing", "enhancement"],
    "dominant_colors": ["actual", "product", "colors", "only"],
    "camera_angle": "specific angle description"
}
```

CRITICAL: For 'dominant_colors', extract ONLY the authentic colors of the PRODUCT itself (not background/props). Be specific about actual product appearance (e.g., "vibrant red", "golden yellow", "metallic chrome").
"""

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": analysis_instruction},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                        ]
                    }
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            analysis_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            import re
            import json
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', analysis_text, re.DOTALL)
            if json_match:
                analysis_data = json.loads(json_match.group(1))
            else:
                analysis_data = json.loads(analysis_text)
            
            logger.info(f"✅ Custom client base64 analysis completed [ID: {request_id}]")
            return analysis_data
            
        except Exception as e:
            logger.error(f"💥 Custom client base64 analysis error: {str(e)}")
            # Return fallback
            return {
                "product_type": "unknown",
                "product_name": "Product",
                "lighting_style": "natural", 
                "background_type": "neutral",
                "composition_style": "standard",
                "style_preference": "modern",
                "current_quality": "amateur",
                "improvement_areas": ["lighting", "composition"],
                "dominant_colors": ["neutral"],
                "camera_angle": "front"
            }
    
    def _validate_analysis_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate dan normalize analysis result"""
        
        # Required fields dengan defaults
        validated = {
            "product_type": result.get("product_type", "unknown"),
            "product_name": result.get("product_name", "Product"),
            "lighting_style": result.get("lighting_style", "natural"),
            "background_type": result.get("background_type", "neutral"),
            "composition_style": result.get("composition_style", "standard"),
            "style_preference": result.get("style_preference", "modern"),
            "current_quality": result.get("current_quality", "amateur"),
            "improvement_areas": result.get("improvement_areas", ["lighting", "composition"]),
            "dominant_colors": result.get("dominant_colors", ["neutral"]),
            "camera_angle": result.get("camera_angle", "front")
        }
        
        # Normalize values ke expected format
        validated["product_type"] = self._normalize_product_type(validated["product_type"])
        validated["style_preference"] = self._normalize_style_preference(validated["style_preference"])
        validated["dominant_colors"] = self._normalize_colors(validated["dominant_colors"])
        
        return validated
    
    def _normalize_product_type(self, product_type: str) -> str:
        """Normalize product type ke wizard categories"""
        type_mapping = {
            "food": "food_beverage",
            "beverage": "food_beverage", 
            "drink": "food_beverage",
            "electronics": "electronics",
            "tech": "electronics",
            "gadget": "electronics",
            "cosmetics": "beauty_wellness",
            "beauty": "beauty_wellness",
            "skincare": "beauty_wellness",
            "accessories": "accessories",
            "jewelry": "accessories",
            "watch": "accessories",
            "clothing": "fashion",
            "fashion": "fashion",
            "apparel": "fashion"
        }
        
        normalized = type_mapping.get(product_type.lower(), "other")
        return normalized
    
    def _normalize_style_preference(self, style: str) -> str:
        """Normalize style ke wizard options"""
        style_mapping = {
            "luxury": "luxury",
            "premium": "luxury",
            "elegant": "luxury", 
            "modern": "modern",
            "contemporary": "modern",
            "minimalist": "minimalist",
            "simple": "minimalist",
            "clean": "minimalist",
            "vintage": "vintage",
            "retro": "vintage",
            "classic": "classic",
            "traditional": "classic"
        }
        
        return style_mapping.get(style.lower(), "modern")
    
    def _normalize_colors(self, colors) -> list:
        """Normalize and validate color data"""
        if not colors:
            return ["natural product tone"]
        
        if isinstance(colors, str):
            # Split comma-separated string
            colors = [c.strip() for c in colors.split(',')]
        
        if isinstance(colors, list):
            # Filter out generic/vague colors
            generic_colors = ["neutral", "normal", "standard", "basic", "typical", "regular"]
            normalized = []
            
            for color in colors:
                if isinstance(color, str):
                    color = color.strip().lower()
                    if color and color not in generic_colors and len(color) > 2:
                        normalized.append(color)
            
            # Return normalized colors or fallback
            if normalized:
                return normalized[:5]  # Max 5 colors
            else:
                return ["natural product tone"]
        
        return ["natural product tone"]
    
    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis kalau Vision API gagal"""
        return {
            "product_type": "other",
            "product_name": "Product",
            "lighting_style": "natural",
            "background_type": "neutral",
            "composition_style": "standard", 
            "style_preference": "modern",
            "current_quality": "amateur",
            "improvement_areas": ["lighting", "composition", "background"],
            "dominant_colors": ["neutral"],
            "camera_angle": "front"
        }
