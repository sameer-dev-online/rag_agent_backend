"""
Document upload page for the RAG system.

This page allows users to upload documents (PDF, DOCX, TXT) to the RAG system
for processing and indexing. Uploaded documents become part of the knowledge base.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.api_client import upload_documents, check_backend_health
from utils.session_manager import (
    init_session_state,
    update_backend_status,
    get_backend_status,
    set_upload_result,
)
from utils.ui_components import (
    show_backend_status,
    show_loading_spinner,
    render_file_info,
    render_metric_card,
    render_error_box,
    render_success_box,
)
from config.settings import ALLOWED_FILE_TYPES, MAX_FILE_SIZE_MB

# Page configuration
st.set_page_config(
    page_title="Upload - RAG Assistant",
    page_icon="📤",
    layout="wide",
)

# Initialize session state
init_session_state()

# Check backend health on page load
if "upload_health_checked" not in st.session_state:
    health_result = check_backend_health()
    update_backend_status(health_result["success"])
    st.session_state.upload_health_checked = True

# Sidebar
st.sidebar.title("⚙️ Settings")

# Show backend status
is_connected = get_backend_status() == "connected"
show_backend_status(is_connected)

st.sidebar.markdown("---")
st.sidebar.markdown("### Supported File Types")
st.sidebar.info(
    f"""
    **Accepted formats:**
    - PDF (.pdf)
    - Microsoft Word (.docx)
    - Text files (.txt)

    **Max file size:** {MAX_FILE_SIZE_MB} MB per file
    """
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Upload Process")
st.sidebar.info(
    """
    When you upload documents:
    1. Files are validated
    2. Content is extracted
    3. Text is split into chunks
    4. Chunks are embedded and stored
    5. Documents become searchable
    """
)

# Main content area
st.title("📤 Upload Documents")

# Warning if backend is disconnected
if not is_connected:
    st.warning(
        "⚠️ Backend is not connected. Please start the backend server to upload documents."
    )
    st.code("python main.py", language="bash")
    st.stop()

# Instructions
st.markdown(
    """
    Upload your documents to add them to the knowledge base. Once processed,
    you can ask questions about these documents in the Chat page.
    """
)

st.markdown("---")

# File uploader
uploaded_files = st.file_uploader(
    "Choose files to upload",
    type=ALLOWED_FILE_TYPES,
    accept_multiple_files=True,
    help=f"Upload PDF, DOCX, or TXT files (max {MAX_FILE_SIZE_MB}MB each)",
)

# Display selected files
if uploaded_files:
    st.markdown("### Selected Files")

    # Show file information
    for file in uploaded_files:
        render_file_info(file.name, len(file.getvalue()))

    # Check file sizes
    oversized_files = [
        f.name
        for f in uploaded_files
        if len(f.getvalue()) > MAX_FILE_SIZE_MB * 1024 * 1024
    ]

    if oversized_files:
        st.error(
            f"⚠️ The following files exceed the {MAX_FILE_SIZE_MB}MB limit: "
            f"{', '.join(oversized_files)}"
        )

    st.markdown("---")

    # Upload button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        upload_button = st.button(
            "🚀 Upload and Process",
            use_container_width=True,
            type="primary",
            disabled=len(oversized_files) > 0,
        )

    # Handle upload
    if upload_button:
        with show_loading_spinner(
            f"Processing {len(uploaded_files)} file(s)... This may take a minute."
        ):
            result = upload_documents(uploaded_files)

        # Store result
        set_upload_result(result)

        if result["success"]:
            # Display success message
            render_success_box(result["message"])

            # Display metrics
            st.markdown("### Processing Results")
            col1, col2 = st.columns(2)

            with col1:
                render_metric_card(
                    "Files Processed",
                    result["files_processed"],
                    "📊",
                )

            with col2:
                render_metric_card(
                    "Chunks Created",
                    result["chunks_created"],
                    "🔢",
                )

            # Display per-file details
            if result.get("details"):
                st.markdown("### File Details")

                for detail in result["details"]:
                    filename = detail.get("filename", "Unknown")
                    status = detail.get("status", "unknown")
                    chunks = detail.get("chunks_created", 0)

                    if status == "success":
                        st.success(
                            f"✓ **{filename}** - {chunks} chunks created"
                        )
                    else:
                        error = detail.get("error", "Unknown error")
                        st.error(f"✗ **{filename}** - {error}")

            # Clear file uploader by rerunning
            st.balloons()
            st.success(
                "✅ Upload complete! You can now chat with your documents."
            )

        else:
            # Display error
            error_msg = result.get("error", "Unknown error occurred")
            render_error_box(error_msg)

            # Show details if available
            if result.get("details"):
                st.markdown("### Error Details")
                for detail in result["details"]:
                    filename = detail.get("filename", "Unknown")
                    error = detail.get("error", "Unknown error")
                    st.error(f"**{filename}**: {error}")

else:
    # No files selected
    st.info(
        "👆 Select one or more files using the uploader above to get started."
    )

# Add spacing at bottom
st.markdown("<br><br>", unsafe_allow_html=True)
