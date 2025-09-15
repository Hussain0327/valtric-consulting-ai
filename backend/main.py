"""
ValtricAI Consulting Agent - Main FastAPI Application

Enterprise-grade consulting AI with dual RAG architecture:
- Global RAG: Consulting frameworks, templates, best practices
- Tenant RAG: Client-specific data with RLS security
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import settings
from rag_system.supabase_client import supabase_manager
from api.routes import chat, sessions, frameworks, analysis, feedback, health, monitoring, exports
from api.middleware.error_handling import ErrorHandlingMiddleware
from api.middleware.rate_limiting import RateLimitingMiddleware
from api.middleware.auth import AuthMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting ValtricAI Consulting Agent")
    
    # Health check both RAG systems
    health_status = supabase_manager.health_check()
    logger.info(f"RAG Health Status: {health_status}")
    
    if not any(health_status.values()):
        logger.error("No RAG systems are available!")
    
    # Start background queue workers
    from services.queue_service import start_queue_workers
    await start_queue_workers()
    logger.info("Background queue workers started")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ValtricAI Consulting Agent")


# Create FastAPI application
app = FastAPI(
    title="ValtricAI Consulting Agent",
    description="""
    Enterprise consulting AI with dual RAG architecture for secure, intelligent business advice.
    
    ## Features
    - **Hybrid RAG**: Global frameworks + client-specific data
    - **Multi-Persona AI**: Associate, Partner, Senior Partner consultants  
    - **Security**: RLS-protected tenant data isolation
    - **Real-time**: WebSocket streaming responses
    - **Frameworks**: SWOT, Porter's 5 Forces, McKinsey 7S integration
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# =============================================================================
# Middleware Configuration
# =============================================================================

# CORS - Configure for your frontend domain
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Custom middleware
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(RateLimitingMiddleware)
app.add_middleware(AuthMiddleware)

# =============================================================================
# Route Registration
# =============================================================================

# Core API routes
app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(monitoring.router, prefix="/api/v1", tags=["Monitoring"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(sessions.router, prefix="/api/v1", tags=["Sessions"])
app.include_router(frameworks.router, prefix="/api/v1", tags=["Frameworks"])
app.include_router(analysis.router, prefix="/api/v1", tags=["Analysis"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])
app.include_router(exports.router, prefix="/api/v1/export", tags=["Export"])

# TEST ENDPOINT - NO AUTH REQUIRED
from test_chat_endpoint import test_router
app.include_router(test_router, prefix="/api/v1", tags=["Test"])

# =============================================================================
# Root Endpoints
# =============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "ValtricAI Consulting Agent",
        "version": "1.0.0",
        "description": "Enterprise consulting AI with dual RAG architecture",
        "features": [
            "Hybrid RAG (Global + Tenant)",
            "Multi-persona consultants", 
            "Real-time streaming",
            "Framework integration",
            "RLS security"
        ],
        "rag_mode": settings.rag_mode.value,
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/api/v1/info")
async def api_info():
    """API configuration information"""
    health_status = supabase_manager.health_check()
    
    return {
        "rag_mode": settings.rag_mode.value,
        "embedding_model": settings.embedding_model,
        "chunk_size": settings.default_chunk_size,
        "max_tokens": settings.max_tokens_per_request,
        "rag_health": health_status,
        "available_modes": [mode.value for mode in settings.rag_mode.__class__]
    }

# =============================================================================
# Exception Handlers
# =============================================================================

@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle validation errors"""
    return JSONResponse(
        status_code=400,
        content={"error": "Validation Error", "detail": str(exc)}
    )

@app.exception_handler(ConnectionError)
async def connection_error_handler(request, exc):
    """Handle connection errors"""
    return JSONResponse(
        status_code=503,
        content={"error": "Service Unavailable", "detail": "Unable to connect to required services"}
    )

# =============================================================================
# Development Server
# =============================================================================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )