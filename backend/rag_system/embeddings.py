"""
OpenAI Embeddings Service for ValtricAI Consulting Agent

Handles text embedding generation for both Global and Tenant RAGs using OpenAI's 
text-embedding-3-small model.
"""

import logging
import openai
from typing import List, Union, Optional
import numpy as np
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import settings, get_openai_config

logger = logging.getLogger(__name__)

# Configure OpenAI client
openai_config = get_openai_config()
openai.api_key = openai_config["api_key"]


class EmbeddingService:
    """Service for generating text embeddings using OpenAI"""
    
    def __init__(self):
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text to embed
            
        Returns:
            List of float values representing the embedding
        """
        try:
            # Clean and truncate text if needed
            cleaned_text = self._clean_text(text)
            
            response = openai.embeddings.create(
                model=self.model,
                input=cleaned_text,
                dimensions=self.dimensions
            )
            
            embedding = response.data[0].embedding
            logger.debug(f"Generated embedding for text of length {len(text)}")
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in a single API call
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            List of embeddings (each embedding is a list of floats)
        """
        try:
            if not texts:
                return []
            
            # Clean texts
            cleaned_texts = [self._clean_text(text) for text in texts]
            
            # OpenAI has limits on batch size - split if needed
            batch_size = 100  # Conservative batch size
            all_embeddings = []
            
            for i in range(0, len(cleaned_texts), batch_size):
                batch = cleaned_texts[i:i + batch_size]
                
                response = openai.embeddings.create(
                    model=self.model,
                    input=batch,
                    dimensions=self.dimensions
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
            logger.info(f"Generated {len(all_embeddings)} embeddings in batch")
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate batch embeddings: {e}")
            raise
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and prepare text for embedding
        
        Args:
            text: Raw input text
            
        Returns:
            Cleaned text ready for embedding
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = " ".join(text.split())
        
        # Truncate if too long (OpenAI has token limits)
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = settings.max_tokens_per_request * 3  # Conservative estimate
        if len(cleaned) > max_chars:
            cleaned = cleaned[:max_chars]
            logger.warning(f"Text truncated from {len(text)} to {len(cleaned)} characters")
        
        return cleaned
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors
        
        Args:
            vec1: First embedding vector
            vec2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1, higher is more similar)
        """
        try:
            # Convert to numpy arrays for efficient computation
            a = np.array(vec1)
            b = np.array(vec2)
            
            # Calculate cosine similarity
            cos_sim = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
            # Ensure result is between 0 and 1
            return max(0.0, float(cos_sim))
            
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            return 0.0
    
    def find_most_similar(
        self, 
        query_embedding: List[float], 
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find the most similar embeddings to a query embedding
        
        Args:
            query_embedding: Query vector
            candidate_embeddings: List of candidate vectors
            top_k: Number of top results to return
            
        Returns:
            List of (index, similarity_score) tuples, sorted by similarity
        """
        try:
            similarities = []
            
            for i, candidate in enumerate(candidate_embeddings):
                similarity = self.cosine_similarity(query_embedding, candidate)
                similarities.append((i, similarity))
            
            # Sort by similarity (highest first) and return top k
            similarities.sort(key=lambda x: x[1], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Failed to find most similar embeddings: {e}")
            return []


# Global embedding service instance
embedding_service = EmbeddingService()