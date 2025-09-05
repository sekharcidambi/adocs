# Enhanced ADocS Service

This enhanced version of the ADocS service generates documentation structures and stores them as organized markdown files in a directory structure.

## Features

- **Documentation Structure Generation**: Uses the original ADocS RAG approach to generate documentation structures
- **Markdown File Storage**: Saves each documentation section as a separate markdown file
- **Organized Directory Structure**: Creates timestamped directories for each repository
- **Repository Metadata Storage**: Saves repository analysis as JSON files
- **Index File Generation**: Creates a README.md index file for easy navigation
- **Safe Filename Handling**: Sanitizes filenames for cross-platform compatibility

## Directory Structure

```
generated_docs/
├── apache_ofbiz-framework/
│   └── 20250105_143022/                    # Timestamped version
│       ├── README.md                       # Index file
│       ├── documentation_structure.json    # ADocS structure
│       ├── repository_metadata.json        # Repository analysis
│       ├── Purpose and Scope.md
│       ├── Enterprise Process Automation Capabilities.md
│       ├── High-Level Architecture.md
│       ├── Core Framework Components.md
│       └── ... (other sections)
└── other_repositories/
    └── ...
```

## Usage

### Command Line Interface

```bash
# Generate documentation for a repository
python enhanced_adocs_service.py generate '{"github_url": "https://github.com/user/repo", "overview": "...", "business_domain": "...", "architecture": {...}, "tech_stack": {...}}' [api_key]

# Get knowledge base statistics
python enhanced_adocs_service.py stats
```

### Python API

```python
from enhanced_adocs_service import EnhancedADocSService

# Initialize service
service = EnhancedADocSService()

# Repository metadata
repo_metadata = {
    "github_url": "https://github.com/user/repo",
    "overview": "Repository description",
    "business_domain": "Software Development",
    "architecture": {
        "pattern": "Microservices",
        "description": "Microservices architecture"
    },
    "tech_stack": {
        "languages": ["Python", "JavaScript"],
        "frontend": ["React"],
        "backend": ["FastAPI"],
        "databases": ["PostgreSQL"],
        "devops": ["Docker"]
    }
}

# Generate and store documentation
result = service.generate_and_store_documentation(repo_metadata)

print(f"Files saved to: {result['output_directory']}")
print(f"Created {len(result['files_created']['markdown_files'])} markdown files")
```

## Integration with Next.js API

To integrate this with the existing Next.js application, modify the `generateDocumentationStructure` function in `/api/analyze-repo/route.ts`:

```typescript
async function generateDocumentationStructure(repoAnalysis: any) {
  try {
    const { spawn } = require('child_process')
    
    const metadata = {
      github_url: repoAnalysis.github_repo,
      overview: repoAnalysis.overview,
      business_domain: repoAnalysis.business_domain,
      architecture: repoAnalysis.architecture,
      tech_stack: repoAnalysis.tech_stack
    }
    
    // Call the enhanced Python service
    const pythonProcess = spawn('/usr/local/bin/python3', [
      '/Users/sekharcidambi/adocs/enhanced_adocs_service.py',
      'generate',
      JSON.stringify(metadata),
      process.env.ANTHROPIC_API_KEY || ''
    ], {
      cwd: '/Users/sekharcidambi/adocs',
      env: { ...process.env, PYTHONPATH: '/Users/sekharcidambi/adocs' }
    })
    
    let output = ''
    let errorOutput = ''
    
    pythonProcess.stdout.on('data', (data) => {
      output += data.toString()
    })
    
    pythonProcess.stderr.on('data', (data) => {
      errorOutput += data.toString()
    })
    
    await new Promise((resolve, reject) => {
      pythonProcess.on('close', (code) => {
        if (code === 0) {
          resolve(output)
        } else {
          reject(new Error(`Python process exited with code ${code}: ${errorOutput}`))
        }
      })
    })
    
    const result = JSON.parse(output)
    
    // Return the documentation structure for the API
    return result.documentation_structure
    
  } catch (error) {
    console.error('Error calling enhanced ADocS service:', error)
    // Fallback logic...
  }
}
```

## File Contents

### Markdown Files

Each markdown file contains:
- Section title and description
- Repository-specific information
- Technology stack details
- Links to related sections
- Contextual information based on the section type

### JSON Files

- **`documentation_structure.json`**: Complete ADocS-generated structure
- **`repository_metadata.json`**: Repository analysis and metadata

### Index File

- **`README.md`**: Navigation index with links to all sections and repository information

## Benefits

1. **Persistent Storage**: Documentation is saved and can be versioned
2. **Easy Navigation**: Index file provides clear navigation structure
3. **Repository-Specific**: Content is tailored to each repository's context
4. **Versioned Output**: Timestamped directories allow for multiple versions
5. **Cross-Platform**: Safe filename handling works on all operating systems
6. **Integration Ready**: Can be easily integrated with existing systems

## Testing

Run the test script to see the service in action:

```bash
python test_enhanced_service.py
```

This will generate sample documentation for the Apache OFBiz repository and show you the file structure created.
