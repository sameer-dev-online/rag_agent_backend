"""
Chat interface page for the RAG system.

This page provides an interactive chat interface where users can ask questions
about uploaded documents and receive AI-generated answers with source citations.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = str(Path(__file__).parent.parent)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.api_client import chat_query, check_backend_health
from utils.session_manager import (
    init_session_state,
    add_message,
    clear_chat_history,
    get_chat_history,
    update_backend_status,
    get_backend_status,
)
from utils.ui_components import (
    render_message,
    show_backend_status,
)
from config.settings import DEFAULT_TOP_K, MIN_TOP_K, MAX_TOP_K

# Page configuration
st.set_page_config(
    page_title="Chat - RAG Assistant",
    page_icon="💬",
    layout="wide",
)

# Custom CSS for better layout
st.markdown(
    """
    <style>
    /* Adjust main container padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 1rem;
    }

    /* Chat messages container */
    .chat-messages {
        max-height: 60vh;
        overflow-y: auto;
        padding: 1rem;
        margin-bottom: 2rem;
    }

    /* Custom scrollbar */
    .chat-messages::-webkit-scrollbar {
        width: 8px;
    }

    .chat-messages::-webkit-scrollbar-track {
        background: #0E1117;
    }

    .chat-messages::-webkit-scrollbar-thumb {
        background: #4A90E2;
        border-radius: 4px;
    }

    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: #5BA0F2;
    }

    /* Input section styling */
    .input-section {
        position: sticky;
        bottom: 0;
        background-color: #0E1117;
        padding: 1rem 0;
        border-top: 1px solid #1E2130;
        margin-top: 1rem;
    }

    /* Thinking indicator */
    .thinking-indicator {
        display: flex;
        align-items: center;
        padding: 10px;
        margin: 10px 0;
        color: #888;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
init_session_state()

# Initialize processing state
if "is_processing" not in st.session_state:
    st.session_state.is_processing = False

# Check backend health on page load (only once per session)
if "health_checked" not in st.session_state:
    health_result = check_backend_health()
    update_backend_status(health_result["success"])
    st.session_state.health_checked = True

# Sidebar
st.sidebar.title("⚙️ Settings")

# Show backend status
is_connected = get_backend_status() == "connected"
show_backend_status(is_connected)

st.sidebar.markdown("---")

# Top-k slider for retrieval
top_k = st.sidebar.slider(
    "Number of chunks to retrieve (top_k)",
    min_value=MIN_TOP_K,
    max_value=MAX_TOP_K,
    value=DEFAULT_TOP_K,
    help="Higher values may provide more context but slower responses",
)

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    clear_chat_history()
    st.session_state.is_processing = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### About")
st.sidebar.info(
    """
    This chat interface uses RAG (Retrieval-Augmented Generation) to answer
    questions based on your uploaded documents.

    **How it works:**
    1. Your question is embedded into a vector
    2. Relevant document chunks are retrieved
    3. AI generates an answer using the context
    4. Sources are provided for transparency
    """
)

# Main content area
st.title("💬 Chat with Your Documents")

# Warning if backend is disconnected
if not is_connected:
    st.warning(
        "⚠️ Backend is not connected. Please start the backend server to use the chat."
    )
    st.code("python main.py", language="bash")
    st.stop()

# Chat messages area
st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

chat_history = get_chat_history()

if len(chat_history) == 0:
    st.info(
        "👋 Welcome! Ask me anything about your uploaded documents. "
        "I'll provide answers based on the document content with source citations."
    )
else:
    # Render all messages
    for message in chat_history:
        render_message(
            role=message["role"],
            content=message["content"],
            sources=message.get("sources", []),
        )

# Show processing indicator if currently processing
if st.session_state.is_processing:
    st.markdown(
        """
        <div class="thinking-indicator">
            <span>⏳ Thinking...</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown('</div>', unsafe_allow_html=True)

# Separator line
st.markdown("---")

# Input section at bottom
st.markdown('<div class="input-section">', unsafe_allow_html=True)

# Create form for better UX (allows Enter key to submit)
with st.form(key="chat_form", clear_on_submit=True):
    col1, col2 = st.columns([6, 1])

    with col1:
        user_input = st.text_input(
            "Your question:",
            placeholder="Ask a question about your documents...",
            key="chat_input_field",
            label_visibility="collapsed",
        )

    with col2:
        send_button = st.form_submit_button(
            "Send",
            use_container_width=True,
            type="primary",
            disabled=st.session_state.is_processing,
        )

st.markdown('</div>', unsafe_allow_html=True)

# Handle message submission
if send_button and user_input.strip():
    # Set processing state
    st.session_state.is_processing = True

    # Add user message to history
    add_message("user", user_input)

    # Rerun to show user message and processing indicator
    st.rerun()

# Process query if there's a pending one
if st.session_state.is_processing and len(chat_history) > 0:
    last_message = chat_history[-1]

    # Only process if last message is from user and no assistant response yet
    if last_message["role"] == "user":
        user_query = last_message["content"]

        # Query the backend
        result = chat_query(user_query, top_k=top_k)

        # Handle response
        if result["success"]:
            # Add assistant response to history
            answer = result["answer"]
            sources = result["sources"]
            add_message("assistant", answer, sources)

            # Show query time in sidebar
            query_time = result.get("query_time_ms", 0.0)
            st.sidebar.success(f"⚡ Query time: {query_time:.0f}ms")
        else:
            # Display error
            error_msg = result.get("error", "Unknown error occurred")

            # Add error to chat history for context
            add_message(
                "assistant",
                f"I encountered an error: {error_msg}",
                sources=[],
            )

        # Reset processing state
        st.session_state.is_processing = False

        # Rerun to show assistant response
        st.rerun()

elif send_button and not user_input.strip():
    st.warning("Please enter a question before sending.")
