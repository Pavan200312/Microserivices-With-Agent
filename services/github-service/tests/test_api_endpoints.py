import pytest
from datetime import datetime
from models.commit import Commit
from models.tracking_session import TrackingSession

class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "GitHub Service"
        assert data["status"] == "running"
        assert data["version"] == "1.0.0"
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "github-service"
        assert "timestamp" in data
    
    def test_get_commits_empty(self, client):
        """Test getting commits when database is empty."""
        response = client.get("/commits")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_commits_with_data(self, client, db_session, sample_commit_data):
        """Test getting commits when data exists."""
        # Create a test commit
        commit = Commit(
            commit_hash=sample_commit_data["commit_hash"],
            author=sample_commit_data["author"],
            author_email=sample_commit_data["author_email"],
            message=sample_commit_data["message"],
            timestamp=datetime.fromisoformat(sample_commit_data["timestamp"].replace('Z', '+00:00')),
            repository=sample_commit_data["repository"],
            branch=sample_commit_data["branch"],
            files_changed=sample_commit_data["files_changed"]
        )
        db_session.add(commit)
        db_session.commit()
        
        response = client.get("/commits")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        
        commit_data = data[0]
        assert commit_data["commit_hash"] == sample_commit_data["commit_hash"]
        assert commit_data["author"] == sample_commit_data["author"]
        assert commit_data["message"] == sample_commit_data["message"]
        assert commit_data["repository"] == sample_commit_data["repository"]
    
    def test_get_commit_by_hash(self, client, db_session, sample_commit_data):
        """Test getting a specific commit by hash."""
        # Create a test commit
        commit = Commit(
            commit_hash=sample_commit_data["commit_hash"],
            author=sample_commit_data["author"],
            author_email=sample_commit_data["author_email"],
            message=sample_commit_data["message"],
            timestamp=datetime.fromisoformat(sample_commit_data["timestamp"].replace('Z', '+00:00')),
            repository=sample_commit_data["repository"],
            branch=sample_commit_data["branch"],
            files_changed=sample_commit_data["files_changed"]
        )
        db_session.add(commit)
        db_session.commit()
        
        response = client.get(f"/commits/{sample_commit_data['commit_hash']}")
        assert response.status_code == 200
        data = response.json()
        assert data["commit_hash"] == sample_commit_data["commit_hash"]
        assert data["author"] == sample_commit_data["author"]
        assert data["message"] == sample_commit_data["message"]
    
    def test_get_commit_by_hash_not_found(self, client):
        """Test getting a commit that doesn't exist."""
        response = client.get("/commits/nonexistent_hash")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Commit not found"
    
    def test_start_tracking_new_session(self, client, mock_github_client):
        """Test starting tracking for a new repository."""
        response = client.post("/start-tracking")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Tracking started successfully" in data["message"]
        assert "session" in data
        assert "commits_fetched" in data
        
        session = data["session"]
        assert session["repository"] == "Pavan200312/Microserivices-With-Agent"
        assert session["branch"] == "main"
        assert session["status"] == "active"
        
        # Verify GitHub client was called
        assert mock_github_client.get_commits_called
    
    def test_start_tracking_existing_session(self, client, db_session, mock_github_client):
        """Test starting tracking when session already exists."""
        # Create an existing tracking session
        session = TrackingSession(
            repository="Pavan200312/Microserivices-With-Agent",
            branch="main",
            status="active"
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.post("/start-tracking")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Tracking started successfully" in data["message"]
        assert "session" in data
        assert "commits_fetched" in data
        
        # Verify GitHub client was called
        assert mock_github_client.get_commits_called
    
    def test_fetch_commits_no_active_sessions(self, client):
        """Test fetching commits when no active sessions exist."""
        response = client.post("/fetch-commits")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "No active tracking sessions"
    
    def test_fetch_commits_with_active_session(self, client, db_session, mock_github_client):
        """Test fetching commits with active session."""
        # Create an active tracking session
        session = TrackingSession(
            repository="test/repo",
            branch="main",
            status="active"
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.post("/fetch-commits")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Fetched" in data["message"]
        assert "total_new_commits" in data
        
        # Verify GitHub client was called
        assert mock_github_client.get_commits_called
    
    def test_get_tracking_sessions_empty(self, client):
        """Test getting tracking sessions when none exist."""
        response = client.get("/tracking-sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_tracking_sessions_with_data(self, client, db_session, sample_tracking_session_data):
        """Test getting tracking sessions when data exists."""
        # Create a test tracking session
        session = TrackingSession(
            repository=sample_tracking_session_data["repository"],
            branch=sample_tracking_session_data["branch"],
            status=sample_tracking_session_data["status"]
        )
        db_session.add(session)
        db_session.commit()
        
        response = client.get("/tracking-sessions")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        
        session_data = data[0]
        assert session_data["repository"] == sample_tracking_session_data["repository"]
        assert session_data["branch"] == sample_tracking_session_data["branch"]
        assert session_data["status"] == sample_tracking_session_data["status"]
    
    def test_start_tracking_github_error(self, client, monkeypatch):
        """Test starting tracking when GitHub API fails."""
        class MockGitHubClient:
            def get_commits(self, repository, branch="main"):
                raise Exception("GitHub API error")
        
        monkeypatch.setattr("main.github_client", MockGitHubClient())
        
        response = client.post("/start-tracking")
        assert response.status_code == 500
        data = response.json()
        assert "Failed to fetch commits" in data["detail"]
    
    def test_fetch_commits_github_error(self, client, db_session, monkeypatch):
        """Test fetching commits when GitHub API fails."""
        # Create an active tracking session
        session = TrackingSession(
            repository="test/repo",
            branch="main",
            status="active"
        )
        db_session.add(session)
        db_session.commit()
        
        class MockGitHubClient:
            def get_commits(self, repository, branch="main"):
                raise Exception("GitHub API error")
        
        monkeypatch.setattr("main.github_client", MockGitHubClient())
        
        response = client.post("/fetch-commits")
        assert response.status_code == 200  # Should handle error gracefully
        data = response.json()
        assert data["total_new_commits"] == 0
    
    def test_commit_duplicate_handling(self, client, db_session, sample_commit_data, mock_github_client):
        """Test that duplicate commits are not stored."""
        # Create an existing commit
        commit = Commit(
            commit_hash=sample_commit_data["commit_hash"],
            author=sample_commit_data["author"],
            author_email=sample_commit_data["author_email"],
            message=sample_commit_data["message"],
            timestamp=datetime.fromisoformat(sample_commit_data["timestamp"].replace('Z', '+00:00')),
            repository=sample_commit_data["repository"],
            branch=sample_commit_data["branch"],
            files_changed=sample_commit_data["files_changed"]
        )
        db_session.add(commit)
        db_session.commit()
        
        # Start tracking (should not add duplicate)
        response = client.post("/start-tracking")
        assert response.status_code == 200
        data = response.json()
        
        # Should fetch commits but not add duplicates
        assert data["commits_fetched"] == 0
        
        # Verify only one commit exists
        commits_response = client.get("/commits")
        commits_data = commits_response.json()
        assert len(commits_data) == 1
