#!/usr/bin/env python3
"""
Comprehensive ADocS Service - Complete repository analysis and documentation generation.
This service handles the full workflow from GitHub URL to enhanced documentation.
"""

import json
import sys
import os
import logging
import re
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import tempfile
import shutil

# Add the src directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import DocStructureGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveADocSService:
    """Comprehensive service for complete repository analysis and documentation generation."""
    
    def __init__(self, knowledge_base_path: str = None, output_dir: str = None, github_token: str = None, anthropic_api_key: str = None):
        """
        Initialize the Comprehensive ADocS service.
        
        Args:
            knowledge_base_path: Path to the knowledge base pickle file
            output_dir: Directory to store generated documentation files
            github_token: GitHub API token for repository access
            anthropic_api_key: Anthropic API key for content generation
        """
        if knowledge_base_path is None:
            knowledge_base_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.pkl')
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), 'generated_docs')
        
        self.knowledge_base_path = knowledge_base_path
        self.output_dir = Path(output_dir)
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.generator = None
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Comprehensive ADocS Service initialized")
        logger.info(f"Knowledge base: {knowledge_base_path}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def _initialize_generator(self):
        """Initialize the DocStructureGenerator if not already done."""
        if self.generator is None:
            try:
                self.generator = DocStructureGenerator(self.knowledge_base_path)
                logger.info("DocStructureGenerator initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DocStructureGenerator: {e}")
                raise
    
    async def _fetch_github_data(self, owner: str, repo: str) -> Dict[str, Any]:
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
    
    def _analyze_repository_structure(self, repo_data: Dict[str, Any], contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze repository structure and determine tech stack, architecture, etc."""
        analysis = {
            'github_repo': repo_data['html_url'],
            'business_domain': '',
            'overview': repo_data.get('description', ''),
            'tech_stack': {
                'languages': [],
                'frontend': [],
                'backend': [],
                'databases': [],
                'devops': [],
            },
            'architecture': {
                'pattern': '',
                'description': '',
            },
            'setup': {
                'install': '',
                'run': '',
                'test': '',
            },
            'metadata': {
                'stars': repo_data['stargazers_count'],
                'forks': repo_data['forks_count'],
                'license': repo_data.get('license', {}).get('name', 'Unknown') if repo_data.get('license') else 'Unknown',
                'status': 'Archived' if repo_data.get('archived') else 'Active',
            },
            'summary': '',
        }
        
        # Analyze files to determine tech stack
        file_analysis = self._analyze_files(contents)
        analysis.update(file_analysis)
        
        # Determine business domain
        analysis['business_domain'] = self._determine_business_domain(repo_data['name'], repo_data.get('description', ''))
        
        # Determine architecture pattern
        analysis['architecture'] = self._determine_architecture_pattern(analysis['tech_stack'])
        
        return analysis
    
    def _analyze_files(self, contents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze repository files to determine technology stack."""
        tech_stack = {
            'languages': [],
            'frontend': [],
            'backend': [],
            'databases': [],
            'devops': [],
        }
        setup_commands = {
            'install': '',
            'run': '',
            'test': '',
        }
        
        # Check for common configuration files
        file_names = [item['name'] for item in contents if item['type'] == 'file']
        
        # Node.js/JavaScript projects
        if 'package.json' in file_names:
            tech_stack['languages'].extend(['JavaScript', 'TypeScript'])
            # We would need to fetch and parse package.json for detailed analysis
            setup_commands['install'] = 'npm install'
            setup_commands['run'] = 'npm start'
            setup_commands['test'] = 'npm test'
        
        # Python projects
        if 'requirements.txt' in file_names or 'pyproject.toml' in file_names or 'setup.py' in file_names:
            tech_stack['languages'].append('Python')
            setup_commands['install'] = 'pip install -r requirements.txt'
            setup_commands['run'] = 'python app.py'
            setup_commands['test'] = 'python -m pytest'
        
        # Java projects
        if 'pom.xml' in file_names:
            tech_stack['languages'].append('Java')
            tech_stack['backend'].append('Maven')
            setup_commands['install'] = 'mvn clean install'
            setup_commands['run'] = 'mvn spring-boot:run'
            setup_commands['test'] = 'mvn test'
        
        if 'build.gradle' in file_names:
            tech_stack['languages'].extend(['Java', 'Kotlin'])
            tech_stack['backend'].append('Gradle')
            setup_commands['install'] = './gradlew build'
            setup_commands['run'] = './gradlew bootRun'
            setup_commands['test'] = './gradlew test'
        
        # Docker
        if 'Dockerfile' in file_names:
            tech_stack['devops'].append('Docker')
            setup_commands['install'] = 'docker build -t app .'
            setup_commands['run'] = 'docker run -p 3000:3000 app'
        
        if 'docker-compose.yml' in file_names or 'docker-compose.yaml' in file_names:
            tech_stack['devops'].append('Docker Compose')
            setup_commands['run'] = 'docker-compose up'
        
        # Frontend frameworks (based on common patterns)
        if any('react' in name.lower() for name in file_names):
            tech_stack['frontend'].append('React')
        if any('vue' in name.lower() for name in file_names):
            tech_stack['frontend'].append('Vue.js')
        if any('angular' in name.lower() for name in file_names):
            tech_stack['frontend'].append('Angular')
        
        return {
            'tech_stack': tech_stack,
            'setup': setup_commands
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
        elif any(keyword in description_lower for keyword in ['e-commerce', 'shopping', 'store']):
            return 'E-Commerce'
        elif any(keyword in description_lower for keyword in ['crm', 'customer', 'management']):
            return 'Customer Relationship Management'
        elif any(keyword in description_lower for keyword in ['erp', 'enterprise', 'business']):
            return 'Enterprise Resource Planning'
        else:
            return 'Software Development'
    
    def _determine_architecture_pattern(self, tech_stack: Dict[str, List[str]]) -> Dict[str, str]:
        """Determine architecture pattern based on technology stack."""
        if 'Docker' in tech_stack['devops'] or 'Docker Compose' in tech_stack['devops']:
            return {
                'pattern': 'Containerized',
                'description': 'Application containerized with Docker'
            }
        elif tech_stack['frontend'] and tech_stack['backend']:
            return {
                'pattern': 'Full-Stack',
                'description': 'Full-stack application with separate frontend and backend'
            }
        elif tech_stack['backend']:
            return {
                'pattern': 'Backend Service',
                'description': 'Backend service or API'
            }
        elif tech_stack['frontend']:
            return {
                'pattern': 'Frontend Application',
                'description': 'Frontend application or UI component'
            }
        else:
            return {
                'pattern': 'Library/Utility',
                'description': f"A library/utility built with {', '.join(tech_stack['languages'])}"
            }
    
    async def _generate_repository_summary(self, repo_analysis: Dict[str, Any]) -> str:
        """Generate repository summary using Claude AI."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            prompt = f"""Analyze this repository and provide a brief summary:

Repository: {repo_analysis['github_repo']}
Description: {repo_analysis['overview']}
Languages: {', '.join(repo_analysis['tech_stack']['languages'])}
Architecture: {repo_analysis['architecture']['pattern']}
Business Domain: {repo_analysis['business_domain']}

Provide a 2-3 sentence summary of what this repository does and its main purpose."""

            response = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=200,
                temperature=0.3,
                messages=[{'role': 'user', 'content': prompt}]
            )

            if response.content[0].type == 'text':
                return response.content[0].text
        except Exception as e:
            logger.warning(f"Failed to generate repository summary: {e}")
        
        return f"{repo_analysis['github_repo']} is a {repo_analysis['business_domain'].lower()} project."
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = '_'.join(filter(None, filename.split('_')))
        return filename.strip()
    
    def _create_repo_directory(self, repo_metadata: Dict[str, Any]) -> Path:
        """Create a directory for the repository documentation."""
        github_url = repo_metadata.get('github_repo', 'unknown')
        if 'github.com/' in github_url:
            parts = github_url.split('github.com/')[-1].rstrip('/')
            owner, repo = parts.split('/')[:2]
            repo_name = f"{owner}_{repo}"
        else:
            repo_name = "unknown_repo"
        
        safe_repo_name = self._sanitize_filename(repo_name)
        repo_dir = self.output_dir / safe_repo_name
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        versioned_dir = repo_dir / timestamp
        versioned_dir.mkdir(parents=True, exist_ok=True)
        
        return versioned_dir
    
    async def _generate_enhanced_content(self, section_title: str, repo_analysis: Dict[str, Any], readme_content: str) -> str:
        """Generate enhanced content for a documentation section using Claude AI."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            # Build comprehensive context
            context = f"""
REPOSITORY: {repo_analysis['github_repo']}
DESCRIPTION: {repo_analysis['overview']}
BUSINESS DOMAIN: {repo_analysis['business_domain']}

TECHNOLOGY STACK:
- Languages: {', '.join(repo_analysis['tech_stack']['languages'])}
- Frontend: {', '.join(repo_analysis['tech_stack']['frontend'])}
- Backend: {', '.join(repo_analysis['tech_stack']['backend'])}
- Databases: {', '.join(repo_analysis['tech_stack']['databases'])}
- DevOps: {', '.join(repo_analysis['tech_stack']['devops'])}

ARCHITECTURE:
- Pattern: {repo_analysis['architecture']['pattern']}
- Description: {repo_analysis['architecture']['description']}

SETUP COMMANDS:
- Install: {repo_analysis['setup']['install']}
- Run: {repo_analysis['setup']['run']}
- Test: {repo_analysis['setup']['test']}

REPOSITORY METADATA:
- Stars: {repo_analysis['metadata']['stars']}
- Forks: {repo_analysis['metadata']['forks']}
- License: {repo_analysis['metadata']['license']}
- Status: {repo_analysis['metadata']['status']}

README CONTENT:
{readme_content}
"""

            prompt = f"""You are creating comprehensive, detailed documentation for a specific GitHub repository section.

CRITICAL INSTRUCTIONS:
- Generate EXTENSIVE, DESCRIPTIVE content SPECIFIC to the actual repository described below
- Create detailed narratives with 3-5 paragraphs minimum per section
- Use ONLY the information provided about this specific repository
- Do NOT use generic knowledge or information about similar projects
- Base your content on the actual technology stack, architecture, and setup commands provided
- Reference the actual README content when relevant
- If information is missing or "Not specified", acknowledge this limitation
- Be specific about the actual implementation, not theoretical concepts
- Write in a professional, technical documentation style
- Include specific details about how THIS repository implements concepts

REPOSITORY CONTEXT:
{context}

TASK: Create comprehensive, detailed content for the section "{section_title}".

REQUIREMENTS FOR CONTENT:
- Write 3-5 detailed paragraphs (minimum 200-300 words per section)
- Provide specific, actionable content tailored to THIS repository
- Include detailed explanations of how this specific repository implements the concepts
- Reference the actual setup commands, architecture patterns, and technology stack
- Explain the business context and technical decisions specific to this project
- Include practical examples based on the actual technology stack used
- Mention specific implementation details, configurations, or patterns used
- Discuss any unique aspects or considerations specific to this implementation
- Use professional technical writing with clear explanations
- Include subsections with headers for better organization
- Provide context about why certain technologies or patterns were chosen for this specific project

Format the response as detailed markdown with proper headers, bullet points, and code blocks where appropriate."""

            response = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=3000,
                temperature=0.1,
                messages=[{'role': 'user', 'content': prompt}]
            )

            if response.content[0].type == 'text':
                return response.content[0].text
        except Exception as e:
            logger.warning(f"Failed to generate enhanced content for '{section_title}': {e}")
        
        return f"# {section_title}\n\nContent for {section_title} section."
    
    def _save_documentation_structure(self, doc_structure: Dict[str, Any], repo_dir: Path) -> str:
        """Save the documentation structure as JSON."""
        structure_file = repo_dir / "documentation_structure.json"
        
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(doc_structure, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Documentation structure saved to: {structure_file}")
        return str(structure_file)
    
    def _save_metadata(self, repo_analysis: Dict[str, Any], repo_dir: Path) -> str:
        """Save the repository analysis as JSON."""
        metadata_file = repo_dir / "repository_metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(repo_analysis, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Repository metadata saved to: {metadata_file}")
        return str(metadata_file)
    
    async def _generate_and_save_enhanced_pages(self, doc_structure: Dict[str, Any], repo_analysis: Dict[str, Any], readme_content: str, repo_dir: Path) -> List[str]:
        """Generate and save enhanced content for all documentation sections."""
        saved_files = []
        
        # Handle ADocS format: array with root object containing children
        if isinstance(doc_structure, list) and len(doc_structure) > 0:
            root_item = doc_structure[0]
            
            async def process_sections(items: List[Dict[str, Any]], parent_path: str = '', parent_title: str = ''):
                for item in items:
                    item_path = parent_path if parent_path else item['title'].lower().replace(' ', '-')
                    section_title = f"{parent_title} > {item['title']}" if parent_title else item['title']
                    
                    try:
                        logger.info(f"🔄 Generating content for: {section_title}")
                        
                        enhanced_content = await self._generate_enhanced_content(
                            item['title'], 
                            repo_analysis, 
                            readme_content
                        )
                        
                        # Save markdown file
                        safe_filename = self._sanitize_filename(item['title'])
                        markdown_file = repo_dir / f"{safe_filename}.md"
                        
                        with open(markdown_file, 'w', encoding='utf-8') as f:
                            f.write(enhanced_content)
                        
                        saved_files.append(str(markdown_file))
                        logger.info(f"✅ Generated content for: {section_title}")
                        
                        # Add delay to prevent rate limiting
                        await asyncio.sleep(0.5)
                        
                    except Exception as error:
                        logger.error(f"❌ Failed to generate content for {section_title}: {error}")
                    
                    # Recursively process nested children
                    if 'children' in item and isinstance(item['children'], list):
                        await process_sections(item['children'], item_path, section_title)
            
            if 'children' in root_item and isinstance(root_item['children'], list):
                await process_sections(root_item['children'])
        
        return saved_files
    
    def _create_index_file(self, repo_analysis: Dict[str, Any], doc_structure: Dict[str, Any], repo_dir: Path, saved_files: List[str]) -> str:
        """Create an index markdown file for the documentation."""
        index_file = repo_dir / "README.md"
        
        github_url = repo_analysis.get('github_repo', 'Unknown')
        repo_name = github_url.split('/')[-1] if '/' in github_url else 'Unknown Repository'
        
        index_content = f"""# {repo_name} Documentation

This directory contains AI-generated comprehensive documentation for the repository: **{github_url}**

## Repository Overview

- **Description**: {repo_analysis.get('overview', 'No description available')}
- **Business Domain**: {repo_analysis.get('business_domain', 'Not specified')}
- **Architecture Pattern**: {repo_analysis.get('architecture', {}).get('pattern', 'Not specified')}
- **Stars**: {repo_analysis.get('metadata', {}).get('stars', 0)}
- **Forks**: {repo_analysis.get('metadata', {}).get('forks', 0)}
- **License**: {repo_analysis.get('metadata', {}).get('license', 'Unknown')}
- **Status**: {repo_analysis.get('metadata', {}).get('status', 'Unknown')}

## Technology Stack

"""
        
        tech_stack = repo_analysis.get('tech_stack', {})
        for category, technologies in tech_stack.items():
            if technologies:
                index_content += f"- **{category.title()}**: {', '.join(technologies)}\n"
        
        index_content += f"""
## Setup Commands

- **Install**: `{repo_analysis.get('setup', {}).get('install', 'Not specified')}`
- **Run**: `{repo_analysis.get('setup', {}).get('run', 'Not specified')}`
- **Test**: `{repo_analysis.get('setup', {}).get('test', 'Not specified')}`

## Generated Documentation

"""
        
        # Add links to all markdown files
        for file_path in saved_files:
            filename = Path(file_path).name
            if filename != "README.md":
                section_name = filename.replace('.md', '').replace('_', ' ')
                index_content += f"- [{section_name}](./{filename})\n"
        
        index_content += f"""
## Generated Files

- `documentation_structure.json` - Complete documentation structure
- `repository_metadata.json` - Repository metadata and analysis

## Usage

This documentation was generated using the Comprehensive ADocS system. Each markdown file contains detailed information about a specific aspect of the repository.

For the most up-to-date information, please refer to the original repository: {github_url}

---
*Generated by Comprehensive ADocS on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        logger.info(f"Index file created: {index_file}")
        return str(index_file)
    
    def _build_navigation_structure(self, doc_structure: Dict[str, Any], saved_files: List[str]) -> List[Dict[str, Any]]:
        """Build navigation structure for the frontend."""
        navigation = []
        
        if isinstance(doc_structure, list) and len(doc_structure) > 0:
            root_item = doc_structure[0]
            
            def build_hierarchy(items: List[Dict[str, Any]], parent_path: str = '', parent_title: str = '') -> List[Dict[str, Any]]:
                result = []
                for item in items:
                    item_path = parent_path if parent_path else item['title'].lower().replace(' ', '-')
                    section_title = f"{parent_title} > {item['title']}" if parent_title else item['title']
                    
                    # Find corresponding file
                    safe_filename = self._sanitize_filename(item['title'])
                    corresponding_file = next((f for f in saved_files if f.endswith(f"{safe_filename}.md")), None)
                    
                    child_item = {
                        'title': item['title'],
                        'path': item_path,
                        'type': 'docs',
                        'hasContent': bool(corresponding_file),
                        'content': None  # Content will be loaded by frontend as needed
                    }
                    
                    # Add children if they exist
                    if 'children' in item and isinstance(item['children'], list):
                        child_item['children'] = build_hierarchy(item['children'], item_path, section_title)
                    
                    result.append(child_item)
                return result
            
            if 'children' in root_item and isinstance(root_item['children'], list):
                navigation = build_hierarchy(root_item['children'])
        
        return navigation
    
    async def analyze_and_generate_documentation(self, github_url: str) -> Dict[str, Any]:
        """
        Complete workflow: analyze repository and generate comprehensive documentation.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Dictionary with analysis results, documentation structure, and file paths
        """
        try:
            # Parse GitHub URL
            url_match = re.match(r'github\.com/([^/]+)/([^/]+)', github_url)
            if not url_match:
                raise ValueError('Invalid GitHub URL')
            
            owner, repo = url_match.groups()
            logger.info(f"Analyzing repository: {owner}/{repo}")
            
            # Initialize generator
            self._initialize_generator()
            
            # Fetch GitHub data
            github_data = await self._fetch_github_data(owner, repo)
            
            # Analyze repository structure
            repo_analysis = self._analyze_repository_structure(
                github_data['repository'], 
                github_data['contents']
            )
            
            # Generate repository summary
            repo_analysis['summary'] = await self._generate_repository_summary(repo_analysis)
            
            # Create repository directory
            repo_dir = self._create_repo_directory(repo_analysis)
            
            # Save repository metadata
            metadata_file = self._save_metadata(repo_analysis, repo_dir)
            
            # Generate documentation structure using ADocS
            doc_structure = self.generator.generate(repo_analysis, api_key=self.anthropic_api_key)
            
            # Save documentation structure
            structure_file = self._save_documentation_structure(doc_structure, repo_dir)
            
            # Generate and save enhanced content
            saved_files = await self._generate_and_save_enhanced_pages(
                doc_structure, 
                repo_analysis, 
                github_data['readme'], 
                repo_dir
            )
            
            # Create index file
            index_file = self._create_index_file(repo_analysis, doc_structure, repo_dir, saved_files)
            
            # Build navigation structure
            navigation = self._build_navigation_structure(doc_structure, saved_files)
            
            result = {
                "success": True,
                "repository": {
                    "name": github_data['repository']['name'],
                    "description": github_data['repository'].get('description', ''),
                    "owner": github_data['repository']['owner']['login'],
                    "stars": github_data['repository']['stargazers_count'],
                    "language": github_data['repository'].get('language', ''),
                    "topics": github_data['repository'].get('topics', []),
                    "createdAt": github_data['repository']['created_at'],
                    "updatedAt": github_data['repository']['updated_at'],
                    # Enhanced metadata from analysis
                    "businessDomain": repo_analysis['business_domain'],
                    "techStack": repo_analysis['tech_stack'],
                    "architecture": repo_analysis['architecture'],
                    "setup": repo_analysis['setup'],
                    "metadata": repo_analysis['metadata'],
                    "summary": repo_analysis['summary'],
                },
                "documentationStructure": doc_structure,
                "navigation": navigation,
                "generatedFiles": {
                    "hasMarkdownFiles": True,
                    "repository": f"{owner}/{repo}",
                    "outputDirectory": str(repo_dir),
                    "files": {
                        "metadata": metadata_file,
                        "structure": structure_file,
                        "index": index_file,
                        "markdownFiles": saved_files
                    },
                    "note": "Documentation has been saved as markdown files in the ADocS generated_docs directory"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Documentation generation completed successfully. Files saved to: {repo_dir}")
            return result
            
        except Exception as e:
            logger.error(f"Error in complete analysis workflow: {e}")
            raise

def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python comprehensive_adocs_service.py <command> [args...]")
        print("Commands:")
        print("  analyze <github_url> - Complete repository analysis and documentation generation")
        print("  stats - Get knowledge base statistics")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "analyze":
            if len(sys.argv) < 3:
                print("Error: analyze command requires GitHub URL")
                sys.exit(1)
            
            github_url = sys.argv[2]
            
            # Create service instance - API keys are handled internally via environment variables
            service = ComprehensiveADocSService()
            
            # Run the complete analysis
            async def run_analysis():
                return await service.analyze_and_generate_documentation(github_url)
            
            result = asyncio.run(run_analysis())
            
            # Output result as JSON
            print(json.dumps(result, indent=2))
            
        elif command == "stats":
            service = ComprehensiveADocSService()
            service._initialize_generator()
            stats = service.generator.get_knowledge_base_stats()
            print(json.dumps(stats, indent=2))
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
