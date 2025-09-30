#!/usr/bin/env python3
"""
Configuration verification for AtoZ Bot (no Docker required)
"""
import os
import sys
from datetime import datetime

def check_file_structure():
    """Check if all required files exist"""
    print("📁 File Structure Check:")
    
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "backend/app/main.py",
        "backend/app/database/connection.py",
        "frontend/package.json",
        "frontend/Dockerfile",
        "database/schema.sql"
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_files_exist = False
    
    return all_files_exist

def check_dockerfile():
    """Check Dockerfile configuration"""
    print("\n🐳 Dockerfile Check:")
    
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        
        checks = [
            ("Python base image", "FROM python:3.11-slim" in content),
            ("Working directory", "WORKDIR /app" in content),
            ("Requirements install", "pip install" in content),
            ("Backend copy", "COPY backend/" in content),
            ("Port exposure", "EXPOSE 8000" in content),
            ("Health check", "HEALTHCHECK" in content),
            ("Uvicorn command", "uvicorn" in content)
        ]
        
        all_checks_pass = True
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_checks_pass = False
        
        return all_checks_pass
    except Exception as e:
        print(f"❌ Error reading Dockerfile: {e}")
        return False

def check_docker_compose():
    """Check docker-compose.yml configuration"""
    print("\n🐳 Docker Compose Check:")
    
    try:
        with open("docker-compose.yml", "r") as f:
            content = f.read()
        
        checks = [
            ("Version", "version: '3.8'" in content),
            ("App service", "app:" in content),
            ("Database service", "database:" in content),
            ("Redis service", "redis:" in content),
            ("PostgreSQL image", "postgres:15-alpine" in content),
            ("Redis image", "redis:7-alpine" in content),
            ("Network configuration", "networks:" in content),
            ("Volume configuration", "volumes:" in content)
        ]
        
        all_checks_pass = True
        for check_name, check_result in checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_checks_pass = False
        
        return all_checks_pass
    except Exception as e:
        print(f"❌ Error reading docker-compose.yml: {e}")
        return False

def check_backend_config():
    """Check backend configuration"""
    print("\n🔧 Backend Configuration Check:")
    
    try:
        # Check main.py
        with open("backend/app/main.py", "r") as f:
            main_content = f.read()
        
        main_checks = [
            ("FastAPI import", "from fastapi import FastAPI" in main_content),
            ("CORS middleware", "CORSMiddleware" in main_content),
            ("Health endpoint", "/health" in main_content),
            ("WebSocket support", "WebSocket" in main_content),
            ("Database connection", "from app.database.connection" in main_content)
        ]
        
        all_main_checks = True
        for check_name, check_result in main_checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_main_checks = False
        
        # Check database connection
        with open("backend/app/database/connection.py", "r") as f:
            db_content = f.read()
        
        db_checks = [
            ("PostgreSQL URL", "postgresql://" in db_content),
            ("SQLAlchemy engine", "create_engine" in db_content),
            ("Redis connection", "redis" in db_content),
            ("Connection retry", "retry" in db_content.lower())
        ]
        
        all_db_checks = True
        for check_name, check_result in db_checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_db_checks = False
        
        return all_main_checks and all_db_checks
    except Exception as e:
        print(f"❌ Error checking backend configuration: {e}")
        return False

def check_frontend_config():
    """Check frontend configuration"""
    print("\n🎨 Frontend Configuration Check:")
    
    try:
        # Check package.json
        with open("frontend/package.json", "r") as f:
            package_content = f.read()
        
        package_checks = [
            ("React dependencies", "react" in package_content),
            ("TypeScript support", "typescript" in package_content),
            ("Vite build tool", "vite" in package_content),
            ("Build script", "build" in package_content)
        ]
        
        all_package_checks = True
        for check_name, check_result in package_checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_package_checks = False
        
        # Check frontend Dockerfile
        with open("frontend/Dockerfile", "r") as f:
            frontend_dockerfile = f.read()
        
        frontend_checks = [
            ("Node.js base", "FROM node:" in frontend_dockerfile),
            ("NPM install", "npm install" in frontend_dockerfile),
            ("Build command", "npm run build" in frontend_dockerfile),
            ("Port exposure", "EXPOSE" in frontend_dockerfile)
        ]
        
        all_frontend_checks = True
        for check_name, check_result in frontend_checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_frontend_checks = False
        
        return all_package_checks and all_frontend_checks
    except Exception as e:
        print(f"❌ Error checking frontend configuration: {e}")
        return False

def check_environment_variables():
    """Check environment variable configuration"""
    print("\n🌍 Environment Variables Check:")
    
    try:
        with open("docker-compose.yml", "r") as f:
            content = f.read()
        
        env_checks = [
            ("DATABASE_URL", "DATABASE_URL" in content),
            ("REDIS_URL", "REDIS_URL" in content),
            ("PYTHONPATH", "PYTHONPATH" in content),
            ("PostgreSQL credentials", "POSTGRES_USER" in content),
            ("PostgreSQL database", "POSTGRES_DB" in content)
        ]
        
        all_env_checks = True
        for check_name, check_result in env_checks:
            if check_result:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_env_checks = False
        
        return all_env_checks
    except Exception as e:
        print(f"❌ Error checking environment variables: {e}")
        return False

def main():
    """Main verification function"""
    print("🔍 AtoZ Bot Configuration Verification")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run all checks
    files_ok = check_file_structure()
    dockerfile_ok = check_dockerfile()
    compose_ok = check_docker_compose()
    backend_ok = check_backend_config()
    frontend_ok = check_frontend_config()
    env_ok = check_environment_variables()
    
    print("\n📊 Summary:")
    all_checks = [files_ok, dockerfile_ok, compose_ok, backend_ok, frontend_ok, env_ok]
    
    if all(all_checks):
        print("🎉 All configurations look correct!")
        print("\n🚀 Ready for deployment:")
        print("  - All files are present")
        print("  - Docker configuration is correct")
        print("  - Backend is properly configured for PostgreSQL")
        print("  - Frontend is ready to build")
        print("  - Environment variables are set")
        print("\n📝 Next steps:")
        print("  1. Install Docker and Docker Compose")
        print("  2. Run: docker-compose up -d")
        print("  3. Access: http://localhost:8000")
        return 0
    else:
        print("⚠️  Some configuration issues found.")
        print("Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
