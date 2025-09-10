#!/usr/bin/env python3
"""
Repository Service with GCS Integration - Handles repository listing from Google Cloud Storage.
"""

import logging
from typing import Dict, Any, Optional, List

from .base_service import BaseService
from .storage_service import CloudStorageService

logger = logging.getLogger(__name__)

class RepositoryServiceGCS(BaseService):
    """Service for managing repositories with GCS storage."""
    
    def __init__(self, gcs_bucket: str = None):
        """Initialize the Repository Service with GCS."""
        super().__init__()
        
        # Initialize GCS service
        self.storage_service = CloudStorageService(bucket_name=gcs_bucket)
    
    def get_repositories(self, docs_type: str = "docs") -> Dict[str, Any]:
        """
        Get list of repositories with documentation from GCS.
        
        Args:
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            List of repositories with metadata
        """
        try:
            logger.info(f"Getting repositories from GCS for docs_type: {docs_type}")
            
            # Get repositories from GCS
            repositories = self.storage_service.list_repositories(docs_type)
            
            if not repositories:
                return {
                    "success": True,
                    "repositories": [],
                    "count": 0,
                    "storage": {
                        "type": "gcs",
                        "bucket": self.storage_service.bucket_name
                    }
                }
            
            # Format repositories for API response
            formatted_repos = []
            for repo in repositories:
                formatted_repo = {
                    "name": repo['name'],
                    "github_url": repo['github_url'],
                    "description": repo['metadata'].get('overview', ''),
                    "language": repo['metadata'].get('tech_stack', {}).get('languages', [''])[0] if repo['metadata'].get('tech_stack', {}).get('languages') else '',
                    "stars": 0,  # Not available in metadata
                    "topics": repo['metadata'].get('tech_stack', {}).get('topics', []),
                    "business_domain": repo['metadata'].get('business_domain', ''),
                    "last_updated": repo['last_updated'],
                    "has_documentation": True,
                    "has_wiki": False,  # Could be enhanced to check for wiki docs
                    "storage": {
                        "type": "gcs",
                        "bucket": self.storage_service.bucket_name
                    }
                }
                formatted_repos.append(formatted_repo)
            
            result = {
                "success": True,
                "repositories": formatted_repos,
                "count": len(formatted_repos),
                "storage": {
                    "type": "gcs",
                    "bucket": self.storage_service.bucket_name
                }
            }
            
            logger.info(f"Successfully retrieved {len(formatted_repos)} repositories from GCS")
            return result
            
        except Exception as e:
            logger.error(f"Error getting repositories from GCS: {e}")
            return {
                "success": False,
                "error": str(e),
                "repositories": [],
                "count": 0
            }
    
    def get_repository_info(self, repo_url: str, docs_type: str = "docs") -> Dict[str, Any]:
        """
        Get detailed information about a specific repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Repository information
        """
        try:
            logger.info(f"Getting repository info from GCS: {repo_url}")
            
            # Get repository metadata
            metadata = self.storage_service.get_repository_metadata(repo_url, docs_type)
            if not metadata:
                return {
                    "success": False,
                    "error": "Repository not found in GCS",
                    "repository": repo_url
                }
            
            # Get documentation structure
            doc_structure = self.storage_service.get_documentation_structure(repo_url, docs_type)
            
            result = {
                "success": True,
                "repository": repo_url,
                "metadata": metadata,
                "has_documentation": bool(doc_structure),
                "documentation_structure": doc_structure,
                "storage": {
                    "type": "gcs",
                    "bucket": self.storage_service.bucket_name
                }
            }
            
            logger.info(f"Successfully retrieved repository info from GCS: {repo_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting repository info from GCS: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url
            }
    
    def delete_repository(self, repo_url: str, docs_type: str = "docs") -> Dict[str, Any]:
        """
        Delete all documentation for a repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Deletion result
        """
        try:
            logger.info(f"Deleting repository documentation from GCS: {repo_url}")
            
            success = self.storage_service.delete_repository_docs(repo_url, docs_type)
            
            if success:
                result = {
                    "success": True,
                    "message": f"Repository documentation deleted successfully",
                    "repository": repo_url,
                    "storage": {
                        "type": "gcs",
                        "bucket": self.storage_service.bucket_name
                    }
                }
            else:
                result = {
                    "success": False,
                    "error": "Failed to delete repository documentation",
                    "repository": repo_url
                }
            
            logger.info(f"Repository deletion result: {success}")
            return result
            
        except Exception as e:
            logger.error(f"Error deleting repository from GCS: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url
            }
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Storage statistics
        """
        try:
            stats = self.storage_service.get_storage_stats()
            
            return {
                "success": True,
                "storage_stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
