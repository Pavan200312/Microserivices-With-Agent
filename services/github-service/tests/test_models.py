import pytest
from datetime import datetime
from models.commit import Commit
from models.tracking_session import TrackingSession

class TestCommitModel:
    """Test cases for the Commit model."""
    
    def test_commit_creation(self, db_session):
        """Test creating a new commit."""
        commit = Commit(
            commit_hash="test1234567890abcdef1234567890abcdef12345678",
            author="Test User",
            author_email="test@example.com",
            message="Test commit message",
            timestamp=datetime.now(),
            repository="test/repo",
            branch="main",
            files_changed=[{"filename": "test.py", "status": "added"}]
        )
        
        db_session.add(commit)
        db_session.commit()
        db_session.refresh(commit)
        
        assert commit.id is not None
        assert commit.commit_hash == "test1234567890abcdef1234567890abcdef12345678"
        assert commit.author == "Test User"
        assert commit.message == "Test commit message"
        assert commit.repository == "test/repo"
        assert commit.branch == "main"
        assert commit.files_changed == [{"filename": "test.py", "status": "added"}]
    
    def test_commit_to_dict(self, db_session):
        """Test commit to_dict method."""
        timestamp = datetime.now()
        commit = Commit(
            commit_hash="test1234567890abcdef1234567890abcdef12345678",
            author="Test User",
            author_email="test@example.com",
            message="Test commit message",
            timestamp=timestamp,
            repository="test/repo",
            branch="main",
            files_changed=[{"filename": "test.py", "status": "added"}]
        )
        
        db_session.add(commit)
        db_session.commit()
        db_session.refresh(commit)
        
        commit_dict = commit.to_dict()
        
        assert commit_dict["commit_hash"] == "test1234567890abcdef1234567890abcdef12345678"
        assert commit_dict["author"] == "Test User"
        assert commit_dict["author_email"] == "test@example.com"
        assert commit_dict["message"] == "Test commit message"
        assert commit_dict["repository"] == "test/repo"
        assert commit_dict["branch"] == "main"
        assert commit_dict["files_changed"] == [{"filename": "test.py", "status": "added"}]
        assert "id" in commit_dict
        assert "created_at" in commit_dict
        assert "updated_at" in commit_dict
    
    def test_commit_unique_hash(self, db_session):
        """Test that commit hash must be unique."""
        timestamp = datetime.now()
        commit1 = Commit(
            commit_hash="test1234567890abcdef1234567890abcdef12345678",
            author="Test User",
            message="Test commit message",
            timestamp=timestamp,
            repository="test/repo"
        )
        
        commit2 = Commit(
            commit_hash="test1234567890abcdef1234567890abcdef12345678",  # Same hash
            author="Another User",
            message="Another commit message",
            timestamp=timestamp,
            repository="test/repo"
        )
        
        db_session.add(commit1)
        db_session.commit()
        
        # Adding commit with same hash should raise an error
        with pytest.raises(Exception):
            db_session.add(commit2)
            db_session.commit()

class TestTrackingSessionModel:
    """Test cases for the TrackingSession model."""
    
    def test_tracking_session_creation(self, db_session):
        """Test creating a new tracking session."""
        session = TrackingSession(
            repository="test/repo",
            branch="main",
            status="active"
        )
        
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        assert session.id is not None
        assert session.repository == "test/repo"
        assert session.branch == "main"
        assert session.status == "active"
        assert session.started_at is not None
        assert session.last_polled_at is not None
    
    def test_tracking_session_to_dict(self, db_session):
        """Test tracking session to_dict method."""
        session = TrackingSession(
            repository="test/repo",
            branch="main",
            status="active",
            last_commit_hash="test1234567890abcdef1234567890abcdef12345678"
        )
        
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        session_dict = session.to_dict()
        
        assert session_dict["repository"] == "test/repo"
        assert session_dict["branch"] == "main"
        assert session_dict["status"] == "active"
        assert session_dict["last_commit_hash"] == "test1234567890abcdef1234567890abcdef12345678"
        assert "id" in session_dict
        assert "started_at" in session_dict
        assert "last_polled_at" in session_dict
        assert "created_at" in session_dict
        assert "updated_at" in session_dict
    
    def test_tracking_session_default_values(self, db_session):
        """Test tracking session default values."""
        session = TrackingSession(
            repository="test/repo"
        )
        
        db_session.add(session)
        db_session.commit()
        db_session.refresh(session)
        
        assert session.branch == "main"  # Default value
        assert session.status == "active"  # Default value
        assert session.started_at is not None
        assert session.last_polled_at is not None
