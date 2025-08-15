import requests
import json
import time
import os
from dotenv import load_dotenv
import logging
from typing import Dict, Optional

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama API"""
    
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.model = "codellama"  # Default model
        
    def test_connection(self) -> bool:
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            logger.info(f"Ollama connection successful. Available models: {[m['name'] for m in models]}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama connection failed: {e}")
            return False
    
    def analyze_commit(self, commit_message: str, files_changed: list = None) -> Dict:
        """
        Analyze a commit using Ollama
        
        Args:
            commit_message: The commit message
            files_changed: List of files changed in the commit
            
        Returns:
            Analysis results dictionary
        """
        try:
            start_time = time.time()
            
            # Create prompt for analysis
            prompt = self._create_analysis_prompt(commit_message, files_changed)
            
            # Make request to Ollama
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for consistent results
                    "top_p": 0.9
                }
            }
            
            logger.info(f"Analyzing commit with Ollama: {commit_message[:50]}...")
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            response_text = result.get("response", "")
            
            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Parse the response
            analysis = self._parse_analysis_response(response_text)
            
            logger.info(f"Analysis completed in {processing_time_ms}ms")
            
            return {
                "analysis": analysis,
                "processing_time_ms": processing_time_ms,
                "model_used": self.model,
                "raw_response": response_text
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to analyze commit with Ollama: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}")
            raise
    
    def _create_analysis_prompt(self, commit_message: str, files_changed: list = None) -> str:
        """Create a prompt for commit analysis"""
        
        prompt = f"""
You are an expert code reviewer and commit analyst. Analyze the following commit and provide insights.

Commit Message: {commit_message}

"""
        
        if files_changed:
            prompt += "Files Changed:\n"
            for file_info in files_changed:
                prompt += f"- {file_info.get('filename', 'unknown')} ({file_info.get('status', 'unknown')})\n"
                if file_info.get('additions'):
                    prompt += f"  +{file_info.get('additions')} lines added\n"
                if file_info.get('deletions'):
                    prompt += f"  -{file_info.get('deletions')} lines deleted\n"
        
        prompt += """

Please provide analysis in the following JSON format:
{
    "commit_type": "feature|bugfix|refactor|docs|test|chore",
    "impact": "high|medium|low",
    "summary": "Brief summary of what this commit does",
    "key_changes": ["List of key changes made"],
    "potential_risks": ["Any potential risks or issues"],
    "recommendations": ["Any recommendations for review or follow-up"],
    "complexity": "simple|moderate|complex"
}

Focus on being concise and practical. If you cannot determine something, use "unknown".
"""
        
        return prompt
    
    def _parse_analysis_response(self, response_text: str) -> Dict:
        """Parse the analysis response from Ollama"""
        try:
            # Try to extract JSON from the response
            # Look for JSON-like content between curly braces
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != 0:
                json_str = response_text[start_idx:end_idx]
                analysis = json.loads(json_str)
            else:
                # If no JSON found, create a basic analysis
                analysis = {
                    "commit_type": "unknown",
                    "impact": "unknown",
                    "summary": response_text.strip(),
                    "key_changes": [],
                    "potential_risks": [],
                    "recommendations": [],
                    "complexity": "unknown"
                }
            
            return analysis
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON response: {e}")
            # Return basic analysis if JSON parsing fails
            return {
                "commit_type": "unknown",
                "impact": "unknown",
                "summary": response_text.strip(),
                "key_changes": [],
                "potential_risks": [],
                "recommendations": [],
                "complexity": "unknown",
                "parse_error": str(e)
            }
    
    def get_available_models(self) -> list:
        """Get list of available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            models = response.json().get("models", [])
            return [model["name"] for model in models]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get available models: {e}")
            return []
    
    def load_model(self, model_name: str) -> bool:
        """Load a specific model"""
        try:
            url = f"{self.base_url}/api/generate"
            payload = {
                "model": model_name,
                "prompt": "test",
                "stream": False
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Successfully loaded model: {model_name}")
            self.model = model_name
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            return False
