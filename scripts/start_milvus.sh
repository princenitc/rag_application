#!/bin/bash

# Script to start Milvus using Docker Compose
# This ensures all dependencies are properly started

set -e

echo "=========================================="
echo "Starting Milvus with Docker Compose"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed."
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Stop any existing containers
echo ""
echo "Stopping any existing Milvus containers..."
docker-compose down 2>/dev/null || true

# Start services
echo ""
echo "Starting Milvus services..."
docker-compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to be healthy..."
echo "This may take 30-60 seconds..."

max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker-compose ps | grep -q "Up (healthy)"; then
        echo ""
        echo "✓ Services are healthy!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo -n "."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo ""
    echo "Warning: Services did not become healthy within expected time."
    echo "Check logs with: docker-compose logs"
fi

# Show status
echo ""
echo "=========================================="
echo "Container Status:"
echo "=========================================="
docker-compose ps

# Test connection
echo ""
echo "Testing Milvus connection..."
if curl -s http://localhost:9091/healthz > /dev/null; then
    echo "✓ Milvus is responding on port 9091"
else
    echo "✗ Milvus is not responding yet. Check logs with: docker-compose logs standalone"
fi

echo ""
echo "=========================================="
echo "Milvus Setup Complete!"
echo "=========================================="
echo ""
echo "Milvus is running on: localhost:19530"
echo "MinIO console: http://localhost:9001 (minioadmin/minioadmin)"
echo ""
echo "Useful commands:"
echo "  View logs:    docker-compose logs -f standalone"
echo "  Stop Milvus:  docker-compose down"
echo "  Restart:      docker-compose restart"
echo ""

# Made with Bob
