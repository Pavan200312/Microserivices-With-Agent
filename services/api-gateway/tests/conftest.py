import pytest
import asyncio
from fastapi.testclient import TestClient
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def client():
    """Create a test client."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_github_service_response():
    """Mock response from GitHub service."""
    return [
        {
            "id": 1,
            "commit_hash": "test1234567890abcdef1234567890abcdef12345678",
            "author": "Test User",
            "author_email": "test@example.com",
            "message": "Test commit message",
            "timestamp": "2025-08-15T10:00:00Z",
            "repository": "test/repo",
            "branch": "main",
            "files_changed": [
                {
                    "filename": "test.py",
                    "status": "added",
                    "additions": 10,
                    "deletions": 0,
                    "changes": 10
                }
            ],
            "created_at": "2025-08-15T10:00:00Z",
            "updated_at": None
        }
    ]

@pytest.fixture
def mock_tracking_response():
    """Mock response from tracking endpoint."""
    return {
        "message": "Tracking started successfully. Fetched 1 new commits.",
        "session": {
            "id": 1,
            "repository": "test/repo",
            "branch": "main",
            "status": "active",
            "started_at": "2025-08-15T10:00:00Z",
            "last_commit_hash": "test1234567890abcdef1234567890abcdef12345678",
            "last_polled_at": "2025-08-15T10:00:00Z",
            "created_at": "2025-08-15T10:00:00Z",
            "updated_at": "2025-08-15T10:00:00Z"
        },
        "commits_fetched": 1
    }
