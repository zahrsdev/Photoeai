#!/usr/bin/env python3
"""
Check available models on Sumopod API
"""

import sys
import os
from openai import OpenAI

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings


def check_available_models():
    """Check what models are available with the current API key."""
    
    print("🤖 AVAILABLE MODELS CHECK")
    print("=" * 50)
    
    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.sumopod_api_base_url
        )
        
        # Get available models
        print("📋 Fetching available models...")
        models = client.models.list()
        
        print(f"✅ Found {len(models.data)} available models:")
        print()
        
        for i, model in enumerate(models.data, 1):
            print(f"{i:2d}. {model.id}")
        
        # Suggest the best model for PhotoeAI
        print()
        print("💡 RECOMMENDED MODELS FOR PHOTOEAI:")
        recommended = []
        
        for model in models.data:
            model_name = model.id.lower()
            if any(keyword in model_name for keyword in ['gpt-4', 'gpt-3.5', 'claude', 'llama']):
                recommended.append(model.id)
        
        if recommended:
            for rec in recommended[:3]:  # Show top 3
                print(f"   • {rec}")
        else:
            print(f"   • {models.data[0].id} (first available)")
        
        return models.data
        
    except Exception as e:
        print(f"❌ Failed to fetch models: {e}")
        return []


if __name__ == "__main__":
    available_models = check_available_models()
    
    if available_models:
        print()
        print("🔧 TO UPDATE MODEL IN .ENV FILE:")
        print("   Edit .env and change:")
        print(f"   OPENAI_MODEL={available_models[0].id}")
        print()
        print("   Or use environment variable:")
        print(f"   $env:OPENAI_MODEL='{available_models[0].id}'")
