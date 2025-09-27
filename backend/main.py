"""
FastAPI main application for AtoZ Bot Dashboard
"""
import asyncio
import json
import os
from datetime import datetime
from typing import List

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.bot_control import router as bot_router
from app.database.connection import Base, engine
from app.services.bot_service import BotService

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="AtoZ Bot Dashboard",
    description="Modern dashboard for AtoZ translation bot with real-time analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(bot_router)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()
bot_service = BotService()

@app.get("/")
async def root():
    """Serve the frontend application"""
    return FileResponse("frontend/dist/index.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Send periodic updates
            await asyncio.sleep(5)  # Update every 5 seconds
            
            # Get current bot status and metrics
            from app.database.connection import SessionLocal
            db = SessionLocal()
            
            try:
                # Get bot status
                from app.api.bot_control import get_bot_status
                bot_status = await get_bot_status(db)
                
                # Get dashboard metrics
                dashboard_metrics = bot_service.get_dashboard_metrics(db)
                
                # Send comprehensive update
                update_data = {
                    "type": "status_update",
                    "data": {
                        "timestamp": datetime.utcnow().isoformat(),
                        "bot_status": {
                            "is_running": bot_status.is_running,
                            "session_id": bot_status.session_id,
                            "session_name": bot_status.session_name,
                            "login_status": bot_status.login_status,
                            "total_checks": bot_status.total_checks,
                            "total_accepted": bot_status.total_accepted,
                            "total_rejected": bot_status.total_rejected
                        },
                        "dashboard_metrics": dashboard_metrics
                    }
                }
                
                # Only send if websocket is still connected
                if websocket.client_state == WebSocketState.CONNECTED:
                    await manager.send_personal_message(
                        json.dumps(update_data), 
                        websocket
                    )
                
            except Exception as e:
                print(f"Error in WebSocket update: {e}")
                break
            finally:
                db.close()
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.on_event("startup")
async def startup_event():
    """Startup event - initialize services"""
    print("🚀 AtoZ Bot Dashboard starting up...")
    
    # Start background tasks
    asyncio.create_task(periodic_analytics())
    asyncio.create_task(periodic_cleanup())

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event - cleanup"""
    print("🛑 AtoZ Bot Dashboard shutting down...")

async def periodic_analytics():
    """Create analytics periods every 4 hours"""
    while True:
        await asyncio.sleep(4 * 3600)  # Wait 4 hours
        
        # Create analytics period
        from app.database.connection import SessionLocal
        db = SessionLocal()
        
        try:
            end_time = datetime.utcnow()
            start_time = end_time.replace(hour=(end_time.hour // 4) * 4, minute=0, second=0, microsecond=0)
            
            # Check if period already exists
            from app.models.bot_models import AnalyticsPeriod
            existing = db.query(AnalyticsPeriod).filter(
                AnalyticsPeriod.period_start == start_time
            ).first()
            
            if not existing:
                bot_service.create_analytics_period(db, start_time, end_time)
                
                # Broadcast update to connected clients
                update_data = {
                    "type": "analytics_update",
                    "data": {
                        "message": "New analytics period created",
                        "period_start": start_time.isoformat(),
                        "period_end": end_time.isoformat()
                    }
                }
                await manager.broadcast(json.dumps(update_data))
                
        except Exception as e:
            print(f"Error creating analytics period: {e}")
        finally:
            db.close()

async def periodic_cleanup():
    """Clean up old data every 24 hours"""
    while True:
        await asyncio.sleep(24 * 3600)  # Wait 24 hours
        
        from app.database.connection import SessionLocal
        db = SessionLocal()
        
        try:
            bot_service.cleanup_old_data(db, days=7)
            print("🧹 Old data cleaned up successfully")
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            db.close()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
