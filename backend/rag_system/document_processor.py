"""
Document Processing Pipeline for ValtricAI Consulting Agent

Handles document chunking, text extraction, and preparation for vector storage
in both Global and Tenant RAGs.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from uuid import uuid4
import hashlib

from config.settings import settings
from rag_system.embeddings import embedding_service

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Represents a chunk of processed document"""
    id: str
    text: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = None
    start_position: int = 0
    end_position: int = 0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass 
class ProcessedDocument:
    """Represents a fully processed document with chunks"""
    id: str
    source_path: str
    title: str
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any] = None
    total_tokens: int = 0
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DocumentProcessor:
    """Processes documents into chunks suitable for RAG storage"""
    
    def __init__(self):
        self.chunk_size = settings.default_chunk_size
        self.overlap = settings.default_overlap
        
    def process_document(
        self, 
        text: str, 
        source_path: str = "", 
        title: str = "",
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None,
        generate_embeddings: bool = True
    ) -> ProcessedDocument:
        """
        Process a document into chunks with embeddings
        
        Args:
            text: Raw document text
            source_path: Path or identifier for the document
            title: Document title
            chunk_size: Override default chunk size
            overlap: Override default overlap
            generate_embeddings: Whether to generate embeddings
            
        Returns:
            ProcessedDocument with chunks and metadata
        """
        try:
            # Use provided parameters or defaults
            chunk_size = chunk_size or self.chunk_size
            overlap = overlap or self.overlap
            
            # Clean the text
            cleaned_text = self._clean_text(text)
            
            # Generate document ID
            doc_id = self._generate_document_id(source_path, cleaned_text)
            
            # Create chunks
            chunks = self._chunk_text(
                cleaned_text, 
                chunk_size=chunk_size, 
                overlap=overlap
            )
            
            # Generate embeddings if requested
            if generate_embeddings and chunks:
                chunk_texts = [chunk.text for chunk in chunks]
                embeddings = embedding_service.generate_embeddings_batch(chunk_texts)
                
                for chunk, embedding in zip(chunks, embeddings):
                    chunk.embedding = embedding
            
            # Calculate total tokens (rough estimate)
            total_tokens = len(cleaned_text.split())
            
            processed_doc = ProcessedDocument(
                id=doc_id,
                source_path=source_path,
                title=title or self._extract_title(cleaned_text),
                chunks=chunks,
                metadata={
                    "original_length": len(text),
                    "cleaned_length": len(cleaned_text),
                    "chunk_count": len(chunks),
                    "chunk_size": chunk_size,
                    "overlap": overlap,
                    "has_embeddings": generate_embeddings
                },
                total_tokens=total_tokens
            )
            
            logger.info(f"Processed document '{title}' into {len(chunks)} chunks")
            return processed_doc
            
        except Exception as e:
            logger.error(f"Failed to process document: {e}")
            raise
    
    def _chunk_text(
        self, 
        text: str, 
        chunk_size: int, 
        overlap: int
    ) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Input text to chunk
            chunk_size: Target size for each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        
        # Split into sentences first for better chunk boundaries
        sentences = self._split_into_sentences(text)
        
        current_chunk = ""
        current_pos = 0
        
        for sentence in sentences:
            # If adding this sentence would exceed chunk size, create a chunk
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                chunk = self._create_chunk(current_chunk, current_pos)
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, overlap)
                current_chunk = overlap_text + sentence
                current_pos = len(text) - len(current_chunk)
            else:
                current_chunk += sentence
        
        # Add final chunk if there's remaining text
        if current_chunk.strip():
            chunk = self._create_chunk(current_chunk, current_pos)
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, text: str, start_pos: int) -> DocumentChunk:
        """Create a DocumentChunk from text"""
        chunk_id = str(uuid4())
        cleaned_text = text.strip()
        
        return DocumentChunk(
            id=chunk_id,
            text=cleaned_text,
            start_position=start_pos,
            end_position=start_pos + len(cleaned_text),
            metadata={
                "length": len(cleaned_text),
                "word_count": len(cleaned_text.split())
            }
        )
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for better chunking"""
        # Simple sentence splitting - could be enhanced with nltk or spacy
        sentence_endings = r'[.!?]+\s+'
        sentences = re.split(sentence_endings, text)
        
        # Add sentence endings back (except for last sentence)
        result = []
        for i, sentence in enumerate(sentences[:-1]):
            # Find the ending that was removed
            match = re.search(sentence_endings, text[len(' '.join(sentences[:i+1])):])
            ending = match.group() if match else '. '
            result.append(sentence + ending)
        
        # Add last sentence
        if sentences[-1].strip():
            result.append(sentences[-1])
        
        return result
    
    def _get_overlap_text(self, text: str, overlap: int) -> str:
        """Get overlap text from the end of current chunk"""
        if len(text) <= overlap:
            return text
        
        # Try to find a good breaking point (space or punctuation)
        overlap_text = text[-overlap:]
        
        # Find the first space to avoid breaking words
        first_space = overlap_text.find(' ')
        if first_space > 0:
            overlap_text = overlap_text[first_space:]
        
        return overlap_text
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with processing
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', cleaned)
        
        # Normalize quotes and dashes
        cleaned = cleaned.replace('"', '"').replace('"', '"')
        cleaned = cleaned.replace(''', "'").replace(''', "'")
        cleaned = cleaned.replace('—', '-').replace('–', '-')
        
        return cleaned.strip()
    
    def _extract_title(self, text: str) -> str:
        """Extract title from text (first line or first sentence)"""
        lines = text.split('\n')
        
        # Try first non-empty line
        for line in lines:
            if line.strip():
                title = line.strip()
                # Limit title length
                if len(title) > 100:
                    title = title[:100] + "..."
                return title
        
        # Fallback to first sentence
        sentences = text.split('.')
        if sentences:
            title = sentences[0].strip()
            if len(title) > 100:
                title = title[:100] + "..."
            return title
        
        return "Untitled Document"
    
    def _generate_document_id(self, source_path: str, text: str) -> str:
        """Generate a consistent document ID based on path and content"""
        # Create hash from source path and text content
        content = f"{source_path}:{text[:1000]}"  # Use first 1000 chars
        hash_object = hashlib.sha256(content.encode('utf-8'))
        return hash_object.hexdigest()[:16]  # Use first 16 chars as ID


# Global document processor instance  
document_processor = DocumentProcessor()