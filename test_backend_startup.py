#!/usr/bin/env python3
"""
Test backend startup configuration
"""
import os
import sys

def check_main_py():
    """Check main.py for potential startup issues"""
    print("🔍 Checking main.py configuration...")
    
    try:
        with open("backend/app/main.py", "r") as f:
            content = f.read()
        
        # Check for potential issues
        issues = []
        
        # Check if database connection is tested on startup
        if "Base.metadata.create_all" in content:
            print("✅ Database table creation is present")
        else:
            issues.append("Database table creation missing")
        
        # Check if there's error handling for database connection
        if "try:" in content and "except" in content:
            print("✅ Error handling is present")
        else:
            issues.append("Error handling might be missing")
        
        # Check if CORS is configured
        if "CORSMiddleware" in content:
            print("✅ CORS middleware is configured")
        else:
            issues.append("CORS middleware missing")
        
        # Check if health endpoint exists
        if "/health" in content:
            print("✅ Health endpoint is present")
        else:
            issues.append("Health endpoint missing")
        
        if issues:
            print("⚠️  Potential issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ main.py configuration looks good")
        
        return len(issues) == 0
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return False

def check_database_connection():
    """Check database connection configuration"""
    print("\n🔍 Checking database connection configuration...")
    
    try:
        with open("backend/app/database/connection.py", "r") as f:
            content = f.read()
        
        # Check for potential issues
        issues = []
        
        # Check if PostgreSQL URL is correct
        if "postgresql://atoz_user:atoz_password@database:5432/atoz_bot_db" in content:
            print("✅ PostgreSQL connection string is correct")
        else:
            issues.append("PostgreSQL connection string might be incorrect")
        
        # Check if retry logic is present
        if "retry" in content.lower():
            print("✅ Retry logic is present")
        else:
            issues.append("Retry logic might be missing")
        
        # Check if Redis connection is configured
        if "redis://redis:6379" in content:
            print("✅ Redis connection string is correct")
        else:
            issues.append("Redis connection string might be incorrect")
        
        if issues:
            print("⚠️  Potential issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Database connection configuration looks good")
        
        return len(issues) == 0
    except Exception as e:
        print(f"❌ Error reading database connection: {e}")
        return False

def check_dockerfile():
    """Check Dockerfile for potential issues"""
    print("\n🔍 Checking Dockerfile configuration...")
    
    try:
        with open("Dockerfile", "r") as f:
            content = f.read()
        
        # Check for potential issues
        issues = []
        
        # Check if requirements.txt is copied
        if "COPY backend/requirements.txt" in content:
            print("✅ Requirements file is copied")
        else:
            issues.append("Requirements file not copied")
        
        # Check if pip install is present
        if "pip install" in content:
            print("✅ pip install is present")
        else:
            issues.append("pip install missing")
        
        # Check if working directory is set
        if "WORKDIR /app/backend" in content:
            print("✅ Working directory is set correctly")
        else:
            issues.append("Working directory might be incorrect")
        
        # Check if uvicorn command is correct
        if "uvicorn app.main:app" in content:
            print("✅ Uvicorn command is correct")
        else:
            issues.append("Uvicorn command might be incorrect")
        
        if issues:
            print("⚠️  Potential issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ Dockerfile configuration looks good")
        
        return len(issues) == 0
    except Exception as e:
        print(f"❌ Error reading Dockerfile: {e}")
        return False

def check_docker_compose():
    """Check docker-compose.yml for potential issues"""
    print("\n🔍 Checking docker-compose.yml configuration...")
    
    try:
        with open("docker-compose.yml", "r") as f:
            content = f.read()
        
        # Check for potential issues
        issues = []
        
        # Check if app service depends on database
        if "depends_on:" in content and "database:" in content:
            print("✅ App service depends on database")
        else:
            issues.append("App service might not depend on database")
        
        # Check if database service is configured
        if "postgres:15-alpine" in content:
            print("✅ PostgreSQL service is configured")
        else:
            issues.append("PostgreSQL service might not be configured")
        
        # Check if environment variables are set
        if "DATABASE_URL" in content and "REDIS_URL" in content:
            print("✅ Environment variables are set")
        else:
            issues.append("Environment variables might be missing")
        
        # Check if health checks are configured
        if "healthcheck:" in content:
            print("✅ Health checks are configured")
        else:
            issues.append("Health checks might be missing")
        
        if issues:
            print("⚠️  Potential issues found:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print("✅ docker-compose.yml configuration looks good")
        
        return len(issues) == 0
    except Exception as e:
        print(f"❌ Error reading docker-compose.yml: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 AtoZ Bot Backend Startup Test")
    print("=" * 40)
    
    # Run all checks
    main_ok = check_main_py()
    db_ok = check_database_connection()
    dockerfile_ok = check_dockerfile()
    compose_ok = check_docker_compose()
    
    print("\n📊 Summary:")
    all_checks = [main_ok, db_ok, dockerfile_ok, compose_ok]
    
    if all(all_checks):
        print("✅ All configurations look correct!")
        print("\n💡 The backend startup failure might be due to:")
        print("  1. Database service not ready when app starts")
        print("  2. Network connectivity issues between services")
        print("  3. Database connection timeout")
        print("  4. Missing environment variables in production")
        print("\n🔧 Recommended fixes:")
        print("  1. Add startup delay or retry logic")
        print("  2. Check service dependencies")
        print("  3. Verify database service is healthy")
        print("  4. Check logs for specific error messages")
        return 0
    else:
        print("⚠️  Some configuration issues found.")
        print("Please fix the issues above before deploying.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
