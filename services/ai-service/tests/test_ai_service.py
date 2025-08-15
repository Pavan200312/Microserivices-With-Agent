import pytest
from unittest.mock import patch, Mock
from models.analysis import AIAnalysis

class TestAIService:
    """Test cases for AI service endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "AI Service"
        assert data["status"] == "running"
        assert data["version"] == "1.0.0"
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "ai-service"
        assert "timestamp" in data
    
    def test_analyze_commit_success(self, client, sample_analysis_data):
        """Test successful commit analysis."""
        with patch('services.analysis_service.AnalysisService.analyze_commit') as mock_analyze:
            mock_analyze.return_value = sample_analysis_data["analysis_data"]
            
            response = client.post("/analyze", json={
                "commit_hash": sample_analysis_data["commit_hash"],
                "commit_message": "Test commit message",
                "files_changed": [{"filename": "test.py", "status": "added"}]
            })
            
            assert response.status_code == 200
            data = response.json()
            
            assert "analysis" in data
            assert "processing_time_ms" in data
            assert "model_used" in data
            
            analysis = data["analysis"]
            assert "summary" in analysis
            assert "complexity" in analysis
            assert "risk_level" in analysis
            assert "suggestions" in analysis
            
            mock_analyze.assert_called_once()
    
    def test_analyze_commit_missing_data(self, client):
        """Test commit analysis with missing required data."""
        response = client.post("/analyze", json={
            "commit_hash": "test123"
            # Missing commit_message and files_changed
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_commit_invalid_data(self, client):
        """Test commit analysis with invalid data."""
        response = client.post("/analyze", json={
            "commit_hash": "",
            "commit_message": "",
            "files_changed": []
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_analyze_commit_service_error(self, client):
        """Test commit analysis when service fails."""
        with patch('services.analysis_service.AnalysisService.analyze_commit') as mock_analyze:
            mock_analyze.side_effect = Exception("Analysis service error")
            
            response = client.post("/analyze", json={
                "commit_hash": "test1234567890abcdef1234567890abcdef12345678",
                "commit_message": "Test commit message",
                "files_changed": [{"filename": "test.py", "status": "added"}]
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "Failed to analyze commit" in data["detail"]
    
    def test_get_analysis_by_hash(self, client, db_session, sample_analysis_data):
        """Test getting analysis by commit hash."""
        # Create a test analysis record
        analysis = AIAnalysis(
            commit_hash=sample_analysis_data["commit_hash"],
            analysis_type=sample_analysis_data["analysis_type"],
            analysis_data=sample_analysis_data["analysis_data"],
            model_used=sample_analysis_data["model_used"],
            processing_time_ms=sample_analysis_data["processing_time_ms"]
        )
        db_session.add(analysis)
        db_session.commit()
        
        response = client.get(f"/analysis/{sample_analysis_data['commit_hash']}")
        assert response.status_code == 200
        data = response.json()
        
        assert data["commit_hash"] == sample_analysis_data["commit_hash"]
        assert data["analysis_type"] == sample_analysis_data["analysis_type"]
        assert data["model_used"] == sample_analysis_data["model_used"]
        assert data["processing_time_ms"] == sample_analysis_data["processing_time_ms"]
        
        analysis_data = data["analysis_data"]
        assert analysis_data["summary"] == sample_analysis_data["analysis_data"]["summary"]
        assert analysis_data["complexity"] == sample_analysis_data["analysis_data"]["complexity"]
        assert analysis_data["risk_level"] == sample_analysis_data["analysis_data"]["risk_level"]
        assert analysis_data["suggestions"] == sample_analysis_data["analysis_data"]["suggestions"]
    
    def test_get_analysis_by_hash_not_found(self, client):
        """Test getting analysis for non-existent commit hash."""
        response = client.get("/analysis/nonexistent_hash")
        assert response.status_code == 404
        data = response.json()
        assert data["detail"] == "Analysis not found"
    
    def test_get_all_analyses_empty(self, client):
        """Test getting all analyses when none exist."""
        response = client.get("/analyses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_all_analyses_with_data(self, client, db_session, sample_analysis_data):
        """Test getting all analyses when data exists."""
        # Create test analysis records
        analysis1 = AIAnalysis(
            commit_hash=sample_analysis_data["commit_hash"],
            analysis_type=sample_analysis_data["analysis_type"],
            analysis_data=sample_analysis_data["analysis_data"],
            model_used=sample_analysis_data["model_used"],
            processing_time_ms=sample_analysis_data["processing_time_ms"]
        )
        
        analysis2 = AIAnalysis(
            commit_hash="another1234567890abcdef1234567890abcdef12345678",
            analysis_type="commit_analysis",
            analysis_data={"summary": "Another analysis"},
            model_used="codellama",
            processing_time_ms=1000
        )
        
        db_session.add(analysis1)
        db_session.add(analysis2)
        db_session.commit()
        
        response = client.get("/analyses")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Check first analysis
        first_analysis = data[0]
        assert first_analysis["commit_hash"] == sample_analysis_data["commit_hash"]
        assert first_analysis["analysis_type"] == sample_analysis_data["analysis_type"]
        
        # Check second analysis
        second_analysis = data[1]
        assert second_analysis["commit_hash"] == "another1234567890abcdef1234567890abcdef12345678"
        assert second_analysis["analysis_data"]["summary"] == "Another analysis"
    
    def test_analyze_commit_with_ollama_error(self, client):
        """Test commit analysis when Ollama service fails."""
        with patch('services.ollama_client.OllamaClient.generate_response') as mock_ollama:
            mock_ollama.side_effect = Exception("Ollama service unavailable")
            
            response = client.post("/analyze", json={
                "commit_hash": "test1234567890abcdef1234567890abcdef12345678",
                "commit_message": "Test commit message",
                "files_changed": [{"filename": "test.py", "status": "added"}]
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "Failed to analyze commit" in data["detail"]
    
    def test_analyze_commit_with_large_data(self, client):
        """Test commit analysis with large commit data."""
        large_files_changed = [
            {"filename": f"file{i}.py", "status": "modified"} 
            for i in range(100)
        ]
        
        with patch('services.analysis_service.AnalysisService.analyze_commit') as mock_analyze:
            mock_analyze.return_value = {
                "summary": "Large commit with many files",
                "complexity": "high",
                "risk_level": "medium",
                "suggestions": ["Consider breaking into smaller commits"]
            }
            
            response = client.post("/analyze", json={
                "commit_hash": "test1234567890abcdef1234567890abcdef12345678",
                "commit_message": "Large commit with many changes",
                "files_changed": large_files_changed
            })
            
            assert response.status_code == 200
            data = response.json()
            assert "analysis" in data
            assert data["analysis"]["complexity"] == "high"
    
    def test_analyze_commit_edge_cases(self, client):
        """Test commit analysis with edge case data."""
        edge_cases = [
            {
                "commit_hash": "test1234567890abcdef1234567890abcdef12345678",
                "commit_message": "",  # Empty message
                "files_changed": []
            },
            {
                "commit_hash": "test1234567890abcdef1234567890abcdef12345678",
                "commit_message": "A" * 1000,  # Very long message
                "files_changed": [{"filename": "test.py", "status": "added"}]
            },
            {
                "commit_hash": "test1234567890abcdef1234567890abcdef12345678",
                "commit_message": "Test commit",
                "files_changed": [{"filename": "test.py", "status": "unknown_status"}]
            }
        ]
        
        for case in edge_cases:
            with patch('services.analysis_service.AnalysisService.analyze_commit') as mock_analyze:
                mock_analyze.return_value = {"summary": "Edge case analysis"}
                
                response = client.post("/analyze", json=case)
                
                # Should handle edge cases gracefully
                assert response.status_code in [200, 422]  # 422 for validation errors
                
                if response.status_code == 200:
                    data = response.json()
                    assert "analysis" in data
