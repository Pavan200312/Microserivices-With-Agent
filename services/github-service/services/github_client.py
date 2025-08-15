import requests
import os
from dotenv import load_dotenv
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Load environment variables (only if .env file exists)
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class GitHubClient:
    """Client for interacting with GitHub API"""
    
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        logger.info(f"GitHub token found: {'Yes' if self.token else 'No'}")
        if self.token:
            logger.info(f"Token starts with: {self.token[:10]}...")
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        if not self.token:
            logger.warning("GitHub token not found. Some features may not work.")
    
    def get_commits(self, repository: str, branch: str = "main", since: Optional[str] = None) -> List[Dict]:
        """
        Get commits from a GitHub repository
        
        Args:
            repository: Repository name (e.g., "username/repo")
            branch: Branch name (default: "main")
            since: ISO 8601 timestamp to get commits since
            
        Returns:
            List of commit dictionaries
        """
        try:
            url = f"{self.base_url}/repos/{repository}/commits"
            params = {
                "sha": branch,
                "per_page": 100  # Maximum commits per request
            }
            
            if since:
                params["since"] = since
            
            logger.info(f"Fetching commits from {repository} branch {branch}")
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            commits = response.json()
            logger.info(f"Successfully fetched {len(commits)} commits from {repository}")
            
            # Process commits to extract needed information
            processed_commits = []
            for commit in commits:
                processed_commit = {
                    "commit_hash": commit["sha"],
                    "author": commit["commit"]["author"]["name"],
                    "message": commit["commit"]["message"],
                    "timestamp": commit["commit"]["author"]["date"]
                }
                processed_commits.append(processed_commit)
            
            return processed_commits
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch commits from {repository}: {e}")
            raise
    
    def _get_commit_files(self, repository: str, commit_hash: str) -> List[Dict]:
        """
        Get files changed in a specific commit
        
        Args:
            repository: Repository name
            commit_hash: Commit hash
            
        Returns:
            List of file change dictionaries
        """
        try:
            url = f"{self.base_url}/repos/{repository}/commits/{commit_hash}"
            
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            commit_data = response.json()
            files_changed = []
            
            for file in commit_data.get("files", []):
                file_info = {
                    "filename": file["filename"],
                    "status": file["status"],  # added, modified, removed
                    "additions": file.get("additions", 0),
                    "deletions": file.get("deletions", 0),
                    "changes": file.get("changes", 0)
                }
                files_changed.append(file_info)
            
            return files_changed
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch files for commit {commit_hash}: {e}")
            return []
    
    def get_latest_commit(self, repository: str, branch: str = "main") -> Optional[Dict]:
        """
        Get the latest commit from a repository
        
        Args:
            repository: Repository name
            branch: Branch name
            
        Returns:
            Latest commit dictionary or None
        """
        try:
            commits = self.get_commits(repository, branch, per_page=1)
            return commits[0] if commits else None
            
        except Exception as e:
            logger.error(f"Failed to get latest commit from {repository}: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test GitHub API connection
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/user", headers=self.headers)
            response.raise_for_status()
            
            user_data = response.json()
            logger.info(f"GitHub API connection successful. Authenticated as: {user_data.get('login')}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API connection failed: {e}")
            return False
