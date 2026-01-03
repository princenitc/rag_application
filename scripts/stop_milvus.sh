#!/bin/bash

# Script to stop Milvus services

set -e

echo "=========================================="
echo "Stopping Milvus Services"
echo "=========================================="

# Stop services
docker-compose down

echo ""
echo "✓ Milvus services stopped"
echo ""
echo "To remove all data and start fresh, run:"
echo "  docker-compose down -v"
echo ""

# Made with Bob
