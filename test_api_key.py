#!/usr/bin/env python3
"""
API Key Test - Check if the current Sumopod API key is working
"""

import asyncio
import sys
import os
from openai import OpenAI

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config.settings import settings


async def test_api_key():
    """Test the current API key configuration."""
    
    print("🔑 API KEY CONFIGURATION TEST")
    print("=" * 60)
    
    # Display current configuration
    print(f"📋 Current Settings:")
    print(f"   API Key: {settings.openai_api_key[:20]}..." if len(settings.openai_api_key) > 20 else settings.openai_api_key)
    print(f"   Model: {settings.openai_model}")
    print(f"   Base URL: {settings.sumopod_api_base_url}")
    print()
    
    # Test API connection
    print("🔌 Testing API Connection...")
    
    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.sumopod_api_base_url
        )
        
        # Simple test request
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "user", "content": "Say 'API test successful'"}
            ],
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✅ API Connection SUCCESS!")
        print(f"   Response: {result}")
        
    except Exception as e:
        print(f"❌ API Connection FAILED!")
        print(f"   Error: {str(e)}")
        
        # Provide troubleshooting suggestions
        print()
        print("💡 TROUBLESHOOTING SUGGESTIONS:")
        print("   1. Check if your API key is valid and active")
        print("   2. Verify your Sumopod account has sufficient credits")
        print("   3. Confirm the base URL is correct: https://api.sumopod.com/v1")
        print("   4. Test with a different API key if available")
        print("   5. Check network connectivity and firewall settings")
        
        # Show how to update the API key
        print()
        print("🔧 TO UPDATE API KEY:")
        print("   Option 1: Edit .env file:")
        print("   OPENAI_API_KEY=your-new-api-key-here")
        print()
        print("   Option 2: Set environment variable:")
        print("   $env:OPENAI_API_KEY='your-new-api-key-here'  # PowerShell")
        print("   set OPENAI_API_KEY=your-new-api-key-here     # CMD")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_api_key())
