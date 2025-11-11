"""
LCEL Chains with Citations and Confidence Scoring for RAG
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.documents import Document

from app.rag.advanced_retrievers import get_advanced_retriever
from app.rag.confidence_scorer import RAGConfidenceScorer as ConfidenceScorer
from app.rag.monitoring import record_rag_query
from app.llm.router import get_optimal_llm


class ConfidenceRAGChain:
    """RAG chain with confidence scoring, citations, and reranking"""

    def __init__(self, use_reranking: bool = True, retrieval_strategy: str = None):
        """
        Initialize RAG chain
        
        Args:
            use_reranking: Whether to use reranking (default: True)
            retrieval_strategy: Override retrieval strategy
                - None: Auto-select based on use_reranking
                - "reranking": Semantic + reranking (default if use_reranking=True)
                - "hybrid_reranking": Ensemble + reranking (best quality)
                - "ensemble": Semantic + BM25 (no reranking)
        """
        # Determine retrieval strategy
        if retrieval_strategy is None:
            retrieval_strategy = "reranking" if use_reranking else "ensemble"
        
        self.retrieval_strategy = retrieval_strategy
        self.use_reranking = use_reranking
        self.retriever = get_advanced_retriever(strategy=retrieval_strategy)
        self.confidence_scorer = ConfidenceScorer()
        self.llm = get_optimal_llm("Generate comprehensive answers with citations")

        # Build the LCEL chain
        self.chain = self._build_chain()

    def _build_chain(self):
        """Build the LCEL chain with confidence scoring"""

        # Prompt template
        template = """You are an expert marketing consultant. Use the following context to answer the question.
        Provide a comprehensive, accurate answer with specific citations from the context.

        Context:
        {context}

        Question: {question}

        Instructions:
        - Answer based only on the provided context
        - Include specific citations with source references
        - Be comprehensive but concise
        - If context is insufficient, say so clearly

        Answer:"""

        prompt = ChatPromptTemplate.from_template(template)

        # Chain with confidence scoring
        chain = (
            RunnablePassthrough.assign(
                context=self._format_context,
                confidence=self._calculate_confidence
            )
            | prompt
            | self.llm
            | StrOutputParser()
            | RunnableLambda(self._add_metadata)
        )

        return chain

    def _format_context(self, inputs: Dict[str, Any]) -> str:
        """Format retrieved documents into context string"""
        question = inputs["question"]

        # Retrieve documents (with reranking if enabled)
        docs = self.retriever.get_relevant_documents(question)
        
        # Store docs for confidence calculation
        inputs["retrieved_docs"] = docs

        # Format with citations and rerank scores
        context_parts = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content
            source = doc.metadata.get('source', f'doc_{i}')
            
            # Add rerank score if available
            rerank_score = doc.metadata.get('rerank_score')
            if rerank_score is not None:
                source_info = f"Source {i}: {source} (relevance: {rerank_score:.2f})"
            else:
                source_info = f"Source {i}: {source}"
            
            context_parts.append(f"[{source_info}]\n{content}")

        return "\n\n".join(context_parts)

    def _calculate_confidence(self, inputs: Dict[str, Any]) -> float:
        """Calculate confidence score for the query"""
        question = inputs["question"]
        
        # Use already retrieved docs if available
        docs = inputs.get("retrieved_docs")
        if docs is None:
            docs = self.retriever.get_relevant_documents(question)
        
        # Boost confidence if reranking is enabled (more precise results)
        base_confidence = self.confidence_scorer.calculate_confidence(question, docs)
        
        if self.use_reranking and docs:
            # Check if docs have rerank scores
            has_rerank_scores = any(doc.metadata.get('rerank_score') is not None for doc in docs)
            if has_rerank_scores:
                # Boost confidence by 5-10% for reranked results
                avg_rerank_score = sum(
                    doc.metadata.get('rerank_score', 0) for doc in docs
                ) / len(docs)
                # Normalize rerank score (typically -10 to 10) to 0-1
                normalized_score = (avg_rerank_score + 10) / 20
                confidence_boost = normalized_score * 0.1  # Up to 10% boost
                base_confidence = min(1.0, base_confidence + confidence_boost)
        
        return base_confidence

    def _add_metadata(self, response: str) -> Dict[str, Any]:
        """Add metadata to the response"""
        return {
            "answer": response,
            "timestamp": datetime.utcnow().isoformat(),
            "chain_type": "confidence_rag"
        }

    async def ainvoke(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Async invoke with monitoring"""
        start_time = datetime.utcnow()

        try:
            # Execute chain
            result = await self.chain.ainvoke(inputs)
            
            # Extract reranking metrics if available
            docs = inputs.get("retrieved_docs", [])
            reranking_enabled = self.use_reranking
            avg_rerank_score = 0.0
            
            if docs and reranking_enabled:
                rerank_scores = [
                    doc.metadata.get('rerank_score', 0) 
                    for doc in docs 
                    if doc.metadata.get('rerank_score') is not None
                ]
                if rerank_scores:
                    avg_rerank_score = sum(rerank_scores) / len(rerank_scores)

            # Record metrics
            await record_rag_query(
                query=inputs["question"],
                response=result["answer"],
                confidence=result.get("confidence", 0.0),
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                success=True,
                retriever_type=self.retrieval_strategy,
                num_docs_retrieved=len(docs),
                reranking_enabled=reranking_enabled,
                avg_rerank_score=avg_rerank_score
            )

            return result

        except Exception as e:
            # Record failed query
            await record_rag_query(
                query=inputs["question"],
                response="",
                confidence=0.0,
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                success=False,
                error=str(e),
                retriever_type=self.retrieval_strategy,
                reranking_enabled=self.use_reranking
            )
            raise e


# Global chain instance
_confidence_chain = None


def get_confidence_rag_chain(
    use_reranking: bool = True,
    retrieval_strategy: str = None
) -> ConfidenceRAGChain:
    """
    Get the global confidence RAG chain instance
    
    Args:
        use_reranking: Whether to use reranking (default: True)
        retrieval_strategy: Override retrieval strategy (default: auto-select)
    
    Returns:
        ConfidenceRAGChain instance
    """
    global _confidence_chain
    if _confidence_chain is None:
        _confidence_chain = ConfidenceRAGChain(
            use_reranking=use_reranking,
            retrieval_strategy=retrieval_strategy
        )
    return _confidence_chain


async def query_with_confidence(question: str) -> Dict[str, Any]:
    """Query with confidence scoring and monitoring"""
    chain = get_confidence_rag_chain()
    return await chain.ainvoke({"question": question})


# Convenience functions for different use cases
async def query_marketing_strategy(question: str) -> Dict[str, Any]:
    """Query for marketing strategy questions"""
    llm = get_optimal_llm("Provide strategic marketing advice")
    chain = get_confidence_rag_chain()
    # Override LLM for this specific use case
    chain.llm = llm
    return await chain.ainvoke({"question": question})


async def query_technical_content(question: str) -> Dict[str, Any]:
    """Query for technical content questions"""
    llm = get_optimal_llm("Explain technical concepts clearly")
    chain = get_confidence_rag_chain()
    chain.llm = llm
    return await chain.ainvoke({"question": question})


async def query_creative_content(question: str) -> Dict[str, Any]:
    """Query for creative content generation"""
    llm = get_optimal_llm("Generate creative marketing content")
    chain = get_confidence_rag_chain()
    chain.llm = llm
    return await chain.ainvoke({"question": question})
