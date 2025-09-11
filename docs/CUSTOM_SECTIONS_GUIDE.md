# Custom Sections Injection Guide

This guide explains how to use the config-driven custom section injection feature in ADocS.

## 🎯 Overview

The custom section injection feature allows you to:
- Add custom sections to specific GitHub repositories
- Override default GCS paths for documentation
- Inject custom metadata and branding
- Control section priority and ordering
- Use different injection strategies

## 📁 Configuration Structure

### Repository Configuration File
Location: `config/repository_config.yaml`

```yaml
repositories:
  "https://github.com/facebook/react":
    custom_sections:
      - name: "Getting Started"
        gcs_path: "custom_docs/react/getting-started.md"
        priority: 1
        description: "Quick start guide for React development"
        icon: "🚀"
      - name: "Advanced Patterns"
        gcs_path: "custom_docs/react/advanced-patterns.md"
        priority: 5
        description: "Advanced React patterns and best practices"
        icon: "⚡"
    
    gcs_path_override: "custom_docs/react/"
    custom_metadata:
      maintainer: "Facebook"
      category: "Frontend Framework"
      difficulty: "Intermediate"
      tags: ["javascript", "frontend", "ui", "react"]

global_config:
  custom_docs_bucket: "adocs-custom-docs"
  fallback_to_generated: true
  cache_ttl: 3600
  enable_custom_sections: true
  injection_strategy: "prepend"  # prepend, append, replace, merge
```

## 🔧 Configuration Options

### Custom Section Properties
- **name**: Display name of the section
- **gcs_path**: Path to the markdown file in GCS
- **priority**: Order priority (lower numbers appear first)
- **description**: Section description for navigation
- **icon**: Emoji or icon for the section
- **enabled**: Whether the section is active

### Injection Strategies
1. **prepend**: Add custom sections at the beginning
2. **append**: Add custom sections at the end
3. **replace**: Replace generated sections with custom ones
4. **merge**: Merge custom sections with generated ones by name

### Global Configuration
- **custom_docs_bucket**: GCS bucket for custom documentation
- **fallback_to_generated**: Use generated docs when custom ones are missing
- **cache_ttl**: Cache time-to-live in seconds
- **enable_custom_sections**: Master switch for custom sections
- **injection_strategy**: Default injection strategy

## 🚀 Usage Examples

### 1. Basic Custom Section
```yaml
"https://github.com/your-org/your-repo":
  custom_sections:
    - name: "Quick Start"
      gcs_path: "custom_docs/your-repo/quick-start.md"
      priority: 1
      description: "Get started quickly"
      icon: "🚀"
```

### 2. Multiple Sections with Priority
```yaml
"https://github.com/your-org/your-repo":
  custom_sections:
    - name: "Overview"
      gcs_path: "custom_docs/your-repo/overview.md"
      priority: 1
      icon: "📋"
    - name: "Installation"
      gcs_path: "custom_docs/your-repo/installation.md"
      priority: 2
      icon: "⚙️"
    - name: "Advanced Usage"
      gcs_path: "custom_docs/your-repo/advanced.md"
      priority: 10
      icon: "⚡"
```

### 3. Custom Metadata and Branding
```yaml
"https://github.com/your-org/your-repo":
  custom_sections:
    - name: "Enterprise Guide"
      gcs_path: "custom_docs/your-repo/enterprise.md"
      priority: 1
      icon: "🏢"
  
  custom_metadata:
    maintainer: "Your Organization"
    category: "Enterprise Software"
    difficulty: "Advanced"
    tags: ["enterprise", "scalable", "production"]
    branding:
      primary_color: "#0066cc"
      logo_url: "https://your-org.com/logo.png"
```

## 🔄 API Endpoints

### Get Enhanced Documentation
```bash
# Get complete documentation with custom sections
GET /api/documentation?repo=https://github.com/facebook/react

# Get specific custom section
GET /api/documentation?repo=https://github.com/facebook/react&section=Getting%20Started
```

### Configuration Management
```bash
# Get all repository configurations
GET /api/config/repositories

# Get specific repository configuration
GET /api/config/repositories/facebook_react

# Reload configuration
POST /api/config/reload

# Validate configuration
GET /api/config/validate
```

## 📊 Response Format

### Enhanced Documentation Response
```json
{
  "success": true,
  "repository": "https://github.com/facebook/react",
  "documentationStructure": {
    "sections": [
      {
        "name": "Getting Started",
        "content": "# Getting Started\n\nWelcome to React...",
        "description": "Quick start guide for React development",
        "icon": "🚀",
        "priority": 1,
        "is_custom": true,
        "gcs_path": "custom_docs/react/getting-started.md"
      }
    ]
  },
  "injection_info": {
    "strategy": "prepend",
    "custom_sections_count": 3,
    "custom_docs_bucket": "adocs-custom-docs"
  },
  "custom_metadata": {
    "maintainer": "Facebook",
    "category": "Frontend Framework"
  }
}
```

## 🛠️ Setup Instructions

### 1. Create Configuration Directory
```bash
mkdir -p config
```

### 2. Create Repository Configuration
```bash
# Copy the example configuration
cp docs/CUSTOM_SECTIONS_GUIDE.md config/repository_config.yaml
```

### 3. Set Up Custom Docs Bucket
```bash
# Create GCS bucket for custom docs
gsutil mb gs://adocs-custom-docs
```

### 4. Upload Custom Documentation
```bash
# Upload your custom markdown files
gsutil cp custom_docs/react/getting-started.md gs://adocs-custom-docs/custom_docs/react/
```

### 5. Update Environment Variables
```bash
# Add to your .env file
CUSTOM_DOCS_BUCKET=adocs-custom-docs
ENABLE_CUSTOM_SECTIONS=true
```

### 6. Start Enhanced Service
```bash
# Use the enhanced FastAPI service
python fastapi_service_enhanced.py
```

## 🔍 Troubleshooting

### Common Issues

1. **Custom sections not appearing**
   - Check if `ENABLE_CUSTOM_SECTIONS=true`
   - Verify repository URL matches exactly in config
   - Check GCS bucket permissions

2. **Section content not found**
   - Verify GCS path is correct
   - Check if file exists in custom docs bucket
   - Enable `fallback_to_generated: true`

3. **Configuration not loading**
   - Check YAML syntax
   - Use `/api/config/validate` endpoint
   - Check file permissions

4. **Cache issues**
   - Clear cache with `/api/cache/clear`
   - Check cache TTL settings
   - Restart service

### Debug Commands
```bash
# Validate configuration
curl http://localhost:8000/api/config/validate

# Check repository config
curl http://localhost:8000/api/config/repositories/facebook_react

# Clear cache
curl -X POST http://localhost:8000/api/cache/clear

# Check health
curl http://localhost:8000/health
```

## 📈 Best Practices

1. **Use descriptive section names** that match your content
2. **Set appropriate priorities** for logical ordering
3. **Include helpful descriptions** for navigation
4. **Use consistent icons** for visual consistency
5. **Test with fallback enabled** initially
6. **Monitor cache performance** and adjust TTL as needed
7. **Validate configuration** before deploying
8. **Use version control** for configuration files

## 🔄 Migration from Basic Service

To migrate from the basic service to the enhanced service:

1. **Update imports** in your FastAPI app
2. **Add configuration file** with your custom sections
3. **Set up custom docs bucket** in GCS
4. **Update environment variables**
5. **Test with a few repositories** first
6. **Gradually roll out** to all repositories

The enhanced service is backward compatible and will work with existing generated documentation when no custom configuration is provided.
