from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class AIAnalysis(Base):
    """Model for storing AI analysis results"""
    __tablename__ = "ai_analysis"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Commit information
    commit_hash = Column(String(40), nullable=False, index=True)
    
    # Analysis information
    analysis_type = Column(String(50), default='commit_analysis')
    analysis_data = Column(JSON, nullable=False)  # Store analysis results as JSON
    model_used = Column(String(100), default='codellama')
    
    # Performance metrics
    processing_time_ms = Column(Integer)  # Time taken to process in milliseconds
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AIAnalysis(commit_hash={self.commit_hash}, type={self.analysis_type})>"
    
    def to_dict(self):
        """Convert analysis to dictionary"""
        return {
            "id": self.id,
            "commit_hash": self.commit_hash,
            "analysis_type": self.analysis_type,
            "analysis_data": self.analysis_data,
            "model_used": self.model_used,
            "processing_time_ms": self.processing_time_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
