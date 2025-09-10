#!/usr/bin/env python3
"""
Documentation Service - Handles documentation retrieval and access operations.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

from .base_service import BaseService

logger = logging.getLogger(__name__)

class DocumentationService(BaseService):
    """Service for documentation retrieval and access operations."""
    
    def __init__(self, github_token: str = None, anthropic_api_key: str = None):
        """Initialize the Documentation Service."""
        super().__init__(github_token, anthropic_api_key)
    
    def get_documentation(self, repo_url: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get complete documentation structure for a repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with documentation structure and content
        """
        try:
            repo_name = self._sanitize_repo_name(repo_url)
            latest_doc_path = self._find_latest_doc_path(repo_name, docs_type)
            
            if not latest_doc_path:
                return {
                    'success': False,
                    'error': f'No documentation found for {repo_url}'
                }
            
            # Get documentation structure
            structure = self._get_documentation_structure(latest_doc_path)
            
            # Get all section content
            sections = {}
            available_sections = self._get_available_sections(latest_doc_path)
            
            for section in available_sections:
                section_content = self._get_section_content(latest_doc_path, section)
                if section_content:
                    sections[section] = section_content
            
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
            else:
                # If generated_at exists but is in timestamp format, convert it
                if isinstance(generated_at, str) and len(generated_at) == 15 and generated_at[8] == '_':
                    try:
                        from datetime import datetime
                        dt = datetime.strptime(generated_at, '%Y%m%d_%H%M%S')
                        generated_at = dt.isoformat()
                    except ValueError:
                        pass  # Keep original if conversion fails
            
            return {
                'success': True,
                'repository': repo_url,
                'documentation_type': docs_type,
                'generated_at': generated_at,
                'structure': structure,
                'sections': sections,
                'available_sections': available_sections,
                'hierarchical_sections': self._get_hierarchical_sections(structure),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error getting documentation: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_documentation_section(self, repo_url: str, section: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get specific documentation section content.
        
        Args:
            repo_url: GitHub repository URL
            section: Section name to retrieve
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with section content
        """
        try:
            repo_name = self._sanitize_repo_name(repo_url)
            latest_doc_path = self._find_latest_doc_path(repo_name, docs_type)
            
            if not latest_doc_path:
                return {
                    'success': False,
                    'error': f'No documentation found for {repo_url}'
                }
            
            # Get section content
            section_content = self._get_section_content(latest_doc_path, section)
            
            if not section_content:
                return {
                    'success': False,
                    'error': f'Section "{section}" not found for {repo_url}'
                }
            
            return {
                'success': True,
                'repository': repo_url,
                'section': section,
                'content': section_content,
                'documentation_type': docs_type
            }
            
        except Exception as e:
            logger.error(f"Error getting documentation section: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
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
    
    def _get_section_content(self, doc_path: Path, section: str) -> Optional[str]:
        """Get content of a specific documentation section."""
        try:
            # Try different possible filenames
            possible_files = [
                f"{section}.md",
                f"{section.replace(' ', '_')}.md",
                f"{section.replace(' ', '-')}.md"
            ]
            
            for filename in possible_files:
                section_file = doc_path / filename
                if section_file.exists():
                    return section_file.read_text(encoding='utf-8')
            
            return None
        except Exception as e:
            logger.warning(f"Could not read section {section}: {e}")
            return None
    
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
    
    def _get_hierarchical_sections(self, structure: Any) -> List[Dict[str, Any]]:
        """Get hierarchical sections with indentation levels."""
        hierarchical_sections = []
        
        def extract_hierarchical(items, level=0):
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        title = item.get('title', '')
                        if title:
                            hierarchical_sections.append({
                                'title': title,
                                'level': level,
                                'has_children': bool(item.get('children', []))
                            })
                        children = item.get('children', [])
                        if children:
                            extract_hierarchical(children, level + 1)
            elif isinstance(items, dict):
                # Handle the case where structure is a dict with 'sections' key
                if 'sections' in items:
                    extract_hierarchical(items['sections'], level)
                else:
                    title = items.get('title', '')
                    if title:
                        hierarchical_sections.append({
                            'title': title,
                            'level': level,
                            'has_children': bool(items.get('children', []))
                        })
                    children = items.get('children', [])
                    if children:
                        extract_hierarchical(children, level + 1)
        
        extract_hierarchical(structure)
        return hierarchical_sections
    
    def _get_repo_metadata(self, doc_path: Path) -> Dict[str, Any]:
        """Get repository metadata from documentation directory."""
        try:
            metadata_file = doc_path / 'repository_metadata.json'
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.warning(f"Could not read metadata: {e}")
            return {}
