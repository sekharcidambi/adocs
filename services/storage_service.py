#!/usr/bin/env python3
"""
Google Cloud Storage service for ADocS document storage.
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pathlib import Path
from google.cloud import storage
from google.cloud.exceptions import NotFound

logger = logging.getLogger(__name__)

class CloudStorageService:
    """Service for managing document storage in Google Cloud Storage."""
    
    def __init__(self, bucket_name: str = None, project_id: str = None):
        """
        Initialize the Cloud Storage service.
        
        Args:
            bucket_name: Name of the GCS bucket
            project_id: Google Cloud project ID
        """
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET_NAME', 'adocs-backend-adocs-storage')
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        
        # Initialize the storage client
        try:
            self.client = storage.Client(project=self.project_id)
            self.bucket = self.client.bucket(self.bucket_name)
            logger.info(f"Initialized Cloud Storage service with bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Cloud Storage service: {e}")
            raise
    
    def _sanitize_path(self, path: str) -> str:
        """Sanitize path for GCS object names."""
        # Replace invalid characters
        invalid_chars = ['<', '>', ':', '"', '|', '?', '*']
        for char in invalid_chars:
            path = path.replace(char, '_')
        
        # Remove leading/trailing slashes and normalize
        path = path.strip('/')
        path = '/'.join(filter(None, path.split('/')))
        
        return path
    
    def _get_repo_path(self, repo_url: str, doc_type: str = "docs") -> str:
        """Get the base path for a repository in GCS."""
        # Extract owner/repo from URL
        if 'github.com/' in repo_url:
            parts = repo_url.split('github.com/')[-1].rstrip('/')
            owner, repo = parts.split('/')[:2]
            repo_name = f"{owner}_{repo}"
        else:
            repo_name = "unknown_repo"
        
        # Sanitize and create path - always use generated_docs format
        safe_repo_name = self._sanitize_path(repo_name)
        return f"generated_docs/{safe_repo_name}"
    
    def save_documentation_structure(self, repo_url: str, doc_structure: Dict[str, Any], doc_type: str = "docs") -> str:
        """
        Save documentation structure to GCS.
        
        Args:
            repo_url: GitHub repository URL
            doc_structure: Documentation structure data
            doc_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            GCS object path
        """
        try:
            repo_path = self._get_repo_path(repo_url, doc_type)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_path = f"{repo_path}/{timestamp}/documentation_structure.json"
            
            # Upload to GCS
            blob = self.bucket.blob(object_path)
            blob.upload_from_string(
                json.dumps(doc_structure, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            
            logger.info(f"Saved documentation structure to GCS: {object_path}")
            return object_path
            
        except Exception as e:
            logger.error(f"Error saving documentation structure: {e}")
            raise
    
    def save_repository_metadata(self, repo_url: str, metadata: Dict[str, Any], doc_type: str = "docs") -> str:
        """
        Save repository metadata to GCS.
        
        Args:
            repo_url: GitHub repository URL
            metadata: Repository metadata
            doc_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            GCS object path
        """
        try:
            repo_path = self._get_repo_path(repo_url, doc_type)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_path = f"{repo_path}/{timestamp}/repository_metadata.json"
            
            # Upload to GCS
            blob = self.bucket.blob(object_path)
            blob.upload_from_string(
                json.dumps(metadata, indent=2, ensure_ascii=False),
                content_type='application/json'
            )
            
            logger.info(f"Saved repository metadata to GCS: {object_path}")
            return object_path
            
        except Exception as e:
            logger.error(f"Error saving repository metadata: {e}")
            raise
    
    def save_markdown_file(self, repo_url: str, filename: str, content: str, doc_type: str = "docs") -> str:
        """
        Save a markdown file to GCS.
        
        Args:
            repo_url: GitHub repository URL
            filename: Name of the markdown file
            content: Markdown content
            doc_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            GCS object path
        """
        try:
            repo_path = self._get_repo_path(repo_url, doc_type)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_path = f"{repo_path}/{timestamp}/{filename}"
            
            # Upload to GCS
            blob = self.bucket.blob(object_path)
            blob.upload_from_string(content, content_type='text/markdown')
            
            logger.info(f"Saved markdown file to GCS: {object_path}")
            return object_path
            
        except Exception as e:
            logger.error(f"Error saving markdown file: {e}")
            raise
    
    def save_index_file(self, repo_url: str, content: str, doc_type: str = "docs") -> str:
        """
        Save index file to GCS.
        
        Args:
            repo_url: GitHub repository URL
            content: Index content
            doc_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            GCS object path
        """
        try:
            repo_path = self._get_repo_path(repo_url, doc_type)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            object_path = f"{repo_path}/{timestamp}/README.md"
            
            # Upload to GCS
            blob = self.bucket.blob(object_path)
            blob.upload_from_string(content, content_type='text/markdown')
            
            logger.info(f"Saved index file to GCS: {object_path}")
            return object_path
            
        except Exception as e:
            logger.error(f"Error saving index file: {e}")
            raise
    
    def get_documentation_structure(self, repo_url: str, doc_type: str = "docs") -> Optional[Dict[str, Any]]:
        """
        Get the latest documentation structure from GCS.
        
        Args:
            repo_url: GitHub repository URL
            doc_type: Type of documentation ('docs' or 'wiki') - ignored, always uses generated_docs/
            
        Returns:
            Documentation structure or None if not found
        """
        try:
            repo_path = self._get_repo_path(repo_url, doc_type)
            
            # List all versions and get the latest
            blobs = list(self.bucket.list_blobs(prefix=f"{repo_path}/"))
            structure_blobs = [b for b in blobs if b.name.endswith('/documentation_structure.json')]
            
            if not structure_blobs:
                return None
            
            # Get the latest one (by name, which includes timestamp)
            latest_blob = max(structure_blobs, key=lambda x: x.name)
            
            # Download and parse
            content = latest_blob.download_as_text()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error getting documentation structure: {e}")
            return None
    
    def get_repository_metadata(self, repo_url: str, doc_type: str = "docs") -> Optional[Dict[str, Any]]:
        """
        Get the latest repository metadata from GCS.
        
        Args:
            repo_url: GitHub repository URL
            doc_type: Type of documentation ('docs' or 'wiki') - ignored, always uses generated_docs/
            
        Returns:
            Repository metadata or None if not found
        """
        try:
            repo_path = self._get_repo_path(repo_url, doc_type)
            
            # List all versions and get the latest
            blobs = list(self.bucket.list_blobs(prefix=f"{repo_path}/"))
            metadata_blobs = [b for b in blobs if b.name.endswith('/repository_metadata.json')]
            
            if not metadata_blobs:
                return None
            
            # Get the latest one (by name, which includes timestamp)
            latest_blob = max(metadata_blobs, key=lambda x: x.name)
            
            # Download and parse
            content = latest_blob.download_as_text()
            return json.loads(content)
            
        except Exception as e:
            logger.error(f"Error getting repository metadata: {e}")
            return None
    
    def get_markdown_file(self, repo_url: str, filename: str, doc_type: str = "docs") -> Optional[str]:
        """
        Get a markdown file from GCS.
        
        Args:
            repo_url: GitHub repository URL
            filename: Name of the markdown file
            doc_type: Type of documentation ('docs' or 'wiki') - ignored, always uses generated_docs/
            
        Returns:
            Markdown content or None if not found
        """
        try:
            repo_path = self._get_repo_path(repo_url, doc_type)
            
            # List all versions and get the latest
            blobs = list(self.bucket.list_blobs(prefix=f"{repo_path}/"))
            file_blobs = [b for b in blobs if b.name.endswith(f'/{filename}')]
            
            if not file_blobs:
                return None
            
            # Get the latest one (by name, which includes timestamp)
            latest_blob = max(file_blobs, key=lambda x: x.name)
            
            # Download content
            return latest_blob.download_as_text()
            
        except Exception as e:
            logger.error(f"Error getting markdown file: {e}")
            return None
    
    def list_repositories(self, doc_type: str = "docs") -> List[Dict[str, Any]]:
        """
        List all repositories with documentation in GCS.
        
        Args:
            doc_type: Type of documentation ('docs' or 'wiki') - ignored, always uses generated_docs/
            
        Returns:
            List of repository information
        """
        try:
            repositories = []
            prefix = "generated_docs/"
            
            logger.info(f"Searching for repositories with prefix: {prefix}")
            
            # List all blobs with the prefix (without delimiter to get all files)
            blobs = list(self.bucket.list_blobs(prefix=prefix))
            
            # Get unique repository paths with their blob names
            repo_info = {}
            for blob in blobs:
                if blob.name.endswith('/documentation_structure.json'):
                    # Extract repo path (remove timestamp and filename)                    # Structure: generated_docs/repo_name/timestamp/documentation_structure.json
                    parts = blob.name.split('/')
                    if len(parts) >= 4:  # Need at least 4 parts for the nested structure
                        repo_path = '/'.join(parts[:2])  # generated_docs/repo_name
                        repo_info[repo_path] = blob.name
            
            logger.info(f"Found {len(repo_info)} repository paths with prefix {prefix}")
            
            # Get metadata for each repository
            for repo_path, structure_blob_name in repo_info.items():
                repo_name = repo_path.split('/')[-1]
                github_url = f"https://github.com/{repo_name.replace('_', '/')}"
                
                # Try to get metadata
                metadata = self._get_repository_metadata_legacy(repo_path, structure_blob_name)
                if metadata:
                    repositories.append({
                        'name': repo_name,
                        'github_url': github_url,
                        'metadata': metadata,
                        'last_updated': metadata.get('timestamp', 'Unknown'),
                        'storage_path': repo_path
                    })
                    logger.info(f"Added repository: {repo_name}")
            
            logger.info(f"Returning {len(repositories)} repositories")
            return repositories
            
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return []
    
    def _get_repository_metadata_legacy(self, repo_path: str, structure_blob_name: str) -> Optional[Dict[str, Any]]:
        """Get repository metadata for legacy format."""
        try:
            # Try to find metadata file in the same directory as structure file
            parts = structure_blob_name.split('/')
            if len(parts) >= 3:
                # Replace documentation_structure.json with repository_metadata.json
                metadata_path = '/'.join(parts[:-1]) + '/repository_metadata.json'
                
                blob = self.bucket.blob(metadata_path)
                if blob.exists():
                    content = blob.download_as_text()
                    return json.loads(content)
                else:
                    # If no metadata file, create basic metadata from structure
                    structure_blob = self.bucket.blob(structure_blob_name)
                    if structure_blob.exists():
                        content = structure_blob.download_as_text()
                        structure = json.loads(content)
                        
                        # Create basic metadata
                        repo_name = repo_path.split('/')[-1]
                        github_url = f"https://github.com/{repo_name.replace('_', '/')}"
                        
                        return {
                            'github_url': github_url,
                            'overview': f"Documentation for {repo_name}",
                            'business_domain': 'Software Development',
                            'tech_stack': {'languages': [], 'topics': []},
                            'architecture': {'description': 'Repository documentation'},
                            'timestamp': structure_blob.time_created.isoformat() if structure_blob.time_created else 'Unknown'
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting legacy metadata: {e}")
            return None
    
    def delete_repository_docs(self, repo_url: str, doc_type: str = "docs") -> bool:
        """
        Delete all documentation for a repository.
        
        Args:
            repo_url: GitHub repository URL
            doc_type: Type of documentation ('docs' or 'wiki') - ignored, always uses generated_docs/
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo_path = self._get_repo_path(repo_url, doc_type)
            
            # List all blobs for this repository
            blobs = list(self.bucket.list_blobs(prefix=f"{repo_path}/"))
            
            # Delete all blobs
            for blob in blobs:
                blob.delete()
            
            logger.info(f"Deleted all documentation for repository: {repo_url}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting repository documentation: {e}")
            return False
    
    def get_raw_file_content(self, gcs_path: str) -> Optional[str]:
        """
        Get raw file content from GCS by path.
        
        Args:
            gcs_path: Full GCS path to the file (e.g., 'custom_docs/repo/file.md')
            
        Returns:
            File content or None if not found
        """
        try:
            blob = self.bucket.blob(gcs_path)
            if blob.exists():
                content = blob.download_as_text()
                logger.info(f"Successfully retrieved file content from: {gcs_path}")
                return content
            else:
                logger.warning(f"File not found in GCS: {gcs_path}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving file content from {gcs_path}: {e}")
            return None

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Storage statistics
        """
        try:
            total_size = 0
            total_files = 0
            repo_count = set()
            
            # List all blobs
            blobs = list(self.bucket.list_blobs())
            
            for blob in blobs:
                total_size += blob.size or 0
                total_files += 1
                
                # Extract repo name for counting
                parts = blob.name.split('/')
                if len(parts) >= 2:
                    repo_count.add('/'.join(parts[:2]))
            
            return {
                'total_size_bytes': total_size,
                'total_files': total_files,
                'unique_repositories': len(repo_count),
                'bucket_name': self.bucket_name
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}
