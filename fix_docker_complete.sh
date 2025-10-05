#!/bin/bash

echo "🔧 Complete Docker Fix Script"
echo "============================="

# Fix permissions
echo "🔧 Fixing Docker permissions..."
sudo usermod -aG docker $USER
sudo systemctl restart docker

echo "⚠️  Please run: newgrp docker"
echo "   Or log out and log back in"
echo "   Then press Enter to continue..."
read -p "Press Enter when Docker permissions are fixed..."

# Test Docker access
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker access still not working. Please fix permissions first."
    exit 1
fi

echo "✅ Docker access working!"

# Stop containers
echo "🛑 Stopping containers..."
docker compose down --volumes --remove-orphans

# Fix port in docker-compose.yml
echo "🔧 Fixing PostgreSQL port..."
sed -i 's/"5433:5432"/"5432:5432"/' docker-compose.yml

# Rebuild
echo "🔨 Rebuilding containers..."
docker compose build --no-cache

# Start
echo "🚀 Starting system..."
docker compose up -d

# Check status
echo "📊 Checking status..."
docker compose ps

echo "🎉 Fix complete! Check logs with: docker compose logs app"
