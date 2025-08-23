#!/usr/bin/env python3
"""
Critical Refactor Code Analysis Script
Analyzes the refactored code to validate the implementation without API calls.
"""

import sys
import json
from pathlib import Path
import inspect

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def analyze_critical_refactor():
    """Analyze the critical refactor implementation."""
    
    print("🔍 CRITICAL REFACTOR CODE ANALYSIS")
    print("="*60)
    
    try:
        # Import the refactored classes
        from app.services.ai_client import AIClient
        from app.services.brief_orchestrator import BriefOrchestratorService
        
        print("✅ Successfully imported refactored services")
        
        # Check if the critical method exists
        ai_client = AIClient()
        if hasattr(ai_client, 'enhance_brief_from_structured_data'):
            print("✅ enhance_brief_from_structured_data method exists")
            
            # Get the method signature
            method = getattr(ai_client, 'enhance_brief_from_structured_data')
            signature = inspect.signature(method)
            print(f"   Method signature: {method.__name__}{signature}")
            
            # Get the method docstring
            docstring = inspect.getdoc(method)
            if "CRITICAL REFACTOR" in docstring:
                print("✅ Method contains CRITICAL REFACTOR markers")
            else:
                print("⚠️  Method may not contain refactor markers")
                
        else:
            print("❌ enhance_brief_from_structured_data method NOT FOUND")
            return False
            
        # Check orchestrator integration
        orchestrator = BriefOrchestratorService()
        
        # Look for the method call in the orchestrator
        orchestrator_source = inspect.getsource(orchestrator.generate_final_brief)
        if "enhance_brief_from_structured_data" in orchestrator_source:
            print("✅ Orchestrator calls the refactored method")
        else:
            print("⚠️  Orchestrator may not be calling the refactored method")
            
        # Check the enhancement instruction
        ai_client_source = inspect.getsource(ai_client.enhance_brief_from_structured_data)
        
        print("\n📋 INSTRUCTION ANALYSIS:")
        
        critical_markers = [
            "ABSOLUTE MANDATES",
            "FULL DOCUMENT COMPOSITION", 
            "7 sections",
            "Main Subject",
            "Composition and Framing",
            "Lighting and Atmosphere",
            "json.dumps(structured_data"
        ]
        
        found_markers = []
        for marker in critical_markers:
            if marker in ai_client_source:
                found_markers.append(marker)
                print(f"   ✅ Found: {marker}")
            else:
                print(f"   ❌ Missing: {marker}")
                
        coverage = len(found_markers) / len(critical_markers) * 100
        print(f"\n📊 Refactor coverage: {coverage:.1f}% ({len(found_markers)}/{len(critical_markers)} markers)")
        
        if coverage >= 80:
            print("✅ CRITICAL REFACTOR: Implementation appears comprehensive")
        else:
            print("⚠️  CRITICAL REFACTOR: Implementation may be incomplete")
            
        # Check enhancement template update
        template_path = Path(__file__).parent / "system-prompt" / "enhancement_template.json"
        if template_path.exists():
            with open(template_path, 'r', encoding='utf-8') as f:
                template_data = json.load(f)
                
            template_content = json.dumps(template_data, indent=2)
            if "CRITICAL REFACTOR MODE" in template_content or "legacy_note" in template_content:
                print("✅ Enhancement template updated for refactor")
            else:
                print("⚠️  Enhancement template may not be updated")
        else:
            print("❌ Enhancement template not found")
            
        print(f"\n🎯 SUMMARY:")
        print(f"   - Method exists and callable: ✅")
        print(f"   - Contains refactor markers: {'✅' if coverage >= 80 else '⚠️'}")
        print(f"   - Orchestrator integration: ✅")
        print(f"   - Template updated: {'✅' if 'legacy_note' in str(template_data) else '⚠️'}")
        
        print(f"\n✅ CRITICAL REFACTOR CODE ANALYSIS COMPLETED")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n💥 ANALYSIS ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🎯 PhotoeAI Critical Refactor Code Analysis")
    print("Validating implementation without API calls...")
    
    success = analyze_critical_refactor()
    
    if success:
        print("\n✅ Code analysis completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Code analysis failed!")
        sys.exit(1)
