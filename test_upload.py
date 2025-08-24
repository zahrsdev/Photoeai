import streamlit as st

st.title("🧪 Image Upload Test")

# Test 1: Basic file uploader
st.markdown("## Test 1: Basic File Uploader")
uploaded_file = st.file_uploader("Test Upload", type=["jpg", "png", "webp"])

if uploaded_file:
    st.success(f"File uploaded: {uploaded_file.name}")
    st.image(uploaded_file, width=200)
else:
    st.info("No file uploaded yet")

# Test 2: In form
st.markdown("## Test 2: File Uploader in Form")
with st.form("test_form"):
    uploaded_file2 = st.file_uploader("Test Upload 2", type=["jpg", "png", "webp"])
    submit = st.form_submit_button("Submit")
    
if submit:
    if uploaded_file2:
        st.success(f"Form file: {uploaded_file2.name}")
    else:
        st.warning("No file in form")
