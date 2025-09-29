#!/usr/bin/env python3
"""
Test PostgreSQL database connection
"""
import os
import sys
import psycopg2
from sqlalchemy import create_engine, text

def test_postgresql_connection():
    """Test direct PostgreSQL connection"""
    try:
        # Test direct psycopg2 connection
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="atoz_bot_db",
            user="atoz_user",
            password="atoz_password"
        )
        print("✅ Direct PostgreSQL connection successful")
        
        # Test basic query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ PostgreSQL version: {version[0]}")
        
        # Test UUID extension
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'uuid-ossp';")
        if cursor.fetchone():
            print("✅ UUID extension is available")
        else:
            print("❌ UUID extension not found")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Direct PostgreSQL connection failed: {e}")
        return False

def test_sqlalchemy_connection():
    """Test SQLAlchemy connection"""
    try:
        # Test SQLAlchemy connection
        database_url = "postgresql://atoz_user:atoz_password@localhost:5432/atoz_bot_db"
        engine = create_engine(database_url, pool_pre_ping=True)
        
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ SQLAlchemy connection successful")
            
            # Test if tables exist
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            print(f"✅ Found tables: {tables}")
            
        return True
        
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def main():
    print("🔍 Testing PostgreSQL Database Connection...")
    print("=" * 50)
    
    # Test direct connection
    direct_ok = test_postgresql_connection()
    print()
    
    # Test SQLAlchemy connection
    sqlalchemy_ok = test_sqlalchemy_connection()
    print()
    
    if direct_ok and sqlalchemy_ok:
        print("🎉 All database tests passed!")
        return 0
    else:
        print("❌ Some database tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
