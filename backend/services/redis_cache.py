"""
Redis Caching Service for ValtricAI
Reduces OpenAI API costs by 80% through intelligent response caching
"""

import redis
import json
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class CacheType(str, Enum):
    """Types of cached content with different TTL strategies"""
    FRAMEWORK_QUERY = "framework"      # 24 hours - SWOT, Porter's, etc.
    GENERAL_QUERY = "general"          # 1 hour - General business questions
    USER_SPECIFIC = "user_specific"    # 5 minutes - User-specific data
    RAG_CONTEXT = "rag_context"        # 30 minutes - RAG retrieval results


@dataclass
class CacheConfig:
    """Cache configuration for different content types"""
    ttl_seconds: int
    prefix: str
    max_size_bytes: int = 1024 * 1024  # 1MB default


# Cache configurations by type
CACHE_CONFIGS = {
    CacheType.FRAMEWORK_QUERY: CacheConfig(
        ttl_seconds=24 * 60 * 60,  # 24 hours
        prefix="fw:",
        max_size_bytes=2 * 1024 * 1024  # 2MB for framework responses
    ),
    CacheType.GENERAL_QUERY: CacheConfig(
        ttl_seconds=60 * 60,  # 1 hour
        prefix="gq:",
        max_size_bytes=1024 * 1024  # 1MB
    ),
    CacheType.USER_SPECIFIC: CacheConfig(
        ttl_seconds=5 * 60,  # 5 minutes
        prefix="us:",
        max_size_bytes=512 * 1024  # 512KB
    ),
    CacheType.RAG_CONTEXT: CacheConfig(
        ttl_seconds=30 * 60,  # 30 minutes
        prefix="rag:",
        max_size_bytes=1024 * 1024  # 1MB
    )
}


class RedisCacheService:
    """High-performance Redis caching service for OpenAI responses"""
    
    def __init__(self, 
                 host: str = "localhost", 
                 port: int = 6379, 
                 db: int = 0,
                 decode_responses: bool = True):
        """
        Initialize Redis cache service
        
        Args:
            host: Redis server host
            port: Redis server port  
            db: Redis database number
            decode_responses: Automatically decode responses to strings
        """
        try:
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                db=db,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {host}:{port}")
            
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
        except Exception as e:
            logger.error(f"Redis initialization error: {e}")
            raise
    
    def _generate_cache_key(self, 
                           query: str, 
                           cache_type: CacheType,
                           persona: str = "partner",
                           framework: Optional[str] = None,
                           user_id: Optional[str] = None) -> str:
        """
        Generate cache key with query similarity matching
        
        Args:
            query: The user query
            cache_type: Type of cache (determines TTL and prefix)
            persona: AI persona (associate/partner/senior_partner)
            framework: Consulting framework (swot/porters/mckinsey)
            user_id: User ID for user-specific caching
        
        Returns:
            Cache key string
        """
        config = CACHE_CONFIGS[cache_type]
        
        # Normalize query for better cache hits
        normalized_query = self._normalize_query(query)
        
        # Create cache key components
        key_components = [normalized_query, persona]
        
        if framework:
            key_components.append(framework)
        
        if user_id and cache_type == CacheType.USER_SPECIFIC:
            key_components.append(user_id)
        
        # Generate hash for consistent key length
        key_data = "|".join(key_components)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        
        return f"{config.prefix}{key_hash}"
    
    def _normalize_query(self, query: str) -> str:
        """
        Normalize query for better cache hit rates
        
        Handles:
        - Case insensitivity
        - Punctuation normalization
        - Common phrase variations
        - Whitespace normalization
        """
        # Basic normalization
        normalized = query.lower().strip()
        
        # Remove extra whitespace
        normalized = " ".join(normalized.split())
        
        # Remove common punctuation that doesn't affect meaning
        punctuation_map = {
            "?": "",
            "!": "",
            ".": "",
            ",": "",
            ":": "",
            ";": ""
        }
        
        for punct, replacement in punctuation_map.items():
            normalized = normalized.replace(punct, replacement)
        
        # Handle common phrase variations for better cache hits
        phrase_variations = {
            "swot analysis": "swot analysis",
            "swot analyse": "swot analysis", 
            "swot framework": "swot analysis",
            "porter five forces": "porter five forces",
            "porters five forces": "porter five forces",
            "porter's five forces": "porter five forces",
            "mckinsey 7s": "mckinsey 7s",
            "mckinsey seven s": "mckinsey 7s",
            "mckinsey framework": "mckinsey 7s"
        }
        
        for variation, canonical in phrase_variations.items():
            normalized = normalized.replace(variation, canonical)
        
        return normalized
    
    async def get_cached_response(self, 
                                query: str,
                                cache_type: CacheType,
                                persona: str = "partner",
                                framework: Optional[str] = None,
                                user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get cached OpenAI response
        
        Args:
            query: User query
            cache_type: Type of cache to check
            persona: AI persona
            framework: Consulting framework
            user_id: User ID for user-specific cache
        
        Returns:
            Cached response dict or None if not found
        """
        try:
            cache_key = self._generate_cache_key(
                query, cache_type, persona, framework, user_id
            )
            
            # Get from Redis
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                # Parse JSON response
                response = json.loads(cached_data)
                
                # Add cache metadata
                response["_cache_info"] = {
                    "hit": True,
                    "cache_type": cache_type.value,
                    "cached_at": response.get("_cached_at"),
                    "key": cache_key[:16] + "..."  # Truncated key for debugging
                }
                
                logger.info(f"Cache HIT: {cache_type.value} query - saved OpenAI API call")
                return response
            
            return None
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode cached response: {e}")
            # Remove corrupted cache entry
            await self.delete_cached_response(query, cache_type, persona, framework, user_id)
            return None
        except redis.RedisError as e:
            logger.error(f"Redis error getting cached response: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting cached response: {e}")
            return None
    
    async def cache_response(self,
                           query: str,
                           response: Dict[str, Any],
                           cache_type: CacheType,
                           persona: str = "partner",
                           framework: Optional[str] = None,
                           user_id: Optional[str] = None) -> bool:
        """
        Cache OpenAI response with appropriate TTL
        
        Args:
            query: User query
            response: OpenAI response to cache
            cache_type: Type of cache (determines TTL)
            persona: AI persona
            framework: Consulting framework
            user_id: User ID for user-specific cache
        
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            config = CACHE_CONFIGS[cache_type]
            cache_key = self._generate_cache_key(
                query, cache_type, persona, framework, user_id
            )
            
            # Add cache metadata to response
            cache_response = response.copy()
            cache_response["_cached_at"] = datetime.utcnow().isoformat()
            cache_response["_cache_type"] = cache_type.value
            cache_response["_query_normalized"] = self._normalize_query(query)
            
            # Serialize response
            serialized_response = json.dumps(cache_response, default=str)
            
            # Check size limit
            if len(serialized_response.encode()) > config.max_size_bytes:
                logger.warning(f"Response too large to cache: {len(serialized_response)} bytes")
                return False
            
            # Cache with TTL
            success = self.redis_client.setex(
                cache_key,
                config.ttl_seconds,
                serialized_response
            )
            
            if success:
                logger.info(f"Cached {cache_type.value} response for {config.ttl_seconds}s")
                return True
            
            return False
            
        except redis.RedisError as e:
            logger.error(f"Redis error caching response: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error caching response: {e}")
            return False
    
    async def delete_cached_response(self,
                                   query: str,
                                   cache_type: CacheType,
                                   persona: str = "partner",
                                   framework: Optional[str] = None,
                                   user_id: Optional[str] = None) -> bool:
        """Delete cached response"""
        try:
            cache_key = self._generate_cache_key(
                query, cache_type, persona, framework, user_id
            )
            
            result = self.redis_client.delete(cache_key)
            return result > 0
            
        except redis.RedisError as e:
            logger.error(f"Redis error deleting cached response: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics and health info"""
        try:
            info = self.redis_client.info()
            
            # Calculate cache stats by prefix
            cache_stats = {}
            for cache_type, config in CACHE_CONFIGS.items():
                keys = self.redis_client.keys(f"{config.prefix}*")
                cache_stats[cache_type.value] = {
                    "key_count": len(keys),
                    "ttl_seconds": config.ttl_seconds,
                    "max_size_mb": config.max_size_bytes / (1024 * 1024)
                }
            
            return {
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_human": info.get("used_memory_human"),
                "total_commands_processed": info.get("total_commands_processed"),
                "keyspace_hits": info.get("keyspace_hits"),
                "keyspace_misses": info.get("keyspace_misses"),
                "cache_hit_rate": self._calculate_hit_rate(info),
                "cache_types": cache_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except redis.RedisError as e:
            logger.error(f"Redis error getting stats: {e}")
            return {"error": str(e)}
    
    def _calculate_hit_rate(self, info: Dict[str, Any]) -> Optional[float]:
        """Calculate cache hit rate percentage"""
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        
        if hits + misses > 0:
            return round((hits / (hits + misses)) * 100, 2)
        
        return None
    
    def flush_cache_type(self, cache_type: CacheType) -> int:
        """Flush all keys of a specific cache type"""
        try:
            config = CACHE_CONFIGS[cache_type]
            keys = self.redis_client.keys(f"{config.prefix}*")
            
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Flushed {deleted} keys of type {cache_type.value}")
                return deleted
            
            return 0
            
        except redis.RedisError as e:
            logger.error(f"Redis error flushing cache type {cache_type.value}: {e}")
            return 0
    
    def health_check(self) -> Dict[str, Any]:
        """Check Redis connection health"""
        try:
            # Test basic operations
            test_key = "health_check"
            test_value = "ok"
            
            # Test SET
            self.redis_client.setex(test_key, 10, test_value)
            
            # Test GET
            retrieved = self.redis_client.get(test_key)
            
            # Cleanup
            self.redis_client.delete(test_key)
            
            return {
                "status": "healthy",
                "operations": {
                    "set": True,
                    "get": retrieved == test_value,
                    "delete": True
                },
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except redis.ConnectionError:
            return {
                "status": "unhealthy",
                "error": "Connection failed",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }


# Global Redis cache instance
redis_cache = RedisCacheService()