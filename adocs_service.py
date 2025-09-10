#!/usr/bin/env python3
"""
ADocS Service - Main service orchestrator for all ADocS operations.
This service provides a clean interface for all frontend operations.
"""

import json
import sys
import os
import logging
import asyncio
from typing import Dict, Any, Optional

# Add services directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from services.repository_service import RepositoryService
from services.documentation_service import DocumentationService
from services.analysis_service import AnalysisService
from services.wiki_service import WikiService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ADocSService:
    """Main ADocS service orchestrator."""
    
    def __init__(self, github_token: str = None, anthropic_api_key: str = None):
        """
        Initialize the ADocS service.
        
        Args:
            github_token: GitHub API token for repository access
            anthropic_api_key: Anthropic API key for content generation
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        
        # Initialize all services
        self.repository_service = RepositoryService(self.github_token, self.anthropic_api_key)
        self.documentation_service = DocumentationService(self.github_token, self.anthropic_api_key)
        self.analysis_service = AnalysisService(self.github_token, self.anthropic_api_key)
        self.wiki_service = WikiService(self.github_token, self.anthropic_api_key)
        
        logger.info("ADocS Service initialized with all sub-services")
    
    def get_repositories(self, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get list of repositories for which cached documentation exists.
        
        Args:
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with success status and list of repositories
        """
        logger.info(f"Getting repositories for docs_type: {docs_type}")
        return self.repository_service.get_repositories(docs_type)
    
    def get_documentation(self, repo_url: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get complete documentation for a repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with documentation content
        """
        logger.info(f"Getting documentation for {repo_url} (type: {docs_type})")
        return self.documentation_service.get_documentation(repo_url, docs_type)
    
    def get_documentation_section(self, repo_url: str, section: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get specific documentation section for a repository.
        
        Args:
            repo_url: GitHub repository URL
            section: Section name to retrieve
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with section content
        """
        logger.info(f"Getting section '{section}' for {repo_url} (type: {docs_type})")
        return self.documentation_service.get_documentation_section(repo_url, section, docs_type)
    
    async def analyze_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Analyze a repository and generate documentation structure.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing repository: {repo_url}")
        return await self.analysis_service.analyze_repository(repo_url)
    
    async def generate_wiki(self, repo_url: str) -> Dict[str, Any]:
        """
        Generate enhanced wiki-style documentation from existing documentation.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary with wiki generation results
        """
        logger.info(f"Generating wiki for repository: {repo_url}")
        return await self.wiki_service.generate_wiki(repo_url)
    
    def get_repository_info(self, repo_url: str, docs_type: str = 'docs') -> Dict[str, Any]:
        """
        Get detailed information about a specific repository.
        
        Args:
            repo_url: GitHub repository URL
            docs_type: Type of documentation ('docs' or 'wiki')
            
        Returns:
            Dictionary with repository information
        """
        logger.info(f"Getting repository info for {repo_url} (type: {docs_type})")
        return self.repository_service.get_repository_info(repo_url, docs_type)


def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python adocs_service.py <command> [args...]")
        print("Commands:")
        print("  get-repositories [docs_type] - Get list of repositories with cached docs")
        print("  get-documentation <repo_url> [docs_type] - Get complete documentation")
        print("  get-section <repo_url> <section> [docs_type] - Get specific section")
        print("  analyze <repo_url> - Analyze repository and generate docs")
        print("  generate-wiki <repo_url> - Generate enhanced wiki documentation")
        print("  get-info <repo_url> [docs_type] - Get repository information")
        sys.exit(1)

    command = sys.argv[1]

    try:
        # Initialize service
        service = ADocSService()

        if command == "get-repositories":
            docs_type = sys.argv[2] if len(sys.argv) > 2 else 'docs'
            result = service.get_repositories(docs_type)
            print(json.dumps(result, indent=2))

        elif command == "get-documentation":
            if len(sys.argv) < 3:
                print("Error: get-documentation command requires repository URL")
                sys.exit(1)
            repo_url = sys.argv[2]
            docs_type = sys.argv[3] if len(sys.argv) > 3 else 'docs'
            result = service.get_documentation(repo_url, docs_type)
            print(json.dumps(result, indent=2))

        elif command == "get-section":
            if len(sys.argv) < 4:
                print("Error: get-section command requires repository URL and section name")
                sys.exit(1)
            repo_url = sys.argv[2]
            section = sys.argv[3]
            docs_type = sys.argv[4] if len(sys.argv) > 4 else 'docs'
            result = service.get_documentation_section(repo_url, section, docs_type)
            print(json.dumps(result, indent=2))

        elif command == "analyze":
            if len(sys.argv) < 3:
                print("Error: analyze command requires repository URL")
                sys.exit(1)
            repo_url = sys.argv[2]
            result = asyncio.run(service.analyze_repository(repo_url))
            print(json.dumps(result, indent=2))

        elif command == "generate-wiki":
            if len(sys.argv) < 3:
                print("Error: generate-wiki command requires repository URL")
                sys.exit(1)
            repo_url = sys.argv[2]
            result = asyncio.run(service.generate_wiki(repo_url))
            print(json.dumps(result, indent=2))

        elif command == "get-info":
            if len(sys.argv) < 3:
                print("Error: get-info command requires repository URL")
                sys.exit(1)
            repo_url = sys.argv[2]
            docs_type = sys.argv[3] if len(sys.argv) > 3 else 'docs'
            result = service.get_repository_info(repo_url, docs_type)
            print(json.dumps(result, indent=2))

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()