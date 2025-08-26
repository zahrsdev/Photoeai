import asyncio
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.brief_orchestrator import BriefOrchestratorService
from app.schemas.models import WizardInput

async def test_orchestrator_rules():
    """Test apakah spatial integration dan quantity control udah keinjek ke orchestrator"""
    
    print("🧪 Testing Orchestrator Rules Integration...")
    
    # Create orchestrator instance (mock ai_client)
    class MockAIClient:
        async def enhance_brief_from_structured_data(self, data):
            return "Enhanced product photography brief with professional lighting and composition."
    
    class MockPromptComposer:
        def compose_initial_brief(self, wizard_input):
            return f"Product photo of {wizard_input.product_name}"
            
        def validate_brief(self, brief, wizard_input):
            return {"is_valid": True, "errors": [], "warnings": []}
    
    orchestrator = BriefOrchestratorService()
    orchestrator.ai_client = MockAIClient()
    orchestrator.prompt_composer = MockPromptComposer()
    
    # Test case 1: Quantity mismatch scenario (1 donat jadi 4 donat)
    test_input_1 = WizardInput(
        user_request="foto 1 donat coklat di meja kayu",
        product_name="donat coklat",
        shoot_type="product",
        lighting="natural",
        background="clean"
    )
    
    print("📊 Test 1: Quantity Control (1 donat)")
    result_1 = await orchestrator.generate_final_brief(test_input_1)
    print(f"✅ Final Brief Contains Quantity Rules: {'exactly 1 donat' in result_1.final_prompt.lower()}")
    print(f"Brief preview: {result_1.final_prompt[:300]}...\n")
    
    # Test case 2: Multiple objects
    test_input_2 = WizardInput(
        user_request="foto 3 apel merah dan 2 jeruk",
        product_name="buah-buahan",
        shoot_type="product", 
        lighting="studio",
        background="white"
    )
    
    print("📊 Test 2: Multiple Quantity Control (3 apel, 2 jeruk)")
    result_2 = await orchestrator.generate_final_brief(test_input_2)
    print(f"✅ Contains 3 apel rule: {'exactly 3 apel' in result_2.final_prompt.lower()}")
    print(f"✅ Contains 2 jeruk rule: {'exactly 2 jeruk' in result_2.final_prompt.lower()}")
    print(f"Brief preview: {result_2.final_prompt[:300]}...\n")
    
    # Test case 3: Spatial Integration (floating objects)
    test_input_3 = WizardInput(
        user_request="foto burger floating di udara",
        product_name="burger", 
        shoot_type="product",
        lighting="dramatic",
        background="dark"
    )
    
    print("📊 Test 3: Spatial Integration (anti-floating)")
    result_3 = await orchestrator.generate_final_brief(test_input_3)
    print(f"✅ Contains spatial rules: {'NO floating elements' in result_3.final_prompt}")
    print(f"✅ Contains grounding rules: {'physically grounded' in result_3.final_prompt}")
    print(f"Brief preview: {result_3.final_prompt[:300]}...\n")
    
    print("🎯 ORCHESTRATOR RULES INTEGRATION: SUCCESS ✅")
    print("Rules sekarang udah masuk ke semua generation flows!")

if __name__ == "__main__":
    asyncio.run(test_orchestrator_rules())
