"""
Authentication Middleware for ValtricAI Consulting Agent
"""

import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for request processing"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with authentication context"""
        
        # Add request ID for tracing
        request.state.request_id = id(request)
        
        # Skip auth for health checks and docs
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY" 
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response