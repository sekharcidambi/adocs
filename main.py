"""
Main script for ADocS (Automated Documentation Structure Generator)

This script demonstrates how to use the DocStructureGenerator to create
documentation structures for new repositories.
"""

import json
import os
import sys
from typing import Dict, Any
import logging

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import DocStructureGenerator
from src.preprocess import KnowledgeBaseBuilder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_sample_metadata(file_path: str) -> Dict[str, Any]:
    """
    Load sample repository metadata from a JSON file.
    
    Args:
        file_path: Path to the analysis JSON file
        
    Returns:
        Repository metadata dictionary
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        logger.info(f"Loaded metadata from: {file_path}")
        return metadata
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file: {e}")
        raise


def create_sample_metadata() -> Dict[str, Any]:
    """
    Create a sample repository metadata for demonstration purposes.
    
    Returns:
        Sample repository metadata dictionary
    """
    return {
        "github_url": "https://github.com/example/sample-project",
        "overview": "A modern web application built with React and Node.js for managing user tasks and projects. Features real-time collaboration, file sharing, and advanced analytics dashboard.",
        "business_domain": "Productivity Software",
        "architecture": {
            "description": "Microservices architecture with React frontend, Node.js backend, PostgreSQL database, and Redis for caching. Deployed on AWS with Docker containers.",
            "components": ["Frontend", "Backend API", "Database", "Cache Layer", "File Storage"]
        },
        "tech_stack": [
            "React",
            "Node.js",
            "Express",
            "PostgreSQL",
            "Redis",
            "Docker",
            "AWS",
            "TypeScript",
            "Jest",
            "Webpack"
        ],
        "features": [
            "User authentication",
            "Task management",
            "Real-time collaboration",
            "File sharing",
            "Analytics dashboard",
            "Mobile responsive design"
        ],
        "target_audience": "Small to medium businesses and teams looking for project management solutions"
    }


def build_knowledge_base_if_needed() -> bool:
    """
    Build the knowledge base if it doesn't exist.
    
    Returns:
        True if knowledge base was built or already exists, False otherwise
    """
    knowledge_base_path = "/Users/sekharcidambi/adocs/knowledge_base.pkl"
    
    if os.path.exists(knowledge_base_path):
        logger.info("Knowledge base already exists, skipping build process")
        return True
    
    logger.info("Knowledge base not found, building it now...")
    
    try:
        # Check if required data files exist
        deepwiki_path = "/Users/sekharcidambi/adocs/data/deepwiki_docs.json"
        repo_metadata_dir = "/Users/sekharcidambi/adocs/data/repo_metadata"
        
        if not os.path.exists(deepwiki_path):
            logger.warning(f"Deepwiki docs file not found: {deepwiki_path}")
            logger.warning("Please ensure the data files are in place before running the generator")
            return False
        
        if not os.path.exists(repo_metadata_dir):
            logger.warning(f"Repository metadata directory not found: {repo_metadata_dir}")
            logger.warning("Please ensure the data files are in place before running the generator")
            return False
        
        # Build knowledge base
        builder = KnowledgeBaseBuilder()
        docs_mapping = builder.load_deepwiki_docs(deepwiki_path)
        knowledge_base = builder.process_repository_files(repo_metadata_dir, docs_mapping)
        
        if knowledge_base:
            builder.save_knowledge_base(knowledge_base, knowledge_base_path)
            logger.info("Knowledge base built successfully!")
            return True
        else:
            logger.error("Failed to build knowledge base - no entries created")
            return False
            
    except Exception as e:
        logger.error(f"Error building knowledge base: {e}")
        return False


def demonstrate_generator():
    """Demonstrate the documentation structure generator."""
    
    logger.info("=== ADocS Documentation Structure Generator Demo ===")
    
    # Check if knowledge base exists, build if needed
    if not build_knowledge_base_if_needed():
        logger.error("Cannot proceed without knowledge base. Please ensure data files are available.")
        return
    
    try:
        # Initialize the generator
        knowledge_base_path = "/Users/sekharcidambi/adocs/knowledge_base.pkl"
        generator = DocStructureGenerator(knowledge_base_path)
        
        # Display knowledge base statistics
        stats = generator.get_knowledge_base_stats()
        logger.info(f"Knowledge Base Statistics:")
        logger.info(f"  - Total entries: {stats['total_entries']}")
        logger.info(f"  - Unique technologies: {stats['unique_technologies']}")
        logger.info(f"  - Unique business domains: {stats['unique_business_domains']}")
        
        # Load or create sample metadata
        sample_file = "/Users/sekharcidambi/adocs/sample_analysis.json"
        
        if os.path.exists(sample_file):
            logger.info(f"Loading sample metadata from: {sample_file}")
            new_repo_metadata = load_sample_metadata(sample_file)
        else:
            logger.info("Creating sample metadata for demonstration")
            new_repo_metadata = create_sample_metadata()
            
            # Save sample metadata for future use
            with open(sample_file, 'w', encoding='utf-8') as f:
                json.dump(new_repo_metadata, f, indent=2)
            logger.info(f"Sample metadata saved to: {sample_file}")
        
        # Display the input metadata
        logger.info("Input Repository Metadata:")
        logger.info(f"  - URL: {new_repo_metadata.get('github_url', 'N/A')}")
        logger.info(f"  - Overview: {new_repo_metadata.get('overview', 'N/A')[:100]}...")
        logger.info(f"  - Business Domain: {new_repo_metadata.get('business_domain', 'N/A')}")
        logger.info(f"  - Tech Stack: {', '.join(new_repo_metadata.get('tech_stack', []))}")
        
        # Check for API key
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY environment variable not set")
            logger.warning("Please set your Anthropic API key: export ANTHROPIC_API_KEY='your_api_key_here'")
            logger.info("For demonstration, showing what would be generated...")
            
            # Show what the prompt would look like without making the API call
            corpus_text = generator._create_corpus_text(new_repo_metadata)
            new_repo_embedding = generator.model.encode(corpus_text)
            similar_repos = generator._find_similar_repos(new_repo_embedding, k=3)
            
            logger.info("Top 3 similar repositories found:")
            for i, repo in enumerate(similar_repos, 1):
                logger.info(f"  {i}. {repo['repo_url']} (similarity: {repo['similarity_score']:.3f})")
            
            return
        
        # Generate documentation structure
        logger.info("Generating documentation structure...")
        doc_structure = generator.generate(new_repo_metadata, api_key=api_key)
        
        # Save the generated structure
        output_file = "/Users/sekharcidambi/adocs/generated_doc_structure.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(doc_structure, f, indent=2)
        
        logger.info(f"Generated documentation structure saved to: {output_file}")
        logger.info("Generated Documentation Structure:")
        logger.info(json.dumps(doc_structure, indent=2))
        
    except Exception as e:
        logger.error(f"Error in demonstration: {e}")
        raise


def main():
    """Main function."""
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "build":
            # Build knowledge base only
            logger.info("Building knowledge base...")
            if build_knowledge_base_if_needed():
                logger.info("Knowledge base build completed successfully!")
            else:
                logger.error("Knowledge base build failed!")
                sys.exit(1)
            return
        
        elif command == "generate":
            # Generate documentation structure
            if len(sys.argv) < 3:
                logger.error("Usage: python main.py generate <path_to_analysis.json>")
                sys.exit(1)
            
            analysis_file = sys.argv[2]
            if not os.path.exists(analysis_file):
                logger.error(f"Analysis file not found: {analysis_file}")
                sys.exit(1)
            
            try:
                # Load metadata and generate
                metadata = load_sample_metadata(analysis_file)
                generator = DocStructureGenerator("/Users/sekharcidambi/adocs/knowledge_base.pkl")
                
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if not api_key:
                    logger.error("ANTHROPIC_API_KEY environment variable not set")
                    sys.exit(1)
                
                doc_structure = generator.generate(metadata, api_key=api_key)
                
                # Save output
                output_file = f"{os.path.splitext(analysis_file)[0]}_doc_structure.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(doc_structure, f, indent=2)
                
                logger.info(f"Generated documentation structure saved to: {output_file}")
                
            except Exception as e:
                logger.error(f"Error generating documentation structure: {e}")
                sys.exit(1)
            return
        
        elif command == "help":
            print("ADocS - Automated Documentation Structure Generator")
            print("\nUsage:")
            print("  python main.py                    # Run demonstration")
            print("  python main.py build             # Build knowledge base only")
            print("  python main.py generate <file>   # Generate doc structure for specific file")
            print("  python main.py help              # Show this help message")
            print("\nEnvironment Variables:")
            print("  ANTHROPIC_API_KEY                # Required for generation (get from Anthropic Console)")
            return
        
        else:
            logger.error(f"Unknown command: {command}")
            logger.error("Use 'python main.py help' for usage information")
            sys.exit(1)
    
    # Default: run demonstration
    demonstrate_generator()


if __name__ == "__main__":
    main()
