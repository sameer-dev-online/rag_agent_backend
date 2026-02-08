"""
Configuration settings for the Streamlit frontend.

This module contains all API URLs, timeouts, and application constants.
"""

from typing import List

# API Configuration
API_BASE_URL: str = "http://localhost:8000/api/v1"
API_HEALTH_URL: str = "http://localhost:8000/api/v1/health"

# Request Timeouts (seconds)
HEALTH_TIMEOUT: int = 2
CHAT_TIMEOUT: int = 30
UPLOAD_TIMEOUT: int = 60

# File Upload Configuration
MAX_FILE_SIZE_MB: int = 10
ALLOWED_FILE_TYPES: List[str] = ["pdf", "docx", "txt"]

# UI Configuration
APP_TITLE: str = "RAG Chat Assistant"
APP_ICON: str = "💬"
PAGE_LAYOUT: str = "wide"

# Default Query Parameters
DEFAULT_TOP_K: int = 5
MIN_TOP_K: int = 1
MAX_TOP_K: int = 20
