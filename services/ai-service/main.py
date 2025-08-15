from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
import logging
import os
from dotenv import load_dotenv
from datetime import datetime

# Import our modules
from models.database import get_db, init_db
from models.analysis import AIAnalysis
from services.ollama_client import OllamaClient

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Service",
    description="Service for AI analysis of GitHub commits",
    version="1.0.0"
)

# Initialize Ollama client
ollama_client = OllamaClient()

@app.on_event("startup")
async def startup_event():
    """Initialize database and test connections on startup"""
    try:
        init_db()
        logger.info("AI Service database initialized successfully")
        
        # Test Ollama connection
        if ollama_client.test_connection():
            logger.info("Ollama connection successful")
        else:
            logger.warning("Ollama connection failed")
            
    except Exception as e:
        logger.error(f"AI Service startup failed: {e}")
        raise

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AI Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ai-service",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/analyze")
async def analyze_commit(commit_data: Dict):
    """Analyze a commit using AI"""
    try:
        commit_message = commit_data.get("message", "")
        files_changed = commit_data.get("files_changed", [])
        commit_hash = commit_data.get("commit_hash", "")
        
        if not commit_message:
            raise HTTPException(status_code=400, detail="Commit message is required")
        
        logger.info(f"Analyzing commit: {commit_hash}")
        
        # Analyze commit using Ollama
        analysis_result = ollama_client.analyze_commit(commit_message, files_changed)
        
        return {
            "commit_hash": commit_hash,
            "analysis": analysis_result["analysis"],
            "processing_time_ms": analysis_result["processing_time_ms"],
            "model_used": analysis_result["model_used"]
        }
        
    except Exception as e:
        logger.error(f"Failed to analyze commit: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/analysis/{commit_hash}")
async def get_analysis(commit_hash: str, db: Session = Depends(get_db)):
    """Get AI analysis for a specific commit"""
    try:
        # Check if analysis exists in database
        analysis = db.query(AIAnalysis).filter(
            AIAnalysis.commit_hash == commit_hash
        ).first()
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return analysis.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis for {commit_hash}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/{commit_hash}")
async def create_analysis(commit_hash: str, commit_data: Dict, db: Session = Depends(get_db)):
    """Create AI analysis for a commit and store in database"""
    try:
        # Check if analysis already exists
        existing_analysis = db.query(AIAnalysis).filter(
            AIAnalysis.commit_hash == commit_hash
        ).first()
        
        if existing_analysis:
            return {
                "message": "Analysis already exists",
                "analysis": existing_analysis.to_dict()
            }
        
        commit_message = commit_data.get("message", "")
        files_changed = commit_data.get("files_changed", [])
        
        if not commit_message:
            raise HTTPException(status_code=400, detail="Commit message is required")
        
        logger.info(f"Creating analysis for commit: {commit_hash}")
        
        # Analyze commit using Ollama
        analysis_result = ollama_client.analyze_commit(commit_message, files_changed)
        
        # Store analysis in database
        new_analysis = AIAnalysis(
            commit_hash=commit_hash,
            analysis_type="commit_analysis",
            analysis_data=analysis_result["analysis"],
            model_used=analysis_result["model_used"],
            processing_time_ms=analysis_result["processing_time_ms"]
        )
        
        db.add(new_analysis)
        db.commit()
        db.refresh(new_analysis)
        
        logger.info(f"Analysis created and stored for commit: {commit_hash}")
        
        return {
            "message": "Analysis created successfully",
            "analysis": new_analysis.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create analysis for {commit_hash}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/insights")
async def get_insights(db: Session = Depends(get_db)):
    """Get insights from all analyses"""
    try:
        # Get all analyses
        analyses = db.query(AIAnalysis).order_by(AIAnalysis.created_at.desc()).all()
        
        if not analyses:
            return {"message": "No analyses found"}
        
        # Calculate insights
        total_analyses = len(analyses)
        commit_types = {}
        impact_levels = {}
        complexity_levels = {}
        
        for analysis in analyses:
            analysis_data = analysis.analysis_data
            
            # Count commit types
            commit_type = analysis_data.get("commit_type", "unknown")
            commit_types[commit_type] = commit_types.get(commit_type, 0) + 1
            
            # Count impact levels
            impact = analysis_data.get("impact", "unknown")
            impact_levels[impact] = impact_levels.get(impact, 0) + 1
            
            # Count complexity levels
            complexity = analysis_data.get("complexity", "unknown")
            complexity_levels[complexity] = complexity_levels.get(complexity, 0) + 1
        
        return {
            "total_analyses": total_analyses,
            "commit_types": commit_types,
            "impact_levels": impact_levels,
            "complexity_levels": complexity_levels,
            "recent_analyses": [analysis.to_dict() for analysis in analyses[:5]]
        }
        
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_available_models():
    """Get available Ollama models"""
    try:
        models = ollama_client.get_available_models()
        return {
            "available_models": models,
            "current_model": ollama_client.model
        }
        
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/{model_name}/load")
async def load_model(model_name: str):
    """Load a specific Ollama model"""
    try:
        success = ollama_client.load_model(model_name)
        
        if success:
            return {
                "message": f"Model {model_name} loaded successfully",
                "current_model": ollama_client.model
            }
        else:
            raise HTTPException(status_code=400, detail=f"Failed to load model {model_name}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to load model {model_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        reload=True
    )
