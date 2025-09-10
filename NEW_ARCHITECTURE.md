# New ADocS Service Architecture

## Overview

The ADocS service architecture has been completely redesigned to provide a clean, frontend-focused interface that meets the specific requirements of the gwiki application. The new architecture is organized around four core services that directly map to frontend functionality.

## Architecture Design

### Core Principles

1. **Frontend-Focused**: Each service directly maps to frontend requirements
2. **Clean Separation**: Clear boundaries between different functionalities
3. **Unified Interface**: Single entry point (`adocs_service.py`) for all operations
4. **Consistent API**: All services follow the same patterns and return consistent responses
5. **Error Handling**: Comprehensive error handling with meaningful error messages

### Service Architecture

```
ADocS Service Architecture
├── adocs_service.py (Main Orchestrator)
├── services/
│   ├── base_service.py (Common Functionality)
│   ├── repository_service.py (Repository Operations)
│   ├── documentation_service.py (Documentation Access)
│   ├── analysis_service.py (Repository Analysis)
│   └── wiki_service.py (Wiki Generation)
└── Frontend API Routes
    ├── /api/get-repositories (GET)
    ├── /api/get-documentation (GET)
    ├── /api/analyze-repo (POST)
    └── /api/generate-wiki (POST)
```

## Core Services

### 1. RepositoryService (`services/repository_service.py`)

**Purpose**: Handles repository listing and metadata operations

**Frontend Mapping**: `getRepositories` functionality

**Key Methods**:
- `get_repositories(docs_type)`: Get list of repositories with cached docs
- `get_repository_info(repo_url, docs_type)`: Get detailed repository information

**Features**:
- Scans file system for cached documentation
- Supports both 'docs' and 'wiki' types
- Returns repository metadata and available sections
- Handles timestamp management for versioning

### 2. DocumentationService (`services/documentation_service.py`)

**Purpose**: Handles documentation retrieval and access operations

**Frontend Mapping**: `getDocumentation` functionality

**Key Methods**:
- `get_documentation(repo_url, docs_type)`: Get complete documentation structure
- `get_documentation_section(repo_url, section, docs_type)`: Get specific section content

**Features**:
- Retrieves complete documentation with all sections
- Supports section-specific retrieval
- Handles both 'docs' and 'wiki' types
- Provides structured content with metadata

### 3. AnalysisService (`services/analysis_service.py`)

**Purpose**: Handles repository analysis and documentation structure generation

**Frontend Mapping**: `analyze repo` functionality

**Key Methods**:
- `analyze_repository(repo_url)`: Complete repository analysis and documentation generation

**Features**:
- GitHub API integration for repository data
- Repository structure analysis (package.json, requirements.txt, etc.)
- Business domain detection
- Technology stack analysis
- Architecture pattern detection
- Enhanced content generation with Claude AI
- File system management with timestamped directories

### 4. WikiService (`services/wiki_service.py`)

**Purpose**: Handles wiki-style documentation generation from existing documentation

**Frontend Mapping**: `generate wiki` functionality

**Key Methods**:
- `generate_wiki(repo_url)`: Generate enhanced wiki-style documentation

**Features**:
- Document discovery (README, docs/, .md files)
- DeepWiki-style content enhancement
- Rate limiting and retry logic
- Structured output with summaries and improvements
- Enhanced content generation with Claude AI

## Main Service Orchestrator

### ADocSService (`adocs_service.py`)

**Purpose**: Main service orchestrator that provides a unified interface for all operations

**Key Methods**:
- `get_repositories(docs_type)`: Delegate to RepositoryService
- `get_documentation(repo_url, docs_type)`: Delegate to DocumentationService
- `get_documentation_section(repo_url, section, docs_type)`: Delegate to DocumentationService
- `analyze_repository(repo_url)`: Delegate to AnalysisService
- `generate_wiki(repo_url)`: Delegate to WikiService
- `get_repository_info(repo_url, docs_type)`: Delegate to RepositoryService

**Features**:
- Single entry point for all operations
- Consistent error handling
- Unified logging
- Environment variable management

## Frontend API Integration

### API Routes

#### 1. `/api/get-repositories` (GET)
- **Purpose**: Get list of repositories with cached documentation
- **Parameters**: `type` (optional, 'docs' or 'wiki')
- **Backend Service**: RepositoryService.get_repositories()
- **Response**: List of repositories with metadata

#### 2. `/api/get-documentation` (GET)
- **Purpose**: Get complete documentation for a repository
- **Parameters**: `repo`, `type` (optional, 'docs' or 'wiki')
- **Backend Service**: DocumentationService.get_documentation()
- **Response**: Complete documentation structure and content

#### 3. `/api/get-documentation` (GET) with section
- **Purpose**: Get specific documentation section
- **Parameters**: `repo`, `section`, `type` (optional, 'docs' or 'wiki')
- **Backend Service**: DocumentationService.get_documentation_section()
- **Response**: Section content and metadata

#### 4. `/api/analyze-repo` (POST)
- **Purpose**: Analyze repository and generate documentation structure
- **Parameters**: `repoUrl` (GitHub URL)
- **Backend Service**: AnalysisService.analyze_repository()
- **Response**: Analysis results and documentation structure

#### 5. `/api/generate-wiki` (POST)
- **Purpose**: Generate enhanced wiki-style documentation
- **Parameters**: `repoUrl` (GitHub URL)
- **Backend Service**: WikiService.generate_wiki()
- **Response**: Wiki generation results and enhanced pages

## File System Organization

### Directory Structure

```
adocs/
├── services/                    # Service modules
│   ├── __init__.py
│   ├── base_service.py         # Common functionality
│   ├── repository_service.py   # Repository operations
│   ├── documentation_service.py # Documentation access
│   ├── analysis_service.py     # Repository analysis
│   └── wiki_service.py         # Wiki generation
├── generated_docs/             # Generated documentation
│   └── owner_repo/
│       └── YYYYMMDD_HHMMSS/    # Timestamped versions
│           ├── README.md
│           ├── documentation_structure.json
│           ├── repository_metadata.json
│           └── *.md files
├── generated_wiki_docs/        # Generated wiki documentation
│   └── owner_repo/
│       └── YYYYMMDD_HHMMSS/    # Timestamped versions
│           ├── README.md
│           ├── wiki_metadata.json
│           └── *.md files
├── adocs_service.py            # Main orchestrator
└── test_new_architecture.py    # Test script
```

## Command Line Interface

The main service supports command-line operations:

```bash
# Get repositories
python adocs_service.py get-repositories [docs_type]

# Get documentation
python adocs_service.py get-documentation <repo_url> [docs_type]

# Get specific section
python adocs_service.py get-section <repo_url> <section> [docs_type]

# Analyze repository
python adocs_service.py analyze <repo_url>

# Generate wiki
python adocs_service.py generate-wiki <repo_url>

# Get repository info
python adocs_service.py get-info <repo_url> [docs_type]
```

## Response Format

All services return consistent JSON responses:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "metadata": { ... }
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... }
}
```

## Benefits of New Architecture

### 1. Clean Separation of Concerns
- Each service has a single, well-defined responsibility
- Clear boundaries between different functionalities
- Easy to maintain and extend

### 2. Frontend-Focused Design
- Direct mapping to frontend requirements
- Consistent API patterns
- Simplified integration

### 3. Unified Interface
- Single entry point for all operations
- Consistent error handling
- Unified logging and monitoring

### 4. Scalability
- Services can be deployed independently
- Easy to add new services
- Modular design supports growth

### 5. Maintainability
- Clear code organization
- Consistent patterns
- Comprehensive error handling

## Migration from Old Architecture

### Old Services (Deprecated)
- `comprehensive_adocs_service.py` → Replaced by `AnalysisService`
- `wiki_generation_service.py` → Replaced by `WikiService`
- `documentation_retrieval_service.py` → Replaced by `DocumentationService`
- `enhanced_adocs_service.py` → Functionality distributed across services

### New Services (Active)
- `RepositoryService` → New service for repository operations
- `DocumentationService` → Enhanced documentation access
- `AnalysisService` → Streamlined repository analysis
- `WikiService` → Focused wiki generation
- `ADocSService` → Main orchestrator

## Testing

### Test Script
Run the test script to verify the new architecture:

```bash
python test_new_architecture.py
```

### Test Coverage
- Repository listing and metadata
- Documentation retrieval
- Section-specific access
- Repository analysis
- Wiki generation
- Error handling

## Environment Variables

### Required
- `GITHUB_TOKEN`: GitHub API token for repository access
- `ANTHROPIC_API_KEY`: Anthropic API key for AI content generation

### Optional
- `PYTHONPATH`: Python path configuration

## Future Enhancements

### Planned Features
1. **Caching Layer**: Redis-based caching for improved performance
2. **Database Integration**: PostgreSQL for metadata storage
3. **API Rate Limiting**: Built-in rate limiting for external APIs
4. **Monitoring**: Comprehensive logging and monitoring
5. **Authentication**: User authentication and authorization
6. **Batch Operations**: Support for batch processing
7. **Webhooks**: Real-time updates via webhooks

### Service Extensions
1. **SearchService**: Full-text search across documentation
2. **ExportService**: Export documentation in various formats
3. **TemplateService**: Custom documentation templates
4. **AnalyticsService**: Usage analytics and insights

## Conclusion

The new ADocS service architecture provides a clean, maintainable, and scalable foundation for the gwiki application. It directly addresses the frontend requirements while maintaining flexibility for future enhancements. The modular design ensures easy maintenance and extension as the system grows.
