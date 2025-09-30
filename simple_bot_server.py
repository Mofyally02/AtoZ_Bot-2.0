#!/usr/bin/env python3
"""
Simple Bot Server - Direct start/stop functionality
"""
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.app.api.simple_bot_api import router as bot_router

# Create FastAPI app
app = FastAPI(
    title="Simple AtoZ Bot Server",
    description="Simple bot start/stop server",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include bot router
app.include_router(bot_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Simple AtoZ Bot Server", 
        "status": "running",
        "endpoints": {
            "start_bot": "POST /api/bot/start",
            "stop_bot": "POST /api/bot/stop", 
            "status": "GET /api/bot/status",
            "health": "GET /api/bot/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {"status": "healthy", "message": "Server is running"}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple AtoZ Bot Server...")
    print("📡 Available endpoints:")
    print("   POST /api/bot/start - Start the bot")
    print("   POST /api/bot/stop - Stop the bot")
    print("   GET /api/bot/status - Get bot status")
    print("   GET /health - Health check")
    print("🌐 Server will run on http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
