# Multi-Provider Image Generation Support

## Overview

The PhotoeAI backend now supports multiple image generation providers through a unified API interface. Users can provide their own API keys and specify their preferred provider.

## ✅ Supported Providers

### 1. **Stability AI**
- **Auto-detection**: `stability`, `stabilityai` in URL
- **API Format**: Standard Stability AI REST API
- **Models**: `stable-diffusion-xl-1024-v1-0`, `stable-diffusion-v1-5`, etc.
- **Response**: Base64 encoded images with seed information

**Example Configuration:**
```json
{
    "brief_prompt": "Professional product photo...",
    "user_api_key": "sk-your-stability-key",
    "provider": "stability_ai"
}
```

### 2. **OpenAI DALL-E**  
- **Auto-detection**: `openai`, `api.openai.com` in URL
- **API Format**: OpenAI Images API
- **Models**: `dall-e-3`, `dall-e-2`
- **Response**: Public URLs to generated images

**Example Configuration:**
```json
{
    "brief_prompt": "Professional product photo...",
    "user_api_key": "sk-your-openai-key",
    "provider": "openai_dalle"
}
```

### 3. **OpenRouter** 🆕
- **Auto-detection**: `openrouter` in URL
- **API Format**: OpenRouter unified API format
- **Models**: `stability-ai/stable-diffusion-xl`, `midjourney/midjourney`, etc.
- **Response**: URLs or base64 images depending on model

**Example Configuration:**
```json
{
    "brief_prompt": "Professional product photo...",
    "user_api_key": "sk-or-your-openrouter-key",
    "provider": "openrouter"
}
```

### 4. **Sumopod** 🆕
- **Auto-detection**: `sumopod` in URL  
- **API Format**: Sumopod API format
- **Models**: Various Stable Diffusion models
- **Response**: URLs or base64 images

**Example Configuration:**
```json
{
    "brief_prompt": "Professional product photo...",
    "user_api_key": "your-sumopod-key",
    "provider": "sumopod"
}
```

### 5. **Midjourney API** 🆕
- **Auto-detection**: `midjourney` in URL
- **API Format**: Midjourney API wrapper format
- **Models**: `midjourney`
- **Response**: Public URLs to generated images

**Example Configuration:**
```json
{
    "brief_prompt": "Professional product photo...",
    "user_api_key": "your-midjourney-key", 
    "provider": "midjourney"
}
```

### 6. **Generic Provider** 🆕
- **Fallback**: Used when provider cannot be auto-detected
- **API Format**: Generic REST API format
- **Compatible**: Works with most standard text-to-image APIs

## 🚀 How to Use

### Method 1: Auto-Detection (Recommended)
The system automatically detects the provider based on your `IMAGE_API_BASE_URL`:

```bash
# Set in .env file
IMAGE_API_BASE_URL=https://api.stability.ai/v1/generation
```

Then make requests without specifying provider:
```json
POST /api/v1/generate-image
{
    "brief_prompt": "Professional product photo...",
    "user_api_key": "your-api-key"
}
```

### Method 2: Manual Provider Selection
Override the auto-detection by specifying the provider:

```json
POST /api/v1/generate-image
{
    "brief_prompt": "Professional product photo...",
    "user_api_key": "your-api-key",
    "provider": "openai_dalle"
}
```

## 🔧 Configuration Examples

### For Stability AI:
```bash
IMAGE_API_BASE_URL=https://api.stability.ai/v1/generation
IMAGE_GENERATION_MODEL=stable-diffusion-xl-1024-v1-0
```

### For OpenAI DALL-E:
```bash
IMAGE_API_BASE_URL=https://api.openai.com/v1
IMAGE_GENERATION_MODEL=dall-e-3
```

### For OpenRouter:
```bash
IMAGE_API_BASE_URL=https://openrouter.ai/api/v1
IMAGE_GENERATION_MODEL=stability-ai/stable-diffusion-xl
```

### For Sumopod:
```bash
IMAGE_API_BASE_URL=https://api.sumopod.com/v1
IMAGE_GENERATION_MODEL=stable-diffusion-xl
```

## 📋 Provider-Specific Features

| Provider | Negative Prompts | Seeds | Custom Models | Response Format |
|----------|-----------------|-------|---------------|----------------|
| Stability AI | ✅ | ✅ | ✅ | Base64 |
| OpenAI DALL-E | ❌ | ❌ | ✅ | URL |
| OpenRouter | ✅ | ✅ | ✅ | URL/Base64 |
| Sumopod | ✅ | ✅ | ✅ | URL/Base64 |
| Midjourney | ❌ | ❌ | ❌ | URL |
| Generic | ✅ | ✅ | ✅ | Varies |

## 🔑 API Key Management

Users provide their own API keys for each service:

- **Stability AI**: Get from https://platform.stability.ai/
- **OpenAI**: Get from https://platform.openai.com/
- **OpenRouter**: Get from https://openrouter.ai/
- **Sumopod**: Get from your Sumopod account
- **Midjourney**: Get from Midjourney API service

## ⚠️ Error Handling

The system provides detailed error messages for:
- Invalid API keys
- Unsupported models
- Rate limiting
- Provider-specific errors
- Network connectivity issues

## 🧪 Testing Different Providers

```python
# Test with different providers
providers = ["stability_ai", "openai_dalle", "openrouter", "sumopod"]

for provider in providers:
    response = requests.post("/api/v1/generate-image", json={
        "brief_prompt": "Test prompt",
        "user_api_key": f"your-{provider}-key",
        "provider": provider
    })
```

## 🔄 Migration Guide

### From Single Provider to Multi-Provider:

1. **Update requests** to include `provider` field (optional)
2. **Test with your preferred provider** 
3. **Update API key management** in your frontend
4. **Handle provider-specific responses** in your UI

### Backward Compatibility:
- Existing integrations continue to work
- Auto-detection maintains seamless operation
- No breaking changes to core API structure

## 📈 Performance Considerations

- **Auto-detection**: Minimal overhead (URL parsing)
- **Response parsing**: Optimized for each provider format
- **Error recovery**: Graceful fallback to generic parsing
- **Timeout handling**: Provider-specific timeout values
