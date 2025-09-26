#!/bin/bash

# Comprehensive setup script for AtoZ Bot Frontend
set -e

echo "🚀 Setting up AtoZ Bot Frontend..."

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

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "package.json not found. Please run this script from the frontend directory."
    exit 1
fi

print_status "Checking system requirements..."

# Check Node.js version
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_VERSION" -lt 16 ]; then
        print_error "Node.js version 16 or higher is required. Current version: $(node --version)"
        exit 1
    fi
    print_success "Node.js version: $(node --version)"
else
    print_error "Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check package manager
PACKAGE_MANAGER=""
if command -v npm &> /dev/null; then
    PACKAGE_MANAGER="npm"
    print_success "Using npm: $(npm --version)"
elif command -v yarn &> /dev/null; then
    PACKAGE_MANAGER="yarn"
    print_success "Using yarn: $(yarn --version)"
elif command -v pnpm &> /dev/null; then
    PACKAGE_MANAGER="pnpm"
    print_success "Using pnpm: $(pnpm --version)"
else
    print_error "No package manager found. Please install npm, yarn, or pnpm."
    exit 1
fi

print_status "Installing dependencies with $PACKAGE_MANAGER..."

# Install dependencies
case $PACKAGE_MANAGER in
    "npm")
        npm install
        ;;
    "yarn")
        yarn install
        ;;
    "pnpm")
        pnpm install
        ;;
esac

print_success "Dependencies installed successfully!"

# Check if Tailwind CSS is properly configured
print_status "Verifying Tailwind CSS configuration..."

if [ -f "tailwind.config.js" ] && [ -f "postcss.config.js" ]; then
    print_success "Tailwind CSS configuration files found"
else
    print_warning "Tailwind CSS configuration files not found or incomplete"
fi

# Check if CSS file exists
if [ -f "src/styles/globals.css" ]; then
    print_success "Global CSS file found"
else
    print_warning "Global CSS file not found"
fi

print_status "Setup complete! 🎉"
echo ""
echo "Available commands:"
echo "  $PACKAGE_MANAGER run dev     - Start development server"
echo "  $PACKAGE_MANAGER run build   - Build for production"
echo "  $PACKAGE_MANAGER run preview - Preview production build"
echo "  $PACKAGE_MANAGER run lint    - Run ESLint"
echo ""
echo "To start the development server, run:"
echo "  $PACKAGE_MANAGER run dev"
echo ""
print_success "Happy coding! 🚀"
