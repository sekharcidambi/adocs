#!/usr/bin/env python3
"""
Documentation Retrieval Service - Retrieves previously generated documentation from file system.
This service handles file system access, timestamp management, and section retrieval.
"""

import json
import sys
import os
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentationRetrievalService:
    """Service for retrieving previously generated documentation from file system."""
    
    def __init__(self, docs_base_path: str = None, wiki_docs_base_path: str = None):
        """
        Initialize the Documentation Retrieval service.
        
        Args:
            docs_base_path: Base path for generated documentation files
            wiki_docs_base_path: Base path for generated wiki documentation files
        """
        if docs_base_path is None:
            docs_base_path = os.path.join(os.path.dirname(__file__), 'generated_docs')
        
        if wiki_docs_base_path is None:
            wiki_docs_base_path = os.path.join(os.path.dirname(__file__), 'generated_wiki_docs')
        
        self.docs_base_path = Path(docs_base_path)
        self.wiki_docs_base_path = Path(wiki_docs_base_path)
        
        logger.info(f"Documentation Retrieval Service initialized")
        logger.info(f"Documentation base path: {self.docs_base_path}")
        logger.info(f"Wiki documentation base path: {self.wiki_docs_base_path}")
    
    def _sanitize_repo_name(self, repo_url: str) -> str:
        """Convert GitHub URL to safe repository name for file system."""
        # Extract owner/repo from URL
        url_match = re.match(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if url_match:
            owner, repo = url_match.groups()
            return f"{owner}_{repo}"
        else:
            # Fallback: use the repo parameter as-is, replacing / with _
            return repo_url.replace('/', '_')
    
    def _find_most_recent_documentation(self, repo_name: str, docs_type: str = 'docs') -> Optional[Path]:
        """Find the most recent documentation directory for a repository."""
        if docs_type == 'wiki':
            base_path = self.wiki_docs_base_path
        else:
            base_path = self.docs_base_path
        
        repo_path = base_path / repo_name
        
        if not repo_path.exists():
            return None
        
        try:
            entries = [entry for entry in repo_path.iterdir() if entry.is_dir()]
            timestamp_dirs = [entry for entry in entries if re.match(r'^\d{8}_\d{6}$', entry.name)]
            
            if not timestamp_dirs:
                return None
            
            # Get the most recent timestamp directory
            latest_dir = sorted(timestamp_dirs, key=lambda x: x.name)[-1]
            return latest_dir
            
        except Exception as e:
            logger.error(f"Error finding documentation for {repo_name}: {e}")
            return None
    
    def _get_available_sections(self, doc_path: Path) -> List[str]:
        """Get list of available documentation sections."""
        try:
            markdown_files = [
                entry.name.replace('.md', '') 
                for entry in doc_path.iterdir() 
                if entry.is_file() and entry.name.endswith('.md') and entry.name != 'README.md'
            ]
            return markdown_files
        except Exception as e:
            logger.error(f"Error getting available sections: {e}")
            return []
    
    def _read_file_safely(self, file_path: Path) -> Optional[str]:
        """Safely read a file and return its content."""
        try:
            if file_path.exists() and file_path.is_file():
                return file_path.read_text(encoding='utf-8')
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def _read_json_file_safely(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Safely read a JSON file and return parsed data."""
        try:
            content = self._read_file_safely(file_path)
            if content:
                return json.loads(content)
            return None
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {e}")
            return None
    
    def get_documentation_structure(self, repo_url: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get complete documentation structure for a repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with documentation structure and metadata
        """
        try:
            repo_name = self._sanitize_repo_name(repo_url)
            logger.info(f"Retrieving documentation structure for: {repo_name} (type: {docs_type})")
            
            # Find the most recent documentation directory
            doc_path = self._find_most_recent_documentation(repo_name, docs_type)
            
            if not doc_path:
                return {
                    "success": False,
                    "error": "No documentation found for this repository",
                    "repository": repo_url,
                    "docs_type": docs_type
                }
            
            # Read documentation files
            structure_file = doc_path / "documentation_structure.json"
            metadata_file = doc_path / "repository_metadata.json"
            index_file = doc_path / "README.md"
            
            structure = self._read_json_file_safely(structure_file)
            metadata = self._read_json_file_safely(metadata_file)
            index_content = self._read_file_safely(index_file)
            
            # Get available sections
            available_sections = self._get_available_sections(doc_path)
            
            # Get section file paths
            section_paths = {}
            for section in available_sections:
                section_file = doc_path / f"{section}.md"
                if section_file.exists():
                    section_paths[section] = str(section_file)
            
            result = {
                "success": True,
                "repository": repo_url,
                "docs_type": docs_type,
                "generated_at": doc_path.name,
                "output_directory": str(doc_path),
                "structure": structure,
                "metadata": metadata,
                "index": index_content,
                "available_sections": available_sections,
                "section_paths": section_paths,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully retrieved documentation structure for {repo_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving documentation structure: {e}")
            return {
                "success": False,
                "error": f"Failed to retrieve documentation: {str(e)}",
                "repository": repo_url,
                "docs_type": docs_type
            }
    
    def get_section_content(self, repo_url: str, section: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get specific section content for a repository.
        
        Args:
            repo_url: GitHub repository URL
            section: Section name to retrieve
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with section content and metadata
        """
        try:
            repo_name = self._sanitize_repo_name(repo_url)
            logger.info(f"Retrieving section '{section}' for: {repo_name} (type: {docs_type})")
            
            # Find the most recent documentation directory
            doc_path = self._find_most_recent_documentation(repo_name, docs_type)
            
            if not doc_path:
                return {
                    "success": False,
                    "error": "No documentation found for this repository",
                    "repository": repo_url,
                    "section": section,
                    "docs_type": docs_type
                }
            
            # Read specific section file
            section_file = doc_path / f"{section}.md"
            content = self._read_file_safely(section_file)
            
            if not content:
                return {
                    "success": False,
                    "error": "Section not found",
                    "repository": repo_url,
                    "section": section,
                    "docs_type": docs_type
                }
            
            result = {
                "success": True,
                "repository": repo_url,
                "section": section,
                "docs_type": docs_type,
                "content": content,
                "file_path": str(section_file),
                "generated_at": doc_path.name,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Successfully retrieved section '{section}' for {repo_name}")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving section content: {e}")
            return {
                "success": False,
                "error": f"Failed to retrieve section: {str(e)}",
                "repository": repo_url,
                "section": section,
                "docs_type": docs_type
            }
    
    def list_available_repositories(self, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        List all available repositories with generated documentation.
        
        Args:
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with list of available repositories
        """
        try:
            if docs_type == 'wiki':
                base_path = self.wiki_docs_base_path
            else:
                base_path = self.docs_base_path
            
            if not base_path.exists():
                return {
                    "success": True,
                    "repositories": [],
                    "docs_type": docs_type
                }
            
            repositories = []
            
            for repo_dir in base_path.iterdir():
                if repo_dir.is_dir():
                    # Get the most recent documentation for this repository
                    latest_doc = self._find_most_recent_documentation(repo_dir.name, docs_type)
                    
                    if latest_doc:
                        # Get basic info about the repository
                        metadata_file = latest_doc / "repository_metadata.json"
                        metadata = self._read_json_file_safely(metadata_file)
                        
                        repositories.append({
                            "name": repo_dir.name,
                            "generated_at": latest_doc.name,
                            "output_directory": str(latest_doc),
                            "metadata": metadata,
                            "available_sections": self._get_available_sections(latest_doc)
                        })
            
            result = {
                "success": True,
                "repositories": repositories,
                "docs_type": docs_type,
                "count": len(repositories),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Found {len(repositories)} repositories with {docs_type} documentation")
            return result
            
        except Exception as e:
            logger.error(f"Error listing repositories: {e}")
            return {
                "success": False,
                "error": f"Failed to list repositories: {str(e)}",
                "docs_type": docs_type
            }
    
    def get_documentation_info(self, repo_url: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get basic information about available documentation for a repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with documentation information
        """
        try:
            repo_name = self._sanitize_repo_name(repo_url)
            
            # Find the most recent documentation directory
            doc_path = self._find_most_recent_documentation(repo_name, docs_type)
            
            if not doc_path:
                return {
                    "success": False,
                    "error": "No documentation found for this repository",
                    "repository": repo_url,
                    "docs_type": docs_type
                }
            
            # Get available sections
            available_sections = self._get_available_sections(doc_path)
            
            # Get section file paths
            section_paths = {}
            for section in available_sections:
                section_file = doc_path / f"{section}.md"
                if section_file.exists():
                    section_paths[section] = str(section_file)
            
            result = {
                "success": True,
                "repository": repo_url,
                "docs_type": docs_type,
                "generated_at": doc_path.name,
                "output_directory": str(doc_path),
                "available_sections": available_sections,
                "section_paths": section_paths,
                "section_count": len(available_sections),
                "timestamp": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting documentation info: {e}")
            return {
                "success": False,
                "error": f"Failed to get documentation info: {str(e)}",
                "repository": repo_url,
                "docs_type": docs_type
            }

def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python documentation_retrieval_service.py <command> [args...]")
        print("Commands:")
        print("  structure <repo_url> [docs_type] - Get complete documentation structure")
        print("  section <repo_url> <section> [docs_type] - Get specific section content")
        print("  list [docs_type] - List all available repositories")
        print("  info <repo_url> [docs_type] - Get basic documentation information")
        sys.exit(1)
    
    command = sys.argv[1]
    service = DocumentationRetrievalService()
    
    try:
        if command == "structure":
            if len(sys.argv) < 3:
                print("Error: structure command requires repository URL")
                sys.exit(1)
            
            repo_url = sys.argv[2]
            docs_type = sys.argv[3] if len(sys.argv) > 3 else 'docs'
            
            result = service.get_documentation_structure(repo_url, docs_type)
            print(json.dumps(result, indent=2))
            
        elif command == "section":
            if len(sys.argv) < 4:
                print("Error: section command requires repository URL and section name")
                sys.exit(1)
            
            repo_url = sys.argv[2]
            section = sys.argv[3]
            docs_type = sys.argv[4] if len(sys.argv) > 4 else 'docs'
            
            result = service.get_section_content(repo_url, section, docs_type)
            print(json.dumps(result, indent=2))
            
        elif command == "list":
            docs_type = sys.argv[2] if len(sys.argv) > 2 else 'docs'
            
            result = service.list_available_repositories(docs_type)
            print(json.dumps(result, indent=2))
            
        elif command == "info":
            if len(sys.argv) < 3:
                print("Error: info command requires repository URL")
                sys.exit(1)
            
            repo_url = sys.argv[2]
            docs_type = sys.argv[3] if len(sys.argv) > 3 else 'docs'
            
            result = service.get_documentation_info(repo_url, docs_type)
            print(json.dumps(result, indent=2))
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
