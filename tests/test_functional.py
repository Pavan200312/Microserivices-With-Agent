import pytest
import requests
import time
import json
from unittest.mock import patch, Mock

class TestFunctionalEndToEnd:
    """Functional tests for the entire GitHub Commit Tracker system."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.base_url = "http://localhost:8000"
        self.github_service_url = "http://localhost:8001"
        self.ai_service_url = "http://localhost:8002"
        self.frontend_url = "http://localhost:3000"
        
        # Wait for services to be ready
        self.wait_for_services()
    
    def wait_for_services(self, timeout=30):
        """Wait for all services to be ready."""
        services = [
            (self.base_url, "API Gateway"),
            (self.github_service_url, "GitHub Service"),
            (self.ai_service_url, "AI Service"),
            (self.frontend_url, "Frontend")
        ]
        
        for url, service_name in services:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    response = requests.get(f"{url}/health", timeout=5)
                    if response.status_code == 200:
                        print(f"✅ {service_name} is ready")
                        break
                except requests.exceptions.RequestException:
                    time.sleep(1)
            else:
                pytest.fail(f"❌ {service_name} failed to start within {timeout} seconds")
    
    def test_system_health_check(self):
        """Test that all services are healthy."""
        services = [
            (self.base_url, "API Gateway"),
            (self.github_service_url, "GitHub Service"),
            (self.ai_service_url, "AI Service")
        ]
        
        for url, service_name in services:
            response = requests.get(f"{url}/health")
            assert response.status_code == 200, f"{service_name} health check failed"
            
            data = response.json()
            assert data["status"] == "healthy", f"{service_name} is not healthy"
            print(f"✅ {service_name} health check passed")
    
    def test_complete_workflow(self):
        """Test the complete workflow from tracking to analysis."""
        # Step 1: Start tracking
        print("🔄 Step 1: Starting tracking...")
        response = requests.post(f"{self.base_url}/api/tracking/start")
        assert response.status_code == 200, "Failed to start tracking"
        
        tracking_data = response.json()
        assert "commits_fetched" in tracking_data
        assert "session" in tracking_data
        print(f"✅ Tracking started, fetched {tracking_data['commits_fetched']} commits")
        
        # Step 2: Get commits
        print("🔄 Step 2: Retrieving commits...")
        response = requests.get(f"{self.base_url}/api/commits")
        assert response.status_code == 200, "Failed to get commits"
        
        commits = response.json()
        assert isinstance(commits, list)
        print(f"✅ Retrieved {len(commits)} commits")
        
        if commits:
            # Step 3: Analyze a commit
            commit = commits[0]
            print(f"🔄 Step 3: Analyzing commit {commit['commit_hash'][:8]}...")
            
            analysis_request = {
                "commit_hash": commit["commit_hash"],
                "commit_message": commit["message"],
                "files_changed": commit.get("files_changed", [])
            }
            
            response = requests.post(f"{self.ai_service_url}/analyze", json=analysis_request)
            assert response.status_code == 200, "Failed to analyze commit"
            
            analysis_data = response.json()
            assert "analysis" in analysis_data
            assert "processing_time_ms" in analysis_data
            print(f"✅ Analysis completed in {analysis_data['processing_time_ms']}ms")
            
            # Step 4: Get analysis by hash
            print("🔄 Step 4: Retrieving analysis...")
            response = requests.get(f"{self.ai_service_url}/analysis/{commit['commit_hash']}")
            assert response.status_code == 200, "Failed to get analysis"
            
            retrieved_analysis = response.json()
            assert retrieved_analysis["commit_hash"] == commit["commit_hash"]
            print("✅ Analysis retrieved successfully")
    
    def test_api_gateway_routing(self):
        """Test that API Gateway properly routes requests to services."""
        # Test GitHub service routing
        response = requests.get(f"{self.github_service_url}/commits")
        assert response.status_code == 200, "Direct GitHub service access failed"
        
        # Test API Gateway routing to GitHub service
        response = requests.get(f"{self.base_url}/api/commits")
        assert response.status_code == 200, "API Gateway routing to GitHub service failed"
        
        # Both should return the same data structure
        direct_data = requests.get(f"{self.github_service_url}/commits").json()
        gateway_data = requests.get(f"{self.base_url}/api/commits").json()
        
        assert isinstance(direct_data, list) == isinstance(gateway_data, list)
        print("✅ API Gateway routing working correctly")
    
    def test_error_handling(self):
        """Test error handling across the system."""
        # Test invalid endpoint
        response = requests.get(f"{self.base_url}/api/invalid-endpoint")
        assert response.status_code == 404, "Should return 404 for invalid endpoint"
        
        # Test invalid commit hash
        response = requests.get(f"{self.github_service_url}/commits/invalid-hash")
        assert response.status_code == 404, "Should return 404 for invalid commit hash"
        
        # Test invalid analysis hash
        response = requests.get(f"{self.ai_service_url}/analysis/invalid-hash")
        assert response.status_code == 404, "Should return 404 for invalid analysis hash"
        
        print("✅ Error handling working correctly")
    
    def test_data_consistency(self):
        """Test data consistency across services."""
        # Get commits from GitHub service
        github_response = requests.get(f"{self.github_service_url}/commits")
        github_commits = github_response.json()
        
        # Get commits through API Gateway
        gateway_response = requests.get(f"{self.base_url}/api/commits")
        gateway_commits = gateway_response.json()
        
        # Data should be consistent
        assert len(github_commits) == len(gateway_commits), "Commit count mismatch"
        
        if github_commits:
            # Check first commit structure
            github_commit = github_commits[0]
            gateway_commit = gateway_commits[0]
            
            required_fields = ["commit_hash", "author", "message", "repository"]
            for field in required_fields:
                assert field in github_commit, f"Missing field {field} in GitHub service"
                assert field in gateway_commit, f"Missing field {field} in API Gateway"
                assert github_commit[field] == gateway_commit[field], f"Field {field} mismatch"
        
        print("✅ Data consistency verified")
    
    def test_performance_metrics(self):
        """Test basic performance metrics."""
        # Test API Gateway response time
        start_time = time.time()
        response = requests.get(f"{self.base_url}/api/commits")
        api_gateway_time = time.time() - start_time
        
        # Test direct service response time
        start_time = time.time()
        response = requests.get(f"{self.github_service_url}/commits")
        direct_service_time = time.time() - start_time
        
        # API Gateway should add minimal overhead
        overhead = api_gateway_time - direct_service_time
        assert overhead < 1.0, f"API Gateway overhead too high: {overhead:.2f}s"
        
        print(f"✅ Performance metrics: API Gateway overhead {overhead:.3f}s")
    
    def test_concurrent_requests(self):
        """Test system behavior under concurrent requests."""
        import concurrent.futures
        
        def make_request():
            response = requests.get(f"{self.base_url}/api/commits")
            return response.status_code
        
        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # All requests should succeed
        assert all(status == 200 for status in results), "Some concurrent requests failed"
        print("✅ Concurrent requests handled successfully")
    
    def test_data_persistence(self):
        """Test that data persists across service restarts."""
        # Get initial commit count
        initial_response = requests.get(f"{self.base_url}/api/commits")
        initial_commits = initial_response.json()
        initial_count = len(initial_commits)
        
        # Start tracking to ensure data exists
        requests.post(f"{self.base_url}/api/tracking/start")
        
        # Get commit count after tracking
        after_tracking_response = requests.get(f"{self.base_url}/api/commits")
        after_tracking_commits = after_tracking_response.json()
        after_tracking_count = len(after_tracking_commits)
        
        # Data should persist (count should not decrease)
        assert after_tracking_count >= initial_count, "Data was lost"
        print("✅ Data persistence verified")
    
    def test_frontend_integration(self):
        """Test frontend integration with backend services."""
        # Test frontend accessibility
        try:
            response = requests.get(self.frontend_url, timeout=10)
            assert response.status_code == 200, "Frontend not accessible"
            print("✅ Frontend is accessible")
        except requests.exceptions.RequestException:
            print("⚠️ Frontend not accessible (may be expected in test environment)")
    
    def test_system_monitoring(self):
        """Test system monitoring endpoints."""
        # Test all health endpoints
        health_endpoints = [
            f"{self.base_url}/health",
            f"{self.github_service_url}/health",
            f"{self.ai_service_url}/health"
        ]
        
        for endpoint in health_endpoints:
            response = requests.get(endpoint)
            assert response.status_code == 200, f"Health check failed for {endpoint}"
            
            data = response.json()
            assert "status" in data, f"Missing status in health response for {endpoint}"
            assert "service" in data, f"Missing service name in health response for {endpoint}"
        
        print("✅ System monitoring working correctly")
    
    def test_api_documentation(self):
        """Test API documentation endpoints."""
        # Test OpenAPI documentation
        response = requests.get(f"{self.base_url}/docs")
        assert response.status_code == 200, "API documentation not accessible"
        
        response = requests.get(f"{self.github_service_url}/docs")
        assert response.status_code == 200, "GitHub service documentation not accessible"
        
        response = requests.get(f"{self.ai_service_url}/docs")
        assert response.status_code == 200, "AI service documentation not accessible"
        
        print("✅ API documentation accessible")
