"""
Hybrid RAG Retrieval Service for ValtricAI Consulting Agent

Orchestrates search across Global RAG (consulting frameworks) and Tenant RAG 
(client data) with intelligent result fusion and context assembly.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from config.settings import settings, RAGMode
from rag_system.supabase_client import supabase_manager
from rag_system.embeddings import embedding_service
from rag_system.document_processor import document_processor

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Represents a single retrieval result with metadata"""
    id: str
    text: str
    similarity_score: float
    source_type: str  # "global" or "tenant"
    source_label: str  # "[Frameworks]" or "[Client]"
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class RetrievalContext:
    """Complete context for a query with retrieved results"""
    query: str
    query_embedding: List[float]
    results: List[RetrievalResult]
    context_text: str
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class HybridRetriever:
    """Main retrieval service for hybrid RAG queries"""
    
    def __init__(self):
        self.max_context_length = settings.max_tokens_per_request
        
    async def retrieve(
        self, 
        query: str, 
        project_id: Optional[str] = None,
        k: int = None,
        mode: Optional[RAGMode] = None
    ) -> RetrievalContext:
        """
        Perform hybrid retrieval across Global and Tenant RAGs
        
        Args:
            query: User query text
            project_id: Project ID for tenant-specific search (required for tenant/hybrid mode)
            k: Number of results to return
            mode: Override default RAG mode
            
        Returns:
            RetrievalContext with assembled results and context
        """
        try:
            # Use provided parameters or defaults
            k = k or settings.fusion_k
            mode = mode or settings.rag_mode
            
            # Generate query embedding
            query_embedding = embedding_service.generate_embedding(query)
            
            # Validate project_id for tenant operations
            if mode in [RAGMode.LOCAL, RAGMode.HYBRID] and not project_id:
                raise ValueError("project_id is required for tenant or hybrid mode")
            
            # Perform retrieval based on mode
            raw_results = await self._perform_retrieval(
                query_embedding, 
                project_id, 
                k, 
                mode,
                query  # Pass the query text for hybrid search
            )
            
            # Convert to RetrievalResult objects
            results = self._convert_to_results(raw_results)
            
            # Assemble context text
            context_text = self._assemble_context(results)
            
            # Create retrieval context
            context = RetrievalContext(
                query=query,
                query_embedding=query_embedding,
                results=results,
                context_text=context_text,
                metadata={
                    "mode": mode.value,
                    "project_id": project_id,
                    "k": k,
                    "total_results": len(results),
                    "global_results": len([r for r in results if r.source_type == "global"]),
                    "tenant_results": len([r for r in results if r.source_type == "tenant"]),
                }
            )
            
            logger.info(f"Retrieved {len(results)} results for query in {mode.value} mode")
            return context
            
        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise
    
    async def _perform_retrieval(
        self, 
        query_embedding: List[float], 
        project_id: Optional[str], 
        k: int, 
        mode: RAGMode,
        query_text: str = ""
    ) -> List[Dict[str, Any]]:
        """Perform the actual retrieval based on mode"""
        
        if mode == RAGMode.GLOBAL:
            return supabase_manager.search_global_chunks(query_embedding, k, query_text)
        
        elif mode == RAGMode.LOCAL:
            return supabase_manager.search_tenant_chunks(query_embedding, project_id, k)
        
        elif mode == RAGMode.HYBRID:
            return supabase_manager.hybrid_search(query_embedding, project_id, k)
        
        else:
            raise ValueError(f"Unknown RAG mode: {mode}")
    
    def _convert_to_results(self, raw_results: List[Dict[str, Any]]) -> List[RetrievalResult]:
        """Convert raw database results to RetrievalResult objects"""
        results = []
        
        for raw in raw_results:
            result = RetrievalResult(
                id=str(raw.get("id") or raw.get("chunk_id", "")),
                text=raw.get("text", ""),
                similarity_score=float(raw.get("similarity", 0.0)),
                source_type=raw.get("source_type", "unknown"),
                source_label=raw.get("source_label", "[Unknown]"),
                metadata={
                    "document_id": raw.get("document_id"),
                    "span": raw.get("span"),
                    "created_at": raw.get("created_at"),
                    **raw.get("metadata", {})
                }
            )
            results.append(result)
        
        return results
    
    def _assemble_context(self, results: List[RetrievalResult]) -> str:
        """Assemble context text from retrieval results"""
        if not results:
            return ""
        
        context_parts = []
        current_length = 0
        
        # Sort results by similarity score (highest first)
        sorted_results = sorted(results, key=lambda x: x.similarity_score, reverse=True)
        
        for result in sorted_results:
            # Format result with source label
            formatted_text = f"{result.source_label} {result.text}"
            
            # Check if adding this result would exceed context length
            estimated_tokens = len(formatted_text.split())
            if current_length + estimated_tokens > self.max_context_length:
                logger.warning(f"Context truncated at {current_length} tokens")
                break
            
            context_parts.append(formatted_text)
            current_length += estimated_tokens
        
        return "\n\n".join(context_parts)
    
    def search_similar_documents(
        self, 
        text: str, 
        project_id: Optional[str] = None,
        threshold: float = None
    ) -> List[RetrievalResult]:
        """
        Find documents similar to provided text
        
        Args:
            text: Input text to find similar documents for
            project_id: Project ID for tenant search
            threshold: Similarity threshold (0-1)
            
        Returns:
            List of similar documents
        """
        try:
            threshold = threshold or settings.similarity_threshold
            
            # Generate embedding for input text
            text_embedding = embedding_service.generate_embedding(text)
            
            # Search both RAGs
            if settings.rag_mode == RAGMode.HYBRID and project_id:
                raw_results = supabase_manager.hybrid_search(text_embedding, project_id, k=20)
            elif project_id:
                raw_results = supabase_manager.search_tenant_chunks(text_embedding, project_id, k=20)
            else:
                raw_results = supabase_manager.search_global_chunks(text_embedding, k=20)
            
            # Convert and filter by threshold
            results = self._convert_to_results(raw_results)
            filtered_results = [r for r in results if r.similarity_score >= threshold]
            
            logger.info(f"Found {len(filtered_results)} similar documents above threshold {threshold}")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Similar document search failed: {e}")
            return []
    
    def get_document_context(
        self, 
        document_id: str, 
        project_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Get full context for a specific document
        
        Args:
            document_id: ID of the document
            project_id: Project ID for tenant documents
            
        Returns:
            Full document text or None if not found
        """
        try:
            # Try tenant RAG first if project_id provided
            if project_id:
                client = supabase_manager.tenant_client
                result = client.table("chunks").select("text").eq("document_id", document_id).execute()
                
                if result.data:
                    # Combine all chunks for this document
                    chunks = sorted(result.data, key=lambda x: x.get("span", [0, 0])[0])
                    return " ".join([chunk["text"] for chunk in chunks])
            
            # Try global RAG
            client = supabase_manager.global_client
            result = client.table("chunks").select("text").eq("document_id", document_id).execute()
            
            if result.data:
                chunks = sorted(result.data, key=lambda x: x.get("span", [0, 0])[0])
                return " ".join([chunk["text"] for chunk in chunks])
            
            logger.warning(f"Document {document_id} not found in any RAG")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get document context: {e}")
            return None


# Global retriever instance
hybrid_retriever = HybridRetriever()