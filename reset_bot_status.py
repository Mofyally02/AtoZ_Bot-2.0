#!/usr/bin/env python3
"""
Reset bot status script
"""
import sys
import os
sys.path.append('/home/mofy/Desktop/Al-Tech Solutions/AtoZ_Bot-2.0/backend')

from app.database.connection import get_db
from sqlalchemy import text
from datetime import datetime, timezone

def reset_bot_status():
    """Reset all bot sessions to stopped status"""
    try:
        db = next(get_db())
        if db:
            # Reset all running sessions to stopped
            db.execute(text("""
                UPDATE bot_sessions 
                SET status = 'stopped', updated_at = :updated_at
                WHERE status = 'running'
            """), {
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
            db.commit()
            print("✅ Reset all running sessions to stopped")
            
            # Show current sessions
            result = db.execute(text("SELECT id, session_name, status, total_checks FROM bot_sessions ORDER BY created_at DESC LIMIT 5"))
            sessions = result.fetchall()
            print("\n📊 Current sessions:")
            for session in sessions:
                print(f"  - {session[0]}: {session[1]} ({session[2]}) - {session[3]} checks")
        else:
            print("❌ Could not connect to database")
    except Exception as e:
        print(f"❌ Error resetting bot status: {e}")

if __name__ == "__main__":
    reset_bot_status()
