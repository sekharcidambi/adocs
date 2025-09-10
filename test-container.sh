#!/bin/bash

# Test script for ADocS container

set -e

echo "🧪 Testing ADocS container locally..."

# Build the container
echo "🏗️  Building container..."
docker build -t adocs-test .

# Run the container in background
echo "🚀 Starting container..."
docker run -d \
  --name adocs-test-container \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY="test-key" \
  -e GITHUB_TOKEN="test-token" \
  adocs-test

# Wait for container to start
echo "⏳ Waiting for container to start..."
sleep 10

# Test health endpoint
echo "🔍 Testing health endpoint..."
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ Health check passed!"
else
    echo "❌ Health check failed!"
    docker logs adocs-test-container
    exit 1
fi

# Test root endpoint
echo "🔍 Testing root endpoint..."
if curl -f -s http://localhost:8000/ > /dev/null; then
    echo "✅ Root endpoint working!"
else
    echo "❌ Root endpoint failed!"
fi

# Show container logs
echo "📋 Container logs:"
docker logs adocs-test-container

# Cleanup
echo "🧹 Cleaning up..."
docker stop adocs-test-container
docker rm adocs-test-container

echo "✅ Container test completed successfully!"
