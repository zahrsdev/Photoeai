"""
PhotoEAI Simple Frontend
========================

A clean, simple interface for AI image generation with:
- User input prompt
- User input API key
- User select provider 
- Click generate button
- Result Image
- Link Image  
- Prompt Output display
"""

import streamlit as st
import requests
import json
from typing import Optional, Dict
import time
import base64
from PIL import Image
import io

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 300  # Increased to 5 minutes for complex operations


def check_server_running(host="localhost", port=8000, timeout=5):
    """Check if the backend server is running"""
    try:
        response = requests.get(f"http://{host}:{port}/api/v1/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False


def generate_comprehensive_brief(user_prompt: str) -> Optional[Dict]:
    """Generate comprehensive photography brief from simple user prompt"""
    try:
        payload = {
            "user_request": user_prompt
        }
        
        response = requests.post(
            f"{API_BASE_URL}/generate-brief-from-prompt",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Brief generation failed: {e}")
        return None


def save_uploaded_image(uploaded_file) -> Optional[str]:
    """Save uploaded image to static/images/uploads/ and return filename"""
    try:
        import os
        
        # Create uploads directory if not exists
        upload_dir = "static/images/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename with timestamp
        timestamp = int(time.time())
        file_extension = uploaded_file.name.split('.')[-1].lower()
        filename = f"product_{timestamp}.{file_extension}"
        
        # Save file
        file_path = os.path.join(upload_dir, filename)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return filename
    except Exception as e:
        st.error(f"❌ Failed to save image: {e}")
        return None


def generate_image_from_brief(comprehensive_brief: str, api_key: str, provider: str = None, 
                            negative_prompt: str = None, uploaded_image_filename: str = None) -> Optional[Dict]:
    """Generate image from comprehensive photography brief"""
    try:
        payload = {
            "brief_prompt": comprehensive_brief,
            "user_api_key": api_key
        }
        
        # Boss: Add image upload support for 2-step flow
        if uploaded_image_filename:
            payload["uploaded_image_filename"] = uploaded_image_filename
        
        if provider:
            payload["provider"] = provider
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
            
        response = requests.post(
            f"{API_BASE_URL}/generate-image",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Image generation failed: {e}")
        return None


def generate_image(prompt: str, api_key: str, provider: str = None, negative_prompt: str = None, 
                  uploaded_image_filename: str = None) -> Optional[Dict]:
    """Generate image from prompt with real-time progress display"""
    try:
        # Create progress placeholders
        progress_placeholder = st.empty()
        progress_bar_placeholder = st.empty()
        
        # Initialize progress bar
        progress_bar = progress_bar_placeholder.progress(0)
        
        if uploaded_image_filename:
            progress_placeholder.info("🎨 Starting full pipeline analysis...")
            progress_bar.progress(10)
        else:
            progress_placeholder.info("🎨 Creating comprehensive photography brief...")
            progress_bar.progress(20)
        
        # Step 1: Generate comprehensive brief from simple prompt (BACKGROUND)
        brief_result = generate_comprehensive_brief(prompt)
        progress_bar.progress(40)
        
        if not brief_result:
            return None
            
        comprehensive_brief = brief_result.get("final_prompt", "")
        if not comprehensive_brief:
            st.error("❌ Failed to generate comprehensive brief")
            return None
        
        # Step 2: Generate image from comprehensive brief with progress tracking
        progress_placeholder.info("🚀 Generating image with enhanced pipeline...")
        progress_bar.progress(60)
        
        result = generate_image_from_brief(
            comprehensive_brief=comprehensive_brief,
            api_key=api_key,
            provider=provider,
            negative_prompt=negative_prompt,
            uploaded_image_filename=uploaded_image_filename
        )
        
        progress_bar.progress(90)
        
        if result:
            progress_bar.progress(100)
            progress_placeholder.success("✅ Image generated successfully!")
            
            # Clean up progress indicators after brief delay
            time.sleep(1)
            progress_placeholder.empty()
            progress_bar_placeholder.empty()
            
            return result
        else:
            progress_placeholder.error("❌ Image generation failed")
            return None
            
    except Exception as e:
        st.error(f"❌ Image generation error: {e}")
        return None


def generate_image_breakthrough(prompt: str, api_key: str, uploaded_image_filename: str) -> Optional[Dict]:
    """
    🚀 BREAKTHROUGH: Generate image using GPT Image-1 Edit API for PERFECT shape preservation
    
    This function uses the breakthrough IMAGE EDIT API instead of text-to-image:
    - Sends image filename to backend instead of base64
    - Backend reads file from static/images/uploads/
    - Uses input_fidelity='high' to preserve original features
    - Applies professional photography enhancement only
    - Result: Enhanced image with PRESERVED original shape!
    """
    try:
        # Create progress placeholders
        progress_placeholder = st.empty()
        progress_bar_placeholder = st.empty()
        
        # Initialize progress bar
        progress_bar = progress_bar_placeholder.progress(0)
        
        progress_placeholder.info("🚀 BREAKTHROUGH: Initializing GPT Image-1 Edit API...")
        progress_bar.progress(10)
        
        # Prepare payload for breakthrough endpoint
        payload = {
            "brief_prompt": prompt,
            "user_api_key": api_key,
            "uploaded_image_filename": uploaded_image_filename,
            "provider": "gpt-image-1",
            "use_raw_prompt": False
        }
        
        progress_placeholder.info("🎯 Calling breakthrough Edit API for shape preservation...")
        progress_bar.progress(30)
        
        # Call the breakthrough endpoint
        response = requests.post(
            f"{API_BASE_URL}/generate-image-breakthrough",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        
        progress_bar.progress(70)
        progress_placeholder.info("🔥 Processing breakthrough result...")
        
        result = response.json()
        
        progress_bar.progress(100)
        progress_placeholder.success("🎉 BREAKTHROUGH SUCCESS: Shape preserved!")
        
        # Clean up progress indicators after brief delay
        time.sleep(1.5)
        progress_placeholder.empty()
        progress_bar_placeholder.empty()
        
        return result
        
    except requests.exceptions.RequestException as e:
        st.error(f"💥 BREAKTHROUGH API Error: {e}")
        return None
    except Exception as e:
        st.error(f"💥 BREAKTHROUGH Error: {e}")
        return None


def enhance_image(original_prompt: str, enhancement_instruction: str, api_key: str, 
                 provider: str = None, seed: int = None) -> Optional[Dict]:
    """Enhance existing image with new instructions using intelligent prompt enhancement"""
    try:
        payload = {
            "original_brief_prompt": original_prompt,
            "enhancement_instruction": enhancement_instruction,
            "user_api_key": api_key
        }
        
        if provider:
            payload["provider"] = provider
        if seed:
            payload["seed"] = seed
            
        response = requests.post(
            f"{API_BASE_URL}/enhance-image",
            json=payload,
            timeout=TIMEOUT
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Image enhancement failed: {e}")
        return None


def main():
    """Main application interface - SIMPLE SINGLE PAGE"""
    
    # Page config
    st.set_page_config(
        page_title="PhotoEAI - AI Image Generator",
        page_icon="🎨",
        layout="centered"
    )
    
    # Header
    st.title("🎨 PhotoEAI - AI Image Generator")
    st.markdown("Upload gambar produk, masukan prompt enhancement, dan generate!")
    st.markdown("---")
    
    # Initialize session state
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    if 'original_prompt' not in st.session_state:
        st.session_state.original_prompt = ""
    
    # SINGLE FORM - SIMPLE!
    with st.form("simple_generation_form", clear_on_submit=False):
        st.subheader("� Generate Enhanced Image")
        
        # 1. Upload Image
        uploaded_file = st.file_uploader(
            "📸 **Upload Product Image**",
            type=["png", "jpg", "jpeg"],
            help="Upload gambar produk yang mau di-enhance"
        )
        
        # Show image preview
        uploaded_image_filename = None
        if uploaded_file is not None:
            st.image(uploaded_file, caption="Original Product Image", use_container_width=True, width=400)
            uploaded_image_filename = save_uploaded_image(uploaded_file)
            if uploaded_image_filename:
                st.success(f"✅ Gambar berhasil disimpan: {uploaded_image_filename}")
            else:
                st.error("❌ Gagal menyimpan gambar!")
        
        # 2. Input Prompt
        prompt = st.text_area(
            "🎯 **Enhancement Prompt**",
            placeholder="Professional product photography with studio lighting and premium commercial aesthetics",
            height=100,
            help="Describe gimana mau di-enhance fotografinya"
        )
        
        # 3. API Key
        api_key = st.text_input(
            "🔑 **OpenAI API Key**",
            type="password",
            placeholder="sk-proj-...",
            help="OpenAI API key untuk GPT Image-1"
        )
        
        # 4. Generate Button
        generate_clicked = st.form_submit_button(
            "🚀 **GENERATE IMAGE**",
            type="primary",
            use_container_width=True
        )
    
    # Handle form submission
    if generate_clicked:
        if not uploaded_image_filename:
            st.error("❌ Upload gambar produk dulu!")
        elif not prompt.strip():
            st.error("❌ Masukan prompt enhancement!")
        elif not api_key.strip():
            st.error("❌ Masukan OpenAI API key!")
        else:
            # BREAKTHROUGH GENERATION
            with st.spinner("🚀 Processing with GPT Image-1 Edit API..."):
                result = generate_image_breakthrough(
                    prompt=prompt.strip(),
                    api_key=api_key.strip(),
                    uploaded_image_filename=uploaded_image_filename
                )
            
            if result:
                st.session_state.generated_image = result
                st.session_state.original_prompt = prompt.strip()
                st.success("🎉 BREAKTHROUGH SUCCESS!")
                st.rerun()
            else:
                st.error("💥 Generation failed!")
    
    # Display Results - SIMPLE!
    if st.session_state.generated_image:
        st.markdown("---")
        result = st.session_state.generated_image
        
        # Generated Image
        st.subheader("🖼️ Enhanced Image")
        image_url = result.get("image_url", "")
        if image_url:
            st.image(image_url, caption="Enhanced Professional Photography", use_container_width=True)
            st.code(image_url)
        
        # Final Prompt Used
        st.subheader("� Final Enhanced Prompt")
        final_prompt = result.get("comprehensive_brief", result.get("final_enhanced_prompt", ""))
        if final_prompt:
            st.text_area("Prompt yang digunakan:", value=final_prompt, height=200, disabled=True)
        
        # Simple actions
        col1, col2 = st.columns(2)
        with col1:
            if st.button("� **Generate Lagi**", use_container_width=True):
                st.session_state.generated_image = None
                st.rerun()
        with col2:
            if final_prompt:
                st.download_button(
                    "� **Download Prompt**",
                    data=final_prompt,
                    file_name=f"enhanced_prompt_{int(time.time())}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>PhotoEAI - AI Image Generator with Intelligent Enhancement | Powered by FastAPI Backend</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
