# ADocS Google Cloud Deployment Guide

This guide explains how to deploy the ADocS service to Google Cloud Run with an optimized Docker container.

## Prerequisites

1. **Google Cloud CLI**: Install and configure the gcloud CLI
   ```bash
   # Install gcloud CLI (if not already installed)
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   
   # Authenticate
   gcloud auth login
   gcloud auth configure-docker
   ```

2. **Required APIs**: Enable the following APIs in your Google Cloud project:
   - Cloud Build API
   - Cloud Run API
   - Container Registry API

3. **API Keys**: You'll need:
   - Anthropic API key (required)
   - GitHub token (optional, for private repositories)

## Quick Deployment

### Option 1: Automated Deployment Script

1. Set your project ID:
   ```bash
   export PROJECT_ID="your-google-cloud-project-id"
   ```

2. Run the deployment script:
   ```bash
   ./deploy.sh
   ```

The script will:
- Enable required APIs
- Create secrets for API keys
- Build and deploy the container
- Provide the service URL

### Option 2: Manual Deployment

1. **Set up secrets**:
   ```bash
   # Create Anthropic API key secret
   echo -n "your-anthropic-api-key" | gcloud secrets create anthropic-api-key --data-file=-
   
   # Create GitHub token secret (optional)
   echo -n "your-github-token" | gcloud secrets create github-token --data-file=-
   ```

2. **Build and deploy**:
   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

## Container Optimization Features

### Multi-stage Build
- **Builder stage**: Installs dependencies and builds packages
- **Runtime stage**: Contains only runtime dependencies
- **Result**: Smaller final image size

### Optimized Dependencies
- CPU-only versions of ML libraries (no CUDA)
- Specific version pinning for reproducibility
- Minimal runtime dependencies

### Security Features
- Non-root user execution
- Minimal base image (python:3.11-slim)
- No unnecessary system packages

### Performance Features
- Gunicorn with Uvicorn workers for production
- Health checks for container orchestration
- Optimized memory and CPU allocation

## Configuration

### Environment Variables
The service uses the following environment variables:
- `ANTHROPIC_API_KEY`: Required for AI content generation
- `GITHUB_TOKEN`: Optional, for accessing private repositories
- `PYTHONUNBUFFERED=1`: Ensures Python output is not buffered

### Resource Allocation
Default Cloud Run configuration:
- **Memory**: 2GB
- **CPU**: 2 vCPUs
- **Max instances**: 10
- **Min instances**: 0
- **Timeout**: 300 seconds
- **Concurrency**: 80 requests per instance

## Monitoring and Logs

### View logs:
```bash
gcloud run logs read adocs --region=us-central1
```

### Monitor metrics:
- Go to Google Cloud Console → Cloud Run → adocs service
- View metrics, logs, and performance data

## Scaling

The service automatically scales based on demand:
- **Min instances**: 0 (scales to zero when not in use)
- **Max instances**: 10 (configurable in cloudbuild.yaml)
- **Concurrency**: 80 requests per instance

## Cost Optimization

### Features that reduce costs:
1. **Scale to zero**: No cost when not in use
2. **Optimized container**: Smaller image = faster cold starts
3. **Efficient resource usage**: Right-sized memory and CPU
4. **No CUDA dependencies**: Reduced image size and complexity

### Estimated costs:
- **Idle time**: $0 (scales to zero)
- **Active usage**: ~$0.10-0.50 per hour depending on traffic
- **Storage**: Minimal (only application code and generated docs)

## Troubleshooting

### Common Issues:

1. **Build fails**: Check that all required APIs are enabled
2. **Service won't start**: Check logs for missing environment variables
3. **API calls fail**: Verify secrets are properly configured
4. **Memory issues**: Increase memory allocation in cloudbuild.yaml

### Debug commands:
```bash
# Check service status
gcloud run services describe adocs --region=us-central1

# View recent logs
gcloud run logs read adocs --region=us-central1 --limit=50

# Test health endpoint
curl https://your-service-url/health
```

## Local Development

To test the container locally:

```bash
# Build the image
docker build -t adocs .

# Run locally
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY="your-key" \
  -e GITHUB_TOKEN="your-token" \
  adocs
```

## API Endpoints

Once deployed, the service provides:
- `GET /health` - Health check
- `GET /` - API information
- `GET /api/repositories` - List repositories
- `GET /api/documentation` - Get documentation
- `POST /api/analyze` - Analyze repository
- `POST /api/generate-wiki` - Generate wiki

## Security Notes

- API keys are stored as Google Cloud secrets
- Service runs as non-root user
- No sensitive data in container image
- HTTPS enforced by Cloud Run
- CORS configured for web access

## Updates and Maintenance

To update the service:
1. Make code changes
2. Run `./deploy.sh` again
3. Cloud Build will create a new image and deploy it

The deployment is zero-downtime with Cloud Run's rolling updates.
