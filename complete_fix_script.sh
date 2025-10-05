#!/bin/bash

echo "🔧 Complete Fix Script"
echo "====================="

echo "⚠️  CRITICAL: You must run 'newgrp docker' in a NEW terminal first!"
echo "   Or log out and log back in"
echo ""
read -p "Press Enter when Docker permissions are fixed..."

# Test Docker access
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker access not working!"
    echo "   Please run: newgrp docker"
    exit 1
fi

echo "✅ Docker access working!"

# Clean everything
echo "🛑 Cleaning containers..."
docker compose down --volumes --remove-orphans
docker system prune -f

# Rebuild
echo "🔨 Rebuilding with all fixes..."
docker compose build --no-cache

# Start
echo "🚀 Starting system..."
docker compose up -d

# Wait and check
echo "⏳ Waiting for services..."
sleep 15

echo "📊 Checking status..."
docker compose ps

echo "📋 Backend logs:"
docker compose logs app --tail=20

echo "🧪 Testing health check..."
curl -f http://localhost:8000/health || echo "Health check failed"

echo "🎉 Complete fix applied!"
