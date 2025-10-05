#!/bin/bash

# Fix Docker Permissions Script
# This script helps fix Docker permission issues

echo "🔧 Fixing Docker Permissions..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if user is already in docker group
if groups $USER | grep -q '\bdocker\b'; then
    echo "✅ User $USER is already in docker group"
else
    echo "🔧 Adding user $USER to docker group..."
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    echo "✅ User added to docker group"
    echo "⚠️  Please log out and log back in, or run 'newgrp docker'"
    echo "⚠️  Then restart your terminal session"
fi

# Check Docker daemon status
echo "🔍 Checking Docker daemon status..."
if sudo systemctl is-active --quiet docker; then
    echo "✅ Docker daemon is running"
else
    echo "🔧 Starting Docker daemon..."
    sudo systemctl start docker
    sudo systemctl enable docker
    echo "✅ Docker daemon started and enabled"
fi

# Test Docker access
echo "🧪 Testing Docker access..."
if docker ps &> /dev/null; then
    echo "✅ Docker access is working"
else
    echo "❌ Docker access still not working"
    echo "💡 Try running: newgrp docker"
    echo "💡 Or log out and log back in"
fi

echo "🎉 Docker permissions setup complete!"
