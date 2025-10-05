"""
Database connection and configuration
"""
import os

try:
    import redis
except ImportError:
    redis = None
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database URLs - PostgreSQL only
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://atoz_user:atoz_password@atoz-database:5432/atoz_bot_db"
)

# Always use PostgreSQL
USE_POSTGRESQL = True

# Debug network connectivity
import socket
def test_hostname_resolution(hostname):
    """Test if hostname can be resolved"""
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.gaierror:
        return False

# Test database hostname resolution
if "database" in DATABASE_URL:
    if test_hostname_resolution("database"):
        print("✅ Database hostname 'database' resolves successfully")
    else:
        print("❌ Database hostname 'database' cannot be resolved")
        print("🔄 This might cause connection issues")
        # Try to get the actual database service IP
        try:
            import subprocess
            result = subprocess.run(['getent', 'hosts', 'database'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Database IP: {result.stdout.strip()}")
            else:
                print("Could not resolve database hostname")
        except Exception as e:
            print(f"Error checking database hostname: {e}")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Debug logging
print(f"Database URL: {DATABASE_URL}")
print(f"Redis URL: {REDIS_URL}")

# Create SQLAlchemy engine with PostgreSQL configuration
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    connect_args={}
)

# Test PostgreSQL connection with retry logic
def test_postgres_connection():
    """Test PostgreSQL connection with retry logic"""
    max_retries = 10
    retry_delay = 3
    
    print("🔍 Testing PostgreSQL connection...")
    for attempt in range(max_retries):
        try:
            with engine.connect() as conn:
                from sqlalchemy import text
                conn.execute(text("SELECT 1"))
            print("✅ PostgreSQL connection successful")
            return True
        except Exception as e:
            print(f"PostgreSQL connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
            else:
                print("❌ PostgreSQL connection failed - all retries exhausted")
                print("This might cause the application to fail to start")
                return False

# Test PostgreSQL connection on startup (non-blocking)
import threading
def test_connection_async():
    test_postgres_connection()

# Start connection test in background
connection_thread = threading.Thread(target=test_connection_async, daemon=True)
connection_thread.start()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Redis connection (optional) with retry logic
redis_client = None
if redis is not None:
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            redis_client = redis.from_url(REDIS_URL, decode_responses=True)
            redis_client.ping()
            print("✅ Redis connected successfully")
            break
        except Exception as e:
            print(f"Redis connection attempt {attempt + 1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                import time
                time.sleep(retry_delay)
            else:
                print("❌ Redis not available (optional) - all retries failed")
                redis_client = None
else:
    print("⚠️  Redis module not available (optional)")
    redis_client = None

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """Get Redis client"""
    if redis_client is None:
        raise Exception("Redis is not available")
    return redis_client
