"""
Reusable UI components for the Streamlit frontend.

This module provides styled components for consistent UI presentation:
- Message rendering (user and assistant)
- Source badges
- Status indicators
- Loading spinners
"""

from typing import List, Optional, Callable, Any
import streamlit as st
from contextlib import contextmanager


def render_message(
    role: str, content: str, sources: Optional[List[str]] = None
) -> None:
    """
    Render a chat message with appropriate styling.

    User messages appear on the right with blue background.
    Assistant messages appear on the left with gray background.

    Args:
        role (str): Either "user" or "assistant".
        content (str): The message text to display.
        sources (List[str], optional): Source documents (displayed for assistant messages).

    Returns:
        None

    Example:
        >>> render_message("user", "What is the topic?")
        >>> render_message("assistant", "The topic is...", sources=["doc1.pdf"])
    """
    if role == "user":
        # User message: right-aligned, blue background
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                <div style="background-color: #4A90E2; color: white; padding: 10px 15px;
                            border-radius: 15px; max-width: 70%; word-wrap: break-word;">
                    {content}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Assistant message: left-aligned, gray background
        st.markdown(
            f"""
            <div style="display: flex; justify-content: flex-start; margin-bottom: 10px;">
                <div style="background-color: #2E3440; color: #FAFAFA; padding: 10px 15px;
                            border-radius: 15px; max-width: 70%; word-wrap: break-word;">
                    {content}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Display sources if available
        if sources and len(sources) > 0:
            render_sources(sources)


def render_sources(sources: List[str]) -> None:
    """
    Render source document badges below assistant messages.

    Args:
        sources (List[str]): List of source document names.

    Returns:
        None

    Example:
        >>> render_sources(["document1.pdf", "document2.txt"])
    """
    if not sources:
        return

    # Create badges for each source
    badges_html = " ".join(
        [
            f'<span style="background-color: #1E2130; color: #4A90E2; padding: 3px 8px; '
            f'border-radius: 10px; font-size: 0.85em; margin-right: 5px; '
            f'display: inline-block; margin-bottom: 5px;">{source}</span>'
            for source in sources
        ]
    )

    st.markdown(
        f"""
        <div style="margin-left: 10px; margin-bottom: 15px; margin-top: -5px;">
            <small style="color: #888;">Sources: </small>
            {badges_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_backend_status(is_connected: bool) -> None:
    """
    Display backend connection status indicator in the sidebar.

    Args:
        is_connected (bool): True if backend is connected, False otherwise.

    Returns:
        None

    Example:
        >>> show_backend_status(True)
        >>> show_backend_status(False)
    """
    if is_connected:
        st.sidebar.success("✓ Backend Connected")
    else:
        st.sidebar.error("✗ Backend Disconnected")
        st.sidebar.info(
            "Start the backend:\n```bash\ncd /path/to/rag_agent\npython main.py\n```"
        )


@contextmanager
def show_loading_spinner(message: str = "Processing..."):
    """
    Context manager to display a loading spinner during operations.

    Args:
        message (str): Message to display while loading.

    Yields:
        None

    Example:
        >>> with show_loading_spinner("Uploading files..."):
        ...     # Perform upload operation
        ...     result = upload_documents(files)
    """
    with st.spinner(message):
        yield


def render_file_info(filename: str, filesize: int) -> None:
    """
    Render file information with name and size.

    Args:
        filename (str): Name of the file.
        filesize (int): Size of the file in bytes.

    Returns:
        None

    Example:
        >>> render_file_info("document.pdf", 1024000)
    """
    size_mb = filesize / (1024 * 1024)
    size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{filesize / 1024:.2f} KB"

    st.markdown(
        f"""
        <div style="background-color: #1E2130; padding: 8px 12px; border-radius: 8px;
                    margin-bottom: 8px; display: flex; justify-content: space-between;
                    align-items: center;">
            <span style="color: #FAFAFA;">📄 {filename}</span>
            <span style="color: #888; font-size: 0.9em;">{size_str}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: Any, icon: str = "") -> None:
    """
    Render a metric card with label, value, and optional icon.

    Args:
        label (str): Metric label.
        value (Any): Metric value to display.
        icon (str, optional): Optional emoji icon.

    Returns:
        None

    Example:
        >>> render_metric_card("Files Processed", 5, "📊")
        >>> render_metric_card("Chunks Created", 150, "🔢")
    """
    st.markdown(
        f"""
        <div style="background-color: #1E2130; padding: 15px; border-radius: 10px;
                    text-align: center; margin: 5px;">
            <div style="color: #4A90E2; font-size: 2em;">{icon} {value}</div>
            <div style="color: #888; font-size: 0.9em; margin-top: 5px;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_error_box(error_message: str) -> None:
    """
    Render an error message in a styled box.

    Args:
        error_message (str): The error message to display.

    Returns:
        None

    Example:
        >>> render_error_box("Failed to connect to backend")
    """
    st.markdown(
        f"""
        <div style="background-color: #3D1F1F; border-left: 4px solid #E74C3C;
                    padding: 12px; border-radius: 5px; margin: 10px 0;">
            <strong style="color: #E74C3C;">Error:</strong>
            <span style="color: #FAFAFA; margin-left: 8px;">{error_message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_success_box(message: str) -> None:
    """
    Render a success message in a styled box.

    Args:
        message (str): The success message to display.

    Returns:
        None

    Example:
        >>> render_success_box("Documents uploaded successfully!")
    """
    st.markdown(
        f"""
        <div style="background-color: #1F3D1F; border-left: 4px solid #2ECC71;
                    padding: 12px; border-radius: 5px; margin: 10px 0;">
            <strong style="color: #2ECC71;">Success:</strong>
            <span style="color: #FAFAFA; margin-left: 8px;">{message}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
