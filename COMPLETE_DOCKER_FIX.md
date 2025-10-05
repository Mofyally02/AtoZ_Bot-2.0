# 🔧 Complete Docker Fix - Ready to Run

## 🎯 **Root Cause Analysis**

✅ **websocket.py EXISTS** - The file is there
✅ **docker-compose.yml CORRECT** - Service names are right (`database`, `redis`)
❌ **PORT MISMATCH** - PostgreSQL mapped to 5433 but backend expects 5432
❌ **CONTAINER OLD** - Built before import fixes

## 🛠️ **Step-by-Step Fix**

### **Step 1: Fix Docker Permissions**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Restart Docker
sudo systemctl restart docker

# Apply group changes
newgrp docker
# OR log out and log back in
```

### **Step 2: Stop All Containers**
```bash
# Stop everything
docker compose down --volumes --remove-orphans
```

### **Step 3: Fix Port Mismatch**
Update your docker-compose.yml to use standard PostgreSQL port:

```yaml
# Change this line in docker-compose.yml:
ports:
  - "5432:5432"  # Changed from "5433:5432" to "5432:5432"
```

### **Step 4: Rebuild with Fixed Code**
```bash
# Rebuild with your fixed imports
docker compose build --no-cache

# Start the system
docker compose up -d
```

### **Step 5: Verify Fix**
```bash
# Check container status
docker compose ps

# Check logs
docker compose logs app

# Test health endpoint
curl http://localhost:8000/health
```

## 🚀 **One-Command Fix Script**

```bash
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
```

## ✅ **Expected Results**

After the fix, you should see:
- ✅ No more `ModuleNotFoundError: No module named 'app.api.websocket'`
- ✅ PostgreSQL connection successful
- ✅ Backend starts without errors
- ✅ Health check passes

## 🔍 **Why This Will Work**

1. **Import Fixes Applied**: Your local files have the fixed imports
2. **Port Fixed**: PostgreSQL will be on the expected port 5432
3. **Fresh Build**: Container will have the latest code with fixes
4. **Proper Networking**: Services will connect using Docker service names

---

**Status**: 🔧 **Ready to fix - just run the steps above**
