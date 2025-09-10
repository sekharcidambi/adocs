#!/usr/bin/env python3
"""
Analysis Service with GCS Integration - Handles repository analysis and documentation structure generation.
"""

import json
import os
import sys
import logging
import asyncio
import aiohttp
import ssl
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import re
import tempfile
import shutil
import subprocess

# Add the src directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from .base_service import BaseService
from .storage_service import CloudStorageService
from src.generator import DocStructureGenerator

logger = logging.getLogger(__name__)

class AnalysisServiceGCS(BaseService):
    """Service for repository analysis and documentation structure generation with GCS storage."""
    
    def __init__(self, github_token: str = None, anthropic_api_key: str = None, gcs_bucket: str = None):
        """Initialize the Analysis Service with GCS."""
        super().__init__(github_token, anthropic_api_key)
        
        # Initialize the documentation generator
        self.knowledge_base_path = self.base_dir / 'knowledge_base.pkl'
        self.generator = None
        
        # Initialize GCS service
        self.storage_service = CloudStorageService(bucket_name=gcs_bucket)
    
    def _initialize_generator(self):
        """Initialize the DocStructureGenerator if not already done."""
        if self.generator is None:
            try:
                self.generator = DocStructureGenerator(str(self.knowledge_base_path))
                logger.info("DocStructureGenerator initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DocStructureGenerator: {e}")
                raise
    
    async def analyze_repository(self, repo_url: str) -> Dict[str, Any]:
        """
        Analyze a repository and generate documentation structure.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Analysis result with documentation structure
        """
        try:
            logger.info(f"Starting analysis for repository: {repo_url}")
            
            # Initialize generator
            self._initialize_generator()
            
            # Parse GitHub URL
            url_match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if not url_match:
                raise ValueError('Invalid GitHub URL')
            
            owner, repo = url_match.groups()
            logger.info(f"Analyzing repository: {owner}/{repo}")
            
            # Fetch repository data
            repo_data = await self._fetch_repository_data(owner, repo)
            
            # Analyze repository structure
            analysis = self._analyze_repository_structure(repo_data)
            
            # Generate documentation structure
            doc_structure = self.generator.generate(analysis, api_key=self.anthropic_api_key)
            
            # Save to GCS
            gcs_paths = await self._save_to_gcs(repo_url, analysis, doc_structure)
            
            result = {
                "success": True,
                "repository": {
                    "name": repo_data['name'],
                    "description": repo_data.get('description', ''),
                    "owner": repo_data['owner']['login'],
                    "stars": repo_data['stargazers_count'],
                    "language": repo_data.get('language', ''),
                    "topics": repo_data.get('topics', []),
                    "createdAt": repo_data['created_at'],
                    "updatedAt": repo_data['updated_at'],
                },
                "analysis": analysis,
                "documentationStructure": doc_structure,
                "storage": {
                    "type": "gcs",
                    "bucket": self.storage_service.bucket_name,
                    "paths": gcs_paths
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Analysis completed successfully for: {repo_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing repository {repo_url}: {e}")
            return {
                "success": False,
                "error": str(e),
                "repository": repo_url
            }
    
    async def _fetch_repository_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """Fetch repository data from GitHub API."""
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        timeout = aiohttp.ClientTimeout(total=3600)  # 60 minute timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            # Fetch repository information
            repo_url = f'https://api.github.com/repos/{owner}/{repo}'
            async with session.get(repo_url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to fetch repository data: {response.status}")
    
    def _analyze_repository_structure(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repository structure and create metadata."""
        return {
            "github_url": repo_data['html_url'],
            "overview": repo_data.get('description', ''),
            "business_domain": self._determine_business_domain(repo_data['name'], repo_data.get('description', '')),
            "tech_stack": {
                "languages": [repo_data.get('language', '')] if repo_data.get('language') else [],
                "topics": repo_data.get('topics', [])
            },
            "architecture": {
                "description": f"Repository with {repo_data.get('language', 'unknown')} language"
            },
            "features": [],
            "target_audience": "Developers and users"
        }
    
    def _determine_business_domain(self, repo_name: str, description: str) -> str:
        """Determine business domain based on repository name and description."""
        repo_name_lower = repo_name.lower()
        description_lower = description.lower()
        
        if any(keyword in repo_name_lower for keyword in ['web', 'frontend', 'ui', 'client']):
            return 'Web Development'
        elif any(keyword in repo_name_lower for keyword in ['api', 'backend', 'server', 'service']):
            return 'Backend Development'
        elif any(keyword in repo_name_lower for keyword in ['mobile', 'ios', 'android', 'app']):
            return 'Mobile Development'
        elif any(keyword in repo_name_lower for keyword in ['data', 'ml', 'ai', 'analytics']):
            return 'Data Science'
        elif any(keyword in repo_name_lower for keyword in ['devops', 'infra', 'deploy', 'ci']):
            return 'DevOps'
        else:
            return 'Software Development'
    
    async def _save_to_gcs(self, repo_url: str, analysis: Dict[str, Any], doc_structure: Dict[str, Any]) -> Dict[str, str]:
        """Save analysis results and documentation to GCS."""
        try:
            gcs_paths = {}
            
            # Save documentation structure
            structure_path = self.storage_service.save_documentation_structure(
                repo_url, doc_structure, "docs"
            )
            gcs_paths['documentation_structure'] = structure_path
            
            # Save repository metadata
            metadata_path = self.storage_service.save_repository_metadata(
                repo_url, analysis, "docs"
            )
            gcs_paths['repository_metadata'] = metadata_path
            
            # Generate and save markdown files
            markdown_paths = await self._generate_and_save_markdown_files(
                repo_url, doc_structure, analysis
            )
            gcs_paths['markdown_files'] = markdown_paths
            
            # Generate and save index file
            index_content = self._generate_index_content(repo_url, analysis, doc_structure, markdown_paths)
            index_path = self.storage_service.save_index_file(repo_url, index_content, "docs")
            gcs_paths['index_file'] = index_path
            
            logger.info(f"Saved all documentation to GCS for: {repo_url}")
            return gcs_paths
            
        except Exception as e:
            logger.error(f"Error saving to GCS: {e}")
            raise
    
    async def _generate_and_save_markdown_files(self, repo_url: str, doc_structure: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Generate and save markdown files to GCS."""
        markdown_paths = []
        
        try:
            # Handle the correct structure format: dict with 'sections' key
            sections = doc_structure.get('sections', [])
            logger.info(f"🔄 Processing {len(sections)} sections for markdown generation")
            
            async def process_sections(items: List[Dict[str, Any]], parent_title: str = ''):
                for item in items:
                    section_title = f"{parent_title} > {item['title']}" if parent_title else item['title']
                    
                    try:
                        logger.info(f"🔄 Generating content for: {section_title}")
                        
                        # Generate AI-enhanced content using Claude
                        content = await self._generate_ai_enhanced_content(item['title'], item, analysis)
                        
                        # Save markdown file
                        filename = f"{self._sanitize_filename(item['title'])}.md"
                        path = self.storage_service.save_markdown_file(
                            repo_url, filename, content, "docs"
                        )
                        markdown_paths.append(path)
                        
                        logger.info(f"✅ Generated content for: {section_title}")
                        
                    except Exception as error:
                        logger.error(f"❌ Failed to generate content for {section_title}: {error}")
                    
                    # Recursively process nested children
                    if 'children' in item and isinstance(item['children'], list):
                        await process_sections(item['children'], section_title)
            
            # Process all sections
            await process_sections(sections)
            
            return markdown_paths
            
        except Exception as e:
            logger.error(f"Error generating markdown files: {e}")
            return []
    
    async def _generate_ai_enhanced_content(self, section_title: str, section_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate AI-enhanced content for a documentation section using Claude."""
        try:
            # Configure Claude API with extended timeout
            import anthropic
            client = anthropic.Anthropic(
                api_key=self.anthropic_api_key,
                timeout=3600.0  # 60 minute timeout for individual API calls
            )
            
            # Create comprehensive prompt for the section
            prompt = self._create_section_prompt(section_title, section_data, analysis)
            
            # Use the working Claude model with progress tracking
            logger.info(f"🔄 Generating content for: {section_title}")
            logger.info(f"Using claude-sonnet-4-20250514 for content generation: {section_title}")
            
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.3,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            if response.content and response.content[0].text:
                logger.info(f"✅ Generated content for: {section_title}")
                return response.content[0].text
            else:
                logger.warning(f"Empty response from Claude for section: {section_title}")
                return self._create_basic_section_content(section_title, analysis)
                
        except Exception as e:
            logger.error(f"Error generating AI content for section {section_title}: {e}")
            return self._create_basic_section_content(section_title, analysis)
    
    def _create_section_prompt(self, section_title: str, section_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for Claude to generate section content."""
        repo_name = analysis.get('github_url', '').split('/')[-1] if analysis.get('github_url') else 'the repository'
        business_domain = analysis.get('business_domain', 'software development')
        tech_stack = analysis.get('tech_stack', {})
        languages = ', '.join(tech_stack.get('languages', []))
        topics = ', '.join(tech_stack.get('topics', []))
        
        prompt = f"""You are a technical documentation expert. Generate comprehensive, well-structured documentation for the section "{section_title}" of the {repo_name} project.

**Project Context:**
- Repository: {analysis.get('github_url', 'Unknown')}
- Business Domain: {business_domain}
- Primary Languages: {languages}
- Technologies/Topics: {topics}
- Architecture: {analysis.get('architecture', {}).get('description', 'Not specified')}

**Section Context:**
- Section Title: {section_title}
- Section Data: {section_data}

**Requirements:**
1. Create detailed, informative content that would be valuable for developers
2. Include practical examples and implementation details where relevant
3. Structure the content with clear headings and subheadings
4. Make it specific to the {repo_name} project and its {business_domain} domain
5. Include code examples, best practices, and architectural insights
6. Write in a professional, technical tone suitable for developers

**Format:**
- Use proper Markdown formatting
- Include code blocks where appropriate
- Add relevant links and references
- Structure with clear hierarchy (##, ###, etc.)

Generate comprehensive documentation content for the "{section_title}" section:"""

        return prompt
    
    def _create_basic_section_content(self, title: str, analysis: Dict[str, Any]) -> str:
        """Generate basic fallback content for a documentation section."""
        return f"""# {title}

## Overview

This section covers {title.lower()} for the {analysis.get('business_domain', 'software')} project.

## Details

- **Repository**: {analysis.get('github_url', 'Unknown')}
- **Business Domain**: {analysis.get('business_domain', 'Not specified')}
- **Tech Stack**: {', '.join(analysis.get('tech_stack', {}).get('languages', []))}

## Implementation

This section provides detailed information about {title.lower()} and its implementation in the project.

---

*Generated by ADocS on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = '_'.join(filter(None, filename.split('_')))
        return filename.strip()
    
    def _generate_index_content(self, repo_url: str, analysis: Dict[str, Any], doc_structure: Dict[str, Any], markdown_paths: List[str]) -> str:
        """Generate index markdown content."""
        github_url = analysis.get('github_url', 'Unknown')
        repo_name = github_url.split('/')[-1] if '/' in github_url else 'Unknown Repository'
        
        index_content = f"""# {repo_name} Documentation

This directory contains AI-generated comprehensive documentation for the repository: **{github_url}**

## Repository Overview

- **Description**: {analysis.get('overview', 'No description available')}
- **Business Domain**: {analysis.get('business_domain', 'Not specified')}
- **Tech Stack**: {', '.join(analysis.get('tech_stack', {}).get('languages', []))}

## Generated Documentation

This documentation was generated using the ADocS system and is stored in Google Cloud Storage.

## Files Generated

- Documentation structure and metadata
- Multiple markdown files covering different aspects
- Index file for navigation

## Usage

This documentation was generated using the ADocS system with GCS storage integration.

For the most up-to-date information, please refer to the original repository: {github_url}

---
*Generated by ADocS with GCS integration on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return index_content
