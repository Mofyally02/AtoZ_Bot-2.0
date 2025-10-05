#!/bin/bash

echo "🔧 FINAL DOCKER FIX SCRIPT"
echo "========================="

# Step 1: Fix Docker permissions
echo "🔧 Fixing Docker permissions..."
sudo usermod -aG docker $USER
sudo systemctl restart docker

echo "⚠️  CRITICAL: You must run 'newgrp docker' or log out/in"
echo "   Then press Enter to continue..."
read -p "Press Enter when Docker permissions are fixed..."

# Test Docker access
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker access still not working!"
    echo "   Please run: newgrp docker"
    echo "   Or log out and log back in"
    exit 1
fi

echo "✅ Docker access working!"

# Step 2: Fix database connection
echo "🔧 Fixing database connection configuration..."
sed -i 's/@localhost:5432/@database:5432/' backend/app/database/connection.py

# Step 3: Stop and clean everything
echo "🛑 Stopping and cleaning containers..."
docker compose down --volumes --remove-orphans
docker system prune -f

# Step 4: Rebuild from scratch
echo "🔨 Rebuilding everything from scratch..."
docker compose build --no-cache

# Step 5: Start the system
echo "🚀 Starting the system..."
docker compose up -d

# Step 6: Check status
echo "📊 Checking status..."
sleep 10
docker compose ps
docker compose logs app --tail=20

echo "🎉 Complete fix applied!"
echo "📋 Check logs with: docker compose logs app"
