#!/usr/bin/env python3
"""
Debug version of simple_main.py
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/mofy/Desktop/Al-Tech Solutions/AtoZ_Bot-2.0/backend')

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

# Test imports
try:
    from app.database.connection import get_db, engine, Base
    print("✅ Database import successful")
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Database import failed: {e}")
    DATABASE_AVAILABLE = False
    def get_db():
        return None
    engine = None
    Base = None

try:
    from app.api.bot_control import router as bot_router
    print("✅ Bot router import successful")
    print(f"Bot router prefix: {bot_router.prefix}")
except ImportError as e:
    print(f"❌ Bot router import failed: {e}")
    bot_router = None

try:
    from app.services.bot_service import BotService
    print("✅ Bot service import successful")
    bot_service = BotService()
except ImportError as e:
    print(f"❌ Bot service import failed: {e}")
    bot_service = None

try:
    from app.services.connection_monitor import connection_monitor, ServiceType, ConnectionStatus
    print("✅ Connection monitor import successful")
except ImportError as e:
    print(f"❌ Connection monitor import failed: {e}")
    connection_monitor = None

# Create FastAPI app
app = FastAPI(title="AtoZ Bot Dashboard API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Request/Response Logging Middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and responses"""
    start_time = time.time()
    
    # Log incoming request
    print(f"\n🔵 INCOMING REQUEST:")
    print(f"   Method: {request.method}")
    print(f"   URL: {request.url}")
    print(f"   Headers: {dict(request.headers)}")
    
    # Process request
    response = await call_next(request)
    
    # Calculate processing time
    process_time = time.time() - start_time
    
    # Log outgoing response
    print(f"🟢 OUTGOING RESPONSE:")
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print(f"   Process Time: {process_time:.3f}s")
    print(f"   {'='*50}")
    
    return response

# Include routers
print(f"DATABASE_AVAILABLE: {DATABASE_AVAILABLE}")
print(f"bot_router is None: {bot_router is None}")

if bot_router:
    print("Including bot router...")
    app.include_router(bot_router, tags=["bot"])
    print("Bot router included successfully")
else:
    print("Bot router not included")

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AtoZ Bot Dashboard API", "status": "running"}

@app.get("/health")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/health/detailed")
async def detailed_health_check():
    """Detailed health check with all service statuses"""
    if connection_monitor:
        await connection_monitor.force_check_all()
        return connection_monitor.get_status_summary()
    else:
        return {
            "overall_status": "degraded",
            "services": {
                "database": {"status": "unknown", "last_check": None, "retry_count": 0},
                "redis": {"status": "unknown", "last_check": None, "retry_count": 0},
                "bot_process": {"status": "unknown", "last_check": None, "retry_count": 0},
                "external_api": {"status": "healthy", "last_check": None, "retry_count": 0},
                "websocket": {"status": "healthy", "last_check": None, "retry_count": 0}
            },
            "monitoring_active": False,
            "check_interval": 30
        }

@app.get("/debug")
async def debug_info():
    """Debug information"""
    return {
        "database_available": DATABASE_AVAILABLE,
        "bot_router_available": bot_router is not None,
        "bot_service_available": bot_service is not None,
        "connection_monitor_available": connection_monitor is not None,
        "routes": [route.path for route in app.routes]
    }

@app.on_event("startup")
async def startup_event():
    """Startup event to initialize connection monitoring"""
    print("🚀 Starting AtoZ Bot Dashboard API...")
    if DATABASE_AVAILABLE and connection_monitor:
        await connection_monitor.start_monitoring()
        print("✅ Connection monitoring started")
    else:
        print("⚠️ Connection monitoring not started due to missing database/monitor components.")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event to stop connection monitoring"""
    print("🛑 Shutting down AtoZ Bot Dashboard API...")
    if DATABASE_AVAILABLE and connection_monitor:
        await connection_monitor.stop_monitoring()
        print("✅ Connection monitoring stopped")

if __name__ == "__main__":
    import uvicorn
    print("Starting debug server...")
    print("Available routes:", [route.path for route in app.routes])
    uvicorn.run(app, host="0.0.0.0", port=8000)
