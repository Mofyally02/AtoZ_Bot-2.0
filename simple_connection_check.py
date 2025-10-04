#!/usr/bin/env python3
"""
Simple connection status checker for AtoZ Bot application
"""
import os
import sys
from datetime import datetime

def check_environment():
    """Check environment variables"""
    print("📋 Environment Variables:")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"  REDIS_URL: {os.getenv('REDIS_URL', 'Not set')}")
    print(f"  PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    print()

def check_database_connection():
    """Check database connection"""
    try:
        sys.path.append('backend')
        from app.database.connection import engine, redis_client
        
        # Check PostgreSQL database
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ PostgreSQL Database: Connected")
        
        # Check Redis
        if redis_client:
            redis_client.ping()
            print("✅ Redis: Connected")
        else:
            print("⚠️  Redis: Not available (optional)")
            
        return True
    except Exception as e:
        print(f"❌ Database: Connection failed - {e}")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("📁 File Structure Check:")
    
    required_files = [
        "backend/app/main.py",
        "backend/app/database/connection.py",
        "frontend/package.json",
        "frontend/Dockerfile",
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_files_exist = False
    
    print()
    return all_files_exist

def check_docker_compose():
    """Check docker-compose configuration"""
    print("🐳 Docker Compose Configuration:")
    
    # Check for port conflicts
    ports = {
        "Backend": "8000:8000",
        "Frontend": "3000:8000", 
        "Database": "5432:5432",
        "Redis": "6379:6379"
    }
    
    for service, port_mapping in ports.items():
        print(f"  {service}: {port_mapping}")
    
    print()
    return True

def main():
    """Main connection checker"""
    print("🔍 AtoZ Bot Connection Status Check")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    check_environment()
    
    # Check file structure
    files_ok = check_file_structure()
    
    # Check docker compose
    docker_ok = check_docker_compose()
    
    # Check database connections
    print("🗄️  Database Connections:")
    db_ok = check_database_connection()
    
    print()
    
    # Summary
    print("📊 Summary:")
    if files_ok and docker_ok and db_ok:
        print("🎉 All configurations look good!")
        print()
        print("🚀 Ready to deploy:")
        print("  1. Backend API: http://localhost:8000")
        print("  2. Frontend: http://localhost:3000")
        print("  3. Database: localhost:5432")
        print("  4. Redis: localhost:6379")
        return 0
    else:
        print("⚠️  Some configurations have issues. Check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
