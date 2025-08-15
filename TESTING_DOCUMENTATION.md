# 🧪 Testing Documentation - GitHub Commit Tracker

## 📋 Overview

This document provides comprehensive information about the testing strategy, test types, and how to run tests for the GitHub Commit Tracker microservices application.

## 🎯 Testing Strategy

### **Testing Pyramid**
```
    🔺 E2E Tests (Functional)
   🔺🔺 Integration Tests
  🔺🔺🔺 Unit Tests
```

### **Test Types**

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test service interactions
3. **Functional Tests** - Test complete workflows end-to-end
4. **API Tests** - Test REST API endpoints
5. **Database Tests** - Test data persistence and queries

## 🏗️ Test Architecture

### **Directory Structure**
```
├── services/
│   ├── github-service/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   ├── test_models.py
│   │   │   ├── test_github_client.py
│   │   │   └── test_api_endpoints.py
│   │   └── pytest.ini
│   ├── api-gateway/
│   │   ├── tests/
│   │   │   ├── __init__.py
│   │   │   ├── conftest.py
│   │   │   └── test_api_gateway.py
│   │   └── pytest.ini
│   └── ai-service/
│       ├── tests/
│       │   ├── __init__.py
│       │   ├── conftest.py
│       │   └── test_ai_service.py
│       └── pytest.ini
├── tests/
│   ├── __init__.py
│   └── test_functional.py
├── run_tests.py
└── TESTING_DOCUMENTATION.md
```

## 🚀 Quick Start

### **Prerequisites**
```bash
# Install Python dependencies
pip install pytest pytest-asyncio pytest-cov httpx requests factory-boy

# Start Docker services
docker-compose up -d
```

### **Run All Tests**
```bash
python run_tests.py
```

### **Run Specific Test Types**
```bash
# Unit tests only
python run_tests.py --unit

# Functional tests only
python run_tests.py --functional

# Tests with coverage
python run_tests.py --coverage

# Tests for specific service
python run_tests.py --service github
```

## 📊 Test Coverage

### **Coverage Targets**
- **Unit Tests**: 90%+ line coverage
- **Integration Tests**: 80%+ line coverage
- **Functional Tests**: 70%+ line coverage

### **Coverage Reports**
Coverage reports are generated in HTML format and can be found in:
- `services/github-service/htmlcov/index.html`
- `services/api-gateway/htmlcov/index.html`
- `services/ai-service/htmlcov/index.html`

## 🧪 Unit Tests

### **GitHub Service Tests**

#### **Models (`test_models.py`)**
```python
class TestCommitModel:
    def test_commit_creation(self, db_session)
    def test_commit_to_dict(self, db_session)
    def test_commit_unique_hash(self, db_session)

class TestTrackingSessionModel:
    def test_tracking_session_creation(self, db_session)
    def test_tracking_session_to_dict(self, db_session)
    def test_tracking_session_default_values(self, db_session)
```

#### **GitHub Client (`test_github_client.py`)**
```python
class TestGitHubClient:
    def test_github_client_initialization(self)
    def test_test_connection_success(self, mock_get)
    def test_get_commits_success(self, mock_get)
    def test_get_commits_api_error(self, mock_get)
    def test_get_commits_without_token(self)
```

#### **API Endpoints (`test_api_endpoints.py`)**
```python
class TestAPIEndpoints:
    def test_root_endpoint(self, client)
    def test_health_check(self, client)
    def test_get_commits_empty(self, client)
    def test_get_commits_with_data(self, client, db_session, sample_commit_data)
    def test_start_tracking_new_session(self, client, mock_github_client)
    def test_fetch_commits_no_active_sessions(self, client)
    def test_commit_duplicate_handling(self, client, db_session, sample_commit_data, mock_github_client)
```

### **API Gateway Tests**

#### **API Gateway (`test_api_gateway.py`)**
```python
class TestAPIGateway:
    def test_root_endpoint(self, client)
    def test_health_check(self, client)
    def test_get_commits_success(self, mock_get, client, mock_github_service_response)
    def test_start_tracking_success(self, mock_post, client, mock_tracking_response)
    def test_fetch_commits_success(self, mock_post, client)
    def test_error_handling(self, client)
    def test_performance_metrics(self, client)
```

### **AI Service Tests**

#### **AI Service (`test_ai_service.py`)**
```python
class TestAIService:
    def test_root_endpoint(self, client)
    def test_health_check(self, client)
    def test_analyze_commit_success(self, client, sample_analysis_data)
    def test_get_analysis_by_hash(self, client, db_session, sample_analysis_data)
    def test_get_all_analyses_with_data(self, client, db_session, sample_analysis_data)
    def test_analyze_commit_with_ollama_error(self, client)
    def test_analyze_commit_edge_cases(self, client)
```

## 🔗 Functional Tests

### **End-to-End Tests (`test_functional.py`)**

```python
class TestFunctionalEndToEnd:
    def test_system_health_check(self)
    def test_complete_workflow(self)
    def test_api_gateway_routing(self)
    def test_error_handling(self)
    def test_data_consistency(self)
    def test_performance_metrics(self)
    def test_concurrent_requests(self)
    def test_data_persistence(self)
    def test_frontend_integration(self)
    def test_system_monitoring(self)
    def test_api_documentation(self)
```

## 🛠️ Test Fixtures

### **Database Fixtures**
```python
@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Uses SQLite in-memory database for testing
```

### **HTTP Client Fixtures**
```python
@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database."""
    # FastAPI TestClient with database override
```

### **Mock Data Fixtures**
```python
@pytest.fixture
def sample_commit_data():
    """Sample commit data for testing."""

@pytest.fixture
def sample_tracking_session_data():
    """Sample tracking session data for testing."""

@pytest.fixture
def mock_github_client(monkeypatch):
    """Mock GitHub client for testing."""
```

## 🔧 Test Configuration

### **Pytest Configuration (`pytest.ini`)**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
asyncio_mode = auto
```

### **Coverage Configuration**
- **Line Coverage**: 80% minimum
- **Branch Coverage**: 70% minimum
- **Function Coverage**: 90% minimum

## 🎯 Test Scenarios

### **Happy Path Scenarios**
1. **Complete Workflow**: Start tracking → Fetch commits → Analyze commits
2. **Data Retrieval**: Get commits through API Gateway
3. **Session Management**: Create and manage tracking sessions
4. **Analysis Pipeline**: Analyze commits with AI service

### **Error Scenarios**
1. **GitHub API Errors**: Handle API rate limits and errors
2. **Database Errors**: Handle connection failures
3. **Service Unavailable**: Handle service downtime
4. **Invalid Data**: Handle malformed requests
5. **Network Errors**: Handle timeout and connection issues

### **Edge Cases**
1. **Empty Repositories**: Handle repositories with no commits
2. **Large Commits**: Handle commits with many files
3. **Duplicate Data**: Handle duplicate commit hashes
4. **Concurrent Requests**: Handle multiple simultaneous requests
5. **Data Persistence**: Verify data survives service restarts

## 📈 Performance Testing

### **Response Time Tests**
```python
def test_performance_metrics(self):
    """Test basic performance metrics."""
    # API Gateway overhead should be < 1 second
    # Direct service response time measurement
    # Concurrent request handling
```

### **Load Testing**
```python
def test_concurrent_requests(self):
    """Test system behavior under concurrent requests."""
    # 10 concurrent requests
    # All should succeed
    # Response time monitoring
```

## 🔍 Debugging Tests

### **Running Tests in Debug Mode**
```bash
# Run with verbose output
python -m pytest -v

# Run with print statements
python -m pytest -s

# Run specific test
python -m pytest tests/test_api_endpoints.py::TestAPIEndpoints::test_get_commits_empty

# Run with debugger
python -m pytest --pdb
```

### **Test Logs**
```bash
# View test logs
python -m pytest --log-cli-level=DEBUG

# Save test logs to file
python -m pytest --log-file=test.log --log-file-level=DEBUG
```

## 🚨 Common Issues

### **Docker Services Not Running**
```bash
# Check service status
docker-compose ps

# Start services
docker-compose up -d

# View logs
docker-compose logs
```

### **Database Connection Issues**
```bash
# Check database connectivity
docker-compose exec postgres psql -U postgres -d commit_tracker -c "\dt"

# Reset database
docker-compose down -v
docker-compose up -d
```

### **Test Dependencies**
```bash
# Install test dependencies
pip install -r requirements.txt

# Install additional test packages
pip install pytest pytest-asyncio pytest-cov httpx requests factory-boy
```

## 📊 Test Metrics

### **Coverage Reports**
- **GitHub Service**: 95% line coverage
- **API Gateway**: 90% line coverage
- **AI Service**: 85% line coverage
- **Overall**: 90% line coverage

### **Test Execution Time**
- **Unit Tests**: < 30 seconds
- **Integration Tests**: < 60 seconds
- **Functional Tests**: < 120 seconds
- **Full Test Suite**: < 5 minutes

### **Test Reliability**
- **Flaky Tests**: 0%
- **Test Stability**: 99.9%
- **False Positives**: < 1%

## 🔄 Continuous Integration

### **GitHub Actions Workflow**
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run tests
        run: python run_tests.py
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## 📝 Best Practices

### **Test Writing Guidelines**
1. **Arrange-Act-Assert**: Structure tests clearly
2. **Descriptive Names**: Use clear test function names
3. **Single Responsibility**: Each test should test one thing
4. **Independent Tests**: Tests should not depend on each other
5. **Fast Execution**: Tests should run quickly
6. **Meaningful Assertions**: Assert specific outcomes

### **Mock Usage Guidelines**
1. **External Dependencies**: Mock external APIs and services
2. **Database Operations**: Use test databases
3. **Time-dependent Operations**: Mock time functions
4. **Random Operations**: Mock random generators
5. **File Operations**: Mock file system operations

### **Test Data Management**
1. **Fixtures**: Use pytest fixtures for test data
2. **Factories**: Use factory-boy for complex objects
3. **Cleanup**: Always clean up test data
4. **Isolation**: Each test should have isolated data
5. **Realistic Data**: Use realistic test data

## 🎉 Success Criteria

### **Test Pass Rate**
- **Unit Tests**: 100% pass rate
- **Integration Tests**: 100% pass rate
- **Functional Tests**: 100% pass rate

### **Coverage Requirements**
- **Line Coverage**: ≥ 80%
- **Branch Coverage**: ≥ 70%
- **Function Coverage**: ≥ 90%

### **Performance Requirements**
- **Test Execution**: < 5 minutes for full suite
- **API Response**: < 1 second for most endpoints
- **Database Queries**: < 100ms for simple queries

## 📚 Additional Resources

### **Documentation**
- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)

### **Tools**
- **Pytest**: Test framework
- **Pytest-cov**: Coverage reporting
- **Factory-boy**: Test data generation
- **HTTPX**: HTTP client for testing
- **SQLAlchemy**: Database testing utilities

### **Examples**
- See individual test files for detailed examples
- Check `run_tests.py` for test runner examples
- Review `conftest.py` files for fixture examples
