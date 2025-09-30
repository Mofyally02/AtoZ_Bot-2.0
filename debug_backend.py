#!/usr/bin/env python3
"""
Debug backend startup issues
"""
import os
import sys
import traceback

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all imports work"""
    print("🔍 Testing imports...")
    
    try:
        from app.database.connection import engine, Base, SessionLocal
        print("✅ Database connection imports successful")
    except Exception as e:
        print(f"❌ Database connection import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.models.bot_models import BotSession
        print("✅ Bot models import successful")
    except Exception as e:
        print(f"❌ Bot models import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.api.bot_control import router
        print("✅ API router import successful")
    except Exception as e:
        print(f"❌ API router import failed: {e}")
        traceback.print_exc()
        return False
    
    try:
        from app.services.bot_service import BotService
        print("✅ Bot service import successful")
    except Exception as e:
        print(f"❌ Bot service import failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from app.database.connection import engine, Base, SessionLocal
        
        # Test engine connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("This is expected since PostgreSQL isn't running locally")
        return False

def test_fastapi_app():
    """Test FastAPI app creation"""
    print("\n🔍 Testing FastAPI app creation...")
    
    try:
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        from app.api.bot_control import router as bot_router
        from app.database.connection import Base, engine
        
        # Create app
        app = FastAPI(
            title="AtoZ Bot Dashboard API",
            description="API for managing AtoZ Bot operations",
            version="2.0.0"
        )
        
        # Add CORS middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://localhost:5173",
                "http://localhost:5174",
                "http://localhost:5175",
                "http://localhost:8000",
                "*"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Add routers
        app.include_router(bot_router, prefix="/api/v1")
        
        print("✅ FastAPI app creation successful")
        return True
    except Exception as e:
        print(f"❌ FastAPI app creation failed: {e}")
        traceback.print_exc()
        return False

def test_database_tables():
    """Test database table creation"""
    print("\n🔍 Testing database table creation...")
    
    try:
        from app.database.connection import Base, engine
        
        # This will fail locally without PostgreSQL, but we can test the logic
        try:
            Base.metadata.create_all(bind=engine)
            print("✅ Database tables creation logic successful")
            return True
        except Exception as e:
            print(f"⚠️  Database tables creation failed (expected without PostgreSQL): {e}")
            return True  # This is expected locally
    except Exception as e:
        print(f"❌ Database table creation test failed: {e}")
        traceback.print_exc()
        return False

def check_environment():
    """Check environment variables"""
    print("\n🔍 Checking environment variables...")
    
    # Set test environment
    os.environ.setdefault("DATABASE_URL", "postgresql://atoz_user:atoz_password@database:5432/atoz_bot_db")
    os.environ.setdefault("REDIS_URL", "redis://redis:6379")
    os.environ.setdefault("PYTHONPATH", "/app/backend")
    
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print(f"REDIS_URL: {os.environ.get('REDIS_URL')}")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    
    return True

def main():
    """Main debug function"""
    print("🔍 AtoZ Bot Backend Debug")
    print("=" * 40)
    
    # Check environment
    check_environment()
    
    # Test imports
    imports_ok = test_imports()
    
    # Test database connection (will fail locally)
    db_ok = test_database_connection()
    
    # Test FastAPI app
    app_ok = test_fastapi_app()
    
    # Test database tables
    tables_ok = test_database_tables()
    
    print("\n📊 Summary:")
    if imports_ok and app_ok and tables_ok:
        print("✅ Backend code is working correctly")
        print("❌ The issue is likely:")
        print("  1. PostgreSQL not running in Docker")
        print("  2. Database connection timeout")
        print("  3. Service startup order issue")
        print("\n💡 Solutions:")
        print("  1. Check Docker services are running")
        print("  2. Check database service health")
        print("  3. Check service dependencies in docker-compose.yml")
        return 0
    else:
        print("❌ Backend code has issues that need fixing")
        return 1

if __name__ == "__main__":
    sys.exit(main())
