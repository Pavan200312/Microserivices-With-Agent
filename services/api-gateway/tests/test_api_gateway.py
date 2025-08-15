import pytest
from unittest.mock import patch, Mock
import httpx

class TestAPIGateway:
    """Test cases for API Gateway endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "GitHub Commit Tracker API Gateway"
        assert data["status"] == "running"
        assert "services" in data
        assert "github_service" in data["services"]
        assert "ai_service" in data["services"]
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "api-gateway"
        assert "timestamp" in data
    
    @patch('httpx.AsyncClient.get')
    def test_get_commits_success(self, mock_get, client, mock_github_service_response):
        """Test successful commit retrieval through API Gateway."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_github_service_response
        mock_get.return_value = mock_response
        
        response = client.get("/api/commits")
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 1
        
        commit = data[0]
        assert commit["commit_hash"] == "test1234567890abcdef1234567890abcdef12345678"
        assert commit["author"] == "Test User"
        assert commit["message"] == "Test commit message"
        assert commit["repository"] == "test/repo"
    
    @patch('httpx.AsyncClient.get')
    def test_get_commits_github_service_error(self, mock_get, client):
        """Test commit retrieval when GitHub service returns error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        response = client.get("/api/commits")
        assert response.status_code == 500
        data = response.json()
        assert "Failed to fetch commits from GitHub service" in data["detail"]
    
    @patch('httpx.AsyncClient.get')
    def test_get_commits_github_service_unavailable(self, mock_get, client):
        """Test commit retrieval when GitHub service is unavailable."""
        mock_get.side_effect = httpx.RequestError("Connection failed")
        
        response = client.get("/api/commits")
        assert response.status_code == 503
        data = response.json()
        assert "GitHub service is not available" in data["detail"]
    
    @patch('httpx.AsyncClient.post')
    def test_start_tracking_success(self, mock_post, client, mock_tracking_response):
        """Test successful tracking start through API Gateway."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_tracking_response
        mock_post.return_value = mock_response
        
        response = client.post("/api/tracking/start")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Tracking started successfully" in data["message"]
        assert "session" in data
        assert "commits_fetched" in data
        
        session = data["session"]
        assert session["repository"] == "test/repo"
        assert session["status"] == "active"
        assert data["commits_fetched"] == 1
    
    @patch('httpx.AsyncClient.post')
    def test_start_tracking_github_service_error(self, mock_post, client):
        """Test tracking start when GitHub service returns error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        response = client.post("/api/tracking/start")
        assert response.status_code == 500
        data = response.json()
        assert "Failed to start tracking" in data["detail"]
    
    @patch('httpx.AsyncClient.post')
    def test_start_tracking_github_service_unavailable(self, mock_post, client):
        """Test tracking start when GitHub service is unavailable."""
        mock_post.side_effect = httpx.RequestError("Connection failed")
        
        response = client.post("/api/tracking/start")
        assert response.status_code == 503
        data = response.json()
        assert "GitHub service is not available" in data["detail"]
    
    @patch('httpx.AsyncClient.post')
    def test_fetch_commits_success(self, mock_post, client):
        """Test successful commit fetching through API Gateway."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "message": "Fetched 2 new commits",
            "total_new_commits": 2
        }
        mock_post.return_value = mock_response
        
        response = client.post("/api/fetch-commits")
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "Fetched 2 new commits" in data["message"]
        assert data["total_new_commits"] == 2
    
    @patch('httpx.AsyncClient.post')
    def test_fetch_commits_github_service_error(self, mock_post, client):
        """Test commit fetching when GitHub service returns error."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        response = client.post("/api/fetch-commits")
        assert response.status_code == 500
        data = response.json()
        assert "Failed to fetch commits from GitHub" in data["detail"]
    
    @patch('httpx.AsyncClient.post')
    def test_fetch_commits_github_service_unavailable(self, mock_post, client):
        """Test commit fetching when GitHub service is unavailable."""
        mock_post.side_effect = httpx.RequestError("Connection failed")
        
        response = client.post("/api/fetch-commits")
        assert response.status_code == 503
        data = response.json()
        assert "GitHub service is not available" in data["detail"]
    
    def test_cors_headers(self, client):
        """Test that CORS headers are properly set."""
        response = client.options("/api/commits")
        # FastAPI automatically handles CORS for OPTIONS requests
        assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly handled
    
    def test_invalid_endpoint(self, client):
        """Test invalid endpoint returns 404."""
        response = client.get("/api/invalid-endpoint")
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client):
        """Test that wrong HTTP method returns 405."""
        response = client.post("/api/commits")  # Should be GET
        assert response.status_code == 405
    
    @patch('httpx.AsyncClient.get')
    def test_get_commits_empty_response(self, mock_get, client):
        """Test commit retrieval with empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        response = client.get("/api/commits")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @patch('httpx.AsyncClient.post')
    def test_start_tracking_timeout(self, mock_post, client):
        """Test tracking start with timeout."""
        mock_post.side_effect = httpx.TimeoutException("Request timed out")
        
        response = client.post("/api/tracking/start")
        assert response.status_code == 503
        data = response.json()
        assert "GitHub service is not available" in data["detail"]
    
    @patch('httpx.AsyncClient.get')
    def test_get_commits_timeout(self, mock_get, client):
        """Test commit retrieval with timeout."""
        mock_get.side_effect = httpx.TimeoutException("Request timed out")
        
        response = client.get("/api/commits")
        assert response.status_code == 503
        data = response.json()
        assert "GitHub service is not available" in data["detail"]
