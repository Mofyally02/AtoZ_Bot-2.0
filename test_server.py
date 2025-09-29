#!/usr/bin/env python3
"""
Test server to debug routing issues
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/mofy/Desktop/Al-Tech Solutions/AtoZ_Bot-2.0/backend')

from fastapi import FastAPI
from app.api.bot_control import router as bot_router

app = FastAPI()

# Include bot router
app.include_router(bot_router, prefix="/api/bot", tags=["bot"])

@app.get("/")
async def root():
    return {"message": "Test server", "status": "running"}

@app.get("/test")
async def test():
    return {"message": "Test endpoint"}

if __name__ == "__main__":
    import uvicorn
    print("Starting test server...")
    print("Bot router:", bot_router)
    print("App routes:", [route.path for route in app.routes])
    uvicorn.run(app, host="0.0.0.0", port=8001)
