#!/bin/bash

# AtoZ Bot Dashboard - Complete Startup and Test Script
set -e

echo "🚀 Starting AtoZ Bot Dashboard Complete Test"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "backend/main.py" ] || [ ! -f "frontend/package.json" ]; then
    print_error "Please run this script from the AtoZ_Bot-2.0 root directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        print_warning "Port $port is in use, killing process..."
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Clean up any existing processes
print_status "Cleaning up existing processes..."
kill_port 8000  # Backend
kill_port 3000  # Frontend
kill_port 5173  # Vite dev server

# Install backend dependencies
print_status "Installing backend dependencies..."
cd backend
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
    print_success "Backend dependencies installed"
else
    print_warning "No requirements.txt found in backend"
fi
cd ..

# Install frontend dependencies
print_status "Installing frontend dependencies..."
cd frontend
if [ -f "package.json" ]; then
    npm install
    print_success "Frontend dependencies installed"
else
    print_error "No package.json found in frontend"
    exit 1
fi
cd ..

# Start backend in background
print_status "Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
print_status "Waiting for backend to start..."
sleep 5

# Check if backend is running
if check_port 8000; then
    print_success "Backend server is running on port 8000"
else
    print_error "Backend server failed to start"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Test backend API
print_status "Testing backend API..."
python test_integration.py

# Start frontend in background
print_status "Starting frontend development server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
print_status "Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if check_port 3000 || check_port 5173; then
    print_success "Frontend server is running"
else
    print_warning "Frontend server may not be running properly"
fi

# Open browser
print_status "Opening browser..."
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:3000
elif command -v open &> /dev/null; then
    open http://localhost:3000
else
    print_warning "Please open http://localhost:3000 in your browser"
fi

print_success "🎉 AtoZ Bot Dashboard is now running!"
echo ""
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup on exit
cleanup() {
    print_status "Shutting down services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    kill_port 8000
    kill_port 3000
    kill_port 5173
    print_success "All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Keep script running
wait

