"""
Pydantic models for the PhotoeAI backend application.
Defines the data structures for user input, wizard input, and brief output.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class InitialUserRequest(BaseModel):
    """Model for the initial user request containing a simple text description."""
    user_request: str


class WizardInput(BaseModel):
    """
    Comprehensive model for structured product photography parameters.
    Used to capture all aspects of a photography brief through the wizard interface.
    """
    # Section 1: Main Subject & Story
    product_name: Optional[str] = None
    product_type: Optional[str] = None
    user_request: Optional[str] = None
    product_description: Optional[str] = None
    key_features: Optional[str] = None
    product_state: Optional[str] = None
    style_preference: Optional[str] = None

    # Section 2: Composition & Framing
    shot_type: Optional[str] = None
    framing: Optional[str] = None
    compositional_rule: Optional[str] = None
    negative_space: Optional[str] = None

    # Section 3: Lighting & Atmosphere
    lighting_style: Optional[str] = None
    key_light_setup: Optional[str] = None
    fill_light_setup: Optional[str] = None
    rim_light_setup: Optional[str] = None
    mood: Optional[str] = None

    # Section 4: Background & Setting
    environment: Optional[str] = None
    dominant_colors: Optional[str] = None
    accent_colors: Optional[str] = None
    props: Optional[str] = None

    # Section 5: Camera & Lens
    camera_type: Optional[str] = None
    lens_type: Optional[str] = None
    aperture_value: Optional[float] = None
    shutter_speed_value: Optional[int] = None
    iso_value: Optional[int] = None
    visual_effect: Optional[str] = None

    # Section 6: Style & Post-Production
    overall_style: Optional[str] = None
    photographer_influences: Optional[str] = None
    
    # Section 7: Advanced Lighting (NEW - 5 fields)
    light_temperature: Optional[str] = None  # "warm 3200K" or "daylight 5600K"
    shadow_intensity: Optional[str] = None   # "soft", "hard", "medium"
    highlight_control: Optional[str] = None  # "preserved", "blown", "controlled"
    lighting_direction: Optional[str] = None # "front", "side", "back", "top"
    ambient_lighting: Optional[str] = None   # "studio", "natural", "mixed"
    
    # Section 8: Advanced Composition (NEW - 5 fields) 
    perspective_angle: Optional[str] = None   # "eye-level", "low-angle", "high-angle"
    depth_layers: Optional[str] = None        # "foreground", "midground", "background"
    leading_lines: Optional[str] = None       # "diagonal", "curved", "vertical", "none"
    symmetry_type: Optional[str] = None       # "perfect", "asymmetrical", "radial"
    focal_emphasis: Optional[str] = None      # "center", "off-center", "multiple points"
    
    # Section 9: Technical Details (NEW - 5 fields)
    focus_mode: Optional[str] = None          # "manual", "single-point AF", "zone AF"
    metering_mode: Optional[str] = None       # "matrix", "center-weighted", "spot"
    white_balance: Optional[str] = None       # "auto", "daylight", "tungsten", "custom"
    file_format: Optional[str] = None         # "RAW", "JPEG", "TIFF"
    image_stabilization: Optional[str] = None # "on", "off", "lens-based", "body-based"
    
    # Section 10: Brand & Marketing Context (NEW - 5 fields)
    target_audience: Optional[str] = None     # "luxury", "mass market", "professional"
    brand_personality: Optional[str] = None   # "premium", "friendly", "innovative"
    usage_purpose: Optional[str] = None       # "e-commerce", "advertising", "social media"
    seasonal_context: Optional[str] = None    # "spring", "summer", "holiday", "evergreen"
    competitive_differentiation: Optional[str] = None # unique selling points


class BriefOutput(BaseModel):
    """Model for the final enhanced photography brief output."""
    final_prompt: str


# --- NEW MODELS ---

class TextGenerationRequest(BaseModel):
    """
    Request model for text generation using various AI providers.
    Supports the different endpoints shown by the user.
    """
    prompt: str = Field(..., description="The text prompt for generation")
    user_api_key: str = Field(..., description="User-provided API key for the AI service")
    provider: Optional[str] = Field(None, description="Provider override (always uses 'openai' for GPT Image 1)")
    model: Optional[str] = Field(None, description="Specific model to use (e.g., gpt-4o, gemini-2.5-flash)")
    max_tokens: Optional[int] = Field(150, description="Maximum tokens to generate")
    temperature: Optional[float] = Field(0.6, description="Sampling temperature (0.0 to 1.0)")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "Generate a detailed photography brief for luxury skincare products",
                "user_api_key": "your-api-key-here",
                "provider": "openai",
                "model": "openai/gpt-4o",
                "max_tokens": 200,
                "temperature": 0.6
            }
        }


class TextOutput(BaseModel):
    """Output model for text generation responses."""
    generated_text: str = Field(..., description="The generated text content")
    provider_used: str = Field(..., description="Which provider was used for generation")
    model_used: str = Field(..., description="Which model was used for generation")
    generation_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        schema_extra = {
            "example": {
                "generated_text": "A comprehensive photography brief for luxury skincare...",
                "provider_used": "openai", 
                "model_used": "openai/gpt-4o",
                "generation_metadata": {
                    "tokens_used": 156,
                    "response_time": "2.3s",
                    "timestamp": "2024-08-23T10:00:00Z"
                }
            }
        }


class ImageGenerationRequest(BaseModel):
    """Model for the initial image generation request."""
    brief_prompt: str = Field(..., description="The final, enhanced brief prompt generated by the /generate-brief endpoint.")
    user_api_key: str = Field(..., description="User's API key for the image generation service.")
    negative_prompt: Optional[str] = Field(None, description="Optional concepts to exclude from the image.")
    style_preset: Optional[str] = Field("photorealistic", description="Artistic style for the image generation.")
    provider: Optional[str] = Field(None, description="Optional provider override. Only 'openai' supported for GPT Image 1.")
    use_raw_prompt: Optional[bool] = Field(False, description="If True, use the brief_prompt directly without processing it through the wizard system.")
    uploaded_image_base64: Optional[str] = Field(None, description="Base64 encoded uploaded image for 2-step Vision API flow.")
    uploaded_image_filename: Optional[str] = Field(None, description="Filename of uploaded image in static/images/uploads/ (alternative to base64 for performance).")

class ImageEnhancementRequest(BaseModel):
    """Model for iteratively enhancing a previously generated image."""
    original_brief_prompt: str = Field(..., description="The original brief that created the image.")
    generation_id: str = Field(..., description="The unique ID of the image being enhanced.")
    enhancement_instruction: str = Field(..., description="User's instruction for what to change, e.g., 'Make it colder with more condensation.'")
    user_api_key: str = Field(..., description="User's API key for the image generation service.")
    seed: Optional[int] = Field(None, description="The seed of the original image to maintain consistency.")
    provider: Optional[str] = Field(None, description="Optional provider override. Only 'openai' supported for GPT Image 1.")

class ImageOutput(BaseModel):
    """Model for the response after a successful image generation."""
    image_url: str
    generation_id: str
    seed: int
    revised_prompt: str
    final_enhanced_prompt: str  # MISSION 2: Added field for downloadable prompt feature
    model_used: Optional[str] = Field(None, description="AI model used for generation")
    provider_used: Optional[str] = Field(None, description="Provider service used")
    progress_messages: Optional[list] = Field(None, description="Progress messages from pipeline processing")
    session_id: Optional[str] = Field(None, description="Session ID for real-time progress tracking")


class DownloadBriefRequest(BaseModel):
    """MISSION 2: Request model for downloading photography brief as text file."""
    prompt_text: str = Field(..., description="The prompt text to be downloaded as a file")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt_text": "Professional product photography brief with detailed specifications..."
            }
        }

# --- END NEW MODELS ---
