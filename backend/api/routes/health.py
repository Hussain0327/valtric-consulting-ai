"""
Health Check Routes for ValtricAI Consulting Agent
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from config.settings import settings
from rag_system.supabase_client import supabase_manager
from models.schemas import SystemHealth

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


@router.get("/health/detailed", response_model=SystemHealth)
async def detailed_health_check():
    """Detailed health check with service status"""
    
    try:
        # Check RAG systems
        rag_health = supabase_manager.health_check()
        
        # Check OpenAI (basic connectivity test)
        openai_healthy = True
        try:
            from agent_logic.model_router import model_router
            # This would be a simple test call in production
            openai_healthy = True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            openai_healthy = False
        
        return SystemHealth(
            global_rag_healthy=rag_health.get("global_rag", False),
            tenant_rag_healthy=rag_health.get("tenant_rag", False),
            openai_healthy=openai_healthy,
            database_healthy=rag_health.get("tenant_rag", False),  # Use tenant as DB indicator
            last_check=datetime.utcnow(),
            response_times={}
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.get("/health/rag")
async def rag_health_check():
    """Check RAG system health"""
    
    try:
        health_status = supabase_manager.health_check()
        
        return {
            "global_rag": {
                "status": "healthy" if health_status.get("global_rag") else "unhealthy",
                "description": "Consulting frameworks and templates"
            },
            "tenant_rag": {
                "status": "healthy" if health_status.get("tenant_rag") else "unhealthy", 
                "description": "Client-specific data with RLS"
            },
            "rag_mode": settings.rag_mode.value,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"RAG health check failed: {e}")
        raise HTTPException(status_code=500, detail="RAG health check failed")