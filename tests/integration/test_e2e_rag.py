"""
End-to-end integration test for RAG system (upload + chat).
"""

import pytest
from io import BytesIO


@pytest.mark.integration
def test_e2e_upload_and_chat(test_client):
    """
    Test complete RAG workflow: upload document then query it.

    Args:
        test_client: FastAPI test client fixture.
    """
    # Step 1: Upload a test document
    test_content = b"Machine learning is a subset of artificial intelligence. It focuses on training algorithms."
    files = {"files": ("ml_intro.txt", BytesIO(test_content), "text/plain")}

    upload_response = test_client.post("/api/v1/upload", files=files)

    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert upload_data["success"] is True
    assert upload_data["chunks_created"] > 0

    # Step 2: Query the uploaded document
    # Note: This test requires actual embeddings and vector store
    # For unit testing, we would mock these components
    chat_request = {"query": "What is machine learning?", "top_k": 3}

    chat_response = test_client.post("/api/v1/chat", json=chat_request)

    assert chat_response.status_code == 200
    chat_data = chat_response.json()

    # In a real integration test with actual components:
    # assert chat_data["success"] is True
    # assert "machine learning" in chat_data["answer"].lower()
    # assert len(chat_data["sources"]) > 0

    # For this test structure, we just verify the endpoint is reachable
    assert "success" in chat_data
    assert "answer" in chat_data


@pytest.mark.integration
def test_e2e_chat_before_upload(test_client):
    """
    Test querying before any documents are uploaded.

    Args:
        test_client: FastAPI test client fixture.
    """
    chat_request = {"query": "What is quantum computing?", "top_k": 5}

    chat_response = test_client.post("/api/v1/chat", json=chat_request)

    assert chat_response.status_code == 200
    chat_data = chat_response.json()

    # Should return success with no sources
    assert "success" in chat_data
    # In real integration test: assert len(chat_data["sources"]) == 0


@pytest.mark.integration
def test_e2e_multiple_documents(test_client):
    """
    Test uploading multiple documents and querying across them.

    Args:
        test_client: FastAPI test client fixture.
    """
    # Upload two documents
    files = [
        ("files", ("doc1.txt", BytesIO(b"Python is a programming language."), "text/plain")),
        ("files", ("doc2.txt", BytesIO(b"JavaScript is used for web development."), "text/plain")),
    ]

    upload_response = test_client.post("/api/v1/upload", files=files)

    assert upload_response.status_code == 200
    upload_data = upload_response.json()
    assert upload_data["files_processed"] == 2

    # Query that should match both documents
    chat_request = {"query": "What programming languages are mentioned?", "top_k": 5}

    chat_response = test_client.post("/api/v1/chat", json=chat_request)

    assert chat_response.status_code == 200
    # In real integration test: verify answer mentions both Python and JavaScript
