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
    "sqlite:///./atoz_bot.db"
)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=10,
    max_overflow=20,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Redis connection (optional)
redis_client = None
if redis is not None:
    try:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        redis_client.ping()
        print("Redis connected successfully")
    except Exception as e:
        print(f"Redis not available (optional): {e}")
        redis_client = None
else:
    print("Redis module not available (optional)")
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
