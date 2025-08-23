# PhotoEAI Streamlit Application

A user-friendly web interface for the PhotoEAI backend, providing intuitive workflows for generating professional product photography briefs and images.

## 🚀 Quick Start

### Prerequisites
1. Ensure the PhotoEAI backend server is running:
   ```bash
   python run.py
   ```
   The backend should be accessible at `http://localhost:8000`

2. Install Streamlit if not already installed:
   ```bash
   pip install -r requirements.txt
   ```

### Running the App

**Option 1: Using the batch file (Windows)**
```bash
run_streamlit.bat
```

**Option 2: Direct command**
```bash
streamlit run app.py
```

The Streamlit app will be available at `http://localhost:8501`

## 🎯 Features & Workflows

### 1. 🚀 Simple Mode (Auto-Generate)
- **Perfect for**: Quick brief generation with minimal input
- **How it works**: 
  - Enter a simple text description of your photography needs
  - AI automatically extracts and fills all photography parameters
  - Get an enhanced professional brief in seconds
- **Example**: "I need to photograph luxury skincare products for an elegant e-commerce listing"

### 2. ⚙️ Advanced Mode (Manual Config)
- **Perfect for**: Professional photographers who want complete control
- **How it works**:
  - Manually configure all photography parameters
  - Six comprehensive sections covering every aspect:
    - Main Subject & Story
    - Composition & Framing  
    - Lighting & Atmosphere
    - Background & Setting
    - Camera & Lens Settings
    - Style & Post-Production
- **Output**: Highly detailed, customized photography brief

### 3. 📝 Direct Text Generation
- **Perfect for**: Custom text generation with various AI providers
- **Features**:
  - Support for multiple AI providers (OpenAI, Gemini, OpenRouter, SumoPod)
  - Configurable parameters (temperature, max tokens, model selection)
  - Direct API key integration
  - Generation metadata and download options

### 4. 🖼️ Image Generation
- **Perfect for**: Converting photography briefs into actual images
- **Features**:
  - Multiple image generation providers
  - Various style presets (photorealistic, artistic, cinematic, etc.)
  - Negative prompt support
  - Image URL and metadata display
  - Compatible with briefs generated from other workflows

### 5. ℹ️ About & Help
- Comprehensive documentation
- Server status monitoring
- Technical details and troubleshooting

## 🔧 Configuration

### API Keys
The app requires API keys for the AI services you want to use:
- **OpenAI**: For GPT models and DALL-E
- **Google Gemini**: For Gemini models  
- **OpenRouter**: For access to multiple models
- **SumoPod**: For their AI services

### Backend Connection
The app connects to the PhotoEAI backend at `http://localhost:8000/api/v1` by default.

To change this, modify the `API_BASE_URL` constant in `app.py`:
```python
API_BASE_URL = "http://your-backend-url:port/api/v1"
```

## 📋 Available Endpoints

The Streamlit app interfaces with these backend endpoints:
- `POST /api/v1/extract-and-fill` - Extract structured data from user requests
- `POST /api/v1/generate-brief` - Generate enhanced photography briefs
- `POST /api/v1/text/generate` - Direct text generation
- `POST /api/v1/image/generate` - Image generation from briefs

## 🎨 UI Features

### Interactive Forms
- Dynamic form validation
- Real-time parameter updates
- Progress indicators for API calls
- Error handling and user feedback

### Data Display
- Formatted JSON viewers for technical details
- Expandable sections for metadata
- Copy-to-clipboard functionality
- Download buttons for generated content

### Responsive Design
- Wide layout for complex forms
- Column-based layouts for better organization
- Sidebar navigation
- Status indicators

## 🛠️ Troubleshooting

### Common Issues

**1. "Connection Error" or "API Error"**
- Ensure the backend server is running on `localhost:8000`
- Check that all required dependencies are installed
- Verify API keys are correct and have sufficient credits

**2. "Import streamlit could not be resolved"**
- Install Streamlit: `pip install streamlit`
- Or install all requirements: `pip install -r requirements.txt`

**3. "Server Status: 🔴 Disconnected"**
- Start the backend server: `python run.py`
- Check if port 8000 is available
- Review backend logs for errors

**4. Image generation takes too long**
- Image generation can take 1-3 minutes depending on the provider
- The app has extended timeouts for image endpoints
- Check your API provider's status and rate limits

### Development Mode

For development with auto-reload:
```bash
streamlit run app.py --server.runOnSave true
```

## 📁 File Structure

```
photoeai-backend/
├── app.py                 # Main Streamlit application
├── run_streamlit.bat      # Windows batch file to run the app
├── requirements.txt       # Updated with Streamlit dependency
├── app/                   # Backend FastAPI application
│   ├── main.py           # FastAPI main app
│   ├── routers/          # API endpoints
│   ├── services/         # Business logic
│   └── schemas/          # Data models
└── README_STREAMLIT.md   # This file
```

## 🔄 Integration with Backend

The Streamlit app is designed to work seamlessly with the PhotoEAI backend:

1. **Data Models**: Uses the same Pydantic models for request/response validation
2. **Error Handling**: Provides user-friendly error messages for API failures
3. **Workflow Support**: Implements all backend workflows with intuitive UI
4. **Real-time Status**: Shows backend connectivity status
5. **Development Friendly**: Easy to extend with new endpoints and features

## 🚀 Production Deployment

For production deployment:

1. **Backend**: Deploy the FastAPI backend to your server
2. **Frontend**: Update `API_BASE_URL` to point to your production backend
3. **Streamlit**: Deploy using Streamlit Cloud, Docker, or your preferred platform
4. **Security**: Use environment variables for API keys in production

Example production configuration:
```python
import os
API_BASE_URL = os.getenv("PHOTOEAI_API_URL", "http://localhost:8000/api/v1")
```

## 📝 License

This Streamlit application is part of the PhotoEAI project and follows the same licensing terms.
