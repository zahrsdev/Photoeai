"""
Prompt Composer Service for handling autofill, composition, and validation of photography briefs.
"""

import json
from typing import Dict, Any
from loguru import logger
from app.schemas.models import WizardInput
from app.config.settings import settings


class PromptComposerService:
    """
    Service responsible for composing and validating photography briefs.
    Handles autofill with defaults, template composition, and quality validation.
    """
    
    def __init__(self):
        """Initialize the service with configuration from settings."""
        self.defaults = settings.defaults.get("defaults", {})
        self.system_prompt_template = settings.system_prompt_template
        self.quality_rules = settings.quality_rules
    
    def autofill_wizard_input(self, wizard_data: Dict[str, Any]) -> WizardInput:
        """
        Autofill missing wizard input fields with default values.
        
        Args:
            wizard_data: Dictionary containing wizard input data (may have None/null values)
            
        Returns:
            WizardInput object with all fields filled (using defaults where necessary)
        """
        data_id = id(wizard_data)  # Simple data tracking
        
        logger.info(f"🔧 Starting autofill process [ID: {data_id}]", extra={
            "data_id": data_id,
            "input_fields": list(wizard_data.keys()),
            "operation": "autofill_wizard_input"
        })
        
        # Create a copy of the wizard data
        filled_data = wizard_data.copy()
        fields_filled = []
        
        # Fill in any None or missing values with defaults
        for key, default_value in self.defaults.items():
            if key not in filled_data or filled_data[key] is None:
                filled_data[key] = default_value
                fields_filled.append(key)
        
        logger.info(f"✅ Autofill completed [ID: {data_id}]", extra={
            "data_id": data_id,
            "fields_filled": fields_filled,
            "total_fields": len(filled_data),
            "defaults_applied": len(fields_filled),
            "operation": "autofill_wizard_input",
            "status": "success"
        })
        
        # Convert to WizardInput model
        return WizardInput(**filled_data)
    
    def compose_initial_brief(self, wizard_input: WizardInput) -> str:
        """
        Compose an initial photography brief using the system prompt template.
        
        Args:
            wizard_input: Complete wizard input data
            
        Returns:
            Composed initial brief text
        """
        brief_id = id(wizard_input)  # Simple brief tracking
        
        logger.info(f"📝 Starting initial brief composition [ID: {brief_id}]", extra={
            "brief_id": brief_id,
            "product_name": wizard_input.product_name,
            "operation": "compose_initial_brief"
        })
        
        try:
            # Convert wizard input to dictionary for template replacement
            wizard_dict = wizard_input.model_dump()
            
            # Get the prompt structure from template
            prompt_structure = self.system_prompt_template.get("prompt_structure", {})
            
            logger.debug(f"📋 Retrieved prompt template [ID: {brief_id}]", extra={
                "brief_id": brief_id,
                "template_sections": list(prompt_structure.keys()),
                "wizard_fields": list(wizard_dict.keys())
            })
            
            # Build the brief by processing each section
            brief_sections = []
            
            # Introduction
            if "introduction" in prompt_structure:
                brief_sections.append(prompt_structure["introduction"])
                brief_sections.append("")  # Empty line
            
            # Process each section
            section_order = [
                "main_subject",
                "composition_and_framing", 
                "lighting_and_atmosphere",
                "background_and_setting",
                "camera_and_lens",
                "style_and_post_production"
            ]
            
            sections_processed = []
            for section_name in section_order:
                if section_name in prompt_structure:
                    section = prompt_structure[section_name]
                    section_text = self._process_section(section, wizard_dict)
                    if section_text:
                        brief_sections.append(section_text)
                        brief_sections.append("")  # Empty line between sections
                        sections_processed.append(section_name)
            
            # Join all sections
            complete_brief = "\n".join(brief_sections).strip()
            
            logger.info(f"✅ Initial brief composition completed [ID: {brief_id}]", extra={
                "brief_id": brief_id,
                "product_name": wizard_input.product_name,
                "sections_processed": sections_processed,
                "brief_length": len(complete_brief),
                "operation": "compose_initial_brief",
                "status": "success"
            })
            
            return complete_brief
            
        except Exception as e:
            logger.error(f"💥 Critical error in brief composition [ID: {brief_id}]", extra={
                "brief_id": brief_id,
                "product_name": wizard_input.product_name,
                "exception": str(e),
                "exception_type": type(e).__name__,
                "operation": "compose_initial_brief",
                "status": "error"
            })
            return f"Error composing brief: {str(e)}"
    
    def _process_section(self, section: Dict[str, Any], wizard_dict: Dict[str, Any]) -> str:
        """
        Process a section of the prompt template, replacing placeholders with wizard data.
        
        Args:
            section: Section dictionary from the template
            wizard_dict: Wizard input data as dictionary
            
        Returns:
            Processed section text
        """
        section_lines = []
        
        # Add header if present
        if "header" in section:
            section_lines.append(section["header"])
        
        # Process all other keys in the section
        for key, value in section.items():
            if key != "header" and isinstance(value, str):
                # Replace template variables
                processed_line = self._replace_template_variables(value, wizard_dict)
                section_lines.append(processed_line)
        
        return "\n".join(section_lines)
    
    def _replace_template_variables(self, text: str, wizard_dict: Dict[str, Any]) -> str:
        """
        Replace template variables in format {{variable_name}} with actual values.
        
        Args:
            text: Text containing template variables
            wizard_dict: Dictionary with variable values
            
        Returns:
            Text with variables replaced
        """
        import re
        
        # Find all template variables in the format {{variable_name}}
        variables = re.findall(r'\{\{(\w+)\}\}', text)
        
        result = text
        for variable in variables:
            if variable in wizard_dict and wizard_dict[variable] is not None:
                value = str(wizard_dict[variable])
                result = result.replace(f"{{{{{variable}}}}}", value)
            else:
                # If variable not found, replace with placeholder
                result = result.replace(f"{{{{{variable}}}}}", f"[{variable}]")
        
        return result
    
    def validate_extracted_data(self, extracted_data: Dict[str, Any]) -> list:
        """
        Validate extracted data against quality rules.
        
        Args:
            extracted_data: Dictionary containing extracted wizard data
            
        Returns:
            List of validation error messages. Empty list means valid data.
        """
        validation_errors = []
        
        try:
            # Get validation rules
            validation_rules = self.quality_rules.get("validation_rules", [])
            
            for rule in validation_rules:
                rule_name = rule.get("rule_name", "Unknown Rule")
                
                if rule_name == "Check for Completeness":
                    # Check required fields
                    required_fields = rule.get("required_fields", [])
                    for field in required_fields:
                        if field not in extracted_data or extracted_data[field] is None or extracted_data[field] == "":
                            validation_errors.append(f"Required field '{field}' is missing or empty")
                
                elif rule_name == "Check for Vague Language":
                    # Check for banned words
                    banned_words = rule.get("banned_words", {})
                    for field, banned_list in banned_words.items():
                        if field in extracted_data and extracted_data[field]:
                            value = str(extracted_data[field]).lower()
                            for banned_word in banned_list:
                                if banned_word.lower() in value:
                                    validation_errors.append(f"Vague term '{banned_word}' found in '{field}'. Consider being more specific.")
                
                elif rule_name == "Check for Contradictions":
                    # Check logical consistency
                    conditions = rule.get("conditions", [])
                    for condition in conditions:
                        if_condition = condition.get("if", {})
                        then_condition = condition.get("then", {})
                        error_message = condition.get("error", "Logical inconsistency detected")
                        
                        # Simple condition checking (can be expanded)
                        if self._check_condition(if_condition, extracted_data):
                            if not self._check_condition(then_condition, extracted_data):
                                validation_errors.append(error_message)
            
        except Exception as e:
            validation_errors.append(f"Validation system error: {str(e)}")
        
        return validation_errors

    def validate_brief(self, brief: str, wizard_input: WizardInput) -> Dict[str, Any]:
        """
        Validate the composed brief against quality rules.
        
        Args:
            brief: The composed brief text
            wizard_input: The wizard input data
            
        Returns:
            Dictionary containing validation results
        """
        validation_result = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        try:
            # Get validation rules
            validation_rules = self.quality_rules.get("validation_rules", [])
            wizard_dict = wizard_input.model_dump()
            
            for rule in validation_rules:
                rule_name = rule.get("rule_name", "Unknown Rule")
                
                if rule_name == "Check for Completeness":
                    # Check required fields
                    required_fields = rule.get("required_fields", [])
                    for field in required_fields:
                        if field not in wizard_dict or wizard_dict[field] is None or wizard_dict[field] == "":
                            validation_result["errors"].append(f"Required field '{field}' is missing or empty")
                    
                    # Check optional recommended fields (as warnings, not errors)
                    optional_fields = rule.get("optional_recommended_fields", [])
                    for field in optional_fields:
                        if field not in wizard_dict or wizard_dict[field] is None or wizard_dict[field] == "":
                            validation_result["warnings"].append(f"Recommended field '{field}' is missing - brief quality may be improved with this field")
                
                elif rule_name == "Check for Vague Language":
                    # Check for banned words
                    banned_words = rule.get("banned_words", {})
                    for field, banned_list in banned_words.items():
                        if field in wizard_dict and wizard_dict[field]:
                            value = str(wizard_dict[field]).lower()
                            for banned_word in banned_list:
                                if banned_word.lower() in value:
                                    validation_result["warnings"].append(f"Vague term '{banned_word}' found in '{field}'. Consider being more specific.")
                
                elif rule_name == "Check for Color Preservation":
                    # Check color preservation
                    color_validation = rule.get("color_validation", {})
                    
                    # Check if colors are present
                    if color_validation.get("required_color_presence", False):
                        if "dominant_colors" not in wizard_dict or not wizard_dict["dominant_colors"]:
                            validation_result["warnings"].append("No product colors specified - color preservation cannot be verified")
                        else:
                            colors_str = str(wizard_dict["dominant_colors"]).lower()
                            
                            # Check for generic colors
                            avoid_colors = color_validation.get("avoid_generic_colors", [])
                            for generic_color in avoid_colors:
                                if generic_color in colors_str:
                                    validation_result["warnings"].append(f"Generic color term '{generic_color}' found - consider more specific product colors")
                            
                            # Check for preservation indicators (good)
                            preservation_indicators = color_validation.get("color_preservation_indicators", [])
                            has_preservation_indicator = any(indicator in colors_str for indicator in preservation_indicators)
                            
                            # Check for warning keywords (bad)
                            warning_keywords = color_validation.get("warning_keywords", [])
                            has_warning_keyword = any(keyword in colors_str for keyword in warning_keywords)
                            
                            if has_warning_keyword:
                                validation_result["errors"].append("Color stylization detected - ensure original product colors are preserved")
                            elif not has_preservation_indicator and len(preservation_indicators) > 0:
                                validation_result["warnings"].append("Consider using more natural color descriptions to ensure authenticity")
                
                elif rule_name == "Check for Contradictions":
                    # Check logical consistency
                    conditions = rule.get("conditions", [])
                    for condition in conditions:
                        if_condition = condition.get("if", {})
                        then_condition = condition.get("then", {})
                        error_message = condition.get("error", "Logical inconsistency detected")
                        
                        # Simple condition checking (can be expanded)
                        if self._check_condition(if_condition, wizard_dict):
                            if not self._check_condition(then_condition, wizard_dict):
                                validation_result["errors"].append(error_message)
            
            # Set overall validity
            if validation_result["errors"]:
                validation_result["is_valid"] = False
            
        except Exception as e:
            print(f"Error in validate_brief: {e}")
            validation_result["errors"].append(f"Validation error: {str(e)}")
            validation_result["is_valid"] = False
        
        return validation_result
    
    def _check_condition(self, condition: Dict[str, Any], wizard_dict: Dict[str, Any]) -> bool:
        """
        Check if a condition is met based on wizard data.
        
        Args:
            condition: Condition dictionary to check
            wizard_dict: Wizard input data
            
        Returns:
            True if condition is met, False otherwise
        """
        for field, expected in condition.items():
            if field not in wizard_dict:
                return False
            
            actual_value = wizard_dict[field]
            
            if isinstance(expected, dict):
                # Handle complex conditions like {"min": 50}
                if "min" in expected and actual_value and float(actual_value) < expected["min"]:
                    return False
                if "max" in expected and actual_value and float(actual_value) > expected["max"]:
                    return False
                if "not_in" in expected and actual_value in expected["not_in"]:
                    return False
            else:
                # Simple equality check
                if actual_value != expected:
                    return False
        
        return True
