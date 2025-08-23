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

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT = 120


def check_server_running(host="localhost", port=8000, timeout=5):
    """Check if the backend server is running"""
    try:
        response = requests.get(f"http://{host}:{port}/api/v1/health", timeout=timeout)
        return response.status_code == 200
    except:
        return False


def generate_image(prompt: str, api_key: str, provider: str = None, negative_prompt: str = None) -> Optional[Dict]:
    """Generate image from prompt using the backend API"""
    try:
        payload = {
            "brief_prompt": prompt,
            "user_api_key": api_key
        }
        
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
    """Main application interface"""
    
    # Page config
    st.set_page_config(
        page_title="PhotoEAI - AI Image Generator",
        page_icon="🎨",
        layout="centered"
    )
    
    # Header
    st.title("🎨 PhotoEAI - AI Image Generator")
    st.markdown("Simple AI-powered image generation with intelligent enhancement")
    
    # Check server status
    if not check_server_running():
        st.error("❌ Backend server is not running! Please start the server first.")
        st.code("python run.py", language="bash")
        st.stop()
    
    st.success("✅ Backend server is running")
    st.markdown("---")
    
    # Initialize session state
    if 'generated_image' not in st.session_state:
        st.session_state.generated_image = None
    if 'original_prompt' not in st.session_state:
        st.session_state.original_prompt = ""
    if 'generation_result' not in st.session_state:
        st.session_state.generation_result = None
    
    # Tabs for generation and enhancement
    tab1, tab2 = st.tabs(["🎨 Generate New Image", "✨ Enhance Existing Image"])
    
    with tab1:
        # Main form for image generation
        with st.form("image_generation_form"):
            st.subheader("📝 Generate Your Image")
            
            # 1. User input prompt
            prompt = st.text_area(
                "🖼️ **Image Prompt**",
                placeholder="Describe the image you want to generate...\n\nExample: Professional product photography of a luxury skincare bottle with golden accents, soft studio lighting, marble background, high-end cosmetic photography style",
                height=150,
                help="Enter a detailed description of the image you want to create"
            )
            
            # 2. User input API key
            api_key = st.text_input(
                "🔑 **API Key**",
                type="password",
                placeholder="Enter your AI provider API key",
                help="Your API key for the selected AI provider"
            )
            
            # 3. User select provider
            provider = st.selectbox(
                "🤖 **AI Provider**",
                options=["openai", "gemini", "sumopod", "midjourney"],
                index=0,
                help="Choose which AI provider to use for image generation"
            )
            
            # Optional: Negative prompt
            with st.expander("⚙️ Advanced Options (Optional)"):
                negative_prompt = st.text_area(
                    "🚫 **Negative Prompt**",
                    placeholder="Things to avoid in the image (e.g., blurry, low quality, distorted)",
                    help="Optional: Describe what you don't want in the image"
                )
            
            # 4. Click generate button
            generate_clicked = st.form_submit_button(
                "🎨 **Generate Image**",
                type="primary",
                use_container_width=True
            )
        
        # Handle form submission
        if generate_clicked:
            if not prompt.strip():
                st.error("❌ Please enter an image prompt")
            elif not api_key.strip():
                st.error("❌ Please enter your API key")
            else:
                # Show loading
                with st.spinner(f"🎨 Generating image using {provider.upper()}... Please wait..."):
                    result = generate_image(
                        prompt=prompt.strip(),
                        api_key=api_key.strip(),
                        provider=provider,
                        negative_prompt=negative_prompt.strip() if negative_prompt.strip() else None
                    )
                
                if result:
                    # Store in session state
                    st.session_state.generated_image = result
                    st.session_state.original_prompt = prompt.strip()
                    st.session_state.generation_result = result
                    st.success("✅ Image generated successfully!")
                    st.rerun()
                else:
                    st.error("❌ Failed to generate image. Please check your API key and try again.")
    
    with tab2:
        # Enhancement form
        st.subheader("✨ Enhance Your Image")
        
        if st.session_state.generation_result is None:
            st.info("🎨 Generate an image first to use the enhancement feature!")
        else:
            # Show current image
            with st.container():
                st.markdown("**Current Image:**")
                image_url = st.session_state.generation_result.get("image_url", "")
                if image_url:
                    st.image(image_url, caption="Current Generated Image", use_container_width=True)
                
                st.markdown("**Original Prompt:**")
                st.text_area("", value=st.session_state.original_prompt, height=80, disabled=True, key="orig_prompt_display")
            
            # Enhancement form
            with st.form("image_enhancement_form"):
                enhancement_instruction = st.text_area(
                    "🔧 **Enhancement Instruction**",
                    placeholder="How would you like to enhance the image?\n\nExamples:\n- Make it more dramatic and cinematic\n- Add luxury and premium feel\n- Include golden hour lighting\n- Make it more minimalist and clean",
                    height=120,
                    help="Describe how you want to improve or modify the image"
                )
                
                api_key_enhance = st.text_input(
                    "🔑 **API Key**",
                    type="password",
                    placeholder="Enter your AI provider API key",
                    help="Your API key for the selected AI provider",
                    key="enhance_api_key"
                )
                
                provider_enhance = st.selectbox(
                    "🤖 **AI Provider**",
                    options=["openai", "gemini", "sumopod", "midjourney"],
                    index=0,
                    help="Choose which AI provider to use for enhancement",
                    key="enhance_provider"
                )
                
                enhance_clicked = st.form_submit_button(
                    "✨ **Enhance Image**",
                    type="primary",
                    use_container_width=True
                )
            
            # Handle enhancement submission
            if enhance_clicked:
                if not enhancement_instruction.strip():
                    st.error("❌ Please enter an enhancement instruction")
                elif not api_key_enhance.strip():
                    st.error("❌ Please enter your API key")
                else:
                    # Show loading
                    with st.spinner(f"✨ Enhancing image using {provider_enhance.upper()}... Please wait..."):
                        enhanced_result = enhance_image(
                            original_prompt=st.session_state.original_prompt,
                            enhancement_instruction=enhancement_instruction.strip(),
                            api_key=api_key_enhance.strip(),
                            provider=provider_enhance,
                            seed=st.session_state.generation_result.get('seed')
                        )
                    
                    if enhanced_result:
                        # Update session state with enhanced result
                        st.session_state.generated_image = enhanced_result
                        st.session_state.generation_result = enhanced_result
                        st.success("✅ Image enhanced successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to enhance image. Please check your API key and try again.")
    
    # Display results (works for both tabs)
    if st.session_state.generated_image:
        st.markdown("---")
        result = st.session_state.generated_image
        
        # 5. Result Image
        st.subheader("�️ Generated Image")
        image_url = result.get("image_url", "")
        if image_url:
            st.image(image_url, caption="Generated Image", use_container_width=True)
        else:
            st.error("❌ No image URL received")
        
        # 6. Link Image
        st.subheader("🔗 Image Link")
        if image_url:
            st.code(image_url)
            st.markdown(f"**Direct Link:** [Open Image]({image_url})")
        
        # 7. Prompt Output display
        st.subheader("📄 Prompt Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Original Prompt:**")
            st.text_area("", value=st.session_state.original_prompt, height=100, disabled=True, key="original_prompt_display")
        
        with col2:
            # Show the enhanced prompt if available
            enhanced_prompt = result.get("final_enhanced_prompt", "")
            if enhanced_prompt and enhanced_prompt != st.session_state.original_prompt:
                st.markdown("**✨ Enhanced Prompt:**")
                st.text_area("", value=enhanced_prompt, height=100, disabled=True, key="enhanced_prompt_display")
            else:
                revised_prompt = result.get("revised_prompt", "")
                if revised_prompt:
                    st.markdown("**🔄 Revised Prompt:**")
                    st.text_area("", value=revised_prompt, height=100, disabled=True, key="revised_prompt_display")
        
        # Generation metadata
        with st.expander("ℹ️ Generation Details"):
            st.json({
                "generation_id": result.get("generation_id", "Unknown"),
                "seed": result.get("seed", "Unknown"),
                "provider": result.get("provider", "Unknown"),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            })
        
        # Download and action options
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📥 **Download Prompt Details**", use_container_width=True):
                prompt_details = f"""PhotoEAI Generation Details
==========================

Original Prompt:
{st.session_state.original_prompt}

Enhanced Prompt:
{result.get('final_enhanced_prompt', 'N/A')}

Revised Prompt:
{result.get('revised_prompt', 'N/A')}

Generation Info:
- ID: {result.get('generation_id', 'Unknown')}
- Seed: {result.get('seed', 'Unknown')}
- Provider: {result.get('provider', 'Unknown')}
- Timestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}

Image URL:
{image_url}
"""
                st.download_button(
                    "📄 Download Details",
                    data=prompt_details,
                    file_name=f"photoeai_generation_{int(time.time())}.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("🔄 **Generate Another**", use_container_width=True):
                # Clear session state
                st.session_state.generated_image = None
                st.session_state.original_prompt = ""
                st.session_state.generation_result = None
                st.rerun()
        
        with col3:
            if st.button("✨ **Enhance This**", use_container_width=True):
                # Switch to enhancement tab
                st.info("👆 Use the 'Enhance Existing Image' tab above to improve this image!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>PhotoEAI - AI Image Generator with Intelligent Enhancement | Powered by FastAPI Backend</small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
