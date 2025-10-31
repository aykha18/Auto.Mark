"""
Advanced RAG Retrievers - MultiQuery, Ensemble, and Contextual Compression
"""

from typing import List, Dict, Any, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_community.retrievers import BM25Retriever
from langchain_core.vectorstores import VectorStore

from app.rag.vectorstore_manager import get_vector_store
from app.core.config import get_settings
settings = get_settings()


class MultiQueryRetriever(BaseRetriever):
    """Retriever that generates multiple queries and combines results"""

    def __init__(self, vectorstore: VectorStore, llm=None):
        super().__init__()
        self.vectorstore = vectorstore
        self.llm = llm

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get relevant documents using multi-query approach"""

        # Generate multiple query variations
        query_variations = self._generate_query_variations(query)

        all_docs = []
        seen_content = set()

        # Retrieve documents for each query variation
        for q in query_variations:
            docs = self.vectorstore.similarity_search(q, k=3)
            for doc in docs:
                # Deduplicate based on content
                content_hash = hash(doc.page_content[:200])
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_docs.append(doc)

        # Return top results
        return all_docs[:5]

    def _generate_query_variations(self, query: str) -> List[str]:
        """Generate multiple variations of the query"""
        # Simple query expansion for now
        variations = [query]

        # Add some basic variations
        if "how" in query.lower():
            variations.append(query.replace("how", "what is the process"))
        if "what" in query.lower():
            variations.append(query.replace("what", "explain"))

        # Add keyword-focused variations
        words = query.split()
        if len(words) > 3:
            variations.append(" ".join(words[:3]))  # First 3 words
            variations.append(" ".join(words[-3:]))  # Last 3 words

        return list(set(variations))  # Remove duplicates


class EnsembleRetriever(BaseRetriever):
    """Combines semantic search with BM25 keyword search"""

    def __init__(self, vectorstore: VectorStore):
        super().__init__()
        self.vectorstore = vectorstore
        self.bm25_retriever = None
        self.documents = []

    def add_documents(self, documents: List[Document]):
        """Add documents for BM25 indexing"""
        self.documents = documents
        self.bm25_retriever = BM25Retriever.from_documents(documents)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get relevant documents using ensemble approach"""

        # Semantic search results
        semantic_docs = self.vectorstore.similarity_search(query, k=5)

        # BM25 keyword search results
        bm25_docs = []
        if self.bm25_retriever:
            bm25_docs = self.bm25_retriever.get_relevant_documents(query)

        # Combine and deduplicate
        all_docs = semantic_docs + bm25_docs
        seen_content = set()
        unique_docs = []

        for doc in all_docs:
            content_hash = hash(doc.page_content[:200])
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)

        # Re-rank by relevance score (simple approach)
        return unique_docs[:5]


class ContextualCompressionRetriever(BaseRetriever):
    """Compresses retrieved documents to keep only relevant context"""

    def __init__(self, vectorstore: VectorStore, llm=None):
        super().__init__()
        self.vectorstore = vectorstore
        self.llm = llm

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get and compress relevant documents"""

        # First, get more documents than needed
        raw_docs = self.vectorstore.similarity_search(query, k=10)

        # Compress each document
        compressed_docs = []
        for doc in raw_docs:
            compressed_content = self._compress_document(doc, query)
            if compressed_content and len(compressed_content) > 50:  # Minimum length
                compressed_doc = Document(
                    page_content=compressed_content,
                    metadata={**doc.metadata, "original_length": len(doc.page_content)}
                )
                compressed_docs.append(compressed_doc)

        return compressed_docs[:5]

    def _compress_document(self, document: Document, query: str) -> str:
        """Compress document to keep only relevant parts"""
        content = document.page_content

        # Simple compression: keep sentences containing query terms
        query_terms = set(query.lower().split())
        sentences = content.split('.')

        relevant_sentences = []
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in query_terms):
                relevant_sentences.append(sentence.strip())

        # If no relevant sentences found, return original content
        if not relevant_sentences:
            return content

        return '. '.join(relevant_sentences)


# Global retriever instances
_multi_query_retriever = None
_ensemble_retriever = None
_contextual_retriever = None


def get_multi_query_retriever() -> MultiQueryRetriever:
    """Get multi-query retriever instance"""
    global _multi_query_retriever
    if _multi_query_retriever is None:
        vectorstore = get_vector_store()
        _multi_query_retriever = MultiQueryRetriever(vectorstore)
    return _multi_query_retriever


def get_ensemble_retriever() -> EnsembleRetriever:
    """Get ensemble retriever instance"""
    global _ensemble_retriever
    if _ensemble_retriever is None:
        vectorstore = get_vector_store()
        _ensemble_retriever = EnsembleRetriever(vectorstore)
    return _ensemble_retriever


def get_contextual_compression_retriever() -> ContextualCompressionRetriever:
    """Get contextual compression retriever instance"""
    global _contextual_retriever
    if _contextual_retriever is None:
        vectorstore = get_vector_store()
        _contextual_retriever = ContextualCompressionRetriever(vectorstore)
    return _contextual_retriever


def get_advanced_retriever(strategy: str = "ensemble") -> BaseRetriever:
    """Get advanced retriever based on strategy"""
    if strategy == "multi_query":
        return get_multi_query_retriever()
    elif strategy == "ensemble":
        return get_ensemble_retriever()
    elif strategy == "contextual":
        return get_contextual_compression_retriever()
    else:
        # Default to ensemble
        return get_ensemble_retriever()
