#!/usr/bin/env python3
"""
Initialize PostgreSQL database schema for AtoZ Bot
"""
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

def init_database():
    """Initialize the database schema"""
    print("🚀 Initializing PostgreSQL database for AtoZ Bot...")
    
    # Database connection parameters
    db_params = {
        'host': 'localhost',
        'port': 5432,
        'database': 'atoz_bot_db',
        'user': 'atoz_user',
        'password': 'atoz_password'
    }
    
    try:
        # Connect to database
        print("📡 Connecting to PostgreSQL database...")
        conn = psycopg2.connect(**db_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to database successfully")
        
        # Read and execute schema
        schema_file = 'database/schema.sql'
        if os.path.exists(schema_file):
            print(f"📖 Reading schema from {schema_file}...")
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Split into individual statements and execute
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements):
                if statement:
                    try:
                        print(f"   Executing statement {i+1}/{len(statements)}...")
                        cursor.execute(statement)
                        print(f"   ✅ Statement {i+1} executed successfully")
                    except Exception as e:
                        print(f"   ⚠️ Statement {i+1} failed: {e}")
                        # Continue with other statements
                        continue
            
            print("✅ Database schema initialization completed")
        else:
            print(f"❌ Schema file not found: {schema_file}")
            return False
        
        # Test the database by querying tables
        print("\n🔍 Testing database tables...")
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        print(f"✅ Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
        
        # Test inserting a sample bot session
        print("\n🧪 Testing database functionality...")
        cursor.execute("""
            INSERT INTO bot_sessions (session_name, status, login_status)
            VALUES ('test-session', 'running', 'success')
            RETURNING id
        """)
        session_id = cursor.fetchone()[0]
        print(f"✅ Created test session: {session_id}")
        
        # Clean up test session
        cursor.execute("DELETE FROM bot_sessions WHERE id = %s", (session_id,))
        print("✅ Cleaned up test session")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
