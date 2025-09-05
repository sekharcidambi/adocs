"""
Knowledge Base Builder for ADocS (Automated Documentation Structure Generator)

This script processes the repository metadata and documentation structures to create
a knowledge base with vector embeddings for similarity search.
"""

import json
import pickle
import glob
import os
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KnowledgeBaseBuilder:
    """Builds and manages the knowledge base for documentation structure generation."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the knowledge base builder.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        logger.info(f"Initialized sentence transformer model: {model_name}")
    
    def load_deepwiki_docs(self, deepwiki_path: str) -> Dict[str, Any]:
        """
        Load the deepwiki documentation structures.
        
        Args:
            deepwiki_path: Path to the deepwiki_docs.json file
            
        Returns:
            Dictionary mapping github_url to documentation structure
        """
        logger.info(f"Loading deepwiki docs from: {deepwiki_path}")
        
        try:
            with open(deepwiki_path, 'r', encoding='utf-8') as f:
                deepwiki_data = json.load(f)
            
            # Create mapping from github_url to documentation structure
            docs_mapping = {}
            for item in deepwiki_data:
                github_url = item.get('github_url')
                doc_structure = item.get('documentation_structure')
                if github_url and doc_structure:
                    docs_mapping[github_url] = doc_structure
            
            logger.info(f"Loaded {len(docs_mapping)} documentation structures")
            return docs_mapping
            
        except FileNotFoundError:
            logger.error(f"Deepwiki docs file not found: {deepwiki_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing deepwiki docs JSON: {e}")
            raise
    
    def create_corpus_text(self, metadata: Dict[str, Any]) -> str:
        """
        Create a corpus text from repository metadata for embedding generation.
        
        Args:
            metadata: Repository metadata dictionary
            
        Returns:
            Combined text string for embedding
        """
        corpus_parts = []
        
        # Add overview
        overview = metadata.get('overview', '')
        if overview:
            corpus_parts.append(f"Overview: {overview}")
        
        # Add business domain
        business_domain = metadata.get('business_domain', '')
        if business_domain:
            corpus_parts.append(f"Business Domain: {business_domain}")
        
        # Add architecture description
        architecture = metadata.get('architecture', {})
        if isinstance(architecture, dict):
            arch_desc = architecture.get('description', '')
            if arch_desc:
                corpus_parts.append(f"Architecture: {arch_desc}")
        
        # Add tech stack (handle both array and object formats)
        tech_stack = metadata.get('tech_stack', [])
        if tech_stack:
            if isinstance(tech_stack, dict):
                # Handle object format with categories
                all_techs = []
                for category, techs in tech_stack.items():
                    if isinstance(techs, list):
                        all_techs.extend(techs)
                    else:
                        all_techs.append(str(techs))
                tech_string = ', '.join(all_techs)
            elif isinstance(tech_stack, list):
                # Handle array format
                tech_string = ', '.join(tech_stack)
            else:
                # Handle string format
                tech_string = str(tech_stack)
            corpus_parts.append(f"Tech Stack: {tech_string}")
        
        return ' '.join(corpus_parts)
    
    def process_repository_files(self, repo_metadata_dir: str, docs_mapping: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process all repository analysis files and create embeddings.
        
        Args:
            repo_metadata_dir: Directory containing analysis JSON files
            docs_mapping: Mapping from github_url to documentation structure
            
        Returns:
            List of knowledge base entries with metadata, embeddings, and doc structures
        """
        logger.info(f"Processing repository files from: {repo_metadata_dir}")
        
        # Get all analysis files
        pattern = os.path.join(repo_metadata_dir, "*_analysis.json")
        analysis_files = glob.glob(pattern)
        
        if not analysis_files:
            logger.warning(f"No analysis files found matching pattern: {pattern}")
            return []
        
        logger.info(f"Found {len(analysis_files)} analysis files")
        
        knowledge_base = []
        processed_count = 0
        skipped_count = 0
        
        for file_path in analysis_files:
            try:
                # Read the analysis file
                with open(file_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Extract repository URL (try both field names)
                repo_url = metadata.get('github_url', '') or metadata.get('github_repo', '')
                if not repo_url:
                    logger.warning(f"No github_url or github_repo found in {file_path}, skipping")
                    skipped_count += 1
                    continue
                
                # Find corresponding documentation structure
                doc_structure = docs_mapping.get(repo_url)
                if not doc_structure:
                    logger.warning(f"No documentation structure found for {repo_url}, skipping")
                    skipped_count += 1
                    continue
                
                # Create corpus text
                corpus_text = self.create_corpus_text(metadata)
                
                # Generate embedding
                embedding = self.model.encode(corpus_text)
                
                # Create knowledge base entry
                kb_entry = {
                    'repo_url': repo_url,
                    'metadata': metadata,
                    'doc_structure': doc_structure,
                    'embedding': embedding,
                    'corpus_text': corpus_text  # Store for debugging
                }
                
                knowledge_base.append(kb_entry)
                processed_count += 1
                
                if processed_count % 10 == 0:
                    logger.info(f"Processed {processed_count} repositories...")
                
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
                skipped_count += 1
                continue
        
        logger.info(f"Knowledge base creation complete:")
        logger.info(f"  - Processed: {processed_count}")
        logger.info(f"  - Skipped: {skipped_count}")
        logger.info(f"  - Total entries: {len(knowledge_base)}")
        
        return knowledge_base
    
    def save_knowledge_base(self, knowledge_base: List[Dict[str, Any]], output_path: str) -> None:
        """
        Save the knowledge base to a pickle file.
        
        Args:
            knowledge_base: List of knowledge base entries
            output_path: Path to save the pickle file
        """
        logger.info(f"Saving knowledge base to: {output_path}")
        
        try:
            with open(output_path, 'wb') as f:
                pickle.dump(knowledge_base, f)
            
            logger.info(f"Knowledge base saved successfully with {len(knowledge_base)} entries")
            
        except Exception as e:
            logger.error(f"Error saving knowledge base: {e}")
            raise


def main():
    """Main function to build the knowledge base."""
    
    # Configuration
    DEEPWIKI_PATH = "/Users/sekharcidambi/adocs/data/deepwiki_docs.json"
    REPO_METADATA_DIR = "/Users/sekharcidambi/adocs/data/repo_metadata"
    OUTPUT_PATH = "/Users/sekharcidambi/adocs/knowledge_base.pkl"
    
    try:
        # Initialize builder
        builder = KnowledgeBaseBuilder()
        
        # Load deepwiki documentation structures
        docs_mapping = builder.load_deepwiki_docs(DEEPWIKI_PATH)
        
        # Process repository files
        knowledge_base = builder.process_repository_files(REPO_METADATA_DIR, docs_mapping)
        
        if not knowledge_base:
            logger.error("No knowledge base entries created. Exiting.")
            return
        
        # Save knowledge base
        builder.save_knowledge_base(knowledge_base, OUTPUT_PATH)
        
        logger.info("Knowledge base building completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        raise


if __name__ == "__main__":
    main()
