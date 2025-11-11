"""
Cross-Encoder Reranker for RAG
Provides second-stage precision ranking after initial retrieval
"""

import logging
from typing import List, Tuple, Optional
from datetime import datetime

try:
    from sentence_transformers import CrossEncoder
    from langchain_core.documents import Document
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    CrossEncoder = None
    Document = None

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """
    Rerank documents using cross-encoder model for improved precision
    
    Cross-encoders jointly encode query and document, providing more accurate
    relevance scores than bi-encoders (used in embeddings).
    """
    
    def __init__(
        self, 
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2",
        max_length: int = 512
    ):
        """
        Initialize cross-encoder reranker
        
        Args:
            model_name: HuggingFace model name for cross-encoder
            max_length: Maximum sequence length for model
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is required for reranking. "
                "Install with: pip install sentence-transformers"
            )
        
        self.model_name = model_name
        self.max_length = max_length
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Lazy load the cross-encoder model"""
        try:
            self.model = CrossEncoder(self.model_name, max_length=self.max_length)
            logger.info(f"[OK] Cross-encoder model loaded: {self.model_name}")
        except Exception as e:
            logger.error(f"[ERROR] Failed to load cross-encoder model: {e}")
            raise
    
    def rerank(
        self, 
        query: str, 
        documents: List[Document], 
        top_k: int = 5,
        return_scores: bool = True
    ) -> List[Tuple[Document, float]]:
        """
        Rerank documents by relevance to query
        
        Args:
            query: User query
            documents: List of candidate documents from initial retrieval
            top_k: Number of top documents to return
            return_scores: Whether to return scores with documents
        
        Returns:
            List of (document, score) tuples, sorted by relevance (descending)
        """
        if not documents:
            logger.warning("No documents provided for reranking")
            return []
        
        if not self.model:
            logger.error("Cross-encoder model not initialized")
            return [(doc, 0.0) for doc in documents[:top_k]]
        
        try:
            start_time = datetime.utcnow()
            
            # Prepare query-document pairs for cross-encoder
            pairs = []
            for doc in documents:
                # Truncate document content if too long
                content = doc.page_content[:2000]  # Limit to 2000 chars
                pairs.append([query, content])
            
            # Get relevance scores from cross-encoder
            scores = self.model.predict(pairs)
            
            # Convert to list if numpy array
            if hasattr(scores, 'tolist'):
                scores = scores.tolist()
            
            # Pair documents with scores
            doc_score_pairs = list(zip(documents, scores))
            
            # Sort by score (descending)
            doc_score_pairs.sort(key=lambda x: x[1], reverse=True)
            
            # Take top_k
            top_docs = doc_score_pairs[:top_k]
            
            # Calculate reranking time
            rerank_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.info(
                f"[OK] Reranked {len(documents)} docs -> top {len(top_docs)} "
                f"in {rerank_time:.3f}s"
            )
            
            return top_docs if return_scores else [doc for doc, _ in top_docs]
            
        except Exception as e:
            logger.error(f"[ERROR] Reranking failed: {e}")
            # Fallback: return original documents
            return [(doc, 0.0) for doc in documents[:top_k]]
    
    def rerank_with_metadata(
        self,
        query: str,
        documents: List[Document],
        top_k: int = 5
    ) -> List[Document]:
        """
        Rerank documents and add reranking scores to metadata
        
        Args:
            query: User query
            documents: List of candidate documents
            top_k: Number of top documents to return
        
        Returns:
            List of documents with rerank_score in metadata
        """
        reranked_docs_with_scores = self.rerank(query, documents, top_k)
        
        # Add scores to document metadata
        reranked_docs = []
        for doc, score in reranked_docs_with_scores:
            # Create a copy to avoid modifying original
            doc_copy = Document(
                page_content=doc.page_content,
                metadata={**doc.metadata, 'rerank_score': float(score)}
            )
            reranked_docs.append(doc_copy)
        
        return reranked_docs
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            "model_name": self.model_name,
            "max_length": self.max_length,
            "is_loaded": self.model is not None
        }


# Global reranker instance
_reranker = None


def get_reranker(
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-12-v2"
) -> CrossEncoderReranker:
    """Get the global reranker instance"""
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoderReranker(model_name=model_name)
    return _reranker


def rerank_documents(
    query: str,
    documents: List[Document],
    top_k: int = 5
) -> List[Tuple[Document, float]]:
    """Convenience function to rerank documents"""
    reranker = get_reranker()
    return reranker.rerank(query, documents, top_k)

