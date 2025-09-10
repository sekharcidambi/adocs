"""
Documentation Structure Generator for ADocS

This module contains the DocStructureGenerator class that uses RAG (Retrieval-Augmented Generation)
to generate ideal documentation structures for new repositories based on similar repositories
from the knowledge base.
"""

import json
import pickle
import os
from typing import List, Dict, Any, Optional
import anthropic
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DocStructureGenerator:
    """Generates documentation structures using RAG approach."""
    
    def __init__(self, knowledge_base_path: str, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize the documentation structure generator.
        
        Args:
            knowledge_base_path: Path to the knowledge base pickle file
            model_name: Name of the sentence transformer model to use
        """
        self.knowledge_base_path = knowledge_base_path
        self.model_name = model_name
        
        # Load knowledge base
        self.knowledge_base = self._load_knowledge_base()
        
        # Initialize sentence transformer model
        self.model = SentenceTransformer(model_name)
        
        # Initialize Claude API client (will be configured when needed)
        self.claude_client = None
        
        logger.info(f"Initialized DocStructureGenerator with {len(self.knowledge_base)} knowledge base entries")
    
    def _load_knowledge_base(self) -> List[Dict[str, Any]]:
        """
        Load the knowledge base from pickle file.
        
        Returns:
            List of knowledge base entries
        """
        logger.info(f"Loading knowledge base from: {self.knowledge_base_path}")
        
        try:
            with open(self.knowledge_base_path, 'rb') as f:
                knowledge_base = pickle.load(f)
            
            logger.info(f"Loaded {len(knowledge_base)} entries from knowledge base")
            return knowledge_base
            
        except FileNotFoundError:
            logger.error(f"Knowledge base file not found: {self.knowledge_base_path}")
            raise
        except Exception as e:
            logger.error(f"Error loading knowledge base: {e}")
            raise
    
    def _create_corpus_text(self, metadata: Dict[str, Any]) -> str:
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
    
    def _find_similar_repos(self, new_repo_embedding: np.ndarray, k: int = 3) -> List[Dict[str, Any]]:
        """
        Find the most similar repositories based on cosine similarity.
        
        Args:
            new_repo_embedding: Embedding vector of the new repository
            k: Number of similar repositories to return
            
        Returns:
            List of top k most similar repository entries
        """
        logger.info(f"Finding top {k} similar repositories")
        
        # Extract all embeddings from knowledge base
        kb_embeddings = np.array([entry['embedding'] for entry in self.knowledge_base])
        
        # Calculate cosine similarities
        similarities = cosine_similarity([new_repo_embedding], kb_embeddings)[0]
        
        # Get indices of top k most similar repositories
        top_indices = np.argsort(similarities)[-k:][::-1]  # Sort in descending order
        
        # Return the top k entries with their similarity scores
        similar_repos = []
        for idx in top_indices:
            entry = self.knowledge_base[idx].copy()
            entry['similarity_score'] = float(similarities[idx])
            similar_repos.append(entry)
        
        scores = [f'{repo["similarity_score"]:.3f}' for repo in similar_repos]
        logger.info(f"Found similar repositories with scores: {scores}")
        
        return similar_repos
    
    def _configure_claude(self, api_key: Optional[str] = None) -> None:
        """
        Configure the Claude API.
        
        Args:
            api_key: Anthropic API key. If None, will try to get from environment variable
        """
        if api_key is None:
            api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not api_key:
            raise ValueError("Anthropic API key not provided. Set ANTHROPIC_API_KEY environment variable or pass api_key parameter.")
        
        self.claude_client = anthropic.Anthropic(api_key=api_key)
        logger.info("Claude API configured successfully")
    
    def _construct_prompt(self, new_repo_metadata: Dict[str, Any], similar_repos: List[Dict[str, Any]]) -> str:
        """
        Construct the prompt for the LLM.
        
        Args:
            new_repo_metadata: Metadata of the new repository
            similar_repos: List of similar repository entries
            
        Returns:
            Formatted prompt string
        """
        # Create examples string
        examples_str = ""
        for i, repo in enumerate(similar_repos):
            examples_str += f"### Example {i+1}: Similar Repo ({repo['repo_url']})\n"
            examples_str += f"#### Similarity Score: {repo['similarity_score']:.3f}\n"
            examples_str += f"#### Documentation Structure:\n```json\n{json.dumps(repo['doc_structure'], indent=2)}\n```\n\n"
        
        prompt = f"""
As a principal engineer, your task is to create the ideal documentation structure for a new software project.

Analyze the provided metadata for the new repository and use the provided examples from similar projects as a reference to ensure high quality and relevance.

The output MUST be a single, valid JSON object and nothing else. Do not add any explanatory text before or after the JSON.

### New Repository Metadata:
```json
{json.dumps(new_repo_metadata, indent=2)}
```

---

### High-Quality Documentation Examples from Similar Repositories:
{examples_str}

---

### Your Task:
Based on all the information above, generate the `documentation_structure` JSON for the new repository.

The documentation structure should be comprehensive and include all necessary sections for the project type, technology stack, and business domain. Consider the patterns from the similar repositories but adapt them to the specific needs of this new repository.

### CRITICAL: Required JSON Format
The response MUST follow this exact structure:
```json
{{
  "sections": [
    {{
      "title": "Section Title",
      "children": [
        {{
          "title": "Subsection Title",
          "children": []
        }}
      ]
    }}
  ]
}}
```

IMPORTANT FORMAT RULES:
1. Each section MUST be an object with "title" and "children" properties
2. "title" must be a string
3. "children" must be an array of objects (even if empty)
4. Do NOT use strings or arrays directly in the sections array
5. All section objects must have the same structure

Return only the JSON structure, no additional text.
"""
        
        return prompt
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean the LLM response to extract only the JSON content.
        
        Args:
            response: Raw response from the LLM
            
        Returns:
            Cleaned JSON string
        """
        # Remove any markdown code blocks
        if '```json' in response:
            start = response.find('```json') + 7
            end = response.find('```', start)
            if end != -1:
                response = response[start:end]
        elif '```' in response:
            start = response.find('```') + 3
            end = response.find('```', start)
            if end != -1:
                response = response[start:end]
        
        # Remove any leading/trailing whitespace
        response = response.strip()
        
        return response
    
    def generate(self, new_repo_metadata: Dict[str, Any], api_key: Optional[str] = None, k: int = 3) -> Dict[str, Any]:
        """
        Generate documentation structure for a new repository.
        
        Args:
            new_repo_metadata: Metadata of the new repository
            api_key: Anthropic API key (optional, can use environment variable)
            k: Number of similar repositories to use for generation
            
        Returns:
            Generated documentation structure as a dictionary
        """
        logger.info("Starting documentation structure generation")
        
        try:
            # Create corpus text and generate embedding for new repo
            corpus_text = self._create_corpus_text(new_repo_metadata)
            new_repo_embedding = self.model.encode(corpus_text)
            
            logger.info(f"Generated embedding for new repository: {corpus_text[:100]}...")
            
            # Find similar repositories
            similar_repos = self._find_similar_repos(new_repo_embedding, k)
            
            # Configure Claude API
            self._configure_claude(api_key)
            
            # Construct prompt
            prompt = self._construct_prompt(new_repo_metadata, similar_repos)
            
            logger.info("Sending request to Claude API...")
            
            # Try different Claude model names in order of preference
            model_names = [
                "claude-sonnet-4-20250514",
                "claude-3-5-sonnet-20241022",
                "claude-3-5-sonnet-20240620", 
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
            
            response = None
            last_error = None
            
            for model_name in model_names:
                try:
                    logger.info(f"Trying model: {model_name}")
                    response = self.claude_client.messages.create(
                        model=model_name,
                        max_tokens=4000,
                        temperature=0.1,
                        messages=[
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]
                    )
                    logger.info(f"Successfully used model: {model_name}")
                    break
                except Exception as e:
                    last_error = e
                    logger.warning(f"Model {model_name} failed: {e}")
                    continue
            
            if response is None:
                raise ValueError(f"All Claude models failed. Last error: {last_error}")
            
            if not response.content or not response.content[0].text:
                raise ValueError("Empty response from Claude API")
            
            response_text = response.content[0].text
            
            # Clean and parse the response
            cleaned_response = self._clean_json_response(response_text)
            
            # Parse JSON
            try:
                doc_structure = json.loads(cleaned_response)
                logger.info("Successfully generated and parsed documentation structure")
                return doc_structure
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Raw response: {response_text}")
                logger.error(f"Cleaned response: {cleaned_response}")
                raise ValueError(f"Invalid JSON response from LLM: {e}")
        
        except Exception as e:
            logger.error(f"Error in generate method: {e}")
            raise
    
    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary with knowledge base statistics
        """
        if not self.knowledge_base:
            return {"total_entries": 0}
        
        # Get unique tech stacks
        all_tech_stacks = []
        all_business_domains = []
        
        for entry in self.knowledge_base:
            metadata = entry.get('metadata', {})
            
            # Collect tech stacks
            tech_stack = metadata.get('tech_stack', [])
            if isinstance(tech_stack, list):
                all_tech_stacks.extend(tech_stack)
            
            # Collect business domains
            business_domain = metadata.get('business_domain', '')
            if business_domain:
                all_business_domains.append(business_domain)
        
        return {
            "total_entries": len(self.knowledge_base),
            "unique_technologies": len(set(all_tech_stacks)),
            "unique_business_domains": len(set(all_business_domains)),
            "top_technologies": list(set(all_tech_stacks))[:10],
            "business_domains": list(set(all_business_domains))[:10]
        }
