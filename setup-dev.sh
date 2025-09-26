#!/bin/bash

# AtoZ Bot Dashboard Development Setup Script
# This script sets up the development environment

set -e

echo "🚀 Setting up AtoZ Bot Dashboard for development..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p logs/nginx
mkdir -p logs/bot
mkdir -p data/postgres
mkdir -p data/redis
mkdir -p backups

# Generate SSL certificates for development
print_status "Generating SSL certificates for development..."
if [ -f "ssl/generate-dev-certs.sh" ]; then
    chmod +x ssl/generate-dev-certs.sh
    ./ssl/generate-dev-certs.sh
else
    print_warning "SSL certificate generation script not found. Creating placeholder certificates..."
    # Create placeholder certificates
    mkdir -p ssl
    echo "placeholder" > ssl/cert.pem
    echo "placeholder" > ssl/key.pem
    print_warning "Please replace placeholder certificates with real ones for production."
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    if [ -f "env.template" ]; then
        cp env.template .env
        print_warning "Please update .env file with your actual configuration values."
    else
        print_error "Environment template not found. Please create .env file manually."
        exit 1
    fi
else
    print_status ".env file already exists, skipping creation."
fi

# Build and start services
print_status "Building and starting services..."
docker-compose up -d --build

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 10

# Check if services are running
print_status "Checking service health..."

# Check database
if docker-compose exec -T database pg_isready -U atoz_user -d atoz_bot_db > /dev/null 2>&1; then
    print_success "Database is ready"
else
    print_warning "Database might not be ready yet"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is ready"
else
    print_warning "Redis might not be ready yet"
fi

# Check backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    print_success "Backend is ready"
else
    print_warning "Backend might not be ready yet"
fi

# Check frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_success "Frontend is ready"
else
    print_warning "Frontend might not be ready yet"
fi

print_success "Setup completed!"
echo ""
echo "🌐 Access your application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Documentation: http://localhost:8000/docs"
echo ""
echo "📊 Useful commands:"
echo "   View logs: docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart services: docker-compose restart"
echo "   Update services: docker-compose up -d --build"
echo ""
echo "🔧 Development commands:"
echo "   Backend only: cd backend && python main.py"
echo "   Frontend only: cd frontend && npm run dev"
echo "   Bot only: cd bot && python persistent_bot.py"
echo ""
print_warning "Don't forget to update your .env file with actual credentials!"

