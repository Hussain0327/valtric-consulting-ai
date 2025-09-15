"""
Rate Limiting Middleware for ValtricAI Consulting Agent
Production-ready rate limiting with monitoring integration
"""

import logging
import time
import asyncio
from collections import defaultdict
from typing import Optional
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Production-ready rate limiting middleware with monitoring integration"""
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
        self.cleanup_task = None
        self._start_cleanup_task()
    
    def _start_cleanup_task(self):
        """Start background task for cleaning up old requests"""
        async def cleanup_old_requests():
            while True:
                try:
                    await asyncio.sleep(30)  # Cleanup every 30 seconds
                    current_time = time.time()
                    
                    # Clean up old requests for all IPs
                    for ip in list(self.requests.keys()):
                        self.requests[ip] = [
                            req_time for req_time in self.requests[ip]
                            if current_time - req_time < 60
                        ]
                        
                        # Remove empty entries
                        if not self.requests[ip]:
                            del self.requests[ip]
                            
                    logger.debug(f"Rate limit cleanup: {len(self.requests)} active IPs")
                    
                except Exception as e:
                    logger.error(f"Rate limit cleanup failed: {e}")
        
        # Start the cleanup task
        self.cleanup_task = asyncio.create_task(cleanup_old_requests())
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP with proper proxy header handling"""
        
        # Check for forwarded IP headers (from load balancers, proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # X-Forwarded-For can contain multiple IPs, take the first (original client)
            return forwarded_for.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct connection IP
        if request.client and request.client.host:
            return request.client.host
        
        return "unknown"
    
    async def dispatch(self, request: Request, call_next):
        """Apply rate limiting with comprehensive monitoring"""
        
        # Skip rate limiting for health checks and docs
        excluded_paths = ["/", "/health", "/docs", "/redoc", "/api/v1/health", "/api/v1/metrics"]
        if request.url.path in excluded_paths:
            return await call_next(request)
        
        # Get client identifier
        client_ip = self._get_client_ip(request)
        current_time = time.time()
        route = request.url.path
        
        # Clean old requests for this IP
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        # Check rate limit
        current_requests = len(self.requests[client_ip])
        if current_requests >= self.requests_per_minute:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}: {current_requests}/{self.requests_per_minute} RPM on {route}"
            )
            
            # Record rate limit violation
            try:
                from api.routes.monitoring import record_request
                record_request(route, 0, error=True)  # 0ms response time for blocked request
            except ImportError:
                pass
            
            # Calculate retry-after header (seconds until oldest request expires)
            oldest_request = min(self.requests[client_ip]) if self.requests[client_ip] else current_time
            retry_after = max(1, int(60 - (current_time - oldest_request)))
            
            response = JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {self.requests_per_minute} requests per minute allowed",
                    "retry_after": retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + retry_after)),
                    "Retry-After": str(retry_after)
                }
            )
            return response
        
        # Record request
        self.requests[client_ip].append(current_time)
        
        # Process request
        start_time = time.time()
        try:
            response = await call_next(request)
            
            # Record successful request
            try:
                from api.routes.monitoring import record_request
                response_time_ms = (time.time() - start_time) * 1000
                record_request(route, response_time_ms, error=False)
            except ImportError:
                pass
            
        except Exception as e:
            # Record failed request
            try:
                from api.routes.monitoring import record_request
                response_time_ms = (time.time() - start_time) * 1000
                record_request(route, response_time_ms, error=True)
            except ImportError:
                pass
            raise
        
        # Add rate limit headers to successful responses
        remaining = max(0, self.requests_per_minute - len(self.requests[client_ip]))
        oldest_request = min(self.requests[client_ip]) if self.requests[client_ip] else current_time
        reset_time = int(oldest_request + 60)
        
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def get_rate_limit_info(self, client_ip: str) -> dict:
        """Get current rate limit status for an IP"""
        current_time = time.time()
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < 60
        ]
        
        current_requests = len(self.requests[client_ip])
        remaining = max(0, self.requests_per_minute - current_requests)
        oldest_request = min(self.requests[client_ip]) if self.requests[client_ip] else current_time
        reset_time = int(oldest_request + 60)
        
        return {
            "limit": self.requests_per_minute,
            "remaining": remaining,
            "reset": reset_time,
            "current_requests": current_requests
        }