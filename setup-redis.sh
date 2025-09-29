#!/bin/bash

# Redis Setup Script for AtoZ Bot Dashboard
echo "🔧 Setting up Redis for AtoZ Bot Dashboard..."

# Check if Redis is already installed
if command -v redis-server &> /dev/null; then
    echo "✅ Redis is already installed"
    redis-server --version
else
    echo "📦 Installing Redis..."
    
    # Update package list
    sudo apt update
    
    # Install Redis
    sudo apt install -y redis-server
    
    # Enable Redis to start on boot
    sudo systemctl enable redis-server
    
    echo "✅ Redis installed successfully"
fi

# Start Redis service
echo "🚀 Starting Redis service..."
sudo systemctl start redis-server

# Check if Redis is running
if sudo systemctl is-active --quiet redis-server; then
    echo "✅ Redis is running"
else
    echo "❌ Failed to start Redis"
    exit 1
fi

# Test Redis connection
echo "🧪 Testing Redis connection..."
if redis-cli ping | grep -q "PONG"; then
    echo "✅ Redis connection test successful"
else
    echo "❌ Redis connection test failed"
    exit 1
fi

# Configure Redis for production (optional)
echo "⚙️  Configuring Redis..."

# Create Redis configuration backup
sudo cp /etc/redis/redis.conf /etc/redis/redis.conf.backup

# Set Redis to bind to localhost only (security)
sudo sed -i 's/^# bind 127.0.0.1/bind 127.0.0.1/' /etc/redis/redis.conf

# Set maxmemory policy (optional)
sudo sed -i 's/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/' /etc/redis/redis.conf

# Restart Redis to apply configuration
sudo systemctl restart redis-server

echo "✅ Redis configuration updated"

# Install Python Redis client
echo "🐍 Installing Python Redis client..."
cd /home/mofy/Desktop/Al-Tech\ Solutions/AtoZ_Bot-2.0/backend
source venv/bin/activate
pip install redis

echo "✅ Python Redis client installed"

# Test the Redis integration
echo "🧪 Testing Redis integration..."
python -c "
import redis
from app.database.connection import get_redis
try:
    r = get_redis()
    r.set('test_key', 'test_value')
    value = r.get('test_key')
    print(f'✅ Redis integration test successful: {value}')
    r.delete('test_key')
except Exception as e:
    print(f'❌ Redis integration test failed: {e}')
"

echo ""
echo "🎉 Redis setup complete!"
echo ""
echo "📋 Redis Information:"
echo "  - Service: redis-server"
echo "  - Port: 6379"
echo "  - Host: localhost"
echo "  - Status: $(sudo systemctl is-active redis-server)"
echo ""
echo "🔧 Management Commands:"
echo "  - Start: sudo systemctl start redis-server"
echo "  - Stop: sudo systemctl stop redis-server"
echo "  - Restart: sudo systemctl restart redis-server"
echo "  - Status: sudo systemctl status redis-server"
echo "  - CLI: redis-cli"
echo ""
echo "🚀 You can now use the Redis-based bot control system!"
