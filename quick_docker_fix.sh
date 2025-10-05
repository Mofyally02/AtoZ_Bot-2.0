#!/bin/bash

echo "🔧 Quick Docker Fix for Port Conflict"
echo "====================================="

# Fix Docker permissions
echo "🔧 Fixing Docker permissions..."
sudo usermod -aG docker $USER
sudo systemctl restart docker

echo "⚠️  IMPORTANT: Run this command to apply group changes:"
echo "   newgrp docker"
echo ""
echo "   OR log out and log back in"
echo ""
echo "   Then run: docker compose up -d"
echo ""
echo "✅ Port conflicts fixed:"
echo "   - PostgreSQL: 5434:5432 (was 5432:5432)"
echo "   - Redis: 6381:6379 (was 6380:6379)"
echo ""
echo "🎯 Next steps:"
echo "   1. Run: newgrp docker"
echo "   2. Run: docker compose up -d"
echo "   3. Check: docker compose logs app"
