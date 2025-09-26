"""
Simplified FastAPI application for testing deployment
This version doesn't require database or complex dependencies
"""
import os
import sys
from datetime import datetime

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    import uvicorn
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install requirements: pip install -r requirements-minimal.txt")
    sys.exit(1)

# Initialize FastAPI app
app = FastAPI(
    title="AtoZ Bot Dashboard",
    description="Simplified dashboard for testing deployment",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AtoZ Bot Dashboard - Simplified Version",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "message": "Simplified version running successfully"
    }

@app.get("/api/status")
async def get_status():
    """API status endpoint"""
    return {
        "api_status": "operational",
        "database_status": "not_connected",  # Simplified version
        "bot_status": "not_configured",      # Simplified version
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main-simple:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )

