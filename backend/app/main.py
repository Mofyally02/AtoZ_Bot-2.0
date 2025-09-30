"""
FastAPI main application for AtoZ Bot Dashboard
"""
import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List
from uuid import UUID

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.websockets import WebSocketState
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.bot_control import router as bot_router
from app.database.connection import Base, engine
from app.services.bot_service import BotService

# Create database tables
Base.metadata.create_all(bind=engine)

# Custom JSON encoder to handle UUIDs and datetimes
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

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
        try:
            if websocket.client_state == WebSocketState.CONNECTED:
                await websocket.send_text(message)
        except Exception as e:
            # Silently handle closed connections
            if "Cannot call" not in str(e) and "close message" not in str(e):
                print(f"Error sending personal message: {e}")

    async def broadcast(self, message: str):
        disconnected_connections = []
        for connection in self.active_connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_text(message)
                else:
                    disconnected_connections.append(connection)
            except Exception as e:
                # Silently handle closed connections
                if "Cannot call" not in str(e) and "close message" not in str(e):
                    print(f"Error broadcasting to connection: {e}")
                disconnected_connections.append(connection)
        
        # Remove broken connections
        for connection in disconnected_connections:
            if connection in self.active_connections:
                self.active_connections.remove(connection)

manager = ConnectionManager()
bot_service = BotService()

# Background tasks
analytics_task = None
cleanup_task = None

async def periodic_analytics():
    """Create analytics periods every 4 hours"""
    while True:
        await asyncio.sleep(4 * 3600)  # Wait 4 hours
        
        # Create analytics period
        from app.database.connection import SessionLocal
        db = SessionLocal()
        
        try:
            end_time = datetime.now(timezone.utc)
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
                await manager.broadcast(json.dumps(update_data, cls=CustomJSONEncoder))
                
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown"""
    # Startup
    print("🚀 AtoZ Bot Dashboard starting up...")
    
    # Start background tasks
    global analytics_task, cleanup_task
    analytics_task = asyncio.create_task(periodic_analytics())
    cleanup_task = asyncio.create_task(periodic_cleanup())
    
    yield
    
    # Shutdown
    print("🛑 AtoZ Bot Dashboard shutting down...")
    
    # Cancel background tasks
    if analytics_task:
        analytics_task.cancel()
    if cleanup_task:
        cleanup_task.cancel()

# Initialize FastAPI app with lifespan
app = FastAPI(
    title="AtoZ Bot Dashboard",
    description="Modern dashboard for AtoZ translation bot with real-time analytics",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(bot_router)

@app.get("/")
async def root():
    """Serve the frontend application"""
    import os
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist", "index.html")
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    else:
        return {"message": "AtoZ Bot Dashboard API", "status": "running", "frontend": "not available"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            try:
                # Send periodic updates
                await asyncio.sleep(5)  # Update every 5 seconds
                
                # Check if websocket is still connected
                if websocket.client_state != WebSocketState.CONNECTED:
                    break
                
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
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                            "bot_status": {
                                "is_running": bot_status.is_running,
                                "session_id": bot_status.session_id,
                                "session_name": bot_status.session_name,
                                "status": bot_status.status,
                                "login_status": bot_status.login_status,
                                "total_checks": bot_status.total_checks,
                                "total_accepted": bot_status.total_accepted,
                                "total_rejected": bot_status.total_rejected
                            },
                            "dashboard_metrics": dashboard_metrics
                        }
                    }
                    
                    await manager.send_personal_message(
                        json.dumps(update_data, cls=CustomJSONEncoder), 
                        websocket
                    )
                    
                except Exception as e:
                    print(f"Error in WebSocket update: {e}")
                finally:
                    db.close()
                    
            except WebSocketDisconnect:
                break
            except Exception as e:
                if "Cannot call" not in str(e) and "close message" not in str(e):
                    print(f"WebSocket error: {e}")
                break
                
    except Exception as e:
        if "Cannot call" not in str(e) and "close message" not in str(e):
            print(f"WebSocket connection error: {e}")
    finally:
        try:
            manager.disconnect(websocket)
        except:
            pass


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
