# ADocS - Automated Documentation Structure Generator

ADocS is a Python-based system that automatically generates ideal documentation structures for new GitHub repositories using a Retrieval-Augmented Generation (RAG) approach. It leverages a knowledge base of existing repositories to create relevant and comprehensive documentation plans.

## Features

- **RAG-based Generation**: Uses semantic similarity search to find relevant examples from a knowledge base
- **Vector Embeddings**: Employs sentence transformers for semantic understanding
- **LLM Integration**: Uses Anthropic's Claude API with automatic model fallback for intelligent structure generation
- **Scalable Architecture**: Designed to handle thousands of repositories
- **Fast Processing**: Generates documentation structures in under 30 seconds

## Project Structure

```
adocs/
├── src/
│   ├── preprocess.py      # Knowledge base builder
│   └── generator.py       # Documentation structure generator
├── data/
│   ├── repo_metadata/     # Directory containing *_analysis.json files
│   └── deepwiki_docs.json # Documentation structures mapping
├── main.py                # Main script and CLI interface
├── requirements.txt       # Python dependencies
├── sample_analysis.json   # Sample repository metadata
└── README.md             # This file
```

## Installation

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your Anthropic API key**:
   ```bash
   export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
   ```
   
   Get your API key from [Anthropic Console](https://console.anthropic.com/)

## Data Setup

Before running ADocS, you need to set up your data files:

1. **Repository Metadata**: Place your `*_analysis.json` files in `/data/repo_metadata/`
2. **Documentation Structures**: Place your `deepwiki_docs.json` file in `/data/`

### Expected Data Format

**Repository Analysis Files** (`*_analysis.json`):
```json
{
  "github_url": "https://github.com/owner/repo",
  "overview": "Project description...",
  "business_domain": "Domain category",
  "architecture": {
    "description": "Architecture description...",
    "components": ["Component1", "Component2"]
  },
  "tech_stack": ["Technology1", "Technology2", "Technology3"]
}
```

**Deepwiki Docs** (`deepwiki_docs.json`):
```json
[
  {
    "github_url": "https://github.com/owner/repo",
    "documentation_structure": {
      "sections": [
        {
          "title": "Getting Started",
          "subsections": ["Installation", "Quick Start"]
        }
      ]
    }
  }
]
```

## Usage

### Command Line Interface

1. **Build Knowledge Base** (run once or when data is updated):
   ```bash
   python main.py build
   ```

2. **Generate Documentation Structure**:
   ```bash
   python main.py generate path/to/analysis.json
   ```

3. **Run Demonstration**:
   ```bash
   python main.py
   ```

4. **Show Help**:
   ```bash
   python main.py help
   ```

### Programmatic Usage

```python
from src.generator import DocStructureGenerator

# Initialize generator
generator = DocStructureGenerator("knowledge_base.pkl")

# Load your repository metadata
with open("your_analysis.json", "r") as f:
    metadata = json.load(f)

# Generate documentation structure
doc_structure = generator.generate(metadata, api_key="your_api_key")

# Save result
with open("generated_structure.json", "w") as f:
    json.dump(doc_structure, f, indent=2)
```

## How It Works

1. **Knowledge Base Building** (`preprocess.py`):
   - Loads repository metadata and documentation structures
   - Creates semantic embeddings using sentence transformers
   - Stores everything in a pickle file for fast access

2. **Similarity Search** (`generator.py`):
   - Generates embedding for the new repository
   - Finds top 3 most similar repositories using cosine similarity
   - Uses these as examples for the LLM

3. **Structure Generation**:
   - Constructs a detailed prompt with new repo metadata and similar examples
   - Sends prompt to Claude API
   - Validates and returns the generated JSON structure

## Configuration

### Environment Variables

- `ANTHROPIC_API_KEY`: Required for LLM generation

### Model Configuration

The system uses `all-MiniLM-L6-v2` by default for embeddings. You can change this in the constructor:

```python
generator = DocStructureGenerator("knowledge_base.pkl", model_name="your_preferred_model")
```

## Output

The system generates a JSON structure containing the ideal documentation sections for your repository. The structure is tailored to your project's:

- Business domain
- Technology stack
- Architecture
- Target audience

## Performance

- **Knowledge Base Building**: ~2-5 minutes for 200 repositories
- **Structure Generation**: <30 seconds per repository
- **Memory Usage**: ~500MB for 200 repository knowledge base

## Troubleshooting

### Common Issues

1. **"Knowledge base file not found"**:
   - Run `python main.py build` first

2. **"ANTHROPIC_API_KEY not set"**:
   - Set your API key: `export ANTHROPIC_API_KEY="your_key"`

3. **"No analysis files found"**:
   - Ensure your `*_analysis.json` files are in `/data/repo_metadata/`

4. **"Invalid JSON response from LLM"**:
   - Check your API key and internet connection
   - Claude might return malformed JSON occasionally

### Logging

The system provides detailed logging. To see debug information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Follow the existing code structure
2. Add type hints to all functions
3. Include comprehensive error handling
4. Update tests for new features
5. Document any new configuration options

## License

This project is part of the ADocS system for automated documentation generation.
