#!/bin/bash

# AtoZ Bot System Startup Script (PostgreSQL)
# Connects Database, API, WebSocket, and Bot components using PostgreSQL

echo "🚀 Starting AtoZ Bot System..."
echo "=================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down system..."
    docker-compose down
    pkill -f "uvicorn app.main:app"
    pkill -f "npm run dev"
    pkill -f "integrated_bot.py"
    echo "✅ System shutdown complete"
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "📦 Starting database and Redis services..."
docker-compose up -d database redis

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if database is ready
echo "🔍 Checking database connection..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T database pg_isready -U atoz_user -d atoz_bot_db > /dev/null 2>&1; then
        echo "✅ Database is ready"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Waiting for database... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Database failed to start within timeout"
    exit 1
fi

# Check if Redis is ready
echo "🔍 Checking Redis connection..."
max_attempts=15
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is ready"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Waiting for Redis... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Redis failed to start within timeout"
    exit 1
fi

echo "🐍 Starting backend server..."
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.dependencies_installed" ]; then
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
    touch venv/.dependencies_installed
fi

# Start backend server in background
echo "🚀 Starting FastAPI server..."
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

cd ..

# Wait for backend to be ready
echo "⏳ Waiting for backend server..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend server is ready"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Waiting for backend... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Backend server failed to start within timeout"
    cleanup
    exit 1
fi

echo "🌐 Starting frontend server..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend server in background
echo "🚀 Starting React development server..."
nohup npm run dev -- --host 0.0.0.0 --port 3000 > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

cd ..

# Wait for frontend to be ready
echo "⏳ Waiting for frontend server..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend server is ready"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "⏳ Waiting for frontend... (attempt $attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Frontend server failed to start within timeout"
    cleanup
    exit 1
fi

echo ""
echo "🎉 AtoZ Bot System Started Successfully!"
echo "========================================"
echo ""
echo "🌐 Access URLs:"
echo "  Frontend:    http://localhost:3000"
echo "  Backend API: http://localhost:8000"
echo "  API Docs:    http://localhost:8000/docs"
echo "  Health:      http://localhost:8000/health"
echo "  WebSocket:   ws://localhost:8000/ws"
echo ""
echo "📊 System Status:"
echo "  Database:    ✅ Running (PostgreSQL)"
echo "  Redis:       ✅ Running"
echo "  Backend:     ✅ Running (FastAPI)"
echo "  Frontend:    ✅ Running (React)"
echo "  WebSocket:   ✅ Available"
echo ""
echo "🤖 Bot Management:"
echo "  Start Bot:   curl -X POST http://localhost:8000/api/bot/toggle"
echo "  Bot Status:  curl http://localhost:8000/api/bot/status"
echo "  Stop Bot:    curl -X POST http://localhost:8000/api/bot/toggle"
echo ""
echo "📝 Logs:"
echo "  Backend:     logs/backend.log"
echo "  Frontend:    logs/frontend.log"
echo ""
echo "🛑 To stop the system, press Ctrl+C"
echo ""

# Keep script running and monitor processes
while true; do
    sleep 5
    
    # Check if backend is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Backend server stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    # Check if frontend is still running
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "❌ Frontend server stopped unexpectedly"
        cleanup
        exit 1
    fi
    
    # Check if Docker services are still running
    if ! docker-compose ps | grep -q "Up"; then
        echo "❌ Docker services stopped unexpectedly"
        cleanup
        exit 1
    fi
done
