#!/usr/bin/env python3
"""
Connection status checker for AtoZ Bot application
"""
import os
import sys
import requests
import time
from datetime import datetime

def check_service(name, url, timeout=5):
    """Check if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name}: OK ({response.status_code})")
            return True
        else:
            print(f"❌ {name}: Error ({response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {name}: Connection failed - {e}")
        return False

def check_database():
    """Check database connection"""
    try:
        from backend.app.database.connection import engine
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database: Connected")
            return True
    except Exception as e:
        print(f"❌ Database: Connection failed - {e}")
        return False

def check_redis():
    """Check Redis connection"""
    try:
        from backend.app.database.connection import redis_client
        if redis_client:
            redis_client.ping()
            print("✅ Redis: Connected")
            return True
        else:
            print("⚠️  Redis: Not available (optional)")
            return True
    except Exception as e:
        print(f"❌ Redis: Connection failed - {e}")
        return False

def main():
    """Main connection checker"""
    print("🔍 AtoZ Bot Connection Status Check")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    print("📋 Environment Variables:")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"  REDIS_URL: {os.getenv('REDIS_URL', 'Not set')}")
    print(f"  PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    print()
    
    # Check services
    print("🌐 Service Health Checks:")
    services = [
        ("Backend API", "http://localhost:8000/health"),
        ("Frontend", "http://localhost:3000/health"),
    ]
    
    all_services_ok = True
    for name, url in services:
        if not check_service(name, url):
            all_services_ok = False
    
    print()
    
    # Check database connections
    print("🗄️  Database Connections:")
    db_ok = check_database()
    redis_ok = check_redis()
    
    print()
    
    # Summary
    print("📊 Summary:")
    if all_services_ok and db_ok and redis_ok:
        print("🎉 All connections are working properly!")
        return 0
    else:
        print("⚠️  Some connections have issues. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
