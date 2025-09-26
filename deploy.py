#!/usr/bin/env python3
"""
Deployment script for AtoZ Bot Dashboard
This script helps deploy the application to various platforms
"""
import os
import sys
import subprocess
import argparse

def check_requirements():
    """Check if all required files exist"""
    required_files = [
        'main.py',
        'requirements.txt',
        'backend/main.py',
        'backend/requirements.txt',
        'frontend/package.json'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def setup_environment():
    """Set up environment variables"""
    env_vars = {
        'DATABASE_URL': 'postgresql://atoz_user:atoz_password@localhost:5432/atoz_bot_db',
        'REDIS_URL': 'redis://localhost:6379',
        'PYTHONPATH': os.getcwd(),
        'PORT': '8000'
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"✅ Set {key}={value}")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def build_frontend():
    """Build the frontend application"""
    print("🏗️  Building frontend...")
    try:
        os.chdir('frontend')
        subprocess.run(['npm', 'install'], check=True)
        subprocess.run(['npm', 'run', 'build'], check=True)
        os.chdir('..')
        print("✅ Frontend built successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to build frontend: {e}")
        return False

def run_application():
    """Run the application"""
    print("🚀 Starting application...")
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start application: {e}")

def main():
    parser = argparse.ArgumentParser(description='Deploy AtoZ Bot Dashboard')
    parser.add_argument('--check-only', action='store_true', help='Only check requirements')
    parser.add_argument('--no-frontend', action='store_true', help='Skip frontend build')
    parser.add_argument('--no-deps', action='store_true', help='Skip dependency installation')
    
    args = parser.parse_args()
    
    print("🚀 AtoZ Bot Dashboard Deployment Script")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    if args.check_only:
        print("✅ All checks passed!")
        return
    
    # Setup environment
    setup_environment()
    
    # Install dependencies
    if not args.no_deps:
        if not install_dependencies():
            sys.exit(1)
    
    # Build frontend
    if not args.no_frontend:
        if not build_frontend():
            sys.exit(1)
    
    # Run application
    run_application()

if __name__ == '__main__':
    main()


