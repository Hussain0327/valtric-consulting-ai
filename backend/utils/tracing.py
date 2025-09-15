"""
Request Tracing System for ValtricAI
Tracks performance, costs, and usage per request
"""

import time
import uuid
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class TraceEvent:
    """Single trace event for request tracking"""
    request_id: str
    timestamp: datetime
    intent: Optional[str] = None
    route: Optional[str] = None
    retrieve_ms: Optional[float] = None
    generate_ms: Optional[float] = None
    tokens_in: Optional[int] = None
    tokens_out: Optional[int] = None
    cost_usd: Optional[float] = None
    cache_hit: Optional[bool] = None
    error: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    model_used: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging/storage"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class RequestTracer:
    """Context manager for tracing requests"""
    
    def __init__(self, route: str, user_id: Optional[str] = None):
        self.request_id = str(uuid.uuid4())
        self.route = route
        self.user_id = user_id
        self.start_time = time.time()
        self.retrieve_start = None
        self.generate_start = None
        self.trace = TraceEvent(
            request_id=self.request_id,
            timestamp=datetime.utcnow(),
            route=route,
            user_id=user_id
        )
        
    def start_retrieval(self):
        """Mark start of RAG retrieval"""
        self.retrieve_start = time.time()
        
    def end_retrieval(self, cache_hit: bool = False):
        """Mark end of RAG retrieval"""
        if self.retrieve_start:
            self.trace.retrieve_ms = (time.time() - self.retrieve_start) * 1000
            self.trace.cache_hit = cache_hit
            
    def start_generation(self):
        """Mark start of AI generation"""
        self.generate_start = time.time()
        
    def end_generation(self, tokens_in: int, tokens_out: int, model: str):
        """Mark end of AI generation with token counts"""
        if self.generate_start:
            self.trace.generate_ms = (time.time() - self.generate_start) * 1000
        
        self.trace.tokens_in = tokens_in
        self.trace.tokens_out = tokens_out
        self.trace.model_used = model
        self.trace.cost_usd = self._calculate_cost(model, tokens_in, tokens_out)
        
    def set_intent(self, intent: str):
        """Set the detected intent"""
        self.trace.intent = intent
        
    def set_session(self, session_id: str):
        """Set session ID"""
        self.trace.session_id = session_id
        
    def set_error(self, error: str):
        """Set error information"""
        self.trace.error = error
        
    def _calculate_cost(self, model: str, tokens_in: int, tokens_out: int) -> float:
        """Calculate approximate cost in USD"""
        # OpenAI pricing (approximate, as of 2025)
        pricing = {
            "gpt-5-mini": {"input": 0.000001, "output": 0.000002},  # $1/1M input, $2/1M output
            "o4-mini": {"input": 0.00001, "output": 0.00002},       # $10/1M input, $20/1M output
            "text-embedding-3-small": {"input": 0.00001, "output": 0}  # $10/1M tokens
        }
        
        if model in pricing:
            rates = pricing[model]
            cost = (tokens_in * rates["input"]) + (tokens_out * rates["output"])
            return round(cost, 6)
        
        return 0.0
        
    def finish(self):
        """Complete the trace and log it"""
        total_ms = (time.time() - self.start_time) * 1000
        
        # Log trace data
        trace_data = self.trace.to_dict()
        trace_data['total_ms'] = round(total_ms, 2)
        
        logger.info(f"TRACE: {json.dumps(trace_data, default=str)}")
        
        # Could also store in database here for dashboards
        return self.trace


# Global trace storage for current request context
_current_trace: Optional[RequestTracer] = None


def get_current_trace() -> Optional[RequestTracer]:
    """Get current request trace"""
    return _current_trace


def set_current_trace(tracer: RequestTracer):
    """Set current request trace"""
    global _current_trace
    _current_trace = tracer


def clear_current_trace():
    """Clear current request trace"""
    global _current_trace
    _current_trace = None


def trace_request(route: str):
    """Decorator for tracing API requests"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user info from request if available
            user_id = None
            if 'request' in kwargs:
                # Could extract user from JWT token here
                pass
                
            tracer = RequestTracer(route=route, user_id=user_id)
            set_current_trace(tracer)
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                tracer.set_error(str(e))
                raise
            finally:
                tracer.finish()
                clear_current_trace()
                
        return wrapper
    return decorator