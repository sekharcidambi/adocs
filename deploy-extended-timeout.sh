#!/bin/bash

# Deploy ADocS with extended timeout configuration
# This script deploys the service with 60-minute timeout to handle long Claude API calls

set -e

echo "🚀 Deploying ADocS with extended timeout configuration..."

# Get the current project ID
PROJECT_ID=$(gcloud config get-value project)
echo "📋 Project ID: $PROJECT_ID"

# Build and deploy using the extended timeout configuration with optimizations
echo "🔨 Building and deploying with extended timeout and Docker optimizations..."
gcloud builds submit --config cloudbuild-extended-timeout.yaml .

echo "✅ Deployment completed!"
echo "🔧 Service configuration:"
echo "   - Timeout: 60 minutes (3600 seconds)"
echo "   - Memory: 4GB"
echo "   - CPU: 4 cores"
echo "   - Concurrency: 1 (prevents timeouts)"
echo "   - Min instances: 1 (avoids cold starts)"
echo "   - Docker build optimizations: ✅ (caching, BuildKit)"

echo ""
echo "📊 To check the deployment status:"
echo "   gcloud run services describe adocs --region=us-central1"

echo ""
echo "📝 To view logs:"
echo "   gcloud run services logs tail adocs --region=us-central1"
