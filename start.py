#!/usr/bin/env python3
"""
Simple startup script for AtoZ Bot Dashboard
This script provides an easy way to start the application
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import uvicorn
        print("✅ Core dependencies found")
        return True
    except ImportError:
        print("❌ Missing dependencies. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def start_backend():
    """Start the backend server"""
    print("🚀 Starting AtoZ Bot Dashboard Backend...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    # Start the server
    try:
        subprocess.run([
            sys.executable, "main.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend failed to start: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️ Backend stopped by user")
        return True

def main():
    """Main startup function"""
    print("=" * 50)
    print("AtoZ Bot Dashboard Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("requirements.txt").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("❌ Cannot start without required dependencies")
        sys.exit(1)
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    main()
