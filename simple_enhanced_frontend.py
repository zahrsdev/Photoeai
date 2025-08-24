"""
PhotoEAI Simple Frontend 
Simple interface: Upload image + prompt → Generate enhanced image
"""

import streamlit as st
import requests
import json
from typing import Optional, Dict, Any
import time

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 300  # 5 minutes timeout

def check_server_running(host="localhost", port=8000, timeout=5):
    """Check if the backend server is running"""
    try:
        response = requests.get(f"http://{host}:{port}/api/v1/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False

def upload_image(uploaded_file) -> Optional[str]:
    """Upload image to backend and return filename"""
    try:
        files = {"file": uploaded_file}
        response = requests.post(f"{API_BASE_URL}/upload-image", files=files, timeout=30)
        
        if response.status_code == 200:
            return response.json()["filename"]
        else:
            st.error(f"❌ Image upload failed: {response.json().get('detail', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"❌ Error uploading image: {str(e)}")
        return None

def analyze_and_enhance(image_filename: str, user_prompt: str, generate_image: bool = True) -> Optional[Dict]:
    """Analyze image + user prompt and generate enhanced image"""
    try:
        payload = {
            "image_filename": image_filename,
            "user_prompt": user_prompt,
            "generate_image": generate_image
        }
        
        with st.spinner("🤖 AI is analyzing image and generating enhanced version..."):
            response = requests.post(
                f"{API_BASE_URL}/analyze-and-enhance",
                json=payload,
                timeout=TIMEOUT
            )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ Analysis failed: {response.json().get('detail', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="PhotoEAI - Simple Image Enhancer",
        page_icon="📸",
        layout="wide"
    )
    
    st.title("📸 PhotoEAI - Simple Image Enhancer")
    st.markdown("Upload your product image + describe what you want → Get professional enhanced image")
    
    # Check backend
    if not check_server_running():
        st.error("❌ Backend server is not running. Please start the server first.")
        st.info("💡 Run: `python run.py` in your backend directory")
        return
    
    # Main interface
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🖼️ Upload Your Image")
        uploaded_file = st.file_uploader(
            "Choose an image file", 
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload your product image"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Your Image", use_container_width=True)
        
        st.markdown("### ✍️ Describe What You Want")
        user_prompt = st.text_area(
            "Enter your prompt",
            placeholder="e.g., Make this look more professional with better lighting and clean background",
            height=100
        )
        
        # Generate button
        if st.button("🚀 Generate Enhanced Image", disabled=not uploaded_file or not user_prompt.strip()):
            if uploaded_file and user_prompt.strip():
                # Upload image
                filename = upload_image(uploaded_file)
                
                if filename:
                    # Analyze and enhance
                    result = analyze_and_enhance(filename, user_prompt.strip())
                    
                    if result:
                        # Store results
                        st.session_state.result = result
                        st.success("✅ Enhanced image generated!")
                        st.rerun()
    
    with col2:
        st.markdown("### 🎨 Enhanced Result")
        
        if "result" in st.session_state:
            result = st.session_state.result
            
            # Show enhanced image
            if result.get("generated_image_url"):
                st.image(result["generated_image_url"], caption="Enhanced Image", use_container_width=True)
            else:
                st.info("No image generated")
            
            # Show enhanced prompt
            st.markdown("### 🤖 AI Enhanced Prompt")
            with st.expander("View AI Enhanced Prompt", expanded=True):
                st.markdown(result.get("enhanced_brief", "No prompt available"))
        else:
            st.info("👆 Upload an image and add your prompt to get started")

if __name__ == "__main__":
    main()
