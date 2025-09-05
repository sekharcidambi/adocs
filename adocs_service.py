#!/usr/bin/env python3
"""
ADocS Service - Python service wrapper for the ADocS documentation structure generator.
This service can be called from Node.js/Next.js applications to generate documentation structures.
"""

import json
import sys
import os
import logging
from typing import Dict, Any, Optional

# Add the src directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.generator import DocStructureGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ADocSService:
    """Service wrapper for ADocS documentation structure generation."""
    
    def __init__(self, knowledge_base_path: str = None):
        """
        Initialize the ADocS service.
        
        Args:
            knowledge_base_path: Path to the knowledge base pickle file
        """
        if knowledge_base_path is None:
            knowledge_base_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.pkl')
        
        self.knowledge_base_path = knowledge_base_path
        self.generator = None
        
        logger.info(f"ADocS Service initialized with knowledge base: {knowledge_base_path}")
    
    def _initialize_generator(self):
        """Initialize the DocStructureGenerator if not already done."""
        if self.generator is None:
            try:
                self.generator = DocStructureGenerator(self.knowledge_base_path)
                logger.info("DocStructureGenerator initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize DocStructureGenerator: {e}")
                raise
    
    def generate_documentation_structure(self, repo_metadata: Dict[str, Any], api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate documentation structure for a repository.
        
        Args:
            repo_metadata: Repository metadata dictionary
            api_key: Anthropic API key (optional, can use environment variable)
            
        Returns:
            Generated documentation structure
        """
        try:
            self._initialize_generator()
            
            logger.info(f"Generating documentation structure for repository: {repo_metadata.get('github_url', 'Unknown')}")
            
            # Generate the documentation structure using the RAG approach
            doc_structure = self.generator.generate(repo_metadata, api_key=api_key)
            
            logger.info("Documentation structure generated successfully")
            return doc_structure
            
        except Exception as e:
            logger.error(f"Error generating documentation structure: {e}")
            raise
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Knowledge base statistics
        """
        try:
            self._initialize_generator()
            return self.generator.get_knowledge_base_stats()
        except Exception as e:
            logger.error(f"Error getting knowledge base stats: {e}")
            raise

def main():
    """Main function to handle command line usage."""
    if len(sys.argv) < 2:
        print("Usage: python adocs_service.py <command> [args...]")
        print("Commands:")
        print("  generate <metadata_json> [api_key] - Generate documentation structure")
        print("  stats - Get knowledge base statistics")
        sys.exit(1)
    
    command = sys.argv[1]
    service = ADocSService()
    
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
            
            # Generate documentation structure
            result = service.generate_documentation_structure(repo_metadata, api_key)
            
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
