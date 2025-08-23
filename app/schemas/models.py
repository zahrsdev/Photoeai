"""
Pydantic models for the PhotoeAI backend application.
Defines the data structures for user input, wizard input, and brief output.
"""

from pydantic import BaseModel
from typing import Optional


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
    user_request: Optional[str] = None
    product_description: Optional[str] = None
    key_features: Optional[str] = None
    product_state: Optional[str] = None

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


class BriefOutput(BaseModel):
    """Model for the final enhanced photography brief output."""
    final_prompt: str
