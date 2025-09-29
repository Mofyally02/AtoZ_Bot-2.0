#!/usr/bin/env python3
"""
Debug import issues
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/mofy/Desktop/Al-Tech Solutions/AtoZ_Bot-2.0/backend')

try:
    from app.database.connection import get_db, engine, Base
    print("✅ Database import successful")
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Database import failed: {e}")
    DATABASE_AVAILABLE = False

try:
    from app.api.bot_control import router as bot_router
    print("✅ Bot router import successful")
    print(f"Bot router: {bot_router}")
except ImportError as e:
    print(f"❌ Bot router import failed: {e}")
    bot_router = None

try:
    from app.services.bot_service import BotService
    print("✅ Bot service import successful")
except ImportError as e:
    print(f"❌ Bot service import failed: {e}")

try:
    from app.services.connection_monitor import connection_monitor, ServiceType, ConnectionStatus
    print("✅ Connection monitor import successful")
except ImportError as e:
    print(f"❌ Connection monitor import failed: {e}")

print(f"\nDATABASE_AVAILABLE: {DATABASE_AVAILABLE}")
print(f"bot_router is None: {bot_router is None}")

if DATABASE_AVAILABLE and bot_router:
    print("✅ Bot router should be included")
else:
    print("❌ Bot router will NOT be included")
