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
    """RAG chain with confidence scoring and citations"""

    def __init__(self):
        self.retriever = get_advanced_retriever()
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

        # Retrieve documents
        docs = self.retriever.get_relevant_documents(question)

        # Format with citations
        context_parts = []
        for i, doc in enumerate(docs, 1):
            content = doc.page_content
            source = getattr(doc, 'metadata', {}).get('source', f'doc_{i}')
            context_parts.append(f"[Source {i}: {source}]\n{content}")

        return "\n\n".join(context_parts)

    def _calculate_confidence(self, inputs: Dict[str, Any]) -> float:
        """Calculate confidence score for the query"""
        question = inputs["question"]
        docs = self.retriever.get_relevant_documents(question)

        return self.confidence_scorer.calculate_confidence(question, docs)

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

            # Record metrics
            await record_rag_query(
                query=inputs["question"],
                response=result["answer"],
                confidence=result.get("confidence", 0.0),
                execution_time=(datetime.utcnow() - start_time).total_seconds(),
                success=True
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
                error=str(e)
            )
            raise e


# Global chain instance
_confidence_chain = None


def get_confidence_rag_chain() -> ConfidenceRAGChain:
    """Get the global confidence RAG chain instance"""
    global _confidence_chain
    if _confidence_chain is None:
        _confidence_chain = ConfidenceRAGChain()
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
