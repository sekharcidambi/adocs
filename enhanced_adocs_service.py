#!/usr/bin/env python3
"""
Enhanced ADocS Service - Python service wrapper for the ADocS documentation structure generator.
This service generates documentation structures and stores them as markdown files.
"""

import json
import sys
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

# Add the src directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import DocStructureGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedADocSService:
    """Enhanced service wrapper for ADocS documentation structure generation with file storage."""
    
    def __init__(self, knowledge_base_path: str = None, output_dir: str = None):
        """
        Initialize the Enhanced ADocS service.
        
        Args:
            knowledge_base_path: Path to the knowledge base pickle file
            output_dir: Directory to store generated documentation files
        """
        if knowledge_base_path is None:
            knowledge_base_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.pkl')
        
        if output_dir is None:
            output_dir = os.path.join(os.path.dirname(__file__), 'generated_docs')
        
        self.knowledge_base_path = knowledge_base_path
        self.output_dir = Path(output_dir)
        self.generator = None
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(exist_ok=True)
        
        logger.info(f"Enhanced ADocS Service initialized with knowledge base: {knowledge_base_path}")
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
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        # Replace invalid characters with underscores
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        # Remove multiple underscores and trim
        filename = '_'.join(filter(None, filename.split('_')))
        return filename.strip()
    
    def _create_repo_directory(self, repo_metadata: Dict[str, Any]) -> Path:
        """Create a directory for the repository documentation."""
        github_url = repo_metadata.get('github_url', 'unknown')
        # Extract owner/repo from URL
        if 'github.com/' in github_url:
            parts = github_url.split('github.com/')[-1].rstrip('/')
            owner, repo = parts.split('/')[:2]
            repo_name = f"{owner}_{repo}"
        else:
            repo_name = "unknown_repo"
        
        # Sanitize and create directory
        safe_repo_name = self._sanitize_filename(repo_name)
        repo_dir = self.output_dir / safe_repo_name
        
        # Create timestamped subdirectory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        versioned_dir = repo_dir / timestamp
        versioned_dir.mkdir(parents=True, exist_ok=True)
        
        return versioned_dir
    
    def _save_documentation_structure(self, doc_structure: Dict[str, Any], repo_dir: Path) -> str:
        """Save the documentation structure as JSON."""
        structure_file = repo_dir / "documentation_structure.json"
        
        with open(structure_file, 'w', encoding='utf-8') as f:
            json.dump(doc_structure, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Documentation structure saved to: {structure_file}")
        return str(structure_file)
    
    def _save_metadata(self, repo_metadata: Dict[str, Any], repo_dir: Path) -> str:
        """Save the repository metadata as JSON."""
        metadata_file = repo_dir / "repository_metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(repo_metadata, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Repository metadata saved to: {metadata_file}")
        return str(metadata_file)
    
    def _generate_markdown_content(self, section: Dict[str, Any], repo_metadata: Dict[str, Any], level: int = 1) -> str:
        """Generate markdown content for a section."""
        title = section.get('title', 'Untitled')
        children = section.get('children', [])
        
        # Create markdown content
        markdown_lines = []
        
        # Add section title
        markdown_lines.append(f"{'#' * level} {title}")
        markdown_lines.append("")
        
        # Add section description based on title and repository context
        description = self._generate_section_description(title, repo_metadata)
        if description:
            markdown_lines.append(description)
            markdown_lines.append("")
        
        # Add subsections
        if children:
            markdown_lines.append("## Subsections")
            markdown_lines.append("")
            for child in children:
                child_title = child.get('title', 'Untitled')
                markdown_lines.append(f"- [{child_title}](./{self._sanitize_filename(child_title)}.md)")
            markdown_lines.append("")
        
        # Add repository-specific information
        markdown_lines.append("## Repository Information")
        markdown_lines.append("")
        markdown_lines.append(f"- **Repository**: {repo_metadata.get('github_url', 'Unknown')}")
        markdown_lines.append(f"- **Business Domain**: {repo_metadata.get('business_domain', 'Not specified')}")
        markdown_lines.append(f"- **Architecture**: {repo_metadata.get('architecture', {}).get('pattern', 'Not specified')}")
        markdown_lines.append("")
        
        # Add tech stack information
        tech_stack = repo_metadata.get('tech_stack', {})
        if tech_stack:
            markdown_lines.append("## Technology Stack")
            markdown_lines.append("")
            for category, technologies in tech_stack.items():
                if technologies:
                    markdown_lines.append(f"- **{category.title()}**: {', '.join(technologies)}")
            markdown_lines.append("")
        
        return '\n'.join(markdown_lines)
    
    def _generate_section_description(self, title: str, repo_metadata: Dict[str, Any]) -> str:
        """Generate a description for a section based on its title and repository context."""
        title_lower = title.lower()
        
        if 'getting started' in title_lower or 'installation' in title_lower:
            return f"This section covers how to get started with {repo_metadata.get('github_url', 'this repository')}. It includes installation instructions, setup requirements, and initial configuration steps."
        
        elif 'architecture' in title_lower or 'design' in title_lower:
            arch_pattern = repo_metadata.get('architecture', {}).get('pattern', 'Not specified')
            return f"This section describes the architecture and design patterns used in this repository. The system follows a {arch_pattern} architecture pattern."
        
        elif 'api' in title_lower or 'endpoint' in title_lower:
            return f"This section documents the API endpoints and interfaces provided by this repository. It includes request/response formats, authentication, and usage examples."
        
        elif 'deployment' in title_lower or 'production' in title_lower:
            return f"This section covers deployment strategies, production setup, and operational considerations for this repository."
        
        elif 'development' in title_lower or 'contributing' in title_lower:
            return f"This section provides guidance for developers working on this repository, including development setup, coding standards, and contribution guidelines."
        
        elif 'testing' in title_lower:
            return f"This section covers testing strategies, test setup, and how to run tests for this repository."
        
        else:
            return f"This section provides detailed information about {title} in the context of this repository."
    
    def _save_section_markdown(self, section: Dict[str, Any], repo_metadata: Dict[str, Any], repo_dir: Path, level: int = 1) -> List[str]:
        """Save a section and its children as markdown files."""
        saved_files = []
        
        title = section.get('title', 'Untitled')
        children = section.get('children', [])
        
        # Generate and save markdown content for this section
        markdown_content = self._generate_markdown_content(section, repo_metadata, level)
        
        # Create safe filename
        safe_filename = self._sanitize_filename(title)
        markdown_file = repo_dir / f"{safe_filename}.md"
        
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        saved_files.append(str(markdown_file))
        logger.info(f"Markdown file saved: {markdown_file}")
        
        # Recursively save children
        for child in children:
            child_files = self._save_section_markdown(child, repo_metadata, repo_dir, level + 1)
            saved_files.extend(child_files)
        
        return saved_files
    
    def generate_and_store_documentation(self, repo_metadata: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate documentation structure and store as markdown files.
        
        Args:
            repo_metadata: Repository metadata dictionary
            api_key: Anthropic API key (optional, can use environment variable)
            
        Returns:
            Dictionary with generation results and file paths
        """
        try:
            self._initialize_generator()
            
            github_url = repo_metadata.get('github_url', 'Unknown')
            logger.info(f"Generating and storing documentation for repository: {github_url}")
            
            # Create repository directory
            repo_dir = self._create_repo_directory(repo_metadata)
            
            # Save repository metadata
            metadata_file = self._save_metadata(repo_metadata, repo_dir)
            
            # Generate the documentation structure using the RAG approach
            doc_structure = self.generator.generate(repo_metadata, api_key=api_key)
            
            # Save documentation structure
            structure_file = self._save_documentation_structure(doc_structure, repo_dir)
            
            # Save sections as markdown files
            saved_files = []
            if isinstance(doc_structure, list) and len(doc_structure) > 0:
                # Handle array format (new ADocS format)
                root_item = doc_structure[0]
                if 'children' in root_item:
                    for section in root_item['children']:
                        section_files = self._save_section_markdown(section, repo_metadata, repo_dir)
                        saved_files.extend(section_files)
            elif isinstance(doc_structure, dict):
                # Handle object format
                if 'sections' in doc_structure:
                    for section in doc_structure['sections']:
                        section_files = self._save_section_markdown(section, repo_metadata, repo_dir)
                        saved_files.extend(section_files)
            
            # Create index file
            index_file = self._create_index_file(repo_metadata, doc_structure, repo_dir, saved_files)
            
            result = {
                "success": True,
                "repository": github_url,
                "output_directory": str(repo_dir),
                "files_created": {
                    "metadata": metadata_file,
                    "structure": structure_file,
                    "index": index_file,
                    "markdown_files": saved_files
                },
                "documentation_structure": doc_structure,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Documentation generation completed successfully. Files saved to: {repo_dir}")
            return result
            
        except Exception as e:
            logger.error(f"Error generating and storing documentation: {e}")
            raise
    
    def _create_index_file(self, repo_metadata: Dict[str, Any], doc_structure: Dict[str, Any], repo_dir: Path, saved_files: List[str]) -> str:
        """Create an index markdown file for the documentation."""
        index_file = repo_dir / "README.md"
        
        github_url = repo_metadata.get('github_url', 'Unknown')
        repo_name = github_url.split('/')[-1] if '/' in github_url else 'Unknown Repository'
        
        index_content = f"""# {repo_name} Documentation

This directory contains AI-generated documentation for the repository: **{github_url}**

## Generated Files

### Structure Files
- `documentation_structure.json` - Complete documentation structure
- `repository_metadata.json` - Repository metadata and analysis

### Documentation Sections
"""
        
        # Add links to all markdown files
        for file_path in saved_files:
            filename = Path(file_path).name
            if filename != "README.md":
                section_name = filename.replace('.md', '').replace('_', ' ')
                index_content += f"- [{section_name}](./{filename})\n"
        
        index_content += f"""
## Repository Information

- **Business Domain**: {repo_metadata.get('business_domain', 'Not specified')}
- **Architecture Pattern**: {repo_metadata.get('architecture', {}).get('pattern', 'Not specified')}
- **Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Technology Stack

"""
        
        # Add tech stack information
        tech_stack = repo_metadata.get('tech_stack', {})
        for category, technologies in tech_stack.items():
            if technologies:
                index_content += f"- **{category.title()}**: {', '.join(technologies)}\n"
        
        index_content += f"""
## Usage

This documentation was generated using the ADocS (Automated Documentation Structure) system. Each markdown file contains detailed information about a specific aspect of the repository.

For the most up-to-date information, please refer to the original repository: {github_url}
"""
        
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        logger.info(f"Index file created: {index_file}")
        return str(index_file)
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        try:
            self._initialize_generator()
            return self.generator.get_knowledge_base_stats()
        except Exception as e:
            logger.error(f"Error getting knowledge base stats: {e}")
            raise

def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_adocs_service.py <command> [args...]")
        print("Commands:")
        print("  generate <metadata_json> [api_key] - Generate and store documentation")
        print("  stats - Get knowledge base statistics")
        sys.exit(1)
    
    command = sys.argv[1]
    service = EnhancedADocSService()
    
    try:
        if command == "generate":
            if len(sys.argv) < 3:
                print("Error: generate command requires metadata JSON")
                sys.exit(1)
            
            # Parse metadata JSON
            metadata_json = sys.argv[2]
            repo_metadata = json.loads(metadata_json)
            
            # Get API key if provided
            api_key = sys.argv[3] if len(sys.argv) > 3 else None
            
            # Generate and store documentation
            result = service.generate_and_store_documentation(repo_metadata, api_key)
            
            # Output result as JSON
            print(json.dumps(result, indent=2))
            
        elif command == "stats":
            # Get knowledge base statistics
            stats = service.get_knowledge_base_stats()
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
