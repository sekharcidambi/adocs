# API Key Migration: Frontend to Backend

## Overview

All API keys have been moved from the frontend to the backend ADocS services. The frontend no longer handles external API calls or manages API keys.

## Changes Made

### Frontend Changes

1. **Removed API Key Passing**: Frontend APIs no longer pass `GITHUB_TOKEN` or `ANTHROPIC_API_KEY` to backend services
2. **Updated Environment**: Frontend `.env` no longer needs API keys
3. **Simplified API Calls**: Frontend only passes the GitHub repository URL to backend services

### Backend Changes

1. **Internal API Key Management**: All backend services now handle API keys internally via environment variables
2. **Updated Service Constructors**: Services no longer accept API keys as parameters
3. **Environment Configuration**: Backend services read API keys from their own environment

## Architecture

### Before (Frontend Managed API Keys)
```
Frontend (Next.js) → GitHub API + Claude API
Frontend (Next.js) → Backend Services (with API keys)
```

### After (Backend Managed API Keys)
```
Frontend (Next.js) → Backend Services (no API keys)
Backend Services → GitHub API + Claude API
```

## Configuration

### Frontend Environment (.env)
```bash
# No API keys needed in frontend
# All external API calls are handled by backend services
```

### Backend Environment (backend_env_example)
```bash
# GitHub API Token (optional but recommended)
GITHUB_TOKEN=your_github_token_here

# Anthropic Claude API Key (required for AI features)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Python Path Configuration
PYTHONPATH=/Users/sekharcidambi/adocs
```

## Service Updates

### 1. Comprehensive ADocS Service
- **File**: `comprehensive_adocs_service.py`
- **Changes**: Removed API key parameters from constructor and main function
- **Usage**: `python comprehensive_adocs_service.py analyze <github_url>`

### 2. Wiki Generation Service
- **File**: `wiki_generation_service.py`
- **Changes**: Removed API key parameters from constructor and main function
- **Usage**: `python wiki_generation_service.py generate <github_url>`

### 3. Documentation Retrieval Service
- **File**: `documentation_retrieval_service.py`
- **Changes**: No API keys needed (file system operations only)
- **Usage**: `python documentation_retrieval_service.py structure <repo_url>`

## Frontend API Updates

### 1. Analyze Repository API
- **File**: `app/api/analyze-repo/route.ts`
- **Changes**: Removed API key passing to backend service
- **Input**: Only GitHub repository URL

### 2. Generate Wiki API
- **File**: `app/api/generate-wiki/route.ts`
- **Changes**: Removed API key passing to backend service
- **Input**: Only GitHub repository URL

### 3. Get Documentation API
- **File**: `app/api/get-documentation/route.ts`
- **Changes**: No changes needed (no API keys used)
- **Input**: Repository URL and optional section/type parameters

## Benefits

1. **Security**: API keys are no longer exposed in frontend code
2. **Separation of Concerns**: Frontend handles UI, backend handles external APIs
3. **Scalability**: Backend services can be deployed independently
4. **Maintainability**: API key management centralized in backend
5. **Flexibility**: Different environments can have different API key configurations

## Setup Instructions

### For Development

1. **Frontend Setup**:
   ```bash
   cd /Users/sekharcidambi/gwiki
   # No API keys needed in .env
   ```

2. **Backend Setup**:
   ```bash
   cd /Users/sekharcidambi/adocs
   cp backend_env_example .env
   # Edit .env with your API keys
   ```

### For Production

1. **Frontend**: Deploy without API keys
2. **Backend**: Deploy with API keys in environment variables
3. **Environment Variables**: Set `GITHUB_TOKEN` and `ANTHROPIC_API_KEY` in backend environment

## Testing

All test scripts have been updated to work without passing API keys:

```bash
# Test comprehensive service
python test_comprehensive_service.py

# Test wiki generation service
python test_wiki_service.py

# Test documentation retrieval service
python test_documentation_retrieval.py
```

## Migration Complete

✅ Frontend no longer manages API keys
✅ Backend services handle all external API calls
✅ Environment configuration separated
✅ Security improved
✅ Architecture simplified
