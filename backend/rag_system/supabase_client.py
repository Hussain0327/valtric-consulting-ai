"""
Dual Supabase Client Manager for ValtricAI Consulting Agent

Manages connections to:
1. Global RAG - Consulting frameworks, templates, industry data (read-only)
2. Tenant RAG - Client data, sessions, user management (RLS protected)
"""

import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

from config.settings import (
    settings, 
    get_global_supabase_config, 
    get_tenant_supabase_config,
    RAGMode
)

logger = logging.getLogger(__name__)


class SupabaseClientManager:
    """Manages dual Supabase clients for Global and Tenant RAGs"""
    
    def __init__(self):
        self._global_client: Optional[Client] = None
        self._tenant_client: Optional[Client] = None
        self._global_admin_client: Optional[Client] = None
        self._tenant_admin_client: Optional[Client] = None
        
    @property
    def global_client(self) -> Client:
        """Get Global RAG client (anon key, read-only)"""
        if not self._global_client:
            config = get_global_supabase_config()
            self._global_client = create_client(
                config["url"], 
                config["key"],
                options=ClientOptions(
                    auto_refresh_token=False,
                    persist_session=False
                )
            )
        return self._global_client
    
    @property
    def tenant_client(self) -> Client:
        """Get Tenant RAG client (anon key, user context)"""
        if not self._tenant_client:
            config = get_tenant_supabase_config()
            self._tenant_client = create_client(
                config["url"], 
                config["key"],
                options=ClientOptions(
                    auto_refresh_token=True,
                    persist_session=True
                )
            )
        return self._tenant_client
    
    @property 
    def global_admin_client(self) -> Client:
        """Get Global RAG admin client (service role, full access)"""
        if not self._global_admin_client:
            config = get_global_supabase_config()
            self._global_admin_client = create_client(
                config["url"], 
                config["service_role_key"],
                options=ClientOptions(
                    auto_refresh_token=False,
                    persist_session=False
                )
            )
        return self._global_admin_client
    
    @property
    def tenant_admin_client(self) -> Client:
        """Get Tenant RAG admin client (service role, bypasses RLS)"""
        if not self._tenant_admin_client:
            config = get_tenant_supabase_config()
            self._tenant_admin_client = create_client(
                config["url"], 
                config["service_role_key"],
                options=ClientOptions(
                    auto_refresh_token=False,
                    persist_session=False
                )
            )
        return self._tenant_admin_client
    
    def set_tenant_user(self, jwt_token: str) -> None:
        """Set user context for tenant client"""
        try:
            self.tenant_client.auth.set_session(jwt_token, refresh_token=None)
            logger.info("Tenant user context set successfully")
        except Exception as e:
            logger.error(f"Failed to set tenant user context: {e}")
            raise
    
    def search_global_chunks(self, query_vector: List[float], k: int = 8, query_text: str = "") -> List[Dict[str, Any]]:
        """Search Global RAG for consulting frameworks using documents table"""
        try:
            # Use admin client for Global RAG (read-only, no user context needed)
            # Search documents table with text matching
            result = self.global_admin_client.table("documents").select("*").ilike(
                "content", f"%{query_text if query_text else 'consulting framework'}%"
            ).limit(k).execute()
            
            documents = result.data or []
            
            # Convert documents to chunk format for compatibility
            chunks = []
            for doc in documents:
                chunk = {
                    "id": doc.get("id"),
                    "text": doc.get("content", ""),
                    "similarity": 0.8,  # Default similarity for text matches
                    "metadata": {},
                    "source_type": "global",
                    "source_label": "[Frameworks]"
                }
                
                # Try to get metadata from common content table fields
                if doc.get("title"):
                    chunk["metadata"]["title"] = doc["title"]
                if doc.get("url"):
                    chunk["metadata"]["source"] = doc["url"]
                if doc.get("category"):
                    chunk["metadata"]["category"] = doc["category"]
                    
                # Identify framework from content if possible
                content_lower = chunk["text"].lower()
                if "porter" in content_lower or "five forces" in content_lower:
                    chunk["source_label"] = "[Porter's Five Forces]"
                elif "swot" in content_lower:
                    chunk["source_label"] = "[SWOT Analysis]"
                elif "mckinsey" in content_lower or "7s" in content_lower:
                    chunk["source_label"] = "[McKinsey 7S]"
                
                chunks.append(chunk)
                
            logger.info(f"Retrieved {len(chunks)} framework documents from Global RAG using hybrid search")
            return chunks
            
        except Exception as e:
            logger.error(f"Global RAG search failed: {e}")
            return []
    
    def search_tenant_chunks(
        self, 
        query_vector: List[float], 
        project_id: str, 
        k: int = 8
    ) -> List[Dict[str, Any]]:
        """Search Tenant RAG for client-specific data"""
        try:
            result = self.tenant_client.rpc(
                "search_project_chunks_arr",
                {
                    "p_project": project_id,
                    "q": query_vector,
                    "k": k
                }
            ).execute()
            
            chunks = result.data or []
            
            # Add source tagging
            for chunk in chunks:
                chunk["source_type"] = "tenant" 
                chunk["source_label"] = "[Client]"
                
            logger.info(f"Retrieved {len(chunks)} chunks from Tenant RAG for project {project_id}")
            return chunks
            
        except Exception as e:
            logger.error(f"Tenant RAG search failed: {e}")
            return []
    
    def hybrid_search(
        self, 
        query_vector: List[float], 
        project_id: str, 
        k: int = 10
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search across both RAGs with result fusion"""
        
        if settings.rag_mode == RAGMode.GLOBAL:
            return self.search_global_chunks(query_vector, k)
        elif settings.rag_mode == RAGMode.LOCAL:
            return self.search_tenant_chunks(query_vector, project_id, k)
        
        # Hybrid mode - search both RAGs
        global_chunks = self.search_global_chunks(query_vector, k // 2)
        tenant_chunks = self.search_tenant_chunks(query_vector, project_id, k // 2)
        
        # Reciprocal Rank Fusion
        fused_results = self._reciprocal_rank_fusion(
            [global_chunks, tenant_chunks], 
            k=k
        )
        
        logger.info(f"Hybrid search returned {len(fused_results)} fused results")
        return fused_results
    
    def _reciprocal_rank_fusion(
        self, 
        ranked_lists: List[List[Dict[str, Any]]], 
        k: int = 10, 
        c: int = 60
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion algorithm for combining search results
        
        Args:
            ranked_lists: List of ranked result lists
            k: Number of results to return
            c: Constant for RRF formula (typically 60)
        """
        scores = {}
        
        for rank_list in ranked_lists:
            for rank, item in enumerate(rank_list):
                # Create unique key based on content or ID
                item_id = item.get('id') or item.get('chunk_id') or str(hash(item.get('text', '')))
                source_type = item.get('source_type', 'unknown')
                
                key = (item_id, source_type)
                
                # RRF score: 1 / (rank + c)
                rrf_score = 1 / (rank + c)
                
                if key not in scores:
                    scores[key] = {
                        'item': item,
                        'score': 0
                    }
                
                scores[key]['score'] += rrf_score
        
        # Sort by fused score and return top k
        sorted_items = sorted(
            scores.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )[:k]
        
        return [item['item'] for item in sorted_items]
    
    def health_check(self) -> Dict[str, bool]:
        """Check connectivity to both Supabase instances"""
        health = {
            "global_rag": False,
            "tenant_rag": False
        }
        
        try:
            # Test Global RAG - uses 'documents' table for knowledge base
            self.global_client.table("documents").select("count", count="exact").limit(1).execute()
            health["global_rag"] = True
        except Exception as e:
            logger.warning(f"Global RAG health check failed: {e}")
        
        try:
            # Test Tenant RAG - uses 'chunks' table for client data
            self.tenant_admin_client.table("chunks").select("count", count="exact").limit(1).execute()
            health["tenant_rag"] = True
        except Exception as e:
            logger.warning(f"Tenant RAG health check failed: {e}")
            
        return health


# Global client manager instance
supabase_manager = SupabaseClientManager()