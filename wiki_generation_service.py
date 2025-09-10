#!/usr/bin/env python3
"""
Wiki Generation Service - Comprehensive document discovery and enhancement for existing documentation.
This service handles the complete workflow from GitHub URL to enhanced wiki-style documentation.
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
import tempfile
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WikiGenerationService:
    """Service for generating enhanced wiki-style documentation from existing repository documentation."""
    
    def __init__(self, github_token: str = None, anthropic_api_key: str = None, output_dir: str = None):
        """
        Initialize the Wiki Generation service.
        
        Args:
            github_token: GitHub API token for repository access
            anthropic_api_key: Anthropic API key for content generation
            output_dir: Directory to store generated documentation files
        """
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), 'generated_wiki_docs')
        
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.anthropic_api_key = anthropic_api_key or os.getenv('ANTHROPIC_API_KEY')
        self.output_dir = Path(output_dir)
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Wiki Generation Service initialized")
        logger.info(f"Output directory: {self.output_dir}")
    
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
    
    async def _find_documentation_files(self, owner: str, repo: str, contents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find and fetch documentation files recursively."""
        doc_files = []
        doc_patterns = [
            re.compile(r'^readme\.md$', re.IGNORECASE),
            re.compile(r'^docs?/', re.IGNORECASE),
            re.compile(r'\.md$', re.IGNORECASE),
            re.compile(r'^documentation/', re.IGNORECASE),
            re.compile(r'^guide/', re.IGNORECASE),
            re.compile(r'^tutorial/', re.IGNORECASE),
            re.compile(r'^examples?/', re.IGNORECASE),
        ]
        
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        timeout = aiohttp.ClientTimeout(total=3600)  # 60 minute timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            for item in contents:
                if item['type'] == 'file':
                    if any(pattern.search(item['path']) for pattern in doc_patterns):
                        doc_files.append(item)
                elif item['type'] == 'dir':
                    # Recursively search directories
                    try:
                        contents_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{item["path"]}'
                        async with session.get(contents_url, headers=headers) as response:
                            if response.status == 200:
                                sub_contents = await response.json()
                                sub_files = await self._find_documentation_files(owner, repo, sub_contents)
                                doc_files.extend(sub_files)
                    except Exception as e:
                        logger.warning(f"Error accessing directory {item['path']}: {e}")
        
        return doc_files
    
    async def _fetch_file_content(self, owner: str, repo: str, file_path: str) -> str:
        """Fetch content of a specific file from GitHub."""
        headers = {}
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        timeout = aiohttp.ClientTimeout(total=3600)  # 60 minute timeout
        async with aiohttp.ClientSession(timeout=timeout) as session:
            file_url = f'https://api.github.com/repos/{owner}/{repo}/contents/{file_path}'
            async with session.get(file_url, headers=headers) as response:
                if response.status == 200:
                    file_data = await response.json()
                    import base64
                    return base64.b64decode(file_data['content']).decode('utf-8')
                else:
                    raise Exception(f"Failed to fetch file {file_path}: {response.status}")
    
    def _get_title_from_path(self, path: str) -> str:
        """Extract title from file path."""
        filename = path.split('/')[-1]
        name_without_ext = filename.replace('.md', '').replace('.txt', '').replace('.rst', '')
        
        # Convert kebab-case or snake_case to Title Case
        return name_without_ext.replace('-', ' ').replace('_', ' ').title()
    
    def _get_file_type(self, path: str) -> str:
        """Determine file type based on path."""
        lower_path = path.lower()
        
        if 'readme' in lower_path:
            return 'readme'
        elif 'docs' in lower_path or 'documentation' in lower_path:
            return 'docs'
        elif 'example' in lower_path or 'demo' in lower_path:
            return 'code'
        else:
            return 'other'
    
    async def _generate_repository_summary(self, repo_data: Dict[str, Any], pages: List[Dict[str, Any]]) -> str:
        """Generate repository summary using Claude AI."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            page_titles = [p['title'] for p in pages]
            
            prompt = f"""You are analyzing a GitHub repository to create a comprehensive technical deep dive summary similar to DeepWiki's analysis style.

Repository Information:
- Name: {repo_data['name']}
- Description: {repo_data.get('description', 'No description provided')}
- Language: {repo_data.get('language', 'Not specified')}
- Stars: {repo_data['stargazers_count']}
- Topics: {', '.join(repo_data.get('topics', [])) or 'None'}
- Documentation Pages: {', '.join(page_titles)}

Please provide a comprehensive technical analysis summary (4-5 paragraphs) that covers:
1. **Executive Overview**: High-level project purpose, key architectural decisions, and technology choices
2. **System Architecture**: Component relationships, data flow patterns, and architectural principles
3. **Technical Implementation**: Key algorithms, design patterns, and implementation strategies
4. **Performance & Scalability**: Architecture decisions impacting performance, scalability considerations, and optimization opportunities
5. **Development & Quality**: Code quality indicators, testing strategies, development practices, and technical debt assessment
6. **Technical Insights**: Unique architectural patterns, innovative approaches, technical challenges, and lessons learned

Write in a professional, analytical tone suitable for software architects, senior developers, and technical decision-makers. Focus on technical depth, architectural insights, and actionable recommendations similar to DeepWiki's comprehensive analysis style."""

            response = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=800,
                temperature=0.3,
                messages=[{'role': 'user', 'content': prompt}]
            )

            if response.content[0].type == 'text':
                return response.content[0].text
        except Exception as e:
            logger.warning(f"Failed to generate repository summary: {e}")
        
        return 'Unable to generate repository summary at this time.'
    
    async def _generate_enhanced_content(self, content: str, title: str, repo_name: str) -> Dict[str, Any]:
        """Generate enhanced content using Claude AI with DeepWiki-style analysis."""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            prompt = f"""You are an expert software architect and technical analyst creating comprehensive deep dive documentation similar to DeepWiki's detailed codebase analysis. You are analyzing a GitHub repository called "{repo_name}".

Please analyze the following content titled "{title}" and create a DeepWiki-style comprehensive technical deep dive:

{content}

CRITICAL: You must respond with ONLY a valid JSON object. Do not include any other text, explanations, or formatting outside the JSON.

Required JSON format (copy this exactly and fill in the values):

{{
  "summary": "A comprehensive technical summary covering the project's purpose, architecture, and key technologies in 3-4 sentences",
  "enhancedContent": "# {title} - Deep Technical Analysis\\n\\n## Executive Summary\\n[High-level overview of the project, its purpose, and key architectural decisions]\\n\\n## System Architecture\\n[Detailed system architecture including:\\n- Component relationships and data flow\\n- Technology stack and framework choices\\n- Design patterns and architectural principles\\n- System boundaries and interfaces]\\n\\n## Core Implementation\\n[Deep dive into the core implementation including:\\n- Key algorithms and data structures\\n- Critical code paths and logic\\n- Performance-critical components\\n- Error handling and edge cases]\\n\\n## Data Flow & Processing\\n[Analysis of data processing including:\\n- Data ingestion and transformation\\n- Storage strategies and persistence\\n- Caching mechanisms and optimization\\n- Data validation and integrity]\\n\\n## Performance Analysis\\n[Comprehensive performance analysis including:\\n- Bottlenecks and optimization opportunities\\n- Resource utilization patterns\\n- Scalability considerations\\n- Performance monitoring and metrics]\\n\\n## Security & Reliability\\n[Security and reliability analysis including:\\n- Security vulnerabilities and mitigations\\n- Authentication and authorization\\n- Data protection and privacy\\n- Fault tolerance and disaster recovery]\\n\\n## Development & Deployment\\n[Development and deployment analysis including:\\n- Build and deployment pipeline\\n- Testing strategies and coverage\\n- Environment management\\n- CI/CD practices]\\n\\n## Integration & Ecosystem\\n[Integration and ecosystem analysis including:\\n- External dependencies and APIs\\n- Third-party integrations\\n- Ecosystem relationships\\n- API design and versioning]\\n\\n## Code Quality & Technical Debt\\n[Code quality and technical debt analysis including:\\n- Code organization and structure\\n- Documentation quality\\n- Technical debt assessment\\n- Maintainability factors]\\n\\n## Future Roadmap\\n[Future considerations including:\\n- Technical roadmap and evolution\\n- Scalability challenges\\n- Potential improvements\\n- Technology migration strategies]\\n\\n## Technical Insights\\n[Key technical insights including:\\n- Innovative patterns and approaches\\n- Lessons learned and best practices\\n- Technical challenges overcome\\n- Architectural decisions rationale]",
  "keyPoints": ["Architectural insight 1", "Technical pattern 2", "Performance consideration 3", "Security aspect 4", "Scalability factor 5"],
  "suggestedImprovements": ["Architecture improvement 1", "Performance optimization 2", "Security enhancement 3", "Scalability upgrade 4", "Development workflow improvement 5"]
}}

Rules:
1. Start your response with {{ and end with }}
2. No text before or after the JSON
3. Use double quotes for all strings
4. Escape any quotes within strings with backslash
5. The summary should be 3-4 sentences covering technical depth
6. Include 5 key technical insights as an array of strings
7. Include 5 architectural/technical improvements as an array of strings
8. The enhancedContent should follow DeepWiki's comprehensive deep dive format with detailed technical sections
9. Focus on technical depth, architectural patterns, implementation details, and professional analysis
10. Include specific code patterns, design decisions, and technical insights
11. Write in a professional, analytical tone suitable for technical documentation
12. Provide actionable insights and technical recommendations

Create deep dive documentation that matches DeepWiki's level of technical detail, comprehensive analysis, and professional presentation."""

            response = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=2000,
                temperature=0.3,
                messages=[{'role': 'user', 'content': prompt}]
            )

            if response.content[0].type == 'text':
                response_text = response.content[0].text
                
                # Try to extract JSON from the response
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    try:
                        parsed = json.loads(json_match.group(0))
                        
                        # Validate the parsed object has all required fields
                        if (parsed.get('summary') and parsed.get('enhancedContent') and 
                            isinstance(parsed.get('keyPoints'), list) and 
                            isinstance(parsed.get('suggestedImprovements'), list)):
                            return {
                                'summary': parsed['summary'],
                                'enhancedContent': parsed['enhancedContent'],
                                'keyPoints': parsed['keyPoints'],
                                'suggestedImprovements': parsed['suggestedImprovements'],
                            }
                    except json.JSONDecodeError:
                        logger.warning(f"Failed to parse JSON response for {title}")
                
                # Fallback: extract information from text response
                return {
                    'summary': self._extract_summary(response_text),
                    'enhancedContent': content,  # Keep original if parsing fails
                    'keyPoints': self._extract_key_points(response_text),
                    'suggestedImprovements': self._extract_improvements(response_text),
                }
        except Exception as e:
            logger.warning(f"Failed to generate enhanced content for '{title}': {e}")
        
        # Return fallback response
        return {
            'summary': 'Unable to generate summary at this time.',
            'enhancedContent': content,
            'keyPoints': [],
            'suggestedImprovements': [],
        }
    
    def _extract_summary(self, text: str) -> str:
        """Extract summary from text response."""
        summary_match = re.search(r'summary[:\s]+([^.\n]+[.\n])', text, re.IGNORECASE)
        return summary_match.group(1).strip() if summary_match else 'Summary not available.'
    
    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from text response."""
        points_match = re.search(r'key points?[:\s]+([\s\S]*?)(?=\n\n|\n[A-Z]|$)', text, re.IGNORECASE)
        if points_match:
            return [
                point.replace('*', '').replace('-', '').strip()
                for point in points_match.group(1).split('\n')
                if point.strip()
            ]
        return []
    
    def _extract_improvements(self, text: str) -> List[str]:
        """Extract suggested improvements from text response."""
        improvements_match = re.search(r'suggested improvements?[:\s]+([\s\S]*?)(?=\n\n|\n[A-Z]|$)', text, re.IGNORECASE)
        if improvements_match:
            return [
                improvement.replace('*', '').replace('-', '').strip()
                for improvement in improvements_match.group(1).split('\n')
                if improvement.strip()
            ]
        return []
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        filename = '_'.join(filter(None, filename.split('_')))
        return filename.strip()
    
    def _create_repo_directory(self, owner: str, repo: str) -> Path:
        """Create a directory for the repository wiki documentation."""
        repo_name = f"{owner}_{repo}"
        safe_repo_name = self._sanitize_filename(repo_name)
        repo_dir = self.output_dir / safe_repo_name
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        versioned_dir = repo_dir / timestamp
        versioned_dir.mkdir(parents=True, exist_ok=True)
        
        return versioned_dir
    
    async def _save_enhanced_pages(self, enhanced_pages: List[Dict[str, Any]], repo_dir: Path) -> List[str]:
        """Save enhanced pages as markdown files."""
        saved_files = []
        
        for page in enhanced_pages:
            try:
                # Create safe filename
                safe_filename = self._sanitize_filename(page['title'])
                markdown_file = repo_dir / f"{safe_filename}.md"
                
                # Create enhanced content with metadata
                enhanced_content = f"""# {page['title']}

## Summary
{page.get('summary', 'No summary available')}

## Enhanced Content
{page.get('enhancedContent', page.get('originalContent', ''))}

## Key Points
{chr(10).join(f"- {point}" for point in page.get('keyPoints', []))}

## Suggested Improvements
{chr(10).join(f"- {improvement}" for improvement in page.get('suggestedImprovements', []))}

---
*Generated by Wiki Generation Service on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Original file: {page.get('path', 'Unknown')}*
"""
                
                with open(markdown_file, 'w', encoding='utf-8') as f:
                    f.write(enhanced_content)
                
                saved_files.append(str(markdown_file))
                logger.info(f"Enhanced page saved: {markdown_file}")
                
            except Exception as e:
                logger.error(f"Failed to save enhanced page {page.get('title', 'Unknown')}: {e}")
        
        return saved_files
    
    def _create_index_file(self, repo_data: Dict[str, Any], enhanced_pages: List[Dict[str, Any]], repo_dir: Path) -> str:
        """Create an index markdown file for the wiki documentation."""
        index_file = repo_dir / "README.md"
        
        repo_name = repo_data['name']
        repo_url = repo_data['html_url']
        
        index_content = f"""# {repo_name} - Enhanced Wiki Documentation

This directory contains AI-enhanced wiki-style documentation for the repository: **{repo_url}**

## Repository Overview

- **Description**: {repo_data.get('description', 'No description available')}
- **Language**: {repo_data.get('language', 'Not specified')}
- **Stars**: {repo_data['stargazers_count']}
- **Forks**: {repo_data['forks_count']}
- **Topics**: {', '.join(repo_data.get('topics', [])) or 'None'}
- **Created**: {repo_data['created_at']}
- **Updated**: {repo_data['updated_at']}

## Enhanced Documentation Pages

"""
        
        # Add links to all enhanced pages
        for page in enhanced_pages:
            safe_filename = self._sanitize_filename(page['title'])
            index_content += f"- [{page['title']}](./{safe_filename}.md)\n"
        
        index_content += f"""
## Documentation Structure

"""
        
        # Add structure information
        for page in enhanced_pages:
            index_content += f"- **{page['title']}** ({page.get('type', 'other')}): {page.get('path', 'Unknown path')}\n"
        
        index_content += f"""
## Usage

This enhanced wiki documentation was generated using the Wiki Generation Service. Each markdown file contains:

- **Original Content**: The original documentation from the repository
- **Enhanced Analysis**: DeepWiki-style technical analysis and insights
- **Key Points**: Important technical highlights and architectural insights
- **Suggested Improvements**: Recommendations for documentation and technical improvements

For the most up-to-date information, please refer to the original repository: {repo_url}

---
*Generated by Wiki Generation Service on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        logger.info(f"Index file created: {index_file}")
        return str(index_file)
    
    async def generate_enhanced_wiki(self, github_url: str) -> Dict[str, Any]:
        """
        Complete workflow: discover existing documentation and generate enhanced wiki.
        
        Args:
            github_url: GitHub repository URL
            
        Returns:
            Dictionary with enhanced wiki data and file paths
        """
        try:
            # Parse GitHub URL
            url_match = re.match(r'github\.com/([^/]+)/([^/]+)', github_url)
            if not url_match:
                raise ValueError('Invalid GitHub URL')
            
            owner, repo = url_match.groups()
            logger.info(f"Generating enhanced wiki for repository: {owner}/{repo}")
            
            # Fetch GitHub data
            github_data = await self._fetch_github_data(owner, repo)
            repo_data = github_data['repository']
            readme_content = github_data['readme']
            contents = github_data['contents']
            
            # Find documentation files
            doc_files = await self._find_documentation_files(owner, repo, contents)
            logger.info(f"Found {len(doc_files)} documentation files")
            
            # Build pages list
            pages = []
            structure = []
            
            # Add README as first page
            if readme_content:
                pages.append({
                    'title': 'README',
                    'content': readme_content,
                    'path': 'README.md',
                    'type': 'readme',
                })
                structure.append({
                    'title': 'README',
                    'path': 'README.md',
                })
            
            # Add documentation files
            for file in doc_files:
                try:
                    content = await self._fetch_file_content(owner, repo, file['path'])
                    title = self._get_title_from_path(file['path'])
                    file_type = self._get_file_type(file['path'])
                    
                    pages.append({
                        'title': title,
                        'content': content,
                        'path': file['path'],
                        'type': file_type,
                    })
                    structure.append({
                        'title': title,
                        'path': file['path'],
                    })
                except Exception as e:
                    logger.warning(f"Error fetching file {file['path']}: {e}")
            
            # Generate repository summary
            repository_summary = await self._generate_repository_summary(repo_data, pages)
            
            # Enhance documentation with rate limiting
            enhanced_pages = []
            for i, page in enumerate(pages):
                try:
                    # Add delay between requests to avoid rate limiting
                    if i > 0:
                        await asyncio.sleep(1.0)  # 1 second delay
                    
                    logger.info(f"🔄 Enhancing page: {page['title']}")
                    
                    enhanced = await self._generate_enhanced_content(
                        page['content'],
                        page['title'],
                        repo_data['name']
                    )
                    
                    enhanced_pages.append({
                        **page,
                        'originalContent': page['content'],
                        'enhancedContent': enhanced['enhancedContent'],
                        'summary': enhanced['summary'],
                        'keyPoints': enhanced['keyPoints'],
                        'suggestedImprovements': enhanced['suggestedImprovements'],
                    })
                    
                    logger.info(f"✅ Enhanced page: {page['title']}")
                    
                except Exception as error:
                    logger.error(f"❌ Failed to enhance page {page['title']}: {error}")
                    
                    # Check if it's a rate limit error
                    if hasattr(error, 'status') and error.status == 429:
                        logger.info("⏳ Rate limit hit, waiting 60 seconds before continuing...")
                        await asyncio.sleep(60)  # Wait 60 seconds
                        
                        # Try one more time after waiting
                        try:
                            enhanced = await self._generate_enhanced_content(
                                page['content'],
                                page['title'],
                                repo_data['name']
                            )
                            enhanced_pages.append({
                                **page,
                                'originalContent': page['content'],
                                'enhancedContent': enhanced['enhancedContent'],
                                'summary': enhanced['summary'],
                                'keyPoints': enhanced['keyPoints'],
                                'suggestedImprovements': enhanced['suggestedImprovements'],
                            })
                        except Exception as retry_error:
                            logger.error(f"Retry failed for page {page['title']}: {retry_error}")
                            enhanced_pages.append({
                                **page,
                                'originalContent': page['content'],
                                'enhancedContent': page['content'],
                                'summary': 'Unable to generate summary due to rate limiting.',
                                'keyPoints': [],
                                'suggestedImprovements': [],
                            })
                    else:
                        enhanced_pages.append({
                            **page,
                            'originalContent': page['content'],
                            'enhancedContent': page['content'],
                            'summary': 'Unable to generate summary.',
                            'keyPoints': [],
                            'suggestedImprovements': [],
                        })
            
            # Create repository directory
            repo_dir = self._create_repo_directory(owner, repo)
            
            # Save enhanced pages
            saved_files = await self._save_enhanced_pages(enhanced_pages, repo_dir)
            
            # Create index file
            index_file = self._create_index_file(repo_data, enhanced_pages, repo_dir)
            
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
                    "summary": repository_summary,
                },
                "pages": enhanced_pages,
                "structure": structure,
                "generatedFiles": {
                    "hasMarkdownFiles": True,
                    "repository": f"{owner}/{repo}",
                    "outputDirectory": str(repo_dir),
                    "files": {
                        "index": index_file,
                        "enhancedPages": saved_files
                    },
                    "note": "Enhanced wiki documentation has been saved as markdown files"
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Enhanced wiki generation completed successfully. Files saved to: {repo_dir}")
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced wiki generation workflow: {e}")
            raise

def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python wiki_generation_service.py <command> [args...]")
        print("Commands:")
        print("  generate <github_url> - Generate enhanced wiki documentation")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "generate":
            if len(sys.argv) < 3:
                print("Error: generate command requires GitHub URL")
                sys.exit(1)
            
            github_url = sys.argv[2]
            
            # Create service instance - API keys are handled internally via environment variables
            service = WikiGenerationService()
            
            # Run the complete wiki generation
            async def run_generation():
                return await service.generate_enhanced_wiki(github_url)
            
            result = asyncio.run(run_generation())
            
            # Output result as JSON
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
