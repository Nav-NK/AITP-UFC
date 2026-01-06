import streamlit as st
import os
from markitdown import MarkItDown
import requests
from tempfile import NamedTemporaryFile

# --- Configuration ---
st.set_page_config(page_title="Universal Doc Reader", page_icon="📄")

# Setup session for web requests (Requirement [3])
session = requests.Session()
session.headers.update({"User-Agent": "UniversalDocReader/1.0"})

def get_markitdown_engine():
    return MarkItDown(requests_session=session, requests_timeout=5)

# --- UI ---
st.title("📄 Universal Document Reader")

# Debugging toggle in sidebar
debug_mode = st.sidebar.checkbox("Show Technical Error Logs")

uploaded_files = st.file_uploader(
    "Upload Office Docs, PDFs, or HTML", 
    type=["docx", "xlsx", "pptx", "pdf", "html", "htm"], 
    accept_multiple_files=True
)

if uploaded_files:
    md_engine = get_markitdown_engine()
    
    for uploaded_file in uploaded_files:
        file_base_name = os.path.splitext(uploaded_file.name)[0]
        suffix = os.path.splitext(uploaded_file.name)[1]
        
        try:
            # FIX: Create and CLOSE the temp file before processing
            with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # Now that the file is closed and saved, process it
            result = md_engine.convert(tmp_path)
            content = result.text_content

            with st.expander(f"👁️ Preview: {uploaded_file.name}", expanded=True):
                st.text_area("Extracted Content", value=content, height=300, key=f"t_{uploaded_file.name}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📥 Download .md", content, f"{file_base_name}_converted.md", "text/markdown", key=f"m_{uploaded_file.name}")
                with col2:
                    st.download_button("📥 Download .txt", content, f"{file_base_name}_converted.txt", "text/plain", key=f"x_{uploaded_file.name}")

            os.remove(tmp_path)

        except Exception as e:
            # [3] Resilience: Polite Error Handling
            st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")
            if debug_mode:
                st.exception(e) # This shows the exact traceback to help us fix it
else:
    st.info("Please upload a file to begin.")
