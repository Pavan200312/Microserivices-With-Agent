from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class TrackingSession(Base):
    """Model for tracking sessions"""
    __tablename__ = "tracking_sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Repository information
    repository = Column(String(255), nullable=False, index=True)
    branch = Column(String(100), default='main')
    
    # Session status
    status = Column(String(50), default='active')  # active, paused, stopped
    
    # Tracking information
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    last_commit_hash = Column(String(40))  # Last commit hash seen
    last_polled_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<TrackingSession(repository={self.repository}, status={self.status})>"
    
    def to_dict(self):
        """Convert tracking session to dictionary"""
        return {
            "id": self.id,
            "repository": self.repository,
            "branch": self.branch,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "last_commit_hash": self.last_commit_hash,
            "last_polled_at": self.last_polled_at.isoformat() if self.last_polled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
