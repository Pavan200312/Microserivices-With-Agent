import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from models.database import Base, get_db
from models.commit import Commit
from models.tracking_session import TrackingSession
from services.github_client import GitHubClient

# Test database URL (in-memory SQLite for testing)
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Create test engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_commit_data():
    """Sample commit data for testing."""
    return {
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
        ]
    }

@pytest.fixture
def sample_tracking_session_data():
    """Sample tracking session data for testing."""
    return {
        "repository": "test/repo",
        "branch": "main",
        "status": "active"
    }

@pytest.fixture
def mock_github_client(monkeypatch):
    """Mock GitHub client for testing."""
    class MockGitHubClient:
        def __init__(self):
            self.test_connection_called = False
            self.get_commits_called = False
        
        def test_connection(self):
            self.test_connection_called = True
            return True
        
        def get_commits(self, repository, branch="main"):
            self.get_commits_called = True
            return [
                {
                    "commit_hash": "test1234567890abcdef1234567890abcdef12345678",
                    "author": "Test User",
                    "author_email": "test@example.com",
                    "message": "Test commit message",
                    "timestamp": "2025-08-15T10:00:00Z",
                    "repository": repository,
                    "branch": branch,
                    "files_changed": [
                        {
                            "filename": "test.py",
                            "status": "added",
                            "additions": 10,
                            "deletions": 0,
                            "changes": 10
                        }
                    ]
                }
            ]
    
    mock_client = MockGitHubClient()
    monkeypatch.setattr("main.github_client", mock_client)
    return mock_client
