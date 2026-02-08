"""
API client for communicating with the FastAPI RAG backend.

This module provides functions to interact with the backend API endpoints:
- Health check
- Chat/query endpoint
- Document upload endpoint
"""

from typing import Dict, List, Any, Optional
import requests
from requests.exceptions import ConnectionError, Timeout, HTTPError, RequestException

from config.settings import (
    API_BASE_URL,
    API_HEALTH_URL,
    HEALTH_TIMEOUT,
    CHAT_TIMEOUT,
    UPLOAD_TIMEOUT,
)


def check_backend_health() -> Dict[str, Any]:
    """
    Check if the backend server is running and healthy.

    Returns:
        Dict: Response with 'success' (bool) and 'error' (str) if failed.

    Example:
        >>> result = check_backend_health()
        >>> if result['success']:
        ...     print("Backend is healthy")
    """
    try:
        response = requests.get(API_HEALTH_URL, timeout=HEALTH_TIMEOUT)
        response.raise_for_status()
        return {"success": True, "status": response.json().get("status", "ok")}
    except ConnectionError:
        return {
            "success": False,
            "error": "Cannot connect to backend. Is the server running on http://localhost:8000?",
        }
    except Timeout:
        return {
            "success": False,
            "error": "Health check timed out. Backend may be overloaded.",
        }
    except HTTPError as e:
        return {
            "success": False,
            "error": f"Backend returned error: {e.response.status_code}",
        }
    except RequestException as e:
        return {"success": False, "error": f"Request failed: {str(e)}"}


def chat_query(query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Send a chat query to the RAG backend.

    Args:
        query (str): The user's question or query.
        top_k (int): Number of document chunks to retrieve (default: 5).

    Returns:
        Dict: Response containing:
            - success (bool): Whether the request succeeded
            - answer (str): Generated answer from the RAG system
            - sources (List[str]): List of source document names
            - chunks (List[Dict]): Retrieved document chunks with metadata
            - query_time_ms (float): Processing time in milliseconds
            - error (str): Error message if failed

    Example:
        >>> result = chat_query("What is the main topic?", top_k=3)
        >>> if result['success']:
        ...     print(result['answer'])
        ...     print(f"Sources: {result['sources']}")
    """
    try:
        url = f"{API_BASE_URL}/chat"
        payload = {"query": query, "top_k": top_k}

        response = requests.post(url, json=payload, timeout=CHAT_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        # Ensure all expected fields are present
        return {
            "success": data.get("success", True),
            "answer": data.get("answer", ""),
            "sources": data.get("sources", []),
            "chunks": data.get("chunks", []),
            "query_time_ms": data.get("query_time_ms", 0.0),
            "error": data.get("error", None),
        }
    except ConnectionError:
        return {
            "success": False,
            "answer": "",
            "sources": [],
            "chunks": [],
            "query_time_ms": 0.0,
            "error": "Cannot connect to backend. Please start the server: python main.py",
        }
    except Timeout:
        return {
            "success": False,
            "answer": "",
            "sources": [],
            "chunks": [],
            "query_time_ms": 0.0,
            "error": "Query timed out. Try a simpler question or reduce top_k.",
        }
    except HTTPError as e:
        error_msg = f"Backend error: {e.response.status_code}"
        try:
            error_detail = e.response.json().get("detail", str(e))
            error_msg = f"{error_msg} - {error_detail}"
        except Exception:
            pass
        return {
            "success": False,
            "answer": "",
            "sources": [],
            "chunks": [],
            "query_time_ms": 0.0,
            "error": error_msg,
        }
    except RequestException as e:
        return {
            "success": False,
            "answer": "",
            "sources": [],
            "chunks": [],
            "query_time_ms": 0.0,
            "error": f"Request failed: {str(e)}",
        }


def upload_documents(files: List[Any]) -> Dict[str, Any]:
    """
    Upload documents to the RAG backend for ingestion.

    Args:
        files (List): List of UploadedFile objects from Streamlit file_uploader.

    Returns:
        Dict: Response containing:
            - success (bool): Whether upload succeeded
            - files_processed (int): Number of files successfully processed
            - chunks_created (int): Total chunks created from all files
            - message (str): Summary message
            - details (List[Dict]): Per-file processing details
            - error (str): Error message if failed

    Example:
        >>> files = st.file_uploader("Upload", type=["pdf", "txt"])
        >>> if files:
        ...     result = upload_documents(files)
        ...     if result['success']:
        ...         st.success(f"Processed {result['files_processed']} files")
    """
    try:
        url = f"{API_BASE_URL}/upload"

        # Prepare multipart form data
        # Reason: Backend expects 'files' field with multiple files
        files_data = [
            ("files", (file.name, file.getvalue(), file.type))
            for file in files
        ]

        response = requests.post(url, files=files_data, timeout=UPLOAD_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        return {
            "success": data.get("success", True),
            "files_processed": data.get("files_processed", 0),
            "chunks_created": data.get("chunks_created", 0),
            "message": data.get("message", ""),
            "details": data.get("details", []),
            "error": data.get("error", None),
        }
    except ConnectionError:
        return {
            "success": False,
            "files_processed": 0,
            "chunks_created": 0,
            "message": "",
            "details": [],
            "error": "Cannot connect to backend. Please start the server: python main.py",
        }
    except Timeout:
        return {
            "success": False,
            "files_processed": 0,
            "chunks_created": 0,
            "message": "",
            "details": [],
            "error": "Upload timed out. Try uploading fewer or smaller files.",
        }
    except HTTPError as e:
        error_msg = f"Upload failed: {e.response.status_code}"
        try:
            error_detail = e.response.json().get("detail", str(e))
            error_msg = f"{error_msg} - {error_detail}"
        except Exception:
            pass
        return {
            "success": False,
            "files_processed": 0,
            "chunks_created": 0,
            "message": "",
            "details": [],
            "error": error_msg,
        }
    except RequestException as e:
        return {
            "success": False,
            "files_processed": 0,
            "chunks_created": 0,
            "message": "",
            "details": [],
            "error": f"Request failed: {str(e)}",
        }
