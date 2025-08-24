"""
PhotoEAI Enhanced Frontend with Brief Generation Integration
===========================================================

A comprehensive interface that integrates with the enhanced backend:
1. Brief Generation Workflow (Extract → Fill → Generate Brief)
2. Image Generation with Enhanced Briefs
3. Multi-language support with English enforcement
4. Comprehensive brief display and editing
"""

import streamlit as st
import requests
import json
from typing import Optional, Dict, Any
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 120

def check_server_running(host="localhost", port=8000, timeout=5):
    """Check if the backend server is running"""
    try:
        response = requests.get(f"http://{host}:{port}/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def extract_and_fill(user_request: str) -> Optional[Dict]:
    """Extract wizard data from user request"""
    try:
        payload = {"user_request": user_request}
        response = requests.post(
            f"{API_BASE_URL}/extract-and-fill",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Extraction failed: {response.json().get('detail', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error during extraction: {str(e)}")
        return None

def generate_brief(wizard_data: Dict) -> Optional[Dict]:
    """Generate enhanced brief from wizard data"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/generate-brief-from-prompt",
            json=wizard_data,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Brief generation failed: {response.json().get('detail', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error during brief generation: {str(e)}")
        return None

def generate_image(prompt: str, api_key: str, provider: str = None) -> Optional[Dict]:
    """Generate image using the enhanced brief"""
    try:
        payload = {
            "brief_prompt": prompt,
            "user_api_key": api_key
        }
        
        if provider:
            payload["provider"] = provider
            
        response = requests.post(
            f"{API_BASE_URL}/generate-image",
            json=payload,
            timeout=TIMEOUT
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Image generation failed: {response.json().get('detail', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error during image generation: {str(e)}")
        return None

def main():
    """Main Streamlit application"""
    
    # Page configuration
    st.set_page_config(
        page_title="PhotoeAI - Enhanced Brief Generator",
        page_icon="📸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS
    st.markdown("""
    <style>
        .main-header {
            text-align: center;
            padding: 2rem 0;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .workflow-step {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 5px;
        }
        .brief-container {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border: 1px solid #e9ecef;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📸 PhotoeAI - Enhanced Brief Generator</h1>
        <p>Professional photography briefs with AI enhancement and multi-language support</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check server status
    if not check_server_running():
        st.error("❌ Backend server is not running. Please start the server first.")
        st.info("💡 Run: `python app.py` or `uvicorn app.main:app --reload` in your backend directory")
        return
    else:
        st.success("✅ Backend server is running")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # API Key
        api_key = st.text_input(
            "🔑 API Key",
            type="password",
            placeholder="Enter your API key",
            help="Required for image generation"
        )
        
        # Provider selection
        provider = st.selectbox(
            "🤖 AI Provider",
            options=["openai"],
            index=0,
            help="Choose your preferred AI image generation provider"
        )
        
        st.divider()
        
        # Workflow explanation
        st.markdown("""
        ### 📋 Workflow Steps
        1. **Input Request** - Enter your idea in any language
        2. **AI Analysis** - Extract structured data
        3. **Brief Generation** - Create comprehensive photography brief
        4. **Image Creation** - Generate professional images
        """)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Brief Generator", "📸 Image Generator", "📊 Results"])
    
    with tab1:
        st.header("🎯 Professional Brief Generator")
        
        # Step 1: User Input
        st.markdown("""
        <div class="workflow-step">
            <h4>Step 1: Describe Your Photography Vision</h4>
            <p>Enter your photography idea in any language - it will be converted to a professional English brief</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.form("brief_generation_form"):
            # User request input
            user_request = st.text_area(
                "💭 **Your Photography Vision**",
                placeholder="Example: Saya ingin foto produk parfum mewah dengan pencahayaan dramatis...\nOr: I want a luxury perfume photo with dramatic lighting...",
                height=100,
                help="Describe your photography vision in any language"
            )
            
            # Generate brief button
            generate_brief_clicked = st.form_submit_button(
                "🚀 **Generate Professional Brief**",
                type="primary",
                use_container_width=True
            )
        
        # Handle brief generation
        if generate_brief_clicked:
            if not user_request.strip():
                st.error("❌ Please enter your photography vision")
            else:
                # Step 1: Extract and fill wizard data
                st.markdown("""
                <div class="workflow-step">
                    <h4>Step 2: AI Analysis & Data Extraction</h4>
                </div>
                """, unsafe_allow_html=True)
                
                with st.spinner("🔍 Analyzing your request and extracting structured data..."):
                    wizard_data = extract_and_fill(user_request.strip())
                
                if wizard_data:
                    # Display extracted data
                    with st.expander("📋 Extracted Structured Data", expanded=False):
                        st.json(wizard_data)
                    
                    # Step 2: Generate comprehensive brief
                    st.markdown("""
                    <div class="workflow-step">
                        <h4>Step 3: Generating Comprehensive Photography Brief</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    with st.spinner("✨ Generating comprehensive professional brief (English only)..."):
                        brief_result = generate_brief(wizard_data)
                    
                    if brief_result:
                        # Store results in session state
                        st.session_state.wizard_data = wizard_data
                        st.session_state.brief_result = brief_result
                        st.session_state.original_request = user_request.strip()
                        
                        # Display success
                        st.success("✅ Professional brief generated successfully!")
                        
                        # Display brief
                        st.markdown("""
                        <div class="workflow-step">
                            <h4>Step 4: Your Professional Photography Brief</h4>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.container():
                            st.markdown('<div class="brief-container">', unsafe_allow_html=True)
                            
                            # Brief metrics
                            brief_text = brief_result.get("final_prompt", "")
                            word_count = len(brief_text.split())
                            section_count = brief_text.count("##")
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("📝 Word Count", f"{word_count:,}")
                            with col2:
                                st.metric("📋 Sections", section_count)
                            with col3:
                                st.metric("🌐 Language", "English")
                            
                            st.divider()
                            
                            # Display the brief
                            st.markdown("**📖 Complete Professional Brief:**")
                            st.markdown(brief_text)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Next step guidance
                        st.info("✨ Your brief is ready! Go to the **Image Generator** tab to create professional images.")
    
    with tab2:
        st.header("📸 Professional Image Generator")
        
        # Check if brief is available
        if "brief_result" not in st.session_state:
            st.info("🎯 Generate a professional brief first in the **Brief Generator** tab!")
            
            # Allow manual prompt input as fallback
            st.markdown("### 💡 Or Enter Manual Prompt")
            with st.form("manual_image_form"):
                manual_prompt = st.text_area(
                    "📝 **Photography Prompt**",
                    placeholder="Enter your detailed photography prompt...",
                    height=150
                )
                
                manual_generate_clicked = st.form_submit_button(
                    "🎨 **Generate Image**",
                    type="primary",
                    use_container_width=True
                )
            
            if manual_generate_clicked:
                if not manual_prompt.strip():
                    st.error("❌ Please enter a prompt")
                elif not api_key.strip():
                    st.error("❌ Please enter your API key in the sidebar")
                else:
                    with st.spinner(f"🎨 Generating image using {provider.upper()}..."):
                        result = generate_image(manual_prompt.strip(), api_key.strip(), provider)
                    
                    if result:
                        st.session_state.image_result = result
                        st.session_state.used_prompt = manual_prompt.strip()
                        st.success("✅ Image generated successfully!")
        else:
            # Use generated brief for image creation
            brief_text = st.session_state.brief_result.get("final_prompt", "")
            
            st.markdown("### ✨ Using Your Generated Professional Brief")
            
            # Show brief preview
            with st.expander("📖 Brief Preview", expanded=False):
                st.markdown(brief_text[:500] + "..." if len(brief_text) > 500 else brief_text)
            
            # Generate image form
            with st.form("enhanced_image_form"):
                st.markdown("**🎨 Generate Image from Professional Brief**")
                
                # Show brief stats
                word_count = len(brief_text.split())
                st.info(f"📋 Using comprehensive brief: {word_count:,} words, {brief_text.count('##')} sections")
                
                enhanced_generate_clicked = st.form_submit_button(
                    "🚀 **Generate Professional Image**",
                    type="primary",
                    use_container_width=True
                )
            
            if enhanced_generate_clicked:
                if not api_key.strip():
                    st.error("❌ Please enter your API key in the sidebar")
                else:
                    with st.spinner(f"🎨 Generating professional image using {provider.upper()}..."):
                        result = generate_image(brief_text, api_key.strip(), provider)
                    
                    if result:
                        st.session_state.image_result = result
                        st.session_state.used_prompt = brief_text
                        st.success("✅ Professional image generated successfully!")
    
    with tab3:
        st.header("📊 Generation Results")
        
        # Display image result if available
        if "image_result" in st.session_state:
            result = st.session_state.image_result
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("### 🖼️ Generated Image")
                
                if "image_url" in result:
                    st.image(result["image_url"], use_column_width=True)
                    
                    # Download link
                    if "download_url" in result:
                        st.markdown(f"[📥 Download Full Resolution Image]({result['download_url']})")
                
                # Show used prompt
                if "used_prompt" in st.session_state:
                    with st.expander("📝 Used Prompt", expanded=False):
                        st.text_area("Prompt", st.session_state.used_prompt, height=200, disabled=True)
            
            with col2:
                st.markdown("### 📈 Generation Info")
                
                # Image details
                if "width" in result and "height" in result:
                    st.metric("🖼️ Resolution", f"{result['width']}×{result['height']}")
                
                if "provider" in result:
                    st.metric("🤖 Provider", result["provider"].upper())
                
                if "generation_time" in result:
                    st.metric("⏱️ Generation Time", f"{result['generation_time']:.1f}s")
                
                # Brief info if available
                if "brief_result" in st.session_state:
                    brief_text = st.session_state.brief_result.get("final_prompt", "")
                    st.metric("📝 Brief Words", f"{len(brief_text.split()):,}")
                    st.metric("📋 Brief Sections", brief_text.count("##"))
        else:
            st.info("🎨 Generate an image to see results here!")

if __name__ == "__main__":
    main()
