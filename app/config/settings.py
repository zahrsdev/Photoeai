"""
Configuration settings for the PhotoeAI backend application.
Loads environment variables and JSON configuration files with validation.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the directory where this settings file is located
SETTINGS_DIR = Path(__file__).parent.parent.parent  # Go up to photoeai-backend root
ENV_FILE_PATH = SETTINGS_DIR / ".env"


class SystemPromptConfig(BaseModel):
    """
    Central configuration model for all system prompt templates and rules.
    Validates the structure and content of JSON configuration files.
    """
    system_prompt_template: Dict[str, Any] = Field(..., description="Main system prompt template structure")
    enhancement_template: Dict[str, Any] = Field(..., description="AI enhancement instructions and templates")
    quality_rules: Dict[str, Any] = Field(..., description="Validation rules for brief quality")
    stopping_power_rules: Dict[str, Any] = Field(..., description="Elements that create visual stopping power")
    anti_anomaly_rules: Dict[str, Any] = Field(..., description="Rules to prevent visual anomalies")
    defaults: Dict[str, Any] = Field(..., description="Default values for missing fields")
    
    @field_validator('quality_rules')
    @classmethod
    def validate_quality_rules(cls, v):
        """Ensure quality_rules has required validation_rules section."""
        if 'validation_rules' not in v:
            raise ValueError("quality_rules must contain 'validation_rules' section")
        if not isinstance(v['validation_rules'], list):
            raise ValueError("validation_rules must be a list")
        return v
    
    @field_validator('defaults')
    @classmethod
    def validate_defaults(cls, v):
        """Ensure defaults has required defaults section."""
        if 'defaults' not in v:
            raise ValueError("defaults configuration must contain 'defaults' section")
        return v
    
    @field_validator('system_prompt_template')
    @classmethod
    def validate_system_prompt_template(cls, v):
        """Ensure system_prompt_template has required structure."""
        if 'prompt_structure' not in v:
            raise ValueError("system_prompt_template must contain 'prompt_structure' section")
        return v


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and JSON configuration files.
    Serves as the single source of truth for all configurations with validation.
    """
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH), 
        env_file_encoding="utf-8",
        extra="ignore"  # Ignore extra environment variables not defined in the model
    )
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., description="OpenAI API key", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", description="OpenAI model to use", alias="OPENAI_MODEL")

    # --- NEW ---
    # Image Generation Service Configuration
    IMAGE_API_KEY: Optional[str] = Field(None, description="Optional default API Key for the Text-to-Image Service (users can provide their own)")
    IMAGE_API_BASE_URL: str = Field(..., description="Base URL for the Text-to-Image API endpoint")
    IMAGE_GENERATION_MODEL: str = Field(default="stable-diffusion-xl-1024-v1-0", description="Default model for image generation")
    # --- END NEW ---
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Server host address", alias="HOST")
    port: int = Field(default=8000, description="Server port", alias="PORT")
    debug: bool = Field(default=False, description="Debug mode flag", alias="DEBUG")
    
    # Centralized System Configuration (initialized after object creation)
    _prompt_config: SystemPromptConfig = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._load_and_validate_json_configs()
    
    @property
    def prompt_config(self) -> SystemPromptConfig:
        """Access to the validated prompt configuration."""
        return self._prompt_config
    
    def _load_and_validate_json_configs(self):
        """Load and validate all JSON configuration files."""
        system_prompt_dir = SETTINGS_DIR / "system-prompt"
        
        if not system_prompt_dir.exists():
            raise FileNotFoundError(f"Configuration directory '{system_prompt_dir}' not found")
        
        json_files = {
            "system_prompt_template": "system_prompt_template.json",
            "enhancement_template": "enhancement_template.json",
            "quality_rules": "quality_rules.json",
            "stopping_power_rules": "stopping_power_rules.json",
            "anti_anomaly_rules": "anti_anomaly_rules.json",
            "defaults": "defaults.json"
        }
        
        config_data = {}
        
        # Load each JSON file with error handling
        for config_name, filename in json_files.items():
            file_path = system_prompt_dir / filename
            
            if not file_path.exists():
                raise FileNotFoundError(f"Required configuration file '{filename}' not found in {system_prompt_dir}")
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    config_data[config_name] = json.load(f)
                print(f"✅ Loaded {filename}")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON in {filename}: {e}")
            except Exception as e:
                raise RuntimeError(f"Failed to load {filename}: {e}")
        
        # Validate configuration using Pydantic model
        try:
            self._prompt_config = SystemPromptConfig(**config_data)
            print("✅ All configuration files validated successfully")
        except Exception as e:
            raise ValueError(f"Configuration validation failed: {e}")
    
    @property
    def system_prompt_template(self) -> Dict[str, Any]:
        """Backward compatibility access to system_prompt_template."""
        return self._prompt_config.system_prompt_template if self._prompt_config else {}
    
    @property
    def enhancement_template(self) -> Dict[str, Any]:
        """Backward compatibility access to enhancement_template."""
        return self._prompt_config.enhancement_template if self._prompt_config else {}
    
    @property
    def quality_rules(self) -> Dict[str, Any]:
        """Backward compatibility access to quality_rules."""
        return self._prompt_config.quality_rules if self._prompt_config else {}
    
    @property
    def stopping_power_rules(self) -> Dict[str, Any]:
        """Backward compatibility access to stopping_power_rules."""
        return self._prompt_config.stopping_power_rules if self._prompt_config else {}
    
    @property
    def anti_anomaly_rules(self) -> Dict[str, Any]:
        """Backward compatibility access to anti_anomaly_rules."""
        return self._prompt_config.anti_anomaly_rules if self._prompt_config else {}
    
    @property
    def defaults(self) -> Dict[str, Any]:
        """Backward compatibility access to defaults."""
        return self._prompt_config.defaults if self._prompt_config else {}


# Global settings instance - will fail fast if configuration is invalid
try:
    settings = Settings()
    print("🎯 MISSION 2: Centralized configuration system initialized successfully")
except Exception as e:
    print(f"💥 CRITICAL ERROR: Configuration system failed to initialize: {e}")
    raise
