from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .database import Base
import uuid

class Commit(Base):
    """Model for storing GitHub commits"""
    __tablename__ = "commits"
    
    # Primary key - using UUID as per existing schema
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    
    # Commit information - using hash instead of commit_hash
    hash = Column(String(40), unique=True, index=True, nullable=False)
    author = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    commit_timestamp_utc = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Commit(hash={self.hash}, author={self.author}, message={self.message[:50]}...)>"
    
    def to_dict(self):
        """Convert commit to dictionary"""
        return {
            "id": self.id,
            "commit_hash": self.hash,  # Map hash to commit_hash for frontend
            "author": self.author,
            "message": self.message,
            "timestamp": self.commit_timestamp_utc.isoformat() if self.commit_timestamp_utc else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
