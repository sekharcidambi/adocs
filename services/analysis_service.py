#!/usr/bin/env python3
"""
Analysis Service - Handles repository analysis and documentation structure generation.
"""

import json
import os
import sys
import logging
import asyncio
import aiohttp
import ssl
from typing import Dict, Any, Optional, List
from pathlib import Path
import re
import tempfile
import shutil
import subprocess

# Add the src directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from .base_service import BaseService
from src.generator import DocStructureGenerator

logger = logging.getLogger(__name__)

class AnalysisService(BaseService):
    """Service for repository analysis and documentation structure generation."""
    
    def __init__(self, github_token: str = None, anthropic_api_key: str = None):
        """Initialize the Analysis Service."""
        super().__init__(github_token, anthropic_api_key)
        
        # Initialize the documentation generator
        self.knowledge_base_path = self.base_dir / 'knowledge_base.pkl'
        self.generator = None
    
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
            Dictionary with analysis results and documentation structure
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
            
            # Analyze repository structure
            logger.info("Analyzing repository structure")
            analysis = self._analyze_repository_structure(repo_data)
            
            # Generate documentation structure
            logger.info("Generating documentation structure")
            doc_structure = await self._generate_documentation_structure(analysis)
            
            # Create output directory
            repo_name = self._sanitize_repo_name(repo_url)
            output_dir = self._create_repo_directory(repo_name, 'docs')
            
            # Save documentation structure
            self._save_documentation_structure(output_dir, doc_structure)
            
            # Save repository metadata
            self._save_repository_metadata(output_dir, analysis)
            
            # Generate enhanced content for each section
            logger.info("Generating enhanced content for sections")
            try:
                enhanced_sections = await self._generate_enhanced_sections(
                    output_dir, doc_structure, analysis
                )
            except Exception as e:
                logger.error(f"Error generating enhanced sections: {e}")
                enhanced_sections = {}
            
            # Create index file
            self._create_index_file(output_dir, analysis, doc_structure)
            
            return {
                'success': True,
                'repository': repo_url,
                'output_directory': str(output_dir),
                'documentation_structure': doc_structure,
                'analysis': analysis,
                'enhanced_sections': enhanced_sections,
                'generated_at': self._get_timestamp_dir()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing repository: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _fetch_repository_data(self, owner: str, repo: str) -> Dict[str, Any]:
        """Clone repository and extract data using Git."""
        import tempfile
        import shutil
        import subprocess
        
        # Create temporary directory for cloning
        temp_dir = tempfile.mkdtemp()
        repo_path = os.path.join(temp_dir, repo)
        
        try:
            # Clone the repository
            repo_url = f'https://github.com/{owner}/{repo}.git'
            logger.info(f"Cloning repository: {repo_url}")
            
            result = subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, repo_path],
                capture_output=True,
                text=True,
                timeout=3600  # 60 minute timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"Failed to clone repository: {result.stderr}")
            
            # Extract repository information
            repo_data = self._extract_repo_info_from_git(repo_path, owner, repo)
            
            # Read README
            readme_content = self._read_readme(repo_path)
            
            # Get repository contents
            contents_data = self._get_repo_contents(repo_path)
            
            return {
                'repository': repo_data,
                'readme': readme_content,
                'contents': contents_data,
                'repo_path': repo_path  # Keep path for later use
            }
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            raise e
    
    def _extract_repo_info_from_git(self, repo_path: str, owner: str, repo: str) -> Dict[str, Any]:
        """Extract repository information from Git metadata."""
        import subprocess
        from datetime import datetime
        
        try:
            # Get basic git info
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H|%an|%ae|%ad', '--date=iso'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                commit_info = result.stdout.strip().split('|')
                last_commit = {
                    'sha': commit_info[0],
                    'author': commit_info[1],
                    'email': commit_info[2],
                    'date': commit_info[3]
                }
            else:
                last_commit = {}
            
            # Get remote URL
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=repo_path,
                capture_output=True,
                text=True
            )
            html_url = result.stdout.strip() if result.returncode == 0 else f'https://github.com/{owner}/{repo}'
            
            # Create repository data structure similar to GitHub API
            return {
                'name': repo,
                'full_name': f'{owner}/{repo}',
                'description': '',  # Will be extracted from README
                'html_url': html_url,
                'clone_url': f'https://github.com/{owner}/{repo}.git',
                'created_at': last_commit.get('date', ''),
                'updated_at': last_commit.get('date', ''),
                'stargazers_count': 0,  # Not available from git clone
                'forks_count': 0,       # Not available from git clone
                'open_issues_count': 0, # Not available from git clone
                'license': None,
                'topics': [],
                'language': None,  # Will be determined from file analysis
                'size': 0,
                'default_branch': 'main'
            }
            
        except Exception as e:
            logger.warning(f"Failed to extract git info: {e}")
            # Return basic info
            return {
                'name': repo,
                'full_name': f'{owner}/{repo}',
                'description': '',
                'html_url': f'https://github.com/{owner}/{repo}',
                'clone_url': f'https://github.com/{owner}/{repo}.git',
                'created_at': '',
                'updated_at': '',
                'stargazers_count': 0,
                'forks_count': 0,
                'open_issues_count': 0,
                'license': None,
                'topics': [],
                'language': None,
                'size': 0,
                'default_branch': 'main'
            }
    
    def _read_readme(self, repo_path: str) -> str:
        """Read README file from cloned repository."""
        readme_files = ['README.md', 'README.rst', 'README.txt', 'README', 'readme.md', 'readme.rst']
        
        for readme_file in readme_files:
            readme_path = os.path.join(repo_path, readme_file)
            if os.path.exists(readme_path):
                try:
                    with open(readme_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except Exception as e:
                    logger.warning(f"Failed to read {readme_file}: {e}")
                    continue
        
        return ''
    
    def _get_repo_contents(self, repo_path: str) -> List[Dict[str, Any]]:
        """Get repository contents by scanning the filesystem."""
        contents = []
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Skip hidden directories and common build/cache directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist', 'target']]
                
                for file in files:
                    if file.startswith('.'):
                        continue
                        
                    rel_path = os.path.relpath(os.path.join(root, file), repo_path)
                    file_path = os.path.join(root, file)
                    
                    try:
                        stat = os.stat(file_path)
                        contents.append({
                            'name': file,
                            'path': rel_path,
                            'type': 'file',
                            'size': stat.st_size,
                            'download_url': None  # Not applicable for local files
                        })
                    except Exception as e:
                        logger.warning(f"Failed to stat {file_path}: {e}")
                        
        except Exception as e:
            logger.warning(f"Failed to scan repository contents: {e}")
        
        return contents
    
    def _analyze_repository_structure(self, repo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze repository structure and extract metadata."""
        logger.info(f"Analyzing repository structure with data keys: {list(repo_data.keys())}")
        
        repo_info = repo_data.get('repository')
        contents = repo_data.get('contents', [])
        readme = repo_data.get('readme', '')
        
        if repo_info is None:
            logger.error("Repository info is None")
            raise Exception("Repository info is None")
        
        logger.info(f"Repository info: {repo_info.get('name', 'Unknown')}")
        
        # Analyze tech stack
        tech_stack = self._determine_tech_stack(contents)
        
        # Determine business domain
        business_domain = self._determine_business_domain(repo_info, readme)
        
        # Determine architecture pattern
        architecture = self._determine_architecture_pattern(contents, readme)
        
        # Generate overview
        overview = self._generate_overview(repo_info, readme, tech_stack)
        
        return {
            'github_url': repo_info.get('html_url', ''),
            'name': repo_info.get('name', 'Unknown'),
            'description': repo_info.get('description', ''),
            'overview': overview,
            'business_domain': business_domain,
            'tech_stack': tech_stack,
            'architecture': architecture,
            'readme': readme,
            'metadata': {
                'stars': repo_info.get('stargazers_count', 0),
                'forks': repo_info.get('forks_count', 0),
                'open_issues': repo_info.get('open_issues_count', 0),
                'created_at': repo_info.get('created_at', ''),
                'updated_at': repo_info.get('updated_at', ''),
                'license': repo_info.get('license', {}).get('name', '') if repo_info.get('license') else '',
                'homepage': repo_info.get('homepage', ''),
                'status': 'Active'
            }
        }
    
    def _determine_tech_stack(self, contents: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Determine technology stack from repository contents."""
        logger.info(f"Determining tech stack from {len(contents)} files")
        
        if contents and len(contents) > 0:
            logger.info(f"First few files: {[f.get('name', 'unknown') for f in contents[:5]]}")
        
        tech_stack = {
            'languages': [],
            'frontend': [],
            'backend': [],
            'databases': [],
            'devops': []
        }
        
        # Common file patterns and their associated technologies
        patterns = {
            'package.json': ['Node.js', 'JavaScript', 'npm'],
            'requirements.txt': ['Python'],
            'Pipfile': ['Python'],
            'pyproject.toml': ['Python'],
            'Cargo.toml': ['Rust'],
            'go.mod': ['Go'],
            'pom.xml': ['Java', 'Maven'],
            'build.gradle': ['Java', 'Gradle'],
            'Dockerfile': ['Docker'],
            'docker-compose.yml': ['Docker', 'Docker Compose'],
            'composer.json': ['PHP'],
            'Gemfile': ['Ruby'],
            'yarn.lock': ['Node.js', 'Yarn'],
            'package-lock.json': ['Node.js', 'npm'],
            'tsconfig.json': ['TypeScript'],
            'webpack.config.js': ['Webpack'],
            'vite.config.js': ['Vite'],
            'next.config.js': ['Next.js'],
            'nuxt.config.js': ['Nuxt.js'],
            'vue.config.js': ['Vue.js'],
            'angular.json': ['Angular'],
            'react': ['React'],
            'express': ['Express'],
            'fastapi': ['FastAPI'],
            'django': ['Django'],
            'flask': ['Flask'],
            'rails': ['Ruby on Rails'],
            'spring': ['Spring'],
            'laravel': ['Laravel'],
            'symfony': ['Symfony'],
            'postgresql': ['PostgreSQL'],
            'mysql': ['MySQL'],
            'mongodb': ['MongoDB'],
            'redis': ['Redis'],
            'elasticsearch': ['Elasticsearch'],
            'kafka': ['Apache Kafka'],
            'rabbitmq': ['RabbitMQ'],
            'nginx': ['Nginx'],
            'apache': ['Apache'],
            'kubernetes': ['Kubernetes'],
            'terraform': ['Terraform'],
            'ansible': ['Ansible'],
            'jenkins': ['Jenkins'],
            'github-actions': ['GitHub Actions'],
            'gitlab-ci': ['GitLab CI'],
            'travis': ['Travis CI'],
            'circleci': ['CircleCI']
        }
        
        # Scan contents for technology indicators
        for item in contents:
            name = item.get('name', '').lower()
            for pattern, techs in patterns.items():
                if pattern in name:
                    for tech in techs:
                        if tech not in tech_stack['languages'] and tech not in tech_stack['frontend'] and tech not in tech_stack['backend'] and tech not in tech_stack['databases'] and tech not in tech_stack['devops']:
                            # Categorize technology
                            if tech in ['JavaScript', 'TypeScript', 'Python', 'Java', 'Go', 'Rust', 'PHP', 'Ruby', 'C++', 'C#', 'Swift', 'Kotlin']:
                                tech_stack['languages'].append(tech)
                            elif tech in ['React', 'Vue.js', 'Angular', 'Next.js', 'Nuxt.js', 'Svelte', 'Webpack', 'Vite']:
                                tech_stack['frontend'].append(tech)
                            elif tech in ['Node.js', 'Express', 'FastAPI', 'Django', 'Flask', 'Ruby on Rails', 'Spring', 'Laravel', 'Symfony']:
                                tech_stack['backend'].append(tech)
                            elif tech in ['PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch', 'Apache Kafka', 'RabbitMQ']:
                                tech_stack['databases'].append(tech)
                            elif tech in ['Docker', 'Kubernetes', 'Terraform', 'Ansible', 'Jenkins', 'GitHub Actions', 'GitLab CI', 'Travis CI', 'CircleCI', 'Nginx', 'Apache']:
                                tech_stack['devops'].append(tech)
        
        return tech_stack
    
    def _determine_business_domain(self, repo_info: Dict[str, Any], readme: str) -> str:
        """Determine business domain from repository information."""
        if repo_info is None:
            logger.error("repo_info is None in _determine_business_domain")
            return "Unknown"
        
        logger.info(f"Determining business domain for {repo_info.get('name', 'Unknown')}")
        
        # Common business domains and their keywords
        domains = {
            'Web Development': ['web', 'website', 'frontend', 'backend', 'api', 'rest', 'graphql', 'spa', 'pwa'],
            'Mobile Development': ['mobile', 'ios', 'android', 'react-native', 'flutter', 'xamarin', 'cordova'],
            'Data Science': ['data', 'machine learning', 'ai', 'artificial intelligence', 'ml', 'deep learning', 'neural', 'tensorflow', 'pytorch'],
            'DevOps': ['devops', 'deployment', 'ci/cd', 'infrastructure', 'monitoring', 'logging', 'kubernetes', 'docker'],
            'Game Development': ['game', 'gaming', 'unity', 'unreal', 'opengl', 'directx', 'graphics'],
            'Blockchain': ['blockchain', 'cryptocurrency', 'bitcoin', 'ethereum', 'smart contract', 'defi', 'nft'],
            'IoT': ['iot', 'internet of things', 'embedded', 'arduino', 'raspberry pi', 'sensor'],
            'Security': ['security', 'cybersecurity', 'encryption', 'authentication', 'authorization', 'vulnerability'],
            'Developer Tools': ['tool', 'library', 'framework', 'sdk', 'cli', 'plugin', 'extension', 'utility'],
            'E-commerce': ['ecommerce', 'e-commerce', 'shopping', 'payment', 'cart', 'checkout', 'store'],
            'Education': ['education', 'learning', 'tutorial', 'course', 'training', 'academic'],
            'Healthcare': ['healthcare', 'medical', 'health', 'patient', 'hospital', 'clinical'],
            'Finance': ['finance', 'financial', 'banking', 'trading', 'investment', 'accounting'],
            'Productivity': ['productivity', 'collaboration', 'project management', 'task', 'workflow', 'automation']
        }
        
        # Combine repository description and README for analysis
        text = f"{repo_info.get('description', '')} {readme}".lower()
        
        # Count domain keyword matches
        domain_scores = {}
        for domain, keywords in domains.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                domain_scores[domain] = score
        
        # Return domain with highest score, or default
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        else:
            return 'Software Development'
    
    def _determine_architecture_pattern(self, contents: List[Dict[str, Any]], readme: str) -> Dict[str, str]:
        """Determine architecture pattern from repository structure."""
        logger.info("Determining architecture pattern")
        
        if readme is None:
            readme = ""
        
        text = readme.lower()
        
        # Architecture patterns and their indicators
        patterns = {
            'Microservices': ['microservice', 'microservices', 'service-oriented', 'soa'],
            'Monolithic': ['monolith', 'monolithic', 'single application'],
            'Component-based': ['component', 'components', 'modular', 'reusable'],
            'Layered': ['layer', 'layered', 'tier', 'presentation', 'business', 'data'],
            'Event-driven': ['event', 'events', 'event-driven', 'pub/sub', 'publish', 'subscribe'],
            'MVC': ['mvc', 'model-view-controller', 'controller', 'model', 'view'],
            'MVVM': ['mvvm', 'model-view-viewmodel', 'viewmodel'],
            'Serverless': ['serverless', 'lambda', 'function', 'faas'],
            'Client-Server': ['client-server', 'client server', 'client', 'server'],
            'Peer-to-Peer': ['peer-to-peer', 'p2p', 'distributed'],
            'Plugin': ['plugin', 'plugins', 'extensible', 'extension'],
            'Pipeline': ['pipeline', 'pipes', 'stream', 'processing']
        }
        
        # Find architecture pattern
        for pattern, indicators in patterns.items():
            if any(indicator in text for indicator in indicators):
                return {
                    'pattern': pattern,
                    'description': f'{pattern} architecture pattern'
                }
        
        # Default to component-based for most modern applications
        return {
            'pattern': 'Component-based',
            'description': 'Component-based architecture pattern'
        }
    
    def _generate_overview(self, repo_info: Dict[str, Any], readme: str, tech_stack: Dict[str, List[str]]) -> str:
        """Generate a comprehensive overview of the repository."""
        if repo_info is None:
            logger.error("repo_info is None in _generate_overview")
            return "Repository overview not available"
        
        name = repo_info.get('name', 'Unknown')
        description = repo_info.get('description', '')
        
        # Extract first paragraph from README
        readme_summary = ''
        if readme:
            lines = readme.split('\n')
            for line in lines:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('*') and not line.startswith('-'):
                    readme_summary = line
                    break
        
        # Combine information
        overview_parts = []
        if description:
            overview_parts.append(description)
        if readme_summary and readme_summary != description:
            overview_parts.append(readme_summary)
        
        # Add tech stack information
        all_techs = []
        for category, techs in tech_stack.items():
            all_techs.extend(techs)
        
        if all_techs:
            tech_summary = f"Built with {', '.join(all_techs[:5])}"
            if len(all_techs) > 5:
                tech_summary += f" and {len(all_techs) - 5} other technologies"
            overview_parts.append(tech_summary)
        
        return '. '.join(overview_parts) if overview_parts else f"{name} is a software project."
    
    async def _generate_documentation_structure(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate documentation structure using the ADocS generator."""
        try:
            self._initialize_generator()
            
            # Prepare metadata for the generator
            metadata = {
                'github_url': analysis['github_url'],
                'overview': analysis['overview'],
                'business_domain': analysis['business_domain'],
                'architecture': analysis['architecture'],
                'tech_stack': analysis['tech_stack']
            }
            
            # Generate documentation structure
            doc_structure = self.generator.generate(metadata, api_key=self.anthropic_api_key)
            
            if doc_structure is None:
                logger.warning("Generator returned None, using fallback structure")
                return self._create_fallback_documentation_structure(analysis)
            
            return doc_structure
            
        except Exception as e:
            logger.error(f"Failed to generate documentation structure: {e}")
            logger.info("Using fallback documentation structure")
            return self._create_fallback_documentation_structure(analysis)
    
    def _create_fallback_documentation_structure(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic documentation structure when the generator fails."""
        return {
            'sections': [
                {
                    'title': f"{analysis['name']} Overview",
                    'children': [
                        {'title': 'Purpose and Scope'},
                        {'title': 'Architecture Overview'},
                        {'title': 'Technology Stack'},
                        {'title': 'Getting Started'},
                        {'title': 'Key Features'},
                        {'title': 'Documentation'}
                    ]
                }
            ]
        }
    
    def _save_documentation_structure(self, output_dir: Path, doc_structure: Dict[str, Any]):
        """Save documentation structure to JSON file."""
        structure_file = output_dir / 'documentation_structure.json'
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(doc_structure, f, indent=2)
    
    def _save_repository_metadata(self, output_dir: Path, analysis: Dict[str, Any]):
        """Save repository metadata to JSON file."""
        metadata_file = output_dir / 'repository_metadata.json'
        metadata = {
            **analysis,
            'generated_at': self._get_timestamp_dir()
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
    
    async def _generate_enhanced_sections(self, output_dir: Path, doc_structure: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, str]:
        """Generate enhanced content for each documentation section using Claude AI."""
        enhanced_sections = {}
        
        sections = doc_structure.get('sections', [])
        
        logger.info(f"Generating enhanced content for {len(sections)} sections using Claude AI")
        logger.info(f"Sections type: {type(sections)}")
        if sections:
            logger.info(f"First section type: {type(sections[0])}")
            logger.info(f"First section: {sections[0]}")
        
        for i, section in enumerate(sections):
            logger.info(f"Processing section {i}: {section} (type: {type(section)})")
            try:
                if isinstance(section, dict):
                    section_title = section.get('title', '')
                    if section_title:
                        logger.info(f"Creating AI-enhanced content for section: {section_title}")
                        # Generate AI-enhanced content
                        content = await self._generate_ai_enhanced_content(section_title, section, analysis)
                        
                        # Save section file
                        filename = self._sanitize_filename(section_title) + '.md'
                        section_file = output_dir / filename
                        with open(section_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        enhanced_sections[section_title] = content
                        logger.info(f"Successfully created AI-enhanced section: {section_title}")
                    else:
                        logger.warning(f"Section {i} has no title: {section}")
                elif isinstance(section, str):
                    # Handle case where section is just a string
                    logger.info(f"Creating AI-enhanced content for string section: {section}")
                    content = await self._generate_ai_enhanced_content(section, {}, analysis)
                    
                    # Save section file
                    filename = self._sanitize_filename(section) + '.md'
                    section_file = output_dir / filename
                    with open(section_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    enhanced_sections[section] = content
                    logger.info(f"Successfully created AI-enhanced string section: {section}")
                else:
                    logger.warning(f"Skipping unsupported section type {type(section)}: {section}")
            except Exception as e:
                logger.error(f"Error processing section {i}: {e}")
                # Fallback to basic content
                try:
                    section_title = section.get('title', '') if isinstance(section, dict) else str(section)
                    content = self._create_basic_section_content(section_title, analysis)
                    enhanced_sections[section_title] = content
                    logger.info(f"Created fallback content for section: {section_title}")
                except Exception as fallback_error:
                    logger.error(f"Fallback content creation also failed: {fallback_error}")
                    continue
        
        return enhanced_sections
    
    async def _generate_ai_enhanced_content(self, section_title: str, section_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate AI-enhanced content for a documentation section using Claude."""
        try:
            # Configure Claude API
            import anthropic
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            # Create comprehensive prompt for the section
            prompt = self._create_section_prompt(section_title, section_data, analysis)
            
            # Use the working Claude model
            logger.info("Using claude-sonnet-4-20250514 for content generation")
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
                return response.content[0].text
            else:
                logger.warning(f"Empty response from Claude for section: {section_title}")
                return self._create_basic_section_content(section_title, analysis)
                
        except Exception as e:
            logger.error(f"Error generating AI content for section {section_title}: {e}")
            return self._create_basic_section_content(section_title, analysis)
    
    def _create_section_prompt(self, section_title: str, section_data: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Create a comprehensive prompt for generating section content."""
        
        # Extract subsections if available
        subsections = []
        if isinstance(section_data, dict) and 'children' in section_data:
            for child in section_data.get('children', []):
                if isinstance(child, dict) and 'title' in child:
                    subsections.append(child['title'])
        
        # Build tech stack summary
        tech_stack_summary = ""
        tech_stack = analysis.get('tech_stack', {})
        if tech_stack:
            all_techs = []
            for category, techs in tech_stack.items():
                if techs:
                    all_techs.extend(techs)
            tech_stack_summary = ", ".join(all_techs[:10])  # Limit to first 10 technologies
        
        # Get architecture pattern
        architecture = analysis.get('architecture', {})
        arch_pattern = architecture.get('pattern', 'Unknown') if isinstance(architecture, dict) else 'Unknown'
        
        prompt = f"""You are a senior technical writer creating comprehensive documentation for a software project. Generate detailed, professional documentation for the "{section_title}" section.

## Project Context:
- **Repository**: {analysis.get('name', 'Unknown')} ({analysis.get('github_url', 'Unknown')})
- **Business Domain**: {analysis.get('business_domain', 'Unknown')}
- **Architecture Pattern**: {arch_pattern}
- **Technology Stack**: {tech_stack_summary}
- **Project Overview**: {analysis.get('overview', 'No overview available')}

## Section Requirements:
- **Section Title**: {section_title}
- **Subsections to Cover**: {', '.join(subsections) if subsections else 'None specified'}

## Content Guidelines:
1. **Comprehensive Coverage**: Provide detailed, in-depth information about the section topic
2. **Technical Accuracy**: Include specific technical details, patterns, and best practices
3. **Practical Examples**: Include code examples, configuration snippets, or usage patterns where relevant
4. **Professional Structure**: Use clear headings, bullet points, and organized sections
5. **Context-Aware**: Tailor content to the specific technology stack and architecture
6. **Actionable Information**: Provide practical guidance that developers can follow

## Output Format:
- Use Markdown formatting
- Start with a clear section title (# {section_title})
- Include multiple subsections with detailed content
- Use code blocks for examples
- Include bullet points and numbered lists for clarity
- End with relevant links or references if applicable

## Content Depth:
- Aim for 1000-2000 words of substantive content
- Cover theoretical concepts, practical implementation, and real-world considerations
- Include troubleshooting tips, best practices, and common pitfalls
- Provide comprehensive coverage that would be valuable for both beginners and experienced developers

Generate comprehensive, professional documentation that would be suitable for a technical documentation website."""

        return prompt
    
    def _create_basic_section_content(self, section_title: str, analysis: Dict[str, Any]) -> str:
        """Create basic fallback content for a documentation section."""
        content = f"# {section_title}\n\n"
        
        # Add repository-specific information
        content += f"## Repository Information\n\n"
        content += f"- **Repository**: {analysis.get('github_url', 'Unknown')}\n"
        content += f"- **Business Domain**: {analysis.get('business_domain', 'Unknown')}\n"
        
        # Handle architecture - it might be a dict or list
        architecture = analysis.get('architecture', {})
        if isinstance(architecture, dict):
            arch_pattern = architecture.get('pattern', 'Unknown')
        else:
            arch_pattern = 'Unknown'
        content += f"- **Architecture**: {arch_pattern}\n\n"
        
        # Add tech stack information
        tech_stack = analysis.get('tech_stack', {})
        if tech_stack:
            content += f"## Technology Stack\n\n"
            for category, techs in tech_stack.items():
                if techs:
                    content += f"### {category.title()}\n"
                    for tech in techs:
                        content += f"- {tech}\n"
                    content += "\n"
        
        # Add section-specific content
        content += f"## {section_title}\n\n"
        content += f"This section provides detailed information about {section_title.lower()} for the {analysis['name']} project.\n\n"
        content += f"### Overview\n\n"
        content += f"{analysis['overview']}\n\n"
        
        return content
    
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
    
    def _create_index_file(self, output_dir: Path, analysis: Dict[str, Any], doc_structure: Dict[str, Any]):
        """Create README index file for navigation."""
        readme_content = f"# {analysis['name']} Documentation\n\n"
        readme_content += f"## Repository Information\n\n"
        readme_content += f"- **GitHub URL**: {analysis['github_url']}\n"
        readme_content += f"- **Description**: {analysis['description']}\n"
        readme_content += f"- **Business Domain**: {analysis['business_domain']}\n"
        readme_content += f"- **Architecture**: {analysis['architecture']['pattern']}\n"
        readme_content += f"- **Generated**: {self._get_timestamp_dir()}\n\n"
        
        readme_content += f"## Documentation Sections\n\n"
        
        sections = doc_structure.get('sections', [])
        for section in sections:
            section_title = section.get('title', '')
            if section_title:
                filename = self._sanitize_filename(section_title) + '.md'
                readme_content += f"- [{section_title}]({filename})\n"
        
        readme_content += f"\n## Technology Stack\n\n"
        
        if analysis['tech_stack']:
            for category, techs in analysis['tech_stack'].items():
                if techs:
                    readme_content += f"### {category.title()}\n"
                    for tech in techs:
                        readme_content += f"- {tech}\n"
                    readme_content += "\n"
        
        # Save README file
        readme_file = output_dir / 'README.md'
        with open(readme_file, 'w', encoding='utf-8') as f:
            readme_file.write_text(readme_content)
