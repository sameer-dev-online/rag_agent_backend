"""
Tests for upload endpoint.
"""

import pytest
from io import BytesIO
from fastapi.testclient import TestClient


def test_health_check(test_client: TestClient):
    """
    Test health check endpoint.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    response = test_client.get("/api/v1/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint(test_client: TestClient):
    """
    Test root endpoint.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    response = test_client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.skip(reason="Requires OpenAI API key and full integration")
def test_upload_single_file(test_client: TestClient):
    """
    Test uploading a single text file.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    # Create a sample file
    file_content = b"This is a test document for upload."
    files = {"files": ("test.txt", BytesIO(file_content), "text/plain")}

    response = test_client.post("/api/v1/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["files_processed"] == 1
    assert data["chunks_created"] > 0
    assert len(data["details"]) == 1
    assert data["details"][0]["filename"] == "test.txt"
    assert data["details"][0]["status"] == "success"


@pytest.mark.skip(reason="Requires OpenAI API key and full integration")
def test_upload_multiple_files(test_client: TestClient):
    """
    Test uploading multiple files.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    files = [
        ("files", ("test1.txt", BytesIO(b"First document"), "text/plain")),
        ("files", ("test2.txt", BytesIO(b"Second document"), "text/plain")),
    ]

    response = test_client.post("/api/v1/upload", files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["files_processed"] == 2
    assert len(data["details"]) == 2


def test_upload_no_files(test_client: TestClient):
    """
    Test upload with no files.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    response = test_client.post("/api/v1/upload")

    # Should return validation error
    assert response.status_code == 422


@pytest.mark.skip(reason="Needs integration with validation service")
def test_upload_unsupported_file_type(test_client: TestClient):
    """
    Test uploading unsupported file type.

    Args:
        test_client (TestClient): FastAPI test client.
    """
    files = {"files": ("test.exe", BytesIO(b"executable"), "application/x-msdownload")}

    response = test_client.post("/api/v1/upload", files=files)

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "error" in data
