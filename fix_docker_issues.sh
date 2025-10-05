#!/bin/bash

echo "🔧 Docker Issues Fix Script"
echo "=========================="

echo "⚠️  Make sure Docker permissions are fixed first!"
echo "   Run: newgrp docker (in new terminal)"
echo ""
read -p "Press Enter when Docker permissions are fixed..."

# Fix service name issue
echo "🔧 Fixing database connection..."
sed -i 's/@database:5432/@atoz-database:5432/' backend/app/database/connection.py

# Stop and clean
echo "🛑 Stopping containers..."
docker compose down --volumes --remove-orphans

# Rebuild
echo "🔨 Rebuilding with all fixes..."
docker compose build --no-cache

# Start
echo "🚀 Starting system..."
docker compose up -d

# Check status
echo "📊 Checking status..."
sleep 10
docker compose ps

echo "📋 Backend logs:"
docker compose logs app --tail=20

echo "🧪 Testing health check..."
curl -f http://localhost:8000/health || echo "Health check failed"

echo "🎉 Fix complete!"
