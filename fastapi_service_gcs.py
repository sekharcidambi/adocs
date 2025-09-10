#!/usr/bin/env python3
"""
FastAPI Service for ADocS with GCS Integration - REST API endpoints for documentation services.
"""

import asyncio
import logging
import threading
import time
import os
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from functools import lru_cache
import json

from services.repository_service_gcs import RepositoryServiceGCS
from services.documentation_service_gcs import DocumentationServiceGCS
from services.analysis_service_gcs import AnalysisServiceGCS
from services.wiki_service import WikiService
from services.storage_service import CloudStorageService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ADocS API with GCS",
    description="Automated Documentation Service API with Google Cloud Storage",
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

# Configuration
GCS_BUCKET = os.getenv('GCS_BUCKET_NAME', 'adocs-backend-adocs-storage')
CACHE_TTL = 300  # 5 minutes
CACHE_DIR = "/tmp/adocs_cache"

# Ensure cache directory exists
os.makedirs(CACHE_DIR, exist_ok=True)

class CacheManager:
    """Simple file-based cache manager with TTL."""
    
    def __init__(self, cache_dir: str = CACHE_DIR, ttl: int = CACHE_TTL):
        self.cache_dir = cache_dir
        self.ttl = ttl
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path for a key."""
        return os.path.join(self.cache_dir, f"{key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value if not expired."""
        cache_path = self._get_cache_path(key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            # Check if cache is expired
            if time.time() - os.path.getmtime(cache_path) > self.ttl:
                os.remove(cache_path)
                return None
            
            # Load cached data
            with open(cache_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading cache for {key}: {e}")
            return None
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value."""
        cache_path = self._get_cache_path(key)
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(value, f)
        except Exception as e:
            logger.warning(f"Error writing cache for {key}: {e}")
    
    def invalidate(self, key: str) -> None:
        """Invalidate cache entry."""
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            os.remove(cache_path)
    
    def clear_all(self) -> None:
        """Clear all cache entries."""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, filename))

# Initialize services
cache = CacheManager()
repo_service = RepositoryServiceGCS(gcs_bucket=GCS_BUCKET)
doc_service = DocumentationServiceGCS(gcs_bucket=GCS_BUCKET)
analysis_service = AnalysisServiceGCS(
    github_token=os.getenv('GITHUB_TOKEN'),
    anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
    gcs_bucket=GCS_BUCKET
)
wiki_service = WikiService()
storage_service = CloudStorageService(bucket_name=GCS_BUCKET)

# Background task functions
async def analyze_repository_background(repo_url: str):
    """Background task to analyze repository."""
    try:
        logger.info(f"Starting background analysis for: {repo_url}")
        result = await analysis_service.analyze_repository(repo_url)
        
        # Invalidate repositories cache after analysis
        cache.invalidate("repositories_docs")
        cache.invalidate("repositories_wiki")
        
        logger.info(f"Completed background analysis for: {repo_url}")
        logger.info(f"Analysis result: {result.get('success', False)}")
    except Exception as e:
        logger.error(f"Background analysis failed for {repo_url}: {e}")

async def generate_wiki_background(repo_url: str):
    """Background task to generate wiki."""
    try:
        logger.info(f"Starting background wiki generation for: {repo_url}")
        await wiki_service.generate_wiki(repo_url)
        
        # Invalidate repositories cache after wiki generation
        cache.invalidate("repositories_wiki")
        
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
    try:
        # Test GCS connection
        stats = storage_service.get_storage_stats()
        gcs_status = "connected" if stats else "disconnected"
    except Exception as e:
        gcs_status = f"error: {str(e)}"
    
    return {
        "status": "healthy", 
        "service": "ADocS API with GCS",
        "cache_enabled": True,
        "gcs_bucket": GCS_BUCKET,
        "gcs_status": gcs_status
    }

# Get repositories endpoint with caching
@app.get("/api/repositories")
async def get_repositories(docs_type: str = Query("docs", description="Type of documentation")):
    """
    Get list of repositories with cached documentation from GCS.
    
    Args:
        docs_type: Type of documentation ('docs' or 'wiki')
        
    Returns:
        List of repositories with metadata
    """
    try:
        # Create cache key
        cache_key = f"repositories_{docs_type}"
        
        # Try to get from cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Returning cached repositories for docs_type: {docs_type}")
            return cached_result
        
        logger.info(f"Cache miss - fetching repositories from GCS for docs_type: {docs_type}")
        result = repo_service.get_repositories(docs_type)
        
        if not result.get('success', False):
            raise HTTPException(status_code=404, detail=result.get('error', 'No repositories found'))
        
        # Cache the result
        cache.set(cache_key, result)
        logger.info(f"Cached repositories for docs_type: {docs_type}")
        
        return result
    except Exception as e:
        logger.error(f"Error getting repositories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get documentation endpoint with caching
@app.get("/api/documentation")
async def get_documentation(
    repo: str = Query(..., description="GitHub repository URL"),
    section: Optional[str] = Query(None, description="Specific section to retrieve"),
    docs_type: str = Query("docs", description="Type of documentation")
):
    """
    Get documentation for a repository from GCS with caching.
    
    Args:
        repo: GitHub repository URL
        section: Optional specific section to retrieve
        docs_type: Type of documentation ('docs' or 'wiki')
        
    Returns:
        Documentation structure and content
    """
    try:
        # Create cache key
        cache_key = f"documentation_{docs_type}_{repo.replace('/', '_')}"
        if section:
            cache_key += f"_{section}"
        
        # Try to get from cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.info(f"Returning cached documentation for repo: {repo}, section: {section}")
            return cached_result
        
        logger.info(f"Cache miss - fetching documentation from GCS for repo: {repo}, section: {section}, type: {docs_type}")
        
        if section:
            result = doc_service.get_documentation_section(repo, section, docs_type)
        else:
            result = doc_service.get_documentation(repo, docs_type)
        
        if not result.get('success', False):
            raise HTTPException(status_code=404, detail=result.get('error', 'Documentation not found'))
        
        # Cache the result
        cache.set(cache_key, result)
        logger.info(f"Cached documentation for repo: {repo}, section: {section}")
        
        return result
    except Exception as e:
        logger.error(f"Error getting documentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Analyze repository endpoint
@app.post("/api/analyze")
async def analyze_repository(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Start analysis of a new repository in the background with GCS storage.
    
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
            "message": "Repository analysis started in the background. Documentation will be stored in Google Cloud Storage. Please refresh the page in a few minutes to see the results.",
            "repository": request.repo_url,
            "status": "processing",
            "storage": {
                "type": "gcs",
                "bucket": GCS_BUCKET
            }
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

# Storage management endpoints
@app.get("/api/storage/stats")
async def get_storage_stats():
    """Get GCS storage statistics."""
    try:
        stats = storage_service.get_storage_stats()
        return {
            "success": True,
            "storage_stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting storage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/repositories/{repo_path:path}")
async def delete_repository(repo_path: str, docs_type: str = Query("docs", description="Type of documentation")):
    """Delete repository documentation from GCS."""
    try:
        # Convert path back to GitHub URL
        repo_url = f"https://github.com/{repo_path.replace('_', '/')}"
        
        result = repo_service.delete_repository(repo_url, docs_type)
        
        if result.get('success', False):
            # Invalidate cache
            cache.invalidate(f"repositories_{docs_type}")
            cache.invalidate(f"documentation_{docs_type}_{repo_url.replace('/', '_')}")
        
        return result
    except Exception as e:
        logger.error(f"Error deleting repository: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cache management endpoints
@app.post("/api/cache/clear")
async def clear_cache():
    """Clear all cache entries."""
    try:
        cache.clear_all()
        return {"success": True, "message": "Cache cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cache/stats")
async def cache_stats():
    """Get cache statistics."""
    try:
        cache_files = [f for f in os.listdir(cache.cache_dir) if f.endswith('.json')]
        total_size = sum(os.path.getsize(os.path.join(cache.cache_dir, f)) for f in cache_files)
        
        return {
            "success": True,
            "cache_stats": {
                "total_entries": len(cache_files),
                "total_size_bytes": total_size,
                "cache_ttl_seconds": cache.ttl,
                "cache_dir": cache.cache_dir
            }
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "ADocS API with Google Cloud Storage",
        "version": "1.0.0",
        "cache_enabled": True,
        "storage": {
            "type": "gcs",
            "bucket": GCS_BUCKET
        },
        "endpoints": {
            "health": "/health",
            "repositories": "/api/repositories",
            "documentation": "/api/documentation",
            "analyze": "/api/analyze",
            "generate-wiki": "/api/generate-wiki",
            "storage_stats": "/api/storage/stats",
            "cache_clear": "/api/cache/clear",
            "cache_stats": "/api/cache/stats"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "fastapi_service_gcs:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
