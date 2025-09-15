"""
Error Handling Middleware for ValtricAI Consulting Agent
"""

import logging
import traceback
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Global error handling middleware"""
    
    async def dispatch(self, request: Request, call_next):
        """Process request with error handling"""
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as e:
            logger.error(f"Unhandled error in {request.method} {request.url.path}: {e}")
            logger.error(traceback.format_exc())
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "detail": "An unexpected error occurred",
                    "request_id": getattr(request.state, "request_id", None)
                }
            )