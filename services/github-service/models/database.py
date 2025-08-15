from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:191089193@localhost:5432/new%20DB")

# Handle database name with spaces properly
import urllib.parse
from urllib.parse import urlparse

def create_database_engine(database_url):
    """Create database engine with proper handling of database names with spaces"""
    try:
        # Parse the URL
        parsed = urlparse(database_url)
        
        # Extract and decode the database name
        database_name = urllib.parse.unquote(parsed.path.lstrip('/'))
        
        # Reconstruct the URL with proper encoding
        if ' ' in database_name:
            # Use connection parameters instead of URL for databases with spaces
            engine = create_engine(
                f"postgresql://{parsed.username}:{parsed.password}@{parsed.hostname}:{parsed.port}",
                connect_args={"database": database_name}
            )
        else:
            # Use URL directly for databases without spaces
            engine = create_engine(database_url)
        
        return engine
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        # Fallback to direct connection parameters
        return create_engine(
            "postgresql://postgres:191089193@localhost:5432",
            connect_args={"database": "new DB"}
        )

# Create database engine
engine = create_database_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
