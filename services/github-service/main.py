from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

# Import our modules
from models.database import get_db, init_db
from models.commit import Commit
from models.tracking_session import TrackingSession
from services.github_client import GitHubClient

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GitHub Service",
    description="Service for tracking GitHub commits",
    version="1.0.0"
)

# Initialize GitHub client
github_client = GitHubClient()

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
        
        # Test GitHub connection
        if github_client.test_connection():
            logger.info("GitHub API connection successful")
        else:
            logger.warning("GitHub API connection failed")
            
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "GitHub Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "github-service",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/commits")
async def get_commits(db: Session = Depends(get_db)):
    """Get all commits from database"""
    try:
        # Query all commits from database
        commits = db.query(Commit).order_by(Commit.commit_timestamp_utc.desc()).all()
        
        # Convert to list of dictionaries
        commit_list = [commit.to_dict() for commit in commits]
        
        logger.info(f"Retrieved {len(commit_list)} commits from database")
        return commit_list
        
    except Exception as e:
        logger.error(f"Failed to get commits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/commits/{commit_hash}")
async def get_commit(commit_hash: str, db: Session = Depends(get_db)):
    """Get a specific commit by hash"""
    try:
        commit = db.query(Commit).filter(Commit.hash == commit_hash).first()
        
        if not commit:
            raise HTTPException(status_code=404, detail="Commit not found")
        
        return commit.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get commit {commit_hash}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start-tracking")
async def start_tracking(db: Session = Depends(get_db)):
    """Start tracking commits for a repository and fetch initial commits"""
    try:
        # For now, we'll use a default repository
        # In a real application, this would come from the request body
        repository = "Pavan200312/Microserivices-With-Agent"  # Your actual repository
        branch = "main"
        
        # Check if tracking session already exists
        existing_session = db.query(TrackingSession).filter(
            TrackingSession.repository == repository,
            TrackingSession.status == "active"
        ).first()
        
        if existing_session:
            # If session exists, fetch new commits anyway
            logger.info(f"Tracking session already exists for {repository}, fetching commits...")
        else:
            # Create new tracking session
            new_session = TrackingSession(
                repository=repository,
                branch=branch,
                status="active"
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            logger.info(f"Started tracking for repository: {repository}")
        
        # Fetch commits from GitHub and store in database
        try:
            commits = github_client.get_commits(repository=repository, branch=branch)
            new_commits_count = 0
            
            for commit_data in commits:
                # Check if commit already exists using hash as unique identifier
                existing_commit = db.query(Commit).filter(
                    Commit.hash == commit_data["commit_hash"]
                ).first()
                
                if not existing_commit:
                    # Create new commit record matching your schema
                    new_commit = Commit(
                        hash=commit_data["commit_hash"],  # Store in hash column
                        author=commit_data["author"],
                        message=commit_data["message"],
                        commit_timestamp_utc=datetime.fromisoformat(commit_data["timestamp"].replace('Z', '+00:00'))
                    )
                    
                    db.add(new_commit)
                    new_commits_count += 1
                    logger.info(f"Added new commit: {commit_data['commit_hash'][:8]} - {commit_data['message'][:50]}")
            
            # Update session with latest commit hash
            if commits:
                session_to_update = existing_session if existing_session else new_session
                session_to_update.last_commit_hash = commits[0]["commit_hash"]
                session_to_update.last_polled_at = datetime.now()
            
            db.commit()
            logger.info(f"Successfully stored {new_commits_count} new commits for {repository}")
            
            return {
                "message": f"Tracking started successfully. Fetched {new_commits_count} new commits.",
                "session": (existing_session or new_session).to_dict(),
                "commits_fetched": new_commits_count
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch commits for {repository}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to fetch commits: {str(e)}")
        
    except Exception as e:
        logger.error(f"Failed to start tracking: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fetch-commits")
async def fetch_commits(db: Session = Depends(get_db)):
    """Fetch new commits from GitHub and store in database"""
    try:
        # Get active tracking sessions
        active_sessions = db.query(TrackingSession).filter(
            TrackingSession.status == "active"
        ).all()
        
        if not active_sessions:
            return {"message": "No active tracking sessions"}
        
        total_new_commits = 0
        
        for session in active_sessions:
            try:
                # Get commits from GitHub
                commits = github_client.get_commits(
                    repository=session.repository,
                    branch=session.branch
                )
                
                new_commits_count = 0
                
                for commit_data in commits:
                    # Check if commit already exists using hash as unique identifier
                    existing_commit = db.query(Commit).filter(
                        Commit.hash == commit_data["commit_hash"]
                    ).first()
                    
                    if not existing_commit:
                        # Create new commit record matching your schema
                        new_commit = Commit(
                            hash=commit_data["commit_hash"],  # Store in hash column
                            author=commit_data["author"],
                            message=commit_data["message"],
                            commit_timestamp_utc=datetime.fromisoformat(commit_data["timestamp"].replace('Z', '+00:00'))
                        )
                        
                        db.add(new_commit)
                        new_commits_count += 1
                        logger.info(f"Added new commit: {commit_data['commit_hash'][:8]} - {commit_data['message'][:50]}")
                
                # Update session with latest commit hash
                if commits:
                    session.last_commit_hash = commits[0]["commit_hash"]
                    session.last_polled_at = datetime.now()
                
                db.commit()
                total_new_commits += new_commits_count
                
                logger.info(f"Fetched {new_commits_count} new commits for {session.repository}")
                
            except Exception as e:
                logger.error(f"Failed to fetch commits for {session.repository}: {e}")
                continue
        
        return {
            "message": f"Fetched {total_new_commits} new commits",
            "total_new_commits": total_new_commits
        }
        
    except Exception as e:
        logger.error(f"Failed to fetch commits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tracking-sessions")
async def get_tracking_sessions(db: Session = Depends(get_db)):
    """Get all tracking sessions"""
    try:
        sessions = db.query(TrackingSession).all()
        return [session.to_dict() for session in sessions]
        
    except Exception as e:
        logger.error(f"Failed to get tracking sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear-commits")
async def clear_commits(db: Session = Depends(get_db)):
    """Clear all commits from database (for testing purposes)"""
    try:
        # Delete all commits
        deleted_count = db.query(Commit).delete()
        db.commit()
        
        logger.info(f"Cleared {deleted_count} commits from database")
        
        return {
            "message": f"Cleared {deleted_count} commits from database",
            "deleted_count": deleted_count
        }
        
    except Exception as e:
        logger.error(f"Failed to clear commits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )
