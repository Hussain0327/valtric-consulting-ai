"""
Configuration settings for the ValtricAI Consulting Agent
Handles dual RAG architecture with Global and Tenant Supabase instances
"""

import os
from enum import Enum
from typing import Optional
from pydantic import validator
from pydantic_settings import BaseSettings


class RAGMode(str, Enum):
    """RAG operation modes"""
    LOCAL = "local"      # Tenant RAG only
    GLOBAL = "global"    # Global RAG only  
    HYBRID = "hybrid"    # Both RAGs with fusion


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # =============================================================================
    # OpenAI Configuration
    # =============================================================================
    openai_api_key: str
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    max_tokens_per_request: int = 4000
    
    # =============================================================================
    # Global RAG - Consulting Frameworks (Read-Only)
    # =============================================================================
    global_supabase_url: str
    global_supabase_anon_key: str  
    global_supabase_service_role_key: str
    
    # =============================================================================
    # Tenant RAG - Client Data (RLS Protected)
    # =============================================================================
    tenant_supabase_url: str
    tenant_supabase_anon_key: str
    tenant_supabase_service_role_key: str
    tenant_supabase_jwt_secret: str
    
    # =============================================================================
    # RAG Configuration
    # =============================================================================
    rag_mode: RAGMode = RAGMode.HYBRID
    default_chunk_size: int = 500
    default_overlap: int = 50
    
    # =============================================================================
    # Performance & Limits
    # =============================================================================
    max_chunks_per_query: int = 10
    similarity_threshold: float = 0.7
    fusion_k: int = 10  # Results to return after fusion
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables
        
    @validator("rag_mode", pre=True)
    def validate_rag_mode(cls, v):
        """Ensure RAG mode is valid"""
        if isinstance(v, str):
            return RAGMode(v.lower())
        return v


# Global settings instance
settings = Settings()


def get_global_supabase_config() -> dict:
    """Get Global RAG Supabase configuration"""
    return {
        "url": settings.global_supabase_url,
        "key": settings.global_supabase_anon_key,
        "service_role_key": settings.global_supabase_service_role_key,
    }


def get_tenant_supabase_config() -> dict:
    """Get Tenant RAG Supabase configuration"""
    return {
        "url": settings.tenant_supabase_url,
        "key": settings.tenant_supabase_anon_key,
        "service_role_key": settings.tenant_supabase_service_role_key,
        "jwt_secret": settings.tenant_supabase_jwt_secret,
    }


def get_openai_config() -> dict:
    """Get OpenAI configuration"""
    return {
        "api_key": settings.openai_api_key,
        "embedding_model": settings.embedding_model,
        "embedding_dimensions": settings.embedding_dimensions,
        "max_tokens": settings.max_tokens_per_request,
    }