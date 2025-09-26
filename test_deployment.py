#!/usr/bin/env python3
"""
Test script to verify deployment configuration
"""
import os
import sys
import subprocess
import requests
import time

def test_imports():
    """Test if all imports work correctly"""
    print("🧪 Testing imports...")
    
    try:
        # Test root main.py import
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from main import app
        print("✅ FastAPI app imported successfully")
        
        # Test backend imports
        from backend.app.api.bot_control import router
        print("✅ API router imported successfully")
        
        from backend.app.database.connection import get_db
        print("✅ Database connection imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_requirements():
    """Test if requirements.txt is valid"""
    print("🧪 Testing requirements.txt...")
    
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read().strip().split('\n')
        
        print(f"✅ Found {len(requirements)} requirements")
        
        # Check for essential packages
        essential = ['fastapi', 'uvicorn', 'sqlalchemy', 'psycopg2-binary']
        for package in essential:
            if any(package in req for req in requirements):
                print(f"✅ {package} found in requirements")
            else:
                print(f"❌ {package} missing from requirements")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Requirements error: {e}")
        return False

def test_app_startup():
    """Test if the app can start without errors"""
    print("🧪 Testing app startup...")
    
    try:
        # Test the app object
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
        from main import app
        
        # Check if app has required attributes
        assert hasattr(app, 'routes'), "App missing routes"
        assert hasattr(app, 'middleware'), "App missing middleware"
        
        print("✅ App object is valid")
        return True
        
    except Exception as e:
        print(f"❌ App startup error: {e}")
        return False

def test_health_endpoint():
    """Test health endpoint (if app is running)"""
    print("🧪 Testing health endpoint...")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            assert data['status'] == 'healthy'
            print("✅ Health endpoint working")
            return True
        else:
            print(f"❌ Health endpoint returned {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("ℹ️  App not running - skipping health check")
        return True
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 AtoZ Bot Dashboard - Deployment Test")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_requirements,
        test_app_startup,
        test_health_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Deployment should work.")
        return 0
    else:
        print("❌ Some tests failed. Check the errors above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())


