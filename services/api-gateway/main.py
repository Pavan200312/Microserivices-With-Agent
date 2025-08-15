from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="GitHub Commit Tracker API Gateway",
    description="Main entry point for GitHub commit tracking microservices",
    version="1.0.0"
)

# Add CORS middleware (allows frontend to communicate with backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Get service URLs from environment variables
GITHUB_SERVICE_URL = os.getenv("GITHUB_SERVICE_URL", "http://github-service:8001")
AI_SERVICE_URL = os.getenv("AI_SERVICE_URL", "http://ai-service:8002")

@app.get("/")
async def root():
    """Root endpoint - welcome message"""
    return {
        "message": "GitHub Commit Tracker API Gateway",
        "status": "running",
        "services": {
            "github_service": GITHUB_SERVICE_URL,
            "ai_service": AI_SERVICE_URL
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint - tells if the service is running"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "timestamp": "2024-01-01T00:00:00Z"
    }

@app.get("/api/commits")
async def get_commits():
    """Get all commits from GitHub service"""
    try:
        logger.info("Fetching commits from GitHub service")
        
        # Make HTTP request to GitHub service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{GITHUB_SERVICE_URL}/commits")
            
            if response.status_code == 200:
                commits = response.json()
                logger.info(f"Successfully fetched {len(commits)} commits")
                return commits
            else:
                logger.error(f"GitHub service returned error: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch commits from GitHub service"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(
            status_code=503,
            detail="GitHub service is not available"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/tracking/start")
async def start_tracking():
    """Start commit tracking process"""
    try:
        logger.info("Starting commit tracking")
        
        # Make HTTP request to GitHub service to start tracking
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{GITHUB_SERVICE_URL}/start-tracking")
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully started commit tracking")
                return result
            else:
                logger.error(f"Failed to start tracking: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to start commit tracking"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(
            status_code=503,
            detail="GitHub service is not available"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/api/fetch-commits")
async def fetch_commits():
    """Fetch new commits from GitHub and store in database"""
    try:
        logger.info("Fetching new commits from GitHub")
        
        # Make HTTP request to GitHub service to fetch commits
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(f"{GITHUB_SERVICE_URL}/fetch-commits")
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully fetched commits from GitHub")
                return result
            else:
                logger.error(f"Failed to fetch commits: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch commits from GitHub"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(
            status_code=503,
            detail="GitHub service is not available"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/api/analysis/{commit_hash}")
async def get_commit_analysis(commit_hash: str):
    """Get AI analysis for a specific commit"""
    try:
        logger.info(f"Fetching analysis for commit: {commit_hash}")
        
        # Make HTTP request to AI service
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{AI_SERVICE_URL}/analysis/{commit_hash}")
            
            if response.status_code == 200:
                analysis = response.json()
                logger.info(f"Successfully fetched analysis for commit {commit_hash}")
                return analysis
            else:
                logger.error(f"AI service returned error: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to fetch commit analysis"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(
            status_code=503,
            detail="AI service is not available"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.delete("/api/clear-commits")
async def clear_commits():
    """Clear all commits from database (for testing purposes)"""
    try:
        logger.info("Clearing all commits from database")
        
        # Make HTTP request to GitHub service to clear commits
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(f"{GITHUB_SERVICE_URL}/clear-commits")
            
            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully cleared commits from database")
                return result
            else:
                logger.error(f"Failed to clear commits: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail="Failed to clear commits from database"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Request error: {e}")
        raise HTTPException(
            status_code=503,
            detail="GitHub service is not available"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    # Run the server
    uvicorn.run(
        app, 
        host="0.0.0.0",  # Listen on all network interfaces
        port=8000,       # Port number
        reload=True      # Auto-reload on code changes (development)
    )
