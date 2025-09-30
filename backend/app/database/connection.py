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

# Database URLs
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://atoz_user:atoz_password@database:5432/atoz_bot_db"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

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
    # PostgreSQL specific configuration
    connect_args={} if "postgresql" in DATABASE_URL else {"check_same_thread": False}
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
                conn.execute("SELECT 1")
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

# Test connection on startup (non-blocking)
if "postgresql" in DATABASE_URL:
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
