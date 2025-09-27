#!/usr/bin/env python3
"""
Simplified FastAPI backend for AtoZ Bot Dashboard
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
try:
    from sqlalchemy.orm import Session
except ImportError:
    # Fallback for environments without SQLAlchemy
    Session = None
from datetime import datetime
import uvicorn
import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from app.database.connection import get_db, engine, Base
    from app.api.bot_control import router as bot_router
    from app.services.bot_service import BotService
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create bot service instance
    bot_service = BotService()
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"Database components not available: {e}")
    DATABASE_AVAILABLE = False
    # Create mock components
    def get_db():
        return None
    bot_router = None
    bot_service = None

# Create FastAPI app
app = FastAPI(
    title="AtoZ Bot Dashboard API",
    description="API for managing AtoZ translation bot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
if DATABASE_AVAILABLE and bot_router:
    app.include_router(bot_router, prefix="/api/bot", tags=["bot"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AtoZ Bot Dashboard API", "status": "running"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/bot/dashboard/metrics")
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get dashboard metrics"""
    if not DATABASE_AVAILABLE or not bot_service:
        return {
            "active_sessions": 0,
            "total_jobs_today": 0,
            "acceptance_rate_today": 0.0,
            "most_active_language": None,
            "bot_uptime_hours": 0.0,
            "last_activity": None
        }
    
    try:
        metrics = bot_service.get_dashboard_metrics(db)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("🚀 Starting AtoZ Bot Dashboard API...")
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
