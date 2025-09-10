#!/usr/bin/env python3
"""
Repository Service - Handles repository listing and metadata operations.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import re

from .base_service import BaseService

logger = logging.getLogger(__name__)

class RepositoryService(BaseService):
    """Service for repository operations - listing cached repositories."""
    
    def __init__(self, github_token: str = None, anthropic_api_key: str = None):
        """Initialize the Repository Service."""
        super().__init__(github_token, anthropic_api_key)
    
    def get_repositories(self, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get list of repositories for which cached documentation exists.
        
        Args:
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with success status and list of repositories
        """
        try:
            if docs_type == 'wiki':
                base_path = self.wiki_docs_dir
            else:
                base_path = self.docs_dir
            
            repositories = []
            
            if not base_path.exists():
                return {
                    'success': True,
                    'repositories': [],
                    'count': 0
                }
            
            # Scan for repository directories
            for repo_dir in base_path.iterdir():
                if repo_dir.is_dir():
                    repo_name = repo_dir.name
                    
                    # Find the latest documentation version
                    latest_doc_path = self._find_latest_doc_path(repo_name, docs_type)
                    
                    if latest_doc_path:
                        # Extract GitHub URL from repo name
                        github_url = self._repo_name_to_github_url(repo_name)
                        
                        # Get metadata
                        metadata = self._get_repo_metadata(latest_doc_path)
                        
                        # Use timestamp directory name as fallback for generated_at
                        generated_at = metadata.get('generated_at', '')
                        if not generated_at:
                            # Parse timestamp from directory name (YYYYMMDD_HHMMSS)
                            timestamp_str = latest_doc_path.name
                            if len(timestamp_str) == 15 and timestamp_str[8] == '_':
                                try:
                                    from datetime import datetime
                                    dt = datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
                                    generated_at = dt.isoformat()
                                except ValueError:
                                    generated_at = timestamp_str
                            else:
                                generated_at = timestamp_str
                        
                        repositories.append({
                            'name': repo_name,
                            'github_url': github_url,
                            'latest_version': latest_doc_path.name,
                            'generated_at': generated_at,
                            'documentation_type': docs_type,
                            'available_sections': self._get_available_sections(latest_doc_path)
                        })
            
            # Sort by generated_at (most recent first)
            repositories.sort(key=lambda x: x.get('generated_at', ''), reverse=True)
            
            return {
                'success': True,
                'repositories': repositories,
                'count': len(repositories)
            }
            
        except Exception as e:
            logger.error(f"Error getting repositories: {e}")
            return {
                'success': False,
                'error': str(e),
                'repositories': [],
                'count': 0
            }
    
    def _repo_name_to_github_url(self, repo_name: str) -> str:
        """Convert repository name back to GitHub URL."""
        # Replace underscores with slashes
        if '_' in repo_name:
            owner, repo = repo_name.split('_', 1)
            return f"https://github.com/{owner}/{repo}"
        else:
            return f"https://github.com/{repo_name}"
    
    def _get_repo_metadata(self, doc_path: Path) -> Dict[str, Any]:
        """Get repository metadata from documentation directory."""
        try:
            metadata_file = doc_path / 'repository_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Could not read metadata for {doc_path}: {e}")
            return {}
    
    def _get_available_sections(self, doc_path: Path) -> List[str]:
        """Get list of available documentation sections in the correct order."""
        try:
            # First, try to get sections from the documentation structure
            structure = self._get_documentation_structure(doc_path)
            if structure:
                sections = self._extract_sections_from_structure(structure)
                if sections:
                    return sections
            
            # Fallback: get sections from filesystem (alphabetical order)
            markdown_files = [
                entry.name.replace('.md', '') 
                for entry in doc_path.iterdir() 
                if entry.is_file() and entry.name.endswith('.md') and entry.name != 'README.md'
            ]
            return sorted(markdown_files)  # Sort alphabetically as fallback
        except Exception as e:
            logger.error(f"Error getting available sections: {e}")
            return []
    
    def _get_documentation_structure(self, doc_path: Path) -> Dict[str, Any]:
        """Get documentation structure from JSON file."""
        try:
            structure_file = doc_path / 'documentation_structure.json'
            if structure_file.exists():
                with open(structure_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Could not read documentation structure: {e}")
            return {}
    
    def _extract_sections_from_structure(self, structure: Any) -> List[str]:
        """Extract section titles from documentation structure in order."""
        sections = []
        
        def extract_recursive(items):
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        title = item.get('title', '')
                        if title:
                            sections.append(title)
                        children = item.get('children', [])
                        if children:
                            extract_recursive(children)
            elif isinstance(items, dict):
                title = items.get('title', '')
                if title:
                    sections.append(title)
                children = items.get('children', [])
                if children:
                    extract_recursive(children)
        
        extract_recursive(structure)
        return sections
    
    def get_repository_info(self, repo_url: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get detailed information about a specific repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with repository information
        """
        try:
            repo_name = self._sanitize_repo_name(repo_url)
            latest_doc_path = self._find_latest_doc_path(repo_name, docs_type)
            
            if not latest_doc_path:
                return {
                    'success': False,
                    'error': f'No documentation found for {repo_url}'
                }
            
            # Get metadata
            metadata = self._get_repo_metadata(latest_doc_path)
            
            return {
                'success': True,
                'repository': {
                    'name': repo_name,
                    'github_url': repo_url,
                    'latest_version': latest_doc_path.name,
                    'generated_at': metadata.get('generated_at', ''),
                    'documentation_type': docs_type,
                    'available_sections': self._get_available_sections(latest_doc_path),
                    'metadata': metadata
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return {
                'success': False,
                'error': str(e)
            }
