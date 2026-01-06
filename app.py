import streamlit as st
import os
from markitdown import MarkItDown
import requests
from tempfile import NamedTemporaryFile

# --- Configuration & Resilience ---
# Setting up a custom requests session for internal web requests (as per requirement [3])
session = requests.Session()
session.headers.update({"User-Agent": "UniversalDocReader/1.0 (Streamlit App)"})

def get_markitdown_engine():
    # Initialize the engine. 
    # Note: MarkItDown handles Word, Excel, PPTX, PDF, and HTML natively.
    return MarkItDown(requests_session=session, requests_timeout=5)

# --- UI Setup ---
st.set_page_config(page_title="Universal Doc Reader", page_icon="📄")

st.title("📄 Universal Document Reader")
st.markdown("Upload any Office document, PDF, or HTML file to convert it into clean Markdown text.")

# [2] Upload Area: Multiple file support
uploaded_files = st.file_uploader(
    "Drag and drop files here", 
    type=["docx", "xlsx", "pptx", "pdf", "html", "htm"], 
    accept_multiple_files=True
)

if uploaded_files:
    md_engine = get_markitdown_engine()
    
    for uploaded_file in uploaded_files:
        # Generate base filename for naming consistency [4]
        file_base_name = os.path.splitext(uploaded_file.name)[0]
        
        try:
            # Create a temporary file to allow MarkItDown to process the stream
            with NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            # [1] The Engine: Conversion logic
            result = md_engine.convert(tmp_path)
            content = result.text_content

            # [2] Instant Preview: Scrollable box
            with st.expander(f"👁️ Preview: {uploaded_file.name}", expanded=True):
                st.text_area(
                    label="Extracted Content",
                    value=content,
                    height=300,
                    key=f"text_{uploaded_file.name}"
                )

                # [2] Download Options
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="📥 Download as .md",
                        data=content,
                        file_name=f"{file_base_name}_converted.md",
                        mime="text/markdown",
                        key=f"md_{uploaded_file.name}"
                    )
                
                with col2:
                    st.download_button(
                        label="📥 Download as .txt",
                        data=content,
                        file_name=f"{file_base_name}_converted.txt",
                        mime="text/plain",
                        key=f"txt_{uploaded_file.name}"
                    )

            # Cleanup temp file
            os.remove(tmp_path)

        except Exception as e:
            # [3] Resilience: Polite Error Handling
            st.error(f"⚠️ Could not read {uploaded_file.name}. Please check the format.")
            # Optional: Log the error for debugging
            # st.sidebar.write(f"Debug Info: {str(e)}")

else:
    st.info("Please upload a file to begin.")

# Footer
st.divider()
st.caption("Powered by Microsoft MarkItDown & Streamlit")
