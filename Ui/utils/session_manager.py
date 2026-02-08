"""
Session state management for the Streamlit application.

This module provides functions to initialize and manage Streamlit's session state,
including chat history, backend connection status, and upload results.
"""

from typing import List, Dict, Any, Optional
import streamlit as st


def init_session_state() -> None:
    """
    Initialize all session state variables if they don't exist.

    Session state structure:
        - chat_history: List of messages with role, content, and sources
        - backend_status: Connection status ("connected" or "disconnected")
        - last_upload_result: Most recent upload operation result

    Returns:
        None

    Example:
        >>> init_session_state()
        >>> # Access session state
        >>> st.session_state.chat_history
    """
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "backend_status" not in st.session_state:
        st.session_state.backend_status = "disconnected"

    if "last_upload_result" not in st.session_state:
        st.session_state.last_upload_result = None


def add_message(
    role: str, content: str, sources: Optional[List[str]] = None
) -> None:
    """
    Add a message to the chat history.

    Args:
        role (str): Message role, either "user" or "assistant".
        content (str): The message content/text.
        sources (List[str], optional): List of source document names (for assistant messages).

    Returns:
        None

    Example:
        >>> add_message("user", "What is the main topic?")
        >>> add_message("assistant", "The main topic is...", sources=["doc1.pdf"])
    """
    message = {
        "role": role,
        "content": content,
        "sources": sources if sources else [],
    }
    st.session_state.chat_history.append(message)


def clear_chat_history() -> None:
    """
    Clear all messages from the chat history.

    Returns:
        None

    Example:
        >>> clear_chat_history()
        >>> len(st.session_state.chat_history)
        0
    """
    st.session_state.chat_history = []


def get_chat_history() -> List[Dict[str, Any]]:
    """
    Get the current chat history.

    Returns:
        List[Dict]: List of message dictionaries with role, content, and sources.

    Example:
        >>> history = get_chat_history()
        >>> for message in history:
        ...     print(f"{message['role']}: {message['content']}")
    """
    return st.session_state.chat_history


def update_backend_status(is_connected: bool) -> None:
    """
    Update the backend connection status.

    Args:
        is_connected (bool): True if backend is connected, False otherwise.

    Returns:
        None

    Example:
        >>> update_backend_status(True)
        >>> st.session_state.backend_status
        'connected'
    """
    st.session_state.backend_status = (
        "connected" if is_connected else "disconnected"
    )


def get_backend_status() -> str:
    """
    Get the current backend connection status.

    Returns:
        str: Either "connected" or "disconnected".

    Example:
        >>> status = get_backend_status()
        >>> if status == "connected":
        ...     print("Backend is online")
    """
    return st.session_state.backend_status


def set_upload_result(result: Dict[str, Any]) -> None:
    """
    Store the most recent upload operation result.

    Args:
        result (Dict): Upload result dictionary from API response.

    Returns:
        None

    Example:
        >>> result = {"success": True, "files_processed": 2}
        >>> set_upload_result(result)
    """
    st.session_state.last_upload_result = result


def get_upload_result() -> Optional[Dict[str, Any]]:
    """
    Get the most recent upload operation result.

    Returns:
        Optional[Dict]: Upload result dictionary, or None if no uploads yet.

    Example:
        >>> result = get_upload_result()
        >>> if result and result['success']:
        ...     print(f"Last upload: {result['files_processed']} files")
    """
    return st.session_state.last_upload_result
