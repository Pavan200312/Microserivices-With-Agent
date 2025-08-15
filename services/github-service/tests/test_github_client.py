import pytest
from unittest.mock import patch, Mock
from services.github_client import GitHubClient

class TestGitHubClient:
    """Test cases for the GitHub client."""
    
    def test_github_client_initialization(self):
        """Test GitHub client initialization."""
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
            client = GitHubClient()
            assert client.token == 'test_token'
            assert client.base_url == "https://api.github.com"
            assert "Authorization" in client.headers
            assert client.headers["Authorization"] == "token test_token"
    
    def test_github_client_no_token(self):
        """Test GitHub client initialization without token."""
        with patch.dict('os.environ', {}, clear=True):
            client = GitHubClient()
            assert client.token is None
            assert "Authorization" not in client.headers
    
    @patch('requests.get')
    def test_test_connection_success(self, mock_get):
        """Test successful connection to GitHub API."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"login": "testuser"}
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
            client = GitHubClient()
            result = client.test_connection()
            
            assert result is True
            mock_get.assert_called_once_with(
                "https://api.github.com/user",
                headers=client.headers
            )
    
    @patch('requests.get')
    def test_test_connection_failure(self, mock_get):
        """Test failed connection to GitHub API."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'invalid_token'}):
            client = GitHubClient()
            result = client.test_connection()
            
            assert result is False
    
    @patch('requests.get')
    def test_get_commits_success(self, mock_get):
        """Test successful commit retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "sha": "test1234567890abcdef1234567890abcdef12345678",
                "commit": {
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "date": "2025-08-15T10:00:00Z"
                    },
                    "message": "Test commit message"
                },
                "files": [
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
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
            client = GitHubClient()
            commits = client.get_commits("test/repo", "main")
            
            assert len(commits) == 1
            commit = commits[0]
            assert commit["commit_hash"] == "test1234567890abcdef1234567890abcdef12345678"
            assert commit["author"] == "Test User"
            assert commit["author_email"] == "test@example.com"
            assert commit["message"] == "Test commit message"
            assert commit["repository"] == "test/repo"
            assert commit["branch"] == "main"
            assert len(commit["files_changed"]) == 1
            assert commit["files_changed"][0]["filename"] == "test.py"
            
            mock_get.assert_called_once_with(
                "https://api.github.com/repos/test/repo/commits?sha=main",
                headers=client.headers
            )
    
    @patch('requests.get')
    def test_get_commits_api_error(self, mock_get):
        """Test commit retrieval with API error."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("Repository not found")
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
            client = GitHubClient()
            
            with pytest.raises(Exception, match="Repository not found"):
                client.get_commits("invalid/repo", "main")
    
    @patch('requests.get')
    def test_get_commits_empty_response(self, mock_get):
        """Test commit retrieval with empty response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
            client = GitHubClient()
            commits = client.get_commits("test/repo", "main")
            
            assert commits == []
    
    @patch('requests.get')
    def test_get_commits_without_files(self, mock_get):
        """Test commit retrieval when commits have no files."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "sha": "test1234567890abcdef1234567890abcdef12345678",
                "commit": {
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                        "date": "2025-08-15T10:00:00Z"
                    },
                    "message": "Test commit message"
                },
                "files": []  # No files
            }
        ]
        mock_get.return_value = mock_response
        
        with patch.dict('os.environ', {'GITHUB_TOKEN': 'test_token'}):
            client = GitHubClient()
            commits = client.get_commits("test/repo", "main")
            
            assert len(commits) == 1
            commit = commits[0]
            assert commit["files_changed"] == []
    
    def test_get_commits_without_token(self):
        """Test commit retrieval without GitHub token."""
        with patch.dict('os.environ', {}, clear=True):
            client = GitHubClient()
            
            with pytest.raises(ValueError, match="GitHub token is required"):
                client.get_commits("test/repo", "main")
