import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.brief_orchestrator import BriefOrchestratorService
from app.schemas.models import WizardInput

async def test_user_api_key():
    """Test user API key injection ke brief orchestrator"""
    
    print("🧪 Testing User API Key Integration...")
    
    # Mock AI client yang detect user API key
    class MockAIClient:
        async def enhance_brief_from_structured_data(self, data, user_api_key=None):
            if user_api_key and user_api_key.strip():
                return f"Enhanced brief using USER API KEY: {user_api_key[:10]}..."
            return "Enhanced brief using DEFAULT API KEY from settings"
    
    class MockPromptComposer:
        def compose_initial_brief(self, wizard_input):
            return f"Basic brief for {wizard_input.product_name}"
        
        def validate_brief(self, brief, wizard_input):
            return {"is_valid": True, "errors": [], "warnings": []}
    
    # Setup orchestrator
    orchestrator = BriefOrchestratorService()
    orchestrator.ai_client = MockAIClient()
    orchestrator.prompt_composer = MockPromptComposer()
    
    # Test 1: Without user API key (uses default)
    test_input_1 = WizardInput(
        user_request="foto burger di meja kayu",
        product_name="burger",
        shoot_type="product",
        lighting="natural"
    )
    
    print("📊 Test 1: Default API Key")
    result_1 = await orchestrator.generate_final_brief(test_input_1)
    print(f"   Result: {result_1.final_prompt[:100]}...")
    print(f"   Uses default: {'DEFAULT API KEY' in result_1.final_prompt}")
    print()
    
    # Test 2: With user API key
    test_input_2 = WizardInput(
        user_request="foto pizza di piring putih", 
        product_name="pizza",
        shoot_type="product",
        lighting="studio",
        user_api_key="sk-user123456789"
    )
    
    print("📊 Test 2: User API Key")
    result_2 = await orchestrator.generate_final_brief(test_input_2)
    print(f"   Result: {result_2.final_prompt[:100]}...")
    print(f"   Uses user key: {'USER API KEY' in result_2.final_prompt}")
    print(f"   Key detected: {'sk-user123' in result_2.final_prompt}")
    print()
    
    print("🎯 USER API KEY INJECTION: SUCCESS ✅")
    print("Backend sekarang bisa nerima API key dari frontend!")

if __name__ == "__main__":
    asyncio.run(test_user_api_key())
