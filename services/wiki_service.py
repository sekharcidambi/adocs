#!/usr/bin/env python3
"""
Wiki Service - Handles wiki-style documentation generation from existing documentation.
"""

import json
import os
import sys
import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from pathlib import Path
import re
import tempfile
import shutil

from .base_service import BaseService

logger = logging.getLogger(__name__)

class WikiService(BaseService):
    """Service for generating enhanced wiki-style documentation from existing documentation."""
    
    def __init__(self, github_token: str = None, anthropic_api_key: str = None):
        """Initialize the Wiki Service."""
        super().__init__(github_token, anthropic_api_key)
    
    async def generate_wiki(self, repo_url: str) -> Dict[str, Any]:
        """
        Generate enhanced wiki-style documentation from existing repository documentation.
        
        Args:
            repo_url: GitHub repository URL
            
        Returns:
            Dictionary with wiki generation results
        """
        try:
            # Extract owner and repo from URL
            url_match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if not url_match:
                return {
                    'success': False,
                    'error': 'Invalid GitHub URL format'
                }
            
            owner, repo = url_match.groups()
            
            # Fetch repository data
            logger.info(f"Fetching repository data for {owner}/{repo}")
            repo_data = await self._fetch_repository_data(owner, repo)
            
            # Find existing documentation files
            logger.info("Discovering existing documentation files")
            doc_files = await self._find_documentation_files(owner, repo, repo_data['contents'])
            
            # Generate repository summary
            logger.info("Generating repository summary")
            repo_summary = await self._generate_repository_summary(repo_data, doc_files)
            
            # Create output directory
            repo_name = self._sanitize_repo_name(repo_url)
            output_dir = self._create_repo_directory(repo_name, 'wiki')
            
            # Generate enhanced content for each documentation file
            logger.info("Generating enhanced content for documentation files")
            enhanced_pages = await self._generate_enhanced_pages(
                output_dir, doc_files, repo_data, repo_summary
            )
            
            # Create index file
            self._create_wiki_index(output_dir, repo_data, enhanced_pages, repo_summary)
            
            # Save repository metadata
            self._save_wiki_metadata(output_dir, repo_data, repo_summary)
            
            return {
                'success': True,
                'repository': repo_url,
                'output_directory': str(output_dir),
                'pages': enhanced_pages,
                'summary': repo_summary,
                'generated_at': self._get_timestamp_dir()
            }
            
        except Exception as e:
            logger.error(f"Error generating wiki: {e}")
            return {
                'success': False,
                'error': str(e)
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
                    repo_data = await response.json()
                else:
                    raise Exception(f"Failed to fetch repository data: {response.status}")
            
            # Fetch README
            readme_content = ''
            try:
                readme_url = f'https://api.github.com/repos/{owner}/{repo}/readme'
                async with session.get(readme_url, headers=headers) as response:
                    if response.status == 200:
                        readme_data = await response.json()
                        import base64
                        readme_content = base64.b64decode(readme_data['content']).decode('utf-8')
            except Exception as e:
                logger.warning(f"Could not fetch README: {e}")
            
            # Fetch repository contents
            contents_data = []
            try:
                contents_url = f'https://api.github.com/repos/{owner}/{repo}/contents'
                async with session.get(contents_url, headers=headers) as response:
                    if response.status == 200:
                        contents_data = await response.json()
            except Exception as e:
                logger.warning(f"Could not fetch repository contents: {e}")
            
            return {
                'repository': repo_data,
                'readme': readme_content,
                'contents': contents_data
            }
    
    async def _find_documentation_files(self, owner: str, repo: str, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find and fetch documentation files recursively."""
        doc_files = []
        doc_patterns = [
            re.compile(r'^readme\.md$', re.IGNORECASE),
            re.compile(r'^docs?/', re.IGNORECASE),
            re.compile(r'\.md$', re.IGNORECASE),
            re.compile(r'^documentation/', re.IGNORECASE),
            re.compile(r'^guide/', re.IGNORECASE),
            re.compile(r'^manual/', re.IGNORECASE),
            re.compile(r'^tutorial/', re.IGNORECASE),
            re.compile(r'^examples/', re.IGNORECASE),
            re.compile(r'^api/', re.IGNORECASE),
            re.compile(r'^reference/', re.IGNORECASE)
        ]
        
        # Process root level files
        for item in contents:
            if item['type'] == 'file':
                name = item['name'].lower()
                if any(pattern.match(name) for pattern in doc_patterns):
                    content = await self._get_file_content(owner, repo, item['path'])
                    if content:
                        doc_files.append({
                            'path': item['path'],
                            'name': item['name'],
                            'content': content,
                            'type': self._get_file_type(item['name'])
                        })
        
        # Process directories
        for item in contents:
            if item['type'] == 'dir':
                name = item['name'].lower()
                if any(pattern.match(name) for pattern in doc_patterns):
                    # Recursively fetch directory contents
                    dir_files = await self._fetch_directory_contents(owner, repo, item['path'])
                    doc_files.extend(dir_files)
        
        return doc_files
    
    async def _get_file_content(self, owner: str, repo: str, path: str) -> Optional[str]:
        """Get content of a specific file from GitHub."""
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        timeout = aiohttp.ClientTimeout(total=3600)  # 60 minute timeout
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('content'):
                            import base64
                            return base64.b64decode(data['content']).decode('utf-8')
        except Exception as e:
            logger.warning(f"Could not fetch file {path}: {e}")
        
        return None
    
    async def _fetch_directory_contents(self, owner: str, repo: str, path: str) -> List[Dict[str, Any]]:
        """Recursively fetch contents of a directory."""
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        doc_files = []
        
        timeout = aiohttp.ClientTimeout(total=3600)  # 60 minute timeout
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                url = f'https://api.github.com/repos/{owner}/{repo}/contents/{path}'
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        contents = await response.json()
                        
                        for item in contents:
                            if item['type'] == 'file' and item['name'].endswith('.md'):
                                content = await self._get_file_content(owner, repo, item['path'])
                                if content:
                                    doc_files.append({
                                        'path': item['path'],
                                        'name': item['name'],
                                        'content': content,
                                        'type': self._get_file_type(item['name'])
                                    })
                            elif item['type'] == 'dir':
                                # Recursively fetch subdirectory contents
                                sub_files = await self._fetch_directory_contents(owner, repo, item['path'])
                                doc_files.extend(sub_files)
        except Exception as e:
            logger.warning(f"Could not fetch directory {path}: {e}")
        
        return doc_files
    
    def _get_file_type(self, filename: str) -> str:
        """Determine the type of documentation file."""
        name = filename.lower()
        
        if 'readme' in name:
            return 'readme'
        elif 'api' in name:
            return 'api'
        elif 'guide' in name or 'tutorial' in name:
            return 'guide'
        elif 'example' in name or 'demo' in name:
            return 'example'
        elif 'changelog' in name or 'history' in name:
            return 'changelog'
        elif 'contributing' in name:
            return 'contributing'
        elif 'license' in name:
            return 'license'
        elif 'install' in name or 'setup' in name:
            return 'installation'
        else:
            return 'documentation'
    
    async def _generate_repository_summary(self, repo_data: Dict[str, Any], doc_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate comprehensive repository summary."""
        repo_info = repo_data['repository']
        readme = repo_data['readme']
        
        # Basic repository information
        summary = {
            'name': repo_info['name'],
            'description': repo_info.get('description', ''),
            'url': repo_info['html_url'],
            'stars': repo_info['stargazers_count'],
            'forks': repo_info['forks_count'],
            'open_issues': repo_info['open_issues_count'],
            'created_at': repo_info['created_at'],
            'updated_at': repo_info['updated_at'],
            'license': repo_info.get('license', {}).get('name', ''),
            'homepage': repo_info.get('homepage', ''),
            'language': repo_info.get('language', ''),
            'topics': repo_info.get('topics', []),
            'documentation_files': len(doc_files),
            'documentation_types': list(set(doc['type'] for doc in doc_files))
        }
        
        # Generate enhanced summary using Claude AI if available
        if self.anthropic_api_key:
            try:
                enhanced_summary = await self._generate_enhanced_summary(repo_info, readme, doc_files)
                summary.update(enhanced_summary)
            except Exception as e:
                logger.warning(f"Could not generate enhanced summary: {e}")
        
        return summary
    
    async def _generate_enhanced_summary(self, repo_info: Dict[str, Any], readme: str, doc_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate enhanced summary using Claude AI."""
        # This would integrate with Claude AI to generate enhanced summaries
        # For now, we'll create a basic enhanced summary
        
        enhanced = {
            'overview': repo_info.get('description', ''),
            'key_features': [],
            'use_cases': [],
            'target_audience': 'Developers and users',
            'documentation_quality': 'Good' if len(doc_files) > 3 else 'Basic'
        }
        
        # Extract key features from README
        if readme:
            lines = readme.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('*'):
                    feature = line[1:].strip()
                    if feature and len(feature) < 100:
                        enhanced['key_features'].append(feature)
                        if len(enhanced['key_features']) >= 5:
                            break
        
        return enhanced
    
    async def _generate_enhanced_pages(self, output_dir: Path, doc_files: List[Dict[str, Any]], repo_data: Dict[str, Any], repo_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate enhanced content for each documentation page."""
        enhanced_pages = []
        
        for doc_file in doc_files:
            try:
                # Generate enhanced content
                enhanced_content = await self._generate_enhanced_content(
                    doc_file, repo_data, repo_summary
                )
                
                # Save enhanced page
                filename = self._sanitize_filename(doc_file['name'])
                page_path = output_dir / filename
                
                with open(page_path, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                
                enhanced_pages.append({
                    'original_path': doc_file['path'],
                    'filename': filename,
                    'type': doc_file['type'],
                    'title': self._get_title_from_content(enhanced_content)
                })
                
            except Exception as e:
                logger.warning(f"Could not enhance page {doc_file['path']}: {e}")
        
        return enhanced_pages
    
    async def _generate_enhanced_content(self, doc_file: Dict[str, Any], repo_data: Dict[str, Any], repo_summary: Dict[str, Any]) -> str:
        """Generate enhanced content for a documentation page."""
        original_content = doc_file['content']
        file_type = doc_file['type']
        
        # Create enhanced content with DeepWiki-style analysis
        enhanced_content = f"# {self._get_title_from_content(original_content)}\n\n"
        
        # Add repository context
        enhanced_content += f"## Repository Context\n\n"
        enhanced_content += f"- **Repository**: {repo_data['repository']['html_url']}\n"
        enhanced_content += f"- **File Type**: {file_type.title()}\n"
        enhanced_content += f"- **Original Path**: {doc_file['path']}\n\n"
        
        # Add enhanced summary
        enhanced_content += f"## Enhanced Summary\n\n"
        enhanced_content += f"This {file_type} document provides important information about the {repo_data['repository']['name']} project.\n\n"
        
        # Add original content
        enhanced_content += f"## Original Content\n\n"
        enhanced_content += original_content + "\n\n"
        
        # Add analysis and improvements
        enhanced_content += f"## Analysis and Improvements\n\n"
        enhanced_content += self._generate_analysis_section(doc_file, repo_data, repo_summary)
        
        return enhanced_content
    
    def _get_title_from_content(self, content: str) -> str:
        """Extract title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('## '):
                return line[3:].strip()
        return 'Documentation'
    
    def _generate_analysis_section(self, doc_file: Dict[str, Any], repo_data: Dict[str, Any], repo_summary: Dict[str, Any]) -> str:
        """Generate analysis section for enhanced content."""
        analysis = f"### Key Points\n\n"
        
        # Analyze content length and complexity
        content_length = len(doc_file['content'])
        if content_length > 5000:
            analysis += "- Comprehensive documentation with detailed information\n"
        elif content_length > 1000:
            analysis += "- Well-documented with good detail level\n"
        else:
            analysis += "- Brief documentation that could benefit from more detail\n"
        
        # Analyze content structure
        if '##' in doc_file['content']:
            analysis += "- Well-structured with clear sections\n"
        else:
            analysis += "- Could benefit from better section organization\n"
        
        # Analyze code examples
        if '```' in doc_file['content']:
            analysis += "- Includes code examples for better understanding\n"
        else:
            analysis += "- Could benefit from code examples\n"
        
        analysis += f"\n### Suggested Improvements\n\n"
        analysis += f"- Consider adding more detailed explanations\n"
        analysis += f"- Include practical examples and use cases\n"
        analysis += f"- Add links to related documentation\n"
        analysis += f"- Consider adding diagrams or visual aids\n"
        
        return analysis
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for cross-platform compatibility."""
        # Remove or replace invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Remove multiple underscores
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        return filename
    
    def _create_wiki_index(self, output_dir: Path, repo_data: Dict[str, Any], enhanced_pages: List[Dict[str, Any]], repo_summary: Dict[str, Any]):
        """Create wiki index file for navigation."""
        readme_content = f"# {repo_data['repository']['name']} Wiki\n\n"
        readme_content += f"## Repository Information\n\n"
        readme_content += f"- **GitHub URL**: {repo_data['repository']['html_url']}\n"
        readme_content += f"- **Description**: {repo_data['repository'].get('description', '')}\n"
        readme_content += f"- **Stars**: {repo_data['repository']['stargazers_count']}\n"
        readme_content += f"- **Forks**: {repo_data['repository']['forks_count']}\n"
        readme_content += f"- **Language**: {repo_data['repository'].get('language', 'N/A')}\n"
        readme_content += f"- **License**: {repo_data['repository'].get('license', {}).get('name', 'N/A')}\n"
        readme_content += f"- **Generated**: {self._get_timestamp_dir()}\n\n"
        
        readme_content += f"## Enhanced Documentation Pages\n\n"
        
        # Group pages by type
        pages_by_type = {}
        for page in enhanced_pages:
            page_type = page['type']
            if page_type not in pages_by_type:
                pages_by_type[page_type] = []
            pages_by_type[page_type].append(page)
        
        for page_type, pages in pages_by_type.items():
            readme_content += f"### {page_type.title()}\n\n"
            for page in pages:
                readme_content += f"- [{page['title']}]({page['filename']})\n"
            readme_content += "\n"
        
        readme_content += f"## Repository Summary\n\n"
        readme_content += f"- **Documentation Files**: {repo_summary['documentation_files']}\n"
        readme_content += f"- **Documentation Types**: {', '.join(repo_summary['documentation_types'])}\n"
        readme_content += f"- **Documentation Quality**: {repo_summary.get('documentation_quality', 'N/A')}\n\n"
        
        if repo_summary.get('key_features'):
            readme_content += f"### Key Features\n\n"
            for feature in repo_summary['key_features'][:5]:
                readme_content += f"- {feature}\n"
            readme_content += "\n"
        
        # Save README file
        readme_file = output_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def _save_wiki_metadata(self, output_dir: Path, repo_data: Dict[str, Any], repo_summary: Dict[str, Any]):
        """Save wiki metadata to JSON file."""
        metadata_file = output_dir / 'wiki_metadata.json'
        metadata = {
            'repository': repo_data['repository'],
            'summary': repo_summary,
            'generated_at': self._get_timestamp_dir()
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
