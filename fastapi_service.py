#!/usr/bin/env python3
"""
FastAPI Service for ADocS - REST API endpoints for documentation services.
"""

import asyncio
import logging
import threading
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from services.repository_service import RepositoryService
from services.documentation_service import DocumentationService
from services.analysis_service import AnalysisService
from services.wiki_service import WikiService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ADocS API",
    description="Automated Documentation Service API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
repo_service = RepositoryService()
doc_service = DocumentationService()
analysis_service = AnalysisService()
wiki_service = WikiService()

# Background task functions
async def analyze_repository_background(repo_url: str):
    """Background task to analyze repository."""
    try:
        logger.info(f"Starting background analysis for: {repo_url}")
        await analysis_service.analyze_repository(repo_url)
        logger.info(f"Completed background analysis for: {repo_url}")
    except Exception as e:
        logger.error(f"Background analysis failed for {repo_url}: {e}")

async def generate_wiki_background(repo_url: str):
    """Background task to generate wiki."""
    try:
        logger.info(f"Starting background wiki generation for: {repo_url}")
        await wiki_service.generate_wiki(repo_url)
        logger.info(f"Completed background wiki generation for: {repo_url}")
    except Exception as e:
        logger.error(f"Background wiki generation failed for {repo_url}: {e}")

# Pydantic models for request/response
class AnalyzeRequest(BaseModel):
    repo_url: str

class GenerateWikiRequest(BaseModel):
    repo_url: str

class GetDocumentationRequest(BaseModel):
    repo_url: str
    section: Optional[str] = None
    docs_type: str = "docs"

class GetRepositoriesRequest(BaseModel):
    docs_type: str = "docs"

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ADocS API"}

# Get repositories endpoint
@app.get("/api/repositories")
async def get_repositories(docs_type: str = Query("docs", description="Type of documentation")):
    """
    Get list of repositories with cached documentation.
    
    Args:
        docs_type: Type of documentation ('docs' or 'wiki')
        
    Returns:
        List of repositories with metadata
    """
    try:
        logger.info(f"Getting repositories for docs_type: {docs_type}")
        result = repo_service.get_repositories(docs_type)
        
        if not result.get('success', False):
            raise HTTPException(status_code=404, detail=result.get('error', 'No repositories found'))
        
        return result
    except Exception as e:
        logger.error(f"Error getting repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get documentation endpoint
@app.get("/api/documentation")
async def get_documentation(
    repo: str = Query(..., description="GitHub repository URL"),
    section: Optional[str] = Query(None, description="Specific section to retrieve"),
    docs_type: str = Query("docs", description="Type of documentation")
):
    """
    Get documentation for a repository.
    
    Args:
        repo: GitHub repository URL
        section: Optional specific section to retrieve
        docs_type: Type of documentation ('docs' or 'wiki')
        
    Returns:
        Documentation structure and content
    """
    try:
        logger.info(f"Getting documentation for repo: {repo}, section: {section}, type: {docs_type}")
        
        if section:
            result = doc_service.get_documentation_section(repo, section, docs_type)
        else:
            result = doc_service.get_documentation(repo, docs_type)
        
        if not result.get('success', False):
            raise HTTPException(status_code=404, detail=result.get('error', 'Documentation not found'))
        
        return result
    except Exception as e:
        logger.error(f"Error getting documentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analyze repository endpoint
@app.post("/api/analyze")
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Start analysis of a new repository in the background.
    
    Args:
        request: Contains repo_url
        background_tasks: FastAPI background tasks
        
    Returns:
        Immediate response indicating analysis has started
    """
    try:
        logger.info(f"Starting background analysis for repository: {request.repo_url}")
        
        # Add the analysis task to background tasks
        background_tasks.add_task(analyze_repository_background, request.repo_url)
        
        return {
            "success": True,
            "message": "Repository analysis started in the background. Please refresh the page in a few minutes to see the results.",
            "repository": request.repo_url,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error starting repository analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Generate wiki endpoint
@app.post("/api/generate-wiki")
async def generate_wiki(request: GenerateWikiRequest, background_tasks: BackgroundTasks):
    """
    Start wiki generation for a repository in the background.
    
    Args:
        request: Contains repo_url
        background_tasks: FastAPI background tasks
        
    Returns:
        Immediate response indicating wiki generation has started
    """
    try:
        logger.info(f"Starting background wiki generation for repository: {request.repo_url}")
        
        # Add the wiki generation task to background tasks
        background_tasks.add_task(generate_wiki_background, request.repo_url)
        
        return {
            "success": True,
            "message": "Wiki generation started in the background. Please refresh the page in a few minutes to see the results.",
            "repository": request.repo_url,
            "status": "processing"
        }
    except Exception as e:
        logger.error(f"Error starting wiki generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "ADocS API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "repositories": "/api/repositories",
            "documentation": "/api/documentation",
            "analyze": "/api/analyze",
            "generate-wiki": "/api/generate-wiki"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_service:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
