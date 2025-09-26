"""
FastAPI entrypoint for deployment platforms
This file serves as the main entrypoint for deployment platforms that expect
the FastAPI app to be in the root directory.
"""
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import the FastAPI app from the backend
from main import app

# Make the app available for deployment platforms
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False
    )


