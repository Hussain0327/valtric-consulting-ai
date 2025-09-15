"""
Test FastAPI server to verify chat system functionality
"""

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Import all routes
from api.routes.chat import router as chat_router
from api.routes.sessions import router as sessions_router

# Create FastAPI app
app = FastAPI(
    title="ValtricAI Test Server",
    description="Test server for chat functionality",
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

# Add health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "message": "ValtricAI Test Server is running"
    }

# Include routers (no prefix since routes already have paths)
app.include_router(chat_router, prefix="/api", tags=["chat"])
app.include_router(sessions_router, prefix="/api", tags=["sessions"])

if __name__ == "__main__":
    print("Starting ValtricAI Test Server...")
    print("Available endpoints:")
    print("- GET  /health")
    print("- POST /api/chat")
    print("- POST /api/chat/stream") 
    print("- WS   /api/chat/ws")
    print("- GET  /api/sessions")
    print("- POST /api/sessions")
    print("- GET  /api/sessions/{id}")
    print("- PUT  /api/sessions/{id}")
    print("- DELETE /api/sessions/{id}")
    
    uvicorn.run(
        "test_server:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )