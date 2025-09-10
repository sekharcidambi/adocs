#!/usr/bin/env python3
"""
Documentation Service with GCS Integration - Handles documentation retrieval from Google Cloud Storage.
"""

import logging
from typing import Dict, Any, Optional, List

from .base_service import BaseService
from .storage_service import CloudStorageService

logger = logging.getLogger(__name__)

class DocumentationServiceGCS(BaseService):
    """Service for retrieving documentation from Google Cloud Storage."""
    
    def __init__(self, gcs_bucket: str = None):
        """Initialize the Documentation Service with GCS."""
        super().__init__()
        
        # Initialize GCS service
        self.storage_service = CloudStorageService(bucket_name=gcs_bucket)
    
    def get_documentation(self, repo_url: str, docs_type: str = "docs") -> Dict[str, Any]:
        """
        Get complete documentation for a repository from GCS.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Documentation data
        """
        try:
            logger.info(f"Getting documentation from GCS for repo: {repo_url}, type: {docs_type}")
            
            # Get documentation structure
            doc_structure = self.storage_service.get_documentation_structure(repo_url, docs_type)
            if not doc_structure:
                return {
                    "success": False,
                    "error": "Documentation not found in GCS",
                    "repository": repo_url
                }
            
            # Get repository metadata
            metadata = self.storage_service.get_repository_metadata(repo_url, docs_type)
            
            # Build navigation structure
            navigation = self._build_navigation_structure(doc_structure)
            
            result = {
                "success": True,
                "repository": repo_url,
                "documentationStructure": doc_structure,
                "metadata": metadata,
                "navigation": navigation,
                "storage": {
                    "type": "gcs",
                    "bucket": self.storage_service.bucket_name
                }
            }
            
            logger.info(f"Successfully retrieved documentation from GCS for: {repo_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting documentation from GCS: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url
            }
    
    def get_documentation_section(self, repo_url: str, section: str, docs_type: str = "docs") -> Dict[str, Any]:
        """
        Get a specific documentation section from GCS.
        
        Args:
            repo_url: GitHub repository URL
            section: Section name
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Section documentation data
        """
        try:
            logger.info(f"Getting documentation section from GCS: {repo_url}/{section}")
            
            # Try to get the markdown file for this section
            filename = f"{self._sanitize_filename(section)}.md"
            content = self.storage_service.get_markdown_file(repo_url, filename, docs_type)
            
            if not content:
                return {
                    "success": False,
                    "error": f"Section '{section}' not found in GCS",
                    "repository": repo_url,
                    "section": section
                }
            
            result = {
                "success": True,
                "repository": repo_url,
                "section": section,
                "content": content,
                "format": "markdown",
                "storage": {
                    "type": "gcs",
                    "bucket": self.storage_service.bucket_name
                }
            }
            
            logger.info(f"Successfully retrieved section from GCS: {repo_url}/{section}")
            return result
            
        except Exception as e:
            logger.error(f"Error getting documentation section from GCS: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url,
                "section": section
            }
    
    def _build_navigation_structure(self, doc_structure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build navigation structure from documentation structure."""
        navigation = []
        
        if isinstance(doc_structure, list) and len(doc_structure) > 0:
            root_item = doc_structure[0]
            
            def build_hierarchy(items: List[Dict[str, Any]], parent_title: str = '') -> List[Dict[str, Any]]:
                result = []
                for item in items:
                    section_title = f"{parent_title} > {item['title']}" if parent_title else item['title']
                    
                    child_item = {
                        'title': item['title'],
                        'path': self._sanitize_filename(item['title']),
                        'type': 'docs',
                        'hasContent': True,  # Assume content exists in GCS
                        'content': None  # Content will be loaded on demand
                    }
                    
                    # Add children if they exist
                    if 'children' in item and isinstance(item['children'], list):
                        child_item['children'] = build_hierarchy(item['children'], section_title)
                    
                    result.append(child_item)
                return result
            
            if 'children' in root_item and isinstance(root_item['children'], list):
                navigation = build_hierarchy(root_item['children'])
        
        return navigation
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = '_'.join(filter(None, filename.split('_')))
        return filename.strip()
    
    def list_available_sections(self, repo_url: str, docs_type: str = "docs") -> List[str]:
        """
        List all available documentation sections for a repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            List of section names
        """
        try:
            # Get documentation structure
            doc_structure = self.storage_service.get_documentation_structure(repo_url, docs_type)
            if not doc_structure:
                return []
            
            sections = []
            
            if isinstance(doc_structure, list) and len(doc_structure) > 0:
                root_item = doc_structure[0]
                
                def extract_sections(items: List[Dict[str, Any]]):
                    for item in items:
                        sections.append(item['title'])
                        if 'children' in item and isinstance(item['children'], list):
                            extract_sections(item['children'])
                
                if 'children' in root_item and isinstance(root_item['children'], list):
                    extract_sections(root_item['children'])
            
            return sections
            
        except Exception as e:
            logger.error(f"Error listing sections: {e}")
            return []
