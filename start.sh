#!/bin/bash

# Production startup script for ADocS service

set -e

echo "🚀 Starting ADocS service..."

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1
export TRANSFORMERS_CACHE=/app/.cache/transformers
export HF_HOME=/app/.cache/huggingface

# Create necessary directories
mkdir -p /app/generated_docs
mkdir -p /app/generated_wiki_docs
mkdir -p /app/data
mkdir -p /app/.cache/transformers
mkdir -p /app/.cache/huggingface

# Download knowledge base from GCS if not exists
if [ ! -f "/app/knowledge_base.pkl" ]; then
    echo "📥 Downloading knowledge base from GCS..."
    python -c "
import os
from google.cloud import storage

try:
    # Initialize GCS client
    client = storage.Client()
    bucket = client.bucket('adocs-backend-adocs-storage')
    blob = bucket.blob('knowledge/knowledge_base.pkl')
    
    # Download the knowledge base
    blob.download_to_filename('/app/knowledge_base.pkl')
    print('✅ Knowledge base downloaded successfully from GCS')
    
except Exception as e:
    print(f'⚠️  Failed to download knowledge base from GCS: {e}')
    print('Creating placeholder knowledge base...')
    
    # Create a minimal knowledge base structure as fallback
    import pickle
    kb = {'entries': [], 'embeddings': [], 'metadata': []}
    with open('/app/knowledge_base.pkl', 'wb') as f:
        pickle.dump(kb, f)
    print('Placeholder knowledge base created')
"
fi

# Start the FastAPI service with Gunicorn for production
echo "🌐 Starting FastAPI service on port 8000..."
exec gunicorn fastapi_service_gcs:app \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 1000 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 3600 \
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
