#!/bin/bash

# Enhanced ADocS Service Startup Script
# This script starts the enhanced FastAPI service with custom section injection

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Enhanced ADocS Service${NC}"

# Check if custom sections are enabled
if [ "${ENABLE_CUSTOM_SECTIONS:-true}" = "true" ]; then
    echo -e "${BLUE}📋 Custom sections: ENABLED${NC}"
    SERVICE_MODULE="fastapi_service_enhanced"
else
    echo -e "${YELLOW}📋 Custom sections: DISABLED (using basic service)${NC}"
    SERVICE_MODULE="fastapi_service_gcs"
fi

# Check if configuration file exists
CONFIG_FILE="${CONFIG_FILE_PATH:-config/repository_config.yaml}"
if [ -f "$CONFIG_FILE" ]; then
    echo -e "${GREEN}✅ Configuration file found: $CONFIG_FILE${NC}"
else
    echo -e "${YELLOW}⚠️  Configuration file not found: $CONFIG_FILE${NC}"
    echo -e "${YELLOW}   Custom sections will be disabled${NC}"
    SERVICE_MODULE="fastapi_service_gcs"
fi

# Display service information
echo -e "${BLUE}🔧 Service Configuration:${NC}"
echo -e "   Service Module: $SERVICE_MODULE"
echo -e "   Port: 8000"
echo -e "   Workers: 2"
echo -e "   Custom Sections: ${ENABLE_CUSTOM_SECTIONS:-true}"
echo -e "   Config File: $CONFIG_FILE"

# Start the appropriate FastAPI service
echo -e "${GREEN}🌐 Starting FastAPI service...${NC}"
exec gunicorn $SERVICE_MODULE:app \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 3600 \
    --keep-alive 2 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
