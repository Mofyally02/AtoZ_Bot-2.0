#!/bin/bash
# Simple Bot Startup Script

echo "🚀 Starting Simple AtoZ Bot System..."

# Check if PostgreSQL is running
if ! pgrep -x "postgres" > /dev/null; then
    echo "⚠️  PostgreSQL is not running. Please start it first:"
    echo "   sudo systemctl start postgresql"
    exit 1
fi

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is not running. Please start it first:"
    echo "   sudo systemctl start redis"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start the simple bot server
echo "📡 Starting Simple Bot Server on port 8000..."
python3 simple_bot_server.py &
SERVER_PID=$!

# Wait a moment for server to start
sleep 3

# Start the frontend
echo "🎨 Starting Frontend on port 5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ System started successfully!"
echo "🌐 Frontend: http://localhost:5173"
echo "📡 Backend API: http://localhost:8000"
echo ""
echo "📋 Available endpoints:"
echo "   POST /api/bot/start - Start the bot"
echo "   POST /api/bot/stop - Stop the bot"
echo "   GET /api/bot/status - Get bot status"
echo ""
echo "🛑 To stop the system, press Ctrl+C"

# Wait for user to stop
wait
