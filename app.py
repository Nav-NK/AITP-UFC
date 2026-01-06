import streamlit as st
import os
from markitdown import MarkItDown
import requests
from tempfile import NamedTemporaryFile

# --- Configuration ---
st.set_page_config(page_title="Universal Doc Reader", page_icon="📄", layout="wide")

# Setup session for resilience (Requirement [3])
session = requests.Session()
session.headers.update({"User-Agent": "UniversalDocReader/1.0"})

def get_markitdown_engine():
    return MarkItDown(requests_session=session, requests_timeout=5)

def format_size(bytes_size):
    """Converts bytes to a human-readable MB format."""
    return round(bytes_size / (1024 * 1024), 3)

# --- UI ---
st.title("📄 Universal Document Reader")
st.markdown("Convert complex Office docs into lightweight Markdown instantly.")

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
        
        # Get Original Size
        original_size_bytes = uploaded_file.size
        
        try:
            # Create and close temp file for processing stability
            with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name
            
            # Conversion
            result = md_engine.convert(tmp_path)
            content = result.text_content
            
            # Calculate Converted Size
            converted_size_bytes = len(content.encode('utf-8'))
            
            # --- TABBED OUTPUT ---
            st.subheader(f"📄 File: {uploaded_file.name}")
            tab1, tab2 = st.tabs(["🔍 Preview & Download", "📊 File Size Comparison"])

            with tab1:
                st.text_area("Extracted Content", value=content, height=350, key=f"t_{uploaded_file.name}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button("📥 Download .md", content, f"{file_base_name}_converted.md", "text/markdown", key=f"m_{uploaded_file.name}")
                with col2:
                    st.download_button("📥 Download .txt", content, f"{file_base_name}_converted.txt", "text/plain", key=f"x_{uploaded_file.name}")

            with tab2:
                # Calculate metrics
                orig_mb = format_size(original_size_bytes)
                conv_mb = format_size(converted_size_bytes)
                
                # Prevent division by zero if file is somehow 0 bytes
                if original_size_bytes > 0:
                    reduction = round((1 - (converted_size_bytes / original_size_bytes)) * 100, 1)
                else:
                    reduction = 0

                # Display Table
                st.table({
                    "Attribute": ["Original file size", "Converted .txt file size"],
                    "Size (MB)": [f"{orig_mb} MB", f"{conv_mb} MB"]
                })

                # Visual Metric
                st.success(f"📈 **Efficiency Gain:** Text version is **{reduction}% smaller** than the original.")

            os.remove(tmp_path)

        except Exception as e:
            st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")
            if debug_mode:
                st.exception(e)
else:
    st.info("Please upload a file to begin.")
