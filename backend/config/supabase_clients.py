"""
Dual Supabase Client Configuration for ValtricAI

- KB Project: Global consulting frameworks, templates, and RAG knowledge
- Tenant Project: User sessions, conversations, profile memory, and client data
"""

import os
import logging
from supabase import create_client, Client
from typing import Optional

logger = logging.getLogger(__name__)

# Global KB client (consulting frameworks, templates)
kb_client: Optional[Client] = None

# Tenant client (user sessions, conversations, profile memory)
tenant_client: Optional[Client] = None

def init_supabase_clients():
    """Initialize both Supabase clients"""
    global kb_client, tenant_client
    
    try:
        # Initialize KB client (global frameworks)
        kb_url = os.getenv("GLOBAL_SUPABASE_URL")
        kb_key = os.getenv("GLOBAL_SUPABASE_SERVICE_ROLE_KEY")
        
        if not kb_url or not kb_key:
            raise ValueError("Global Supabase credentials missing from environment")
            
        kb_client = create_client(kb_url, kb_key)
        logger.info("Initialized Global KB Supabase client")
        
        # Initialize Tenant client (user sessions & data)
        tenant_url = os.getenv("TENANT_SUPABASE_URL")
        tenant_key = os.getenv("TENANT_SUPABASE_SERVICE_ROLE_KEY")
        
        if not tenant_url or not tenant_key:
            raise ValueError("Tenant Supabase credentials missing from environment")
            
        tenant_client = create_client(tenant_url, tenant_key)
        logger.info("Initialized Tenant Supabase client")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Supabase clients: {e}")
        return False

def get_kb_client() -> Client:
    """Get the Global KB Supabase client"""
    global kb_client
    if kb_client is None:
        if not init_supabase_clients():
            raise RuntimeError("Failed to initialize KB client")
    return kb_client

def get_tenant_client() -> Client:
    """Get the Tenant Supabase client"""
    global tenant_client
    if tenant_client is None:
        if not init_supabase_clients():
            raise RuntimeError("Failed to initialize Tenant client")
    return tenant_client

# Don't initialize clients on module import - do it lazily