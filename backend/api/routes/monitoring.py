"""
Monitoring Routes for ValtricAI
Health checks, metrics, and performance monitoring
"""

import time
import psutil
import logging
from typing import Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from rag_system.supabase_client import supabase_manager
from config.settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Global metrics storage (in production, use Redis or proper metrics DB)
_metrics_store: Dict[str, Any] = {
    "requests_total": 0,
    "requests_by_route": {},
    "response_times": [],
    "errors_total": 0,
    "rag_retrievals": 0,
    "ai_generations": 0,
    "tokens_consumed": 0,
    "cost_usd_total": 0.0,
    "last_reset": datetime.utcnow()
}


class HealthResponse(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str = "1.0.0"
    checks: Dict[str, Dict[str, Any]]


class MetricsResponse(BaseModel):
    """Metrics response model"""
    timestamp: datetime
    uptime_seconds: float
    system: Dict[str, Any]
    application: Dict[str, Any]
    rag: Dict[str, Any]
    ai: Dict[str, Any]


def record_request(route: str, response_time_ms: float, error: bool = False):
    """Record request metrics"""
    _metrics_store["requests_total"] += 1
    _metrics_store["requests_by_route"][route] = _metrics_store["requests_by_route"].get(route, 0) + 1
    _metrics_store["response_times"].append(response_time_ms)
    
    # Keep only last 1000 response times for P95 calculation
    if len(_metrics_store["response_times"]) > 1000:
        _metrics_store["response_times"] = _metrics_store["response_times"][-1000:]
    
    if error:
        _metrics_store["errors_total"] += 1


def record_rag_retrieval():
    """Record RAG retrieval"""
    _metrics_store["rag_retrievals"] += 1


def record_ai_generation(tokens: int, cost_usd: float):
    """Record AI generation metrics"""
    _metrics_store["ai_generations"] += 1
    _metrics_store["tokens_consumed"] += tokens
    _metrics_store["cost_usd_total"] += cost_usd


def calculate_p95_latency() -> float:
    """Calculate P95 latency from response times"""
    times = _metrics_store["response_times"]
    if not times:
        return 0.0
    
    sorted_times = sorted(times)
    p95_index = int(len(sorted_times) * 0.95)
    return sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check endpoint
    Returns service health and dependency status
    """
    checks = {}
    overall_status = "healthy"
    
    # Check RAG systems
    try:
        rag_health = supabase_manager.health_check()
        checks["rag"] = {
            "status": "healthy" if any(rag_health.values()) else "degraded",
            "global_rag": rag_health.get("global_rag", False),
            "tenant_rag": rag_health.get("tenant_rag", False),
            "details": rag_health
        }
        
        if not any(rag_health.values()):
            overall_status = "degraded"
            
    except Exception as e:
        checks["rag"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "unhealthy"
    
    # Check OpenAI connectivity (simple ping)
    try:
        from rag_system.embeddings import embedding_service
        # Simple test - generate a tiny embedding
        test_embedding = embedding_service.generate_embedding("test")
        checks["openai"] = {
            "status": "healthy" if test_embedding else "unhealthy",
            "embedding_dimensions": len(test_embedding) if test_embedding else 0
        }
    except Exception as e:
        checks["openai"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        overall_status = "unhealthy"
    
    # System resources
    try:
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        checks["system"] = {
            "status": "healthy" if memory.percent < 90 and disk.percent < 90 else "degraded",
            "memory_percent": memory.percent,
            "disk_percent": disk.percent,
            "cpu_percent": psutil.cpu_percent(interval=1)
        }
        
        if memory.percent > 95 or disk.percent > 95:
            overall_status = "degraded"
            
    except Exception as e:
        checks["system"] = {
            "status": "unknown",
            "error": str(e)
        }
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.utcnow(),
        checks=checks
    )


@router.get("/metrics", response_model=MetricsResponse)
async def get_metrics():
    """
    Comprehensive metrics endpoint
    Returns performance, usage, and system metrics
    """
    now = datetime.utcnow()
    uptime = (now - _metrics_store["last_reset"]).total_seconds()
    
    # Calculate error rate
    error_rate = 0.0
    if _metrics_store["requests_total"] > 0:
        error_rate = (_metrics_store["errors_total"] / _metrics_store["requests_total"]) * 100
    
    # System metrics
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    system_metrics = {
        "memory_mb": round(memory.used / 1024 / 1024, 1),
        "memory_percent": memory.percent,
        "disk_percent": disk.percent,
        "cpu_percent": psutil.cpu_percent(interval=0.1),
        "load_average": list(psutil.getloadavg()) if hasattr(psutil, 'getloadavg') else []
    }
    
    # Application metrics
    app_metrics = {
        "requests_total": _metrics_store["requests_total"],
        "requests_per_second": round(_metrics_store["requests_total"] / max(uptime, 1), 2),
        "error_rate_percent": round(error_rate, 2),
        "p95_latency_ms": round(calculate_p95_latency(), 2),
        "routes": _metrics_store["requests_by_route"]
    }
    
    # RAG metrics
    rag_metrics = {
        "retrievals_total": _metrics_store["rag_retrievals"],
        "cache_hit_rate": 0.0  # TODO: Implement cache hit tracking
    }
    
    # AI metrics
    ai_metrics = {
        "generations_total": _metrics_store["ai_generations"],
        "tokens_consumed": _metrics_store["tokens_consumed"],
        "cost_usd_total": round(_metrics_store["cost_usd_total"], 4),
        "avg_tokens_per_request": round(
            _metrics_store["tokens_consumed"] / max(_metrics_store["ai_generations"], 1), 1
        )
    }
    
    return MetricsResponse(
        timestamp=now,
        uptime_seconds=uptime,
        system=system_metrics,
        application=app_metrics,
        rag=rag_metrics,
        ai=ai_metrics
    )


@router.post("/metrics/reset")
async def reset_metrics():
    """Reset metrics counters (for testing/debugging)"""
    global _metrics_store
    _metrics_store = {
        "requests_total": 0,
        "requests_by_route": {},
        "response_times": [],
        "errors_total": 0,
        "rag_retrievals": 0,
        "ai_generations": 0,
        "tokens_consumed": 0,
        "cost_usd_total": 0.0,
        "last_reset": datetime.utcnow()
    }
    
    return {"status": "metrics_reset", "timestamp": datetime.utcnow()}


# Make metrics functions available for import
__all__ = [
    "router", 
    "record_request", 
    "record_rag_retrieval", 
    "record_ai_generation",
    "calculate_p95_latency"
]