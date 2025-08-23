"""
Integration tests for the PhotoeAI backend API endpoints.
Tests the main functionality of extract-and-fill and generate-brief endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)


class TestGeneratorEndpoints:
    """Test class for generator API endpoints."""
    
    def test_health_check(self):
        """Test the health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "PhotoeAI Backend"
    
    def test_root_endpoint(self):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "PhotoeAI Backend API"
        assert data["status"] == "running"
    
    def test_extract_and_fill_valid_request(self):
        """Test extract-and-fill endpoint with valid request."""
        test_request = {
            "user_request": "I want a professional photo of a luxury watch on a dark marble surface with dramatic lighting"
        }
        
        response = client.post("/api/v1/extract-and-fill", json=test_request)
        assert response.status_code == 200
        
        data = response.json()
        # Check that response has the expected structure
        assert "product_name" in data
        assert "user_request" in data
        assert "lighting_style" in data
        assert "environment" in data
        
        # Check that user_request is preserved
        assert data["user_request"] == test_request["user_request"]
    
    def test_extract_and_fill_empty_request(self):
        """Test extract-and-fill endpoint with empty request."""
        test_request = {
            "user_request": ""
        }
        
        response = client.post("/api/v1/extract-and-fill", json=test_request)
        assert response.status_code == 400
        assert "cannot be empty" in response.json()["detail"]
    
    def test_extract_and_fill_missing_field(self):
        """Test extract-and-fill endpoint with missing required field."""
        test_request = {}
        
        response = client.post("/api/v1/extract-and-fill", json=test_request)
        assert response.status_code == 422  # Validation error
    
    def test_generate_brief_valid_input(self):
        """Test generate-brief endpoint with valid wizard input."""
        # First get wizard input from extract-and-fill
        extract_request = {
            "user_request": "I need a photo of a red sports car in a modern garage with professional lighting"
        }
        
        extract_response = client.post("/api/v1/extract-and-fill", json=extract_request)
        assert extract_response.status_code == 200
        
        wizard_input = extract_response.json()
        
        # Now generate the brief
        response = client.post("/api/v1/generate-brief", json=wizard_input)
        assert response.status_code == 200
        
        data = response.json()
        assert "final_prompt" in data
        assert len(data["final_prompt"]) > 0
        assert isinstance(data["final_prompt"], str)
    
    def test_generate_brief_minimal_input(self):
        """Test generate-brief endpoint with minimal wizard input."""
        minimal_wizard_input = {
            "product_name": "Test Product",
            "user_request": "Simple product photo",
            "product_description": None,
            "key_features": None,
            "product_state": None,
            "shot_type": None,
            "framing": None,
            "compositional_rule": None,
            "negative_space": None,
            "lighting_style": None,
            "key_light_setup": None,
            "fill_light_setup": None,
            "rim_light_setup": None,
            "mood": None,
            "environment": None,
            "dominant_colors": None,
            "accent_colors": None,
            "props": None,
            "camera_type": None,
            "lens_type": None,
            "aperture_value": None,
            "shutter_speed_value": None,
            "iso_value": None,
            "visual_effect": None,
            "overall_style": None,
            "photographer_influences": None
        }
        
        response = client.post("/api/v1/generate-brief", json=minimal_wizard_input)
        assert response.status_code == 200
        
        data = response.json()
        assert "final_prompt" in data
        assert len(data["final_prompt"]) > 0
    
    def test_generate_brief_invalid_input(self):
        """Test generate-brief endpoint with invalid input."""
        invalid_input = {
            "product_name": None,
            "user_request": None
        }
        
        response = client.post("/api/v1/generate-brief", json=invalid_input)
        assert response.status_code == 400
        assert "must be provided" in response.json()["detail"]
    
    def test_preview_brief_endpoint(self):
        """Test the preview-brief endpoint."""
        # First get wizard input
        extract_request = {
            "user_request": "Photo of a smartphone on a clean white background"
        }
        
        extract_response = client.post("/api/v1/extract-and-fill", json=extract_request)
        assert extract_response.status_code == 200
        
        wizard_input = extract_response.json()
        
        # Get preview
        response = client.post("/api/v1/preview-brief", json=wizard_input)
        assert response.status_code == 200
        
        data = response.json()
        assert "initial_brief" in data
        assert "validation" in data
        assert "wizard_data" in data
        
        # Check validation structure
        validation = data["validation"]
        assert "is_valid" in validation
        assert "errors" in validation
        assert "warnings" in validation
    
    def test_full_workflow(self):
        """Test the complete workflow from user request to final brief."""
        # Step 1: Extract and autofill
        user_request = {
            "user_request": "I want a stunning photo of a gold necklace on black velvet with soft lighting that makes it look luxurious"
        }
        
        extract_response = client.post("/api/v1/extract-and-fill", json=user_request)
        assert extract_response.status_code == 200
        
        wizard_data = extract_response.json()
        
        # Step 2: Generate final brief
        brief_response = client.post("/api/v1/generate-brief", json=wizard_data)
        assert brief_response.status_code == 200
        
        brief_data = brief_response.json()
        assert "final_prompt" in brief_data
        
        # Basic content checks
        final_prompt = brief_data["final_prompt"]
        assert len(final_prompt) > 50  # Should be a substantial prompt
        assert isinstance(final_prompt, str)
        
        print(f"Generated brief length: {len(final_prompt)} characters")
        print(f"Sample of generated brief: {final_prompt[:200]}...")


# Pytest configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
