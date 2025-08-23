# PhotoeAI Backend Engine

AI-powered backend engine for generating professional product photography briefs. This system transforms simple user text requests into comprehensive, world-class photography briefs using a sophisticated dual-LLM architecture.

## 🎯 Core Concept

The engine operates on a **hybrid architecture** using a Large Language Model (LLM) in two distinct roles:

1. **LLM as an Analyst**: Parses simple user requests and intelligently pre-fills a detailed data structure (`WizardInput`)
2. **LLM as a Creative Director**: Takes structured, validated data and creatively enhances it into a final, production-ready brief

## 🏗️ Architecture Overview

### Service-Oriented Architecture with Sequential Data Processing:

- **BriefOrchestratorService**: Main orchestrator coordinating the entire workflow
- **AIClient**: Handles all OpenAI API communications for both extraction and enhancement
- **PromptComposerService**: Manages autofill, template composition, and validation

### Two-Flow System:

**Flow 1 - Extract & Autofill** (`POST /api/v1/extract-and-fill`):
```
User Request → LLM Analysis → Structured Data → Autofill Defaults → Complete Wizard Input
```

**Flow 2 - Final Brief Generation** (`POST /api/v1/generate-brief`):
```
Wizard Input → Compose Brief → Validate → LLM Enhancement → Final Photography Brief
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API Key

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd photoeai-backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment:**
   ```bash
   # Edit .env file and add your OpenAI API key
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4
   DEBUG=True
   ```

5. **Run the application:**
   ```bash
   python run.py
   ```

   Or alternatively:
   ```bash
   uvicorn app.main:app --reload
   ```

### 🔗 API Documentation

Once running, access the interactive API documentation at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 🔑 API Key Requirements

**For Brief Generation:**
- Requires OpenAI API key (configured in `.env`)

**For Image Generation:**
- Users must provide their own image generation API key with each request
- Supports Stability AI and other compatible text-to-image services
- No server-side API key storage required for image generation

## 📋 API Endpoints

### Core Endpoints:

- **POST** `/api/v1/extract-and-fill` - Extract wizard data from user request
- **POST** `/api/v1/generate-brief` - Generate final photography brief
- **POST** `/api/v1/preview-brief` - Preview initial brief (debugging)
- **GET** `/api/v1/health` - Health check

### Image Generation Endpoints:

- **POST** `/api/v1/generate-image` - Generate an image from a final brief (requires user API key)
- **POST** `/api/v1/enhance-image` - Enhance a previously generated image (requires user API key)

### Example Usage:

```python
# 1. Extract and autofill wizard data
request = {
    "user_request": "I want a luxury watch photo on marble with dramatic lighting"
}
# POST /api/v1/extract-and-fill

# 2. Generate final brief (use returned wizard data)
wizard_data = {...}  # From step 1
# POST /api/v1/generate-brief

# 3. Generate image with user's API key
image_request = {
    "brief_prompt": "Final enhanced photography brief...",
    "user_api_key": "your-stability-ai-api-key",
    "negative_prompt": "blurry, low quality",
    "style_preset": "photorealistic"
}
# POST /api/v1/generate-image

# 4. Enhance existing image
enhancement_request = {
    "original_brief_prompt": "Final enhanced photography brief...",
    "generation_id": "gen_12345",
    "enhancement_instruction": "Make it warmer with golden lighting",
    "user_api_key": "your-stability-ai-api-key",
    "seed": 12345
}
# POST /api/v1/enhance-image
```

## 🧪 Testing

Run the integration tests:

```bash
pytest tests/ -v
```

Or run specific test:

```bash
pytest tests/test_generator.py::TestGeneratorEndpoints::test_full_workflow -v
```

## 📁 Project Structure

```
photoeai-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Configuration management
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py              # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── brief_orchestrator.py  # Main orchestrator
│   │   ├── prompt_composer.py     # Template & validation
│   │   └── ai_client.py           # OpenAI integration
│   └── routers/
│       ├── __init__.py
│       └── generator.py           # API endpoints
├── system-prompt/                 # JSON configuration files
│   ├── system_prompt_template.json
│   ├── enhancement_template.json
│   ├── quality_rules.json
│   ├── stopping_power_rules.json
│   ├── anti_anomaly_rules.json
│   └── defaults.json
├── tests/
│   ├── __init__.py
│   └── test_generator.py
├── .env                          # Environment variables
├── .gitignore
├── requirements.txt
├── run.py                        # Startup script
└── README.md
```

## ⚙️ Configuration Files

The `system-prompt/` directory contains JSON configuration files that control the AI behavior:

- **system_prompt_template.json**: Template structure for composing photography briefs
- **enhancement_template.json**: Instructions for the LLM Creative Director
- **quality_rules.json**: Validation rules for brief quality
- **stopping_power_rules.json**: Elements that make photos compelling
- **anti_anomaly_rules.json**: Common issues to avoid in generated images
- **defaults.json**: Default values for missing wizard fields

## 🔧 Development

### Key Technologies:

- **FastAPI**: Modern, fast web framework
- **Pydantic**: Data validation and settings management
- **OpenAI**: AI integration for text analysis and enhancement
- **Uvicorn**: ASGI server for high performance

### Environment Variables:

```bash
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4
HOST=0.0.0.0
PORT=8000
DEBUG=True
```

## 🚨 Important Notes

1. **API Key Security**: Never commit your OpenAI API key to version control
2. **CORS Configuration**: Update CORS settings for production deployment
3. **Error Handling**: The system includes comprehensive error handling and fallbacks
4. **Validation**: All inputs are validated using Pydantic models
5. **Logging**: Debug information is printed to console in development mode

## 🎯 Usage Examples

### Simple Product Photo Request:
```json
{
  "user_request": "Professional photo of a smartphone on white background"
}
```

### Complex Luxury Product Request:
```json
{
  "user_request": "Dramatic photo of a gold watch on black marble with cinematic lighting that shows every detail and makes it look expensive"
}
```

The system will automatically extract relevant photography parameters, apply defaults for missing information, and generate a comprehensive professional brief suitable for high-end product photography.

## 🔍 Monitoring & Health

- Health check endpoint: `GET /api/v1/health`
- Startup/shutdown events logged to console
- Comprehensive error handling with proper HTTP status codes

---

**Status**: ✅ Production Ready  
**Version**: 1.0.0  
**License**: MIT
