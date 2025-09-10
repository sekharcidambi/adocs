#!/usr/bin/env python3
"""
Base Service - Common functionality for all ADocS services.
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseService:
    """Base class for all ADocS services with common functionality."""
    
    def __init__(self, github_token: str = None, anthropic_api_key: str = None):
        """
        Initialize the base service.
        
        Args:
            github_token: GitHub API token for repository access
            anthropic_api_key: Anthropic API key for content generation
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        
        # Base paths
        self.base_dir = Path(__file__).parent.parent
        self.docs_dir = self.base_dir / 'generated_docs'
        self.wiki_docs_dir = self.base_dir / 'generated_wiki_docs'
        
        # Create directories if they don't exist
        self.docs_dir.mkdir(exist_ok=True)
        self.wiki_docs_dir.mkdir(exist_ok=True)
        
        logger.info(f"{self.__class__.__name__} initialized")
    
    def _sanitize_repo_name(self, repo_url: str) -> str:
        """Convert GitHub URL to safe repository name for file system."""
        import re
        # Extract owner/repo from URL
        url_match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if url_match:
            owner, repo = url_match.groups()
            return f"{owner}_{repo}"
        else:
            # Fallback: use the repo parameter as-is, replacing / with _
            return repo_url.replace('/', '_')
    
    def _get_timestamp_dir(self) -> str:
        """Get current timestamp in YYYYMMDD_HHMMSS format."""
        from datetime import datetime
        return datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def _create_repo_directory(self, repo_name: str, docs_type: str = 'docs') -> Path:
        """Create timestamped directory for repository documentation."""
        if docs_type == 'wiki':
            base_path = self.wiki_docs_dir
        else:
            base_path = self.docs_dir
        
        repo_path = base_path / repo_name
        timestamp_dir = repo_path / self._get_timestamp_dir()
        timestamp_dir.mkdir(parents=True, exist_ok=True)
        
        return timestamp_dir
    
    def _find_latest_doc_path(self, repo_name: str, docs_type: str = 'docs') -> Optional[Path]:
        """Find the most recent documentation directory for a repository."""
        if docs_type == 'wiki':
            base_path = self.wiki_docs_dir
        else:
            base_path = self.docs_dir
        
        repo_path = base_path / repo_name
        
        if not repo_path.exists():
            return None
        
        try:
            import re
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
