"""
Main entry point for the Streamlit RAG frontend.

This is the home page that provides navigation to the Chat and Upload pages.
Run this file with: streamlit run app.py
"""

import streamlit as st
from utils.api_client import check_backend_health
from utils.session_manager import init_session_state, update_backend_status
from utils.ui_components import show_backend_status
from config.settings import APP_TITLE, APP_ICON, PAGE_LAYOUT

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded",
)

# Initialize session state
init_session_state()

# Check backend health
if "main_health_checked" not in st.session_state:
    health_result = check_backend_health()
    update_backend_status(health_result["success"])
    st.session_state.main_health_checked = True

# Sidebar
st.sidebar.title("🧭 Navigation")
st.sidebar.markdown(
    """
    Use the navigation above to switch between pages:
    - **Chat**: Ask questions about your documents
    - **Upload Documents**: Add new documents to the knowledge base
    """
)

st.sidebar.markdown("---")
st.sidebar.title("🔗 Backend Status")
show_backend_status(st.session_state.backend_status == "connected")

# Main content
st.title("💬 RAG Chat Assistant")

st.markdown(
    """
    ## Welcome to the RAG Chat Assistant!

    This application uses **Retrieval-Augmented Generation (RAG)** to help you
    chat with your documents. Upload PDFs, Word documents, or text files,
    and then ask questions about them.

    ### 🚀 Getting Started

    1. **Upload Documents**
       - Navigate to the "Upload Documents" page in the sidebar
       - Select your PDF, DOCX, or TXT files
       - Click "Upload and Process" to add them to the knowledge base

    2. **Chat with Your Documents**
       - Navigate to the "Chat" page in the sidebar
       - Ask questions about your uploaded documents
       - Receive AI-generated answers with source citations

    ### 🎯 Features

    - **Multi-format Support**: Upload PDF, DOCX, and TXT files
    - **Smart Retrieval**: Find relevant information from your documents
    - **Source Attribution**: See which documents were used for each answer
    - **Adjustable Retrieval**: Control the number of chunks retrieved (top_k)
    - **Dark Mode**: Professional dark theme for comfortable viewing
    - **Session Persistence**: Chat history maintained during your session

    ### 🛠️ How It Works

    ```
    Your Question → Vector Embedding → Similarity Search → Context Retrieval → AI Answer Generation
    ```

    The system:
    1. Converts your question into a vector embedding
    2. Searches for similar chunks in the vector database
    3. Retrieves the most relevant document chunks
    4. Feeds them to an AI model as context
    5. Generates a grounded, factual answer
    6. Provides source citations for transparency
    """
)

st.markdown("---")

# Backend status check
if st.session_state.backend_status == "connected":
    st.success(
        "✅ **Backend is running!** You can start uploading documents and chatting."
    )
else:
    st.error(
        "❌ **Backend is not running.** Please start the backend server to use the application."
    )
    st.code(
        """
# In a separate terminal, navigate to the project directory and run:
cd /mnt/c/Users/ALPHA/Agentic_coding/rag_agent
python main.py

# The backend will start on http://localhost:8000
        """,
        language="bash",
    )

st.markdown("---")

# Footer
st.markdown(
    """
    <div style="text-align: center; color: #888; padding: 20px;">
        <p>Built with Streamlit, FastAPI, LangChain, and OpenAI</p>
        <p>For questions or issues, refer to the project documentation</p>
    </div>
    """,
    unsafe_allow_html=True,
)
