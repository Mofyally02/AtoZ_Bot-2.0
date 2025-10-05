#!/bin/bash

echo "🔧 Fixing Docker Permissions and Rebuilding Container..."
echo "=================================================="

# Step 1: Fix Docker permissions
echo "🔧 Step 1: Adding user to docker group..."
sudo usermod -aG docker $USER

echo "🔧 Step 2: Restarting Docker daemon..."
sudo systemctl restart docker
sudo systemctl enable docker

echo "⚠️  Step 3: You need to log out and log back in for group changes to take effect"
echo "   Or run: newgrp docker"
echo ""

# Step 4: Wait for user to fix permissions
echo "⏳ Waiting for Docker permissions to be fixed..."
echo "   Please run: newgrp docker"
echo "   Or log out and log back in"
echo "   Then press Enter to continue..."
read -p "Press Enter when Docker permissions are fixed..."

# Step 5: Test Docker access
echo "🧪 Testing Docker access..."
if docker ps > /dev/null 2>&1; then
    echo "✅ Docker access working!"
else
    echo "❌ Docker access still not working. Please fix permissions first."
    exit 1
fi

# Step 6: Stop existing containers
echo "🛑 Stopping existing containers..."
docker compose down

# Step 7: Rebuild with fixed code
echo "🔨 Rebuilding containers with fixed code..."
docker compose build --no-cache

# Step 8: Start the system
echo "🚀 Starting the system..."
docker compose up -d

# Step 9: Check status
echo "📊 Checking container status..."
docker compose ps

echo "🎉 Docker container rebuilt with fixed imports!"
echo "✅ Your system should now work without import errors!"
