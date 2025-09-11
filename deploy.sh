#!/bin/bash

# ADocS Google Cloud Deployment Script
# Comprehensive deployment script with production-ready configuration
# 
# Features:
# - Docker build optimizations with caching
# - Extended timeout support for long-running AI analyses
# - Production resource allocation (4GB RAM, 4 CPU cores)
# - Comprehensive secret and environment management
# - Health checks and deployment validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${PROJECT_ID:-"your-project-id"}
REGION=${REGION:-"us-central1"}
SERVICE_NAME="adocs"
CONFIG_FILE="cloudbuild.yaml"

echo -e "${GREEN}🚀 Starting ADocS deployment to Google Cloud${NC}"
echo -e "${BLUE}📋 Configuration:${NC}"
echo -e "   Project ID: ${PROJECT_ID}"
echo -e "   Region: ${REGION}"
echo -e "   Service: ${SERVICE_NAME}"
echo -e "   Config: ${CONFIG_FILE}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    echo -e "${YELLOW}   Install from: https://cloud.google.com/sdk/docs/install${NC}"
    exit 1
fi

# Check if user is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo -e "${YELLOW}⚠️  Not authenticated with gcloud. Please run: gcloud auth login${NC}"
    exit 1
fi

# Set the project
echo -e "${YELLOW}📋 Setting project to: ${PROJECT_ID}${NC}"
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Create secrets if they don't exist
echo -e "${YELLOW}🔐 Setting up secrets...${NC}"

# Check if ANTHROPIC_API_KEY secret exists
if ! gcloud secrets describe anthropic-api-key &> /dev/null; then
    echo -e "${YELLOW}Creating ANTHROPIC_API_KEY secret...${NC}"
    echo "Please enter your Anthropic API key:"
    read -s ANTHROPIC_KEY
    echo -n "$ANTHROPIC_KEY" | gcloud secrets create anthropic-api-key --data-file=-
    echo -e "${GREEN}✅ ANTHROPIC_API_KEY secret created${NC}"
else
    echo -e "${GREEN}✅ ANTHROPIC_API_KEY secret already exists${NC}"
fi

# Check if GITHUB_TOKEN secret exists
if ! gcloud secrets describe github-token &> /dev/null; then
    echo -e "${YELLOW}Creating GITHUB_TOKEN secret...${NC}"
    echo "Please enter your GitHub token (optional, press Enter to skip):"
    read -s GITHUB_KEY
    if [ ! -z "$GITHUB_KEY" ]; then
        echo -n "$GITHUB_KEY" | gcloud secrets create github-token --data-file=-
        echo -e "${GREEN}✅ GITHUB_TOKEN secret created${NC}"
    else
        echo -e "${YELLOW}⚠️  Skipping GitHub token creation${NC}"
    fi
else
    echo -e "${GREEN}✅ GITHUB_TOKEN secret already exists${NC}"
fi

# Build and deploy using Cloud Build
echo -e "${YELLOW}🏗️  Building and deploying with Cloud Build...${NC}"
echo -e "${BLUE}   Using optimized configuration with Docker caching and extended timeout${NC}"
gcloud builds submit --config $CONFIG_FILE .

# Get the service URL
echo -e "${YELLOW}🔍 Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)")

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${GREEN}🌐 Service Information:${NC}"
echo -e "   URL: ${SERVICE_URL}"
echo -e "   Health: ${SERVICE_URL}/health"
echo -e "   API Docs: ${SERVICE_URL}/docs"
echo ""
echo -e "${BLUE}🔧 Service Configuration:${NC}"
echo -e "   Memory: 4GB"
echo -e "   CPU: 4 cores"
echo -e "   Timeout: 60 minutes"
echo -e "   Min Instances: 1 (warm start)"
echo -e "   Max Instances: 5"
echo -e "   Concurrency: 1 (prevents timeouts)"
echo ""

# Test the deployment
echo -e "${YELLOW}🧪 Testing deployment...${NC}"
if curl -f -s "${SERVICE_URL}/health" > /dev/null; then
    echo -e "${GREEN}✅ Health check passed!${NC}"
else
    echo -e "${RED}❌ Health check failed. Check the logs:${NC}"
    echo "   gcloud run logs read $SERVICE_NAME --region=$REGION"
    echo ""
    echo -e "${YELLOW}📝 Useful commands:${NC}"
    echo "   View logs: gcloud run logs tail $SERVICE_NAME --region=$REGION"
    echo "   Service status: gcloud run services describe $SERVICE_NAME --region=$REGION"
    echo "   Update service: gcloud run services update $SERVICE_NAME --region=$REGION"
fi

echo ""
echo -e "${GREEN}🎉 ADocS is now deployed and running on Google Cloud Run!${NC}"
