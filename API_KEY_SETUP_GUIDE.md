# 🔑 API Key Configuration Guide

## Current Status
✅ **API Key Status**: Ready for configuration  
💡 **Setup Required**: Set your API key using one of the methods below

## Quick Solutions

### Option 1: Get Valid Sumopod API Key
1. **Visit Sumopod**: https://sumopod.com
2. **Create Account** or log into existing account
3. **Generate API Key** from dashboard
4. **Update Configuration** (see methods below)

### Option 2: Use OpenAI Directly (Alternative)
If you have an OpenAI API key, you can switch to direct OpenAI API:

1. **Update .env file**:
```env
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4
SUMOPOD_API_BASE_URL=https://api.openai.com/v1
```

2. **Or set environment variable**:
```powershell
$env:OPENAI_API_KEY='sk-your-openai-key-here'
$env:SUMOPOD_API_BASE_URL='https://api.openai.com/v1'
```

## Configuration Methods

### Method 1: Edit .env File (Recommended)
```bash
# Open .env file and update:
OPENAI_API_KEY=sk-your-new-valid-key-here
```

### Method 2: Environment Variable (Temporary)
```powershell
# PowerShell
$env:OPENAI_API_KEY='sk-your-new-valid-key-here'

# Then restart your application
python run.py
```

### Method 3: Direct Code Update (Not Recommended)
You could hardcode it in settings.py, but this is insecure.

## Verification Steps

### 1. Test API Key
```bash
python test_api_key.py
```

### 2. Test Full System
```bash
python test_madu_trigona_reference.py
```

### 3. Expected Success Output
```
🔌 Testing API Connection...
✅ API Connection SUCCESS!
   Response: API test successful

🎬 Testing Brief Generation Workflow...
✅ Brief generation completed
📄 Final prompt length: 4500+ characters
```

## Cost Considerations

### Sumopod Pricing
- Usually cheaper than direct OpenAI API
- Check current rates at sumopod.com

### OpenAI Direct Pricing
- GPT-4: ~$0.03 per 1K tokens input, ~$0.06 per 1K tokens output
- For PhotoeAI brief generation: ~$0.10-0.20 per request

## Troubleshooting

### Common Issues
1. **Invalid API Key**: Get new key from provider
2. **Insufficient Credits**: Add credits to your account  
3. **Network Issues**: Check firewall/proxy settings
4. **Rate Limits**: Wait and retry, or upgrade plan

### Test Commands
```bash
# Test current configuration
python test_api_key.py

# Test with new key (temporary)
$env:OPENAI_API_KEY='new-key-here'; python test_api_key.py

# Full system test
python test_madu_trigona_reference.py
```

## Next Steps

1. **🔑 Get Valid API Key** from Sumopod or OpenAI
2. **⚙️ Update Configuration** using Method 1 above
3. **🧪 Run Tests** to verify everything works
4. **🚀 Enjoy Full AI Enhancement** for your photography briefs!

---

**Once you have a valid API key, your PhotoeAI system will provide:**
- ✅ AI-powered data extraction from user requests
- ✅ Intelligent brief enhancement and creative direction  
- ✅ Professional-grade photography briefs
- ✅ Complete dual-LLM workflow (Analyst + Creative Director)
