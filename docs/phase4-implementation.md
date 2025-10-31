# Phase 4: Advanced RAG System Implementation

## Overview
Phase 4 focuses on implementing a sophisticated Retrieval-Augmented Generation (RAG) system that enhances the AI agents' knowledge and response accuracy. This phase builds upon the LangChain and LangGraph foundation established in Phase 3.

## Objectives
- Implement vector database with embeddings for semantic search
- Build advanced retrieval strategies (MultiQuery, Ensemble, Contextual Compression)
- Create RAG chains using LangChain Expression Language (LCEL)
- Integrate LangSmith for observability and evaluation
- Ensure high accuracy and relevance in agent responses

## Implementation Steps

### 4.1 Setup Vector Database and Embeddings

#### 4.1.1 Initialize ChromaDB Collections
```python
# app/rag/vectorstore.py
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

class VectorStoreManager:
    """Manages ChromaDB collections for different knowledge domains"""

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-large",
            openai_api_key=settings.llm.openai_api_key
        )

    def create_collection(self, name: str, metadata: dict = None) -> Chroma:
        """Create a new Chroma collection with metadata"""
        return Chroma(
            client=self.client,
            collection_name=name,
            embedding_function=self.embeddings,
            collection_metadata=metadata
        )

    def get_or_create_collection(self, name: str) -> Chroma:
        """Get existing collection or create new one"""
        try:
            return Chroma(
                client=self.client,
                collection_name=name,
                embedding_function=self.embeddings
            )
        except:
            return self.create_collection(name)
```

#### 4.1.2 Document Ingestion Pipeline
```python
# app/rag/ingestion.py
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

class DocumentIngestionPipeline:
    """Pipeline for processing and ingesting documents into vector store"""

    def __init__(self, vector_store: Chroma):
        self.vector_store = vector_store
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )

    def ingest_documents(self, documents: List[Document], metadata: Dict[str, Any] = None):
        """Ingest documents with optional metadata"""
        # Split documents into chunks
        splits = self.text_splitter.split_documents(documents)

        # Add metadata to each split
        if metadata:
            for split in splits:
                split.metadata.update(metadata)

        # Add to vector store
        self.vector_store.add_documents(splits)

    def ingest_from_files(self, file_paths: List[str], source_type: str):
        """Ingest documents from various file formats"""
        documents = []

        for file_path in file_paths:
            if file_path.endswith('.pdf'):
                docs = self._load_pdf(file_path)
            elif file_path.endswith('.md'):
                docs = self._load_markdown(file_path)
            elif file_path.endswith('.txt'):
                docs = self._load_text(file_path)
            else:
                continue

            for doc in docs:
                doc.metadata.update({
                    'source': file_path,
                    'source_type': source_type,
                    'ingestion_date': datetime.utcnow().isoformat()
                })

            documents.extend(docs)

        self.ingest_documents(documents)
```

### 4.2 Build Advanced Retrieval Strategies

#### 4.2.1 MultiQueryRetriever Implementation
```python
# app/rag/retrievers.py
from langchain.retrievers import MultiQueryRetriever
from langchain_openai import ChatOpenAI

class MarketingMultiQueryRetriever:
    """Enhanced MultiQueryRetriever for marketing-specific queries"""

    def __init__(self, vector_store: Chroma, llm: ChatOpenAI):
        self.base_retriever = vector_store.as_retriever(search_kwargs={"k": 5})

        # Custom prompt for generating marketing-related query variations
        query_prompt = PromptTemplate(
            input_variables=["question"],
            template="""You are an AI assistant generating multiple search queries for marketing-related questions.
            Generate 3 different versions of the given question to retrieve relevant marketing information.
            Focus on marketing concepts, strategies, best practices, and industry knowledge.

            Original question: {question}

            Generated queries (one per line):"""
        )

        self.retriever = MultiQueryRetriever.from_llm(
            retriever=self.base_retriever,
            llm=llm,
            prompt=query_prompt
        )

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve documents using multi-query strategy"""
        return self.retriever.get_relevant_documents(query)
```

#### 4.2.2 EnsembleRetriever for Hybrid Search
```python
# app/rag/ensemble_retriever.py
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma

class MarketingEnsembleRetriever:
    """Combines semantic search with BM25 keyword search"""

    def __init__(self, vector_store: Chroma):
        # Semantic search retriever
        semantic_retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 10}
        )

        # Get all documents for BM25
        docs = vector_store.get()['documents']
        doc_objects = [Document(page_content=doc) for doc in docs]

        # BM25 keyword search retriever
        bm25_retriever = BM25Retriever.from_documents(doc_objects)
        bm25_retriever.k = 10

        # Combine with weights (60% semantic, 40% keyword)
        self.retriever = EnsembleRetriever(
            retrievers=[semantic_retriever, bm25_retriever],
            weights=[0.6, 0.4]
        )

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve using hybrid search approach"""
        return self.retriever.get_relevant_documents(query)
```

#### 4.2.3 ContextualCompressionRetriever with Reranking
```python
# app/rag/contextual_compression.py
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CohereRerank
from langchain_community.llms import Cohere

class MarketingContextualCompressionRetriever:
    """Compresses and reranks retrieved documents for better relevance"""

    def __init__(self, base_retriever, cohere_api_key: str):
        # Initialize Cohere for reranking
        cohere_llm = Cohere(
            cohere_api_key=cohere_api_key,
            model="rerank-english-v2.0"
        )

        # Create reranking compressor
        compressor = CohereRerank(
            client=cohere_llm,
            top_n=5  # Keep top 5 most relevant documents
        )

        # Create contextual compression retriever
        self.retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )

    def get_relevant_documents(self, query: str) -> List[Document]:
        """Retrieve and compress documents with reranking"""
        return self.retriever.get_relevant_documents(query)
```

### 4.3 Create RAG Chain with LCEL

#### 4.3.1 RAG Chain Implementation
```python
# app/rag/chains.py
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

class MarketingRAGChain:
    """RAG chain for marketing knowledge retrieval and generation"""

    def __init__(self, retriever, llm: ChatOpenAI):
        self.retriever = retriever
        self.llm = llm

        # Define the RAG prompt template
        self.prompt = ChatPromptTemplate.from_template("""
        You are an expert marketing consultant with deep knowledge of marketing strategies,
        best practices, and industry trends. Use the following context to provide accurate,
        actionable advice.

        Context from marketing knowledge base:
        {context}

        Question: {question}

        Instructions:
        - Provide specific, actionable marketing advice
        - Reference relevant marketing frameworks or methodologies when applicable
        - Include examples or case studies where helpful
        - Be concise but comprehensive
        - If the context doesn't contain enough information, say so clearly

        Answer:""")

        # Build the RAG chain using LCEL
        self.chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def invoke(self, question: str) -> str:
        """Execute the RAG chain"""
        return self.chain.invoke(question)

    async def ainvoke(self, question: str) -> str:
        """Async version of invoke"""
        return await self.chain.ainvoke(question)
```

#### 4.3.2 Response Generation with Citations
```python
# app/rag/citation_chain.py
from typing import List, Dict, Any
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

class CitationRAGChain:
    """RAG chain that provides responses with source citations"""

    def __init__(self, retriever, llm: ChatOpenAI):
        self.retriever = retriever
        self.llm = llm

        self.prompt = ChatPromptTemplate.from_template("""
        You are a marketing expert providing evidence-based advice.
        Use the retrieved documents to answer the question with citations.

        Retrieved documents:
        {context}

        Question: {question}

        Format your response as:
        1. Direct answer to the question
        2. Supporting evidence with citations [Source: document_title, page/section]
        3. Additional insights or recommendations

        If confidence is low, clearly state the limitations.
        """)

        self.chain = (
            {"context": self._format_docs_with_metadata, "question": RunnablePassthrough()}
            | self.prompt
            | self.llm
            | StrOutputParser()
        )

    def _format_docs_with_metadata(self, docs: List[Document]) -> str:
        """Format documents with metadata for citation"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            source = doc.metadata.get('source', 'Unknown')
            title = doc.metadata.get('title', f'Document {i}')
            formatted.append(f"[Document {i}] {title} (Source: {source})\n{doc.page_content}")

        return "\n\n".join(formatted)

    def invoke(self, question: str) -> str:
        """Execute chain with citations"""
        return self.chain.invoke(question)
```

#### 4.3.3 Confidence Scoring for Answers
```python
# app/rag/confidence_scorer.py
from typing import Dict, Any, List
from langchain_core.documents import Document

class RAGConfidenceScorer:
    """Scores confidence in RAG-generated answers"""

    def __init__(self):
        self.confidence_weights = {
            'relevance_score': 0.4,
            'document_count': 0.2,
            'semantic_similarity': 0.3,
            'source_authority': 0.1
        }

    def score_response(self, question: str, retrieved_docs: List[Document], response: str) -> Dict[str, Any]:
        """Calculate confidence score for RAG response"""

        # Calculate relevance score based on semantic similarity
        relevance_score = self._calculate_relevance_score(question, retrieved_docs)

        # Document count factor
        doc_count = len(retrieved_docs)
        doc_score = min(doc_count / 5, 1.0)  # Normalize to 5 docs as max

        # Semantic similarity score
        similarity_score = self._calculate_semantic_similarity(question, retrieved_docs)

        # Source authority score
        authority_score = self._calculate_source_authority(retrieved_docs)

        # Weighted confidence score
        confidence_score = (
            relevance_score * self.confidence_weights['relevance_score'] +
            doc_score * self.confidence_weights['document_count'] +
            similarity_score * self.confidence_weights['semantic_similarity'] +
            authority_score * self.confidence_weights['source_authority']
        )

        return {
            'confidence_score': round(confidence_score, 3),
            'confidence_level': self._get_confidence_level(confidence_score),
            'factors': {
                'relevance_score': relevance_score,
                'document_count': doc_count,
                'semantic_similarity': similarity_score,
                'source_authority': authority_score
            }
        }

    def _calculate_relevance_score(self, question: str, docs: List[Document]) -> float:
        """Calculate relevance based on keyword overlap and context"""
        question_words = set(question.lower().split())
        total_relevance = 0

        for doc in docs:
            doc_words = set(doc.page_content.lower().split())
            overlap = len(question_words.intersection(doc_words))
            relevance = overlap / len(question_words) if question_words else 0
            total_relevance += relevance

        return min(total_relevance / len(docs), 1.0) if docs else 0

    def _calculate_semantic_similarity(self, question: str, docs: List[Document]) -> float:
        """Placeholder for semantic similarity calculation"""
        # In production, use embeddings to calculate semantic similarity
        return 0.8 if docs else 0.0

    def _calculate_source_authority(self, docs: List[Document]) -> float:
        """Score based on source credibility"""
        authority_sources = ['forrester', 'gartner', 'mckinsey', 'harvard', 'stanford']
        authority_count = 0

        for doc in docs:
            source = doc.metadata.get('source', '').lower()
            if any(auth_source in source for auth_source in authority_sources):
                authority_count += 1

        return authority_count / len(docs) if docs else 0

    def _get_confidence_level(self, score: float) -> str:
        """Convert score to confidence level"""
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        else:
            return 'low'
```

### 4.4 Integrate LangSmith for Observability

#### 4.4.1 LangSmith Configuration
```python
# app/core/langsmith_config.py
import os
from langsmith import Client
from langsmith.run_helpers import traceable

class LangSmithManager:
    """Manages LangSmith integration for observability"""

    def __init__(self):
        self.api_key = os.getenv('LANGSMITH_API_KEY')
        self.project_name = os.getenv('LANGSMITH_PROJECT', 'ai-marketing-agents')

        if self.api_key:
            self.client = Client(api_key=self.api_key)
        else:
            self.client = None

    def is_enabled(self) -> bool:
        """Check if LangSmith is properly configured"""
        return self.client is not None

    def trace_rag_operation(self, operation_name: str):
        """Decorator for tracing RAG operations"""
        def decorator(func):
            if self.is_enabled():
                return traceable(
                    run_type="chain",
                    name=operation_name,
                    project_name=self.project_name
                )(func)
            return func
        return decorator

    def create_evaluation_dataset(self, name: str, questions_and_answers: List[Dict]):
        """Create evaluation dataset for RAG quality testing"""
        if not self.is_enabled():
            return

        dataset = self.client.create_dataset(
            dataset_name=name,
            description="RAG evaluation dataset for marketing queries"
        )

        examples = []
        for item in questions_and_answers:
            examples.append({
                "inputs": {"question": item["question"]},
                "outputs": {"answer": item["expected_answer"]},
                "metadata": item.get("metadata", {})
            })

        self.client.create_examples(
            dataset_id=dataset.id,
            examples=examples
        )

        return dataset
```

#### 4.4.2 RAG Evaluation Framework
```python
# app/rag/evaluation.py
from typing import List, Dict, Any
from langsmith.evaluation import evaluate
from langsmith.schemas import Example, Run

class RAGEvaluator:
    """Evaluates RAG system performance using LangSmith"""

    def __init__(self, langsmith_manager: LangSmithManager):
        self.langsmith = langsmith_manager

    def evaluate_rag_system(self, rag_chain, dataset_name: str) -> Dict[str, Any]:
        """Run comprehensive evaluation of RAG system"""

        def predict(inputs: Dict[str, Any]) -> Dict[str, Any]:
            """Prediction function for evaluation"""
            response = rag_chain.invoke(inputs["question"])
            return {"answer": response}

        def score_answer(run: Run, example: Example) -> Dict[str, Any]:
            """Scoring function for evaluation"""
            predicted = run.outputs["answer"]
            expected = example.outputs["answer"]

            # Simple string similarity score (in production, use more sophisticated metrics)
            similarity = self._calculate_similarity(predicted, expected)

            return {
                "answer_similarity": similarity,
                "answer_length": len(predicted),
                "expected_length": len(expected)
            }

        if not self.langsmith.is_enabled():
            return {"error": "LangSmith not configured"}

        # Run evaluation
        results = evaluate(
            predict,
            data=dataset_name,
            evaluators=[score_answer],
            experiment_prefix="rag_evaluation"
        )

        return {
            "experiment_id": results.experiment_id,
            "results": results.to_pandas().to_dict()
        }

    def _calculate_similarity(self, predicted: str, expected: str) -> float:
        """Calculate similarity between predicted and expected answers"""
        # Simple word overlap similarity
        pred_words = set(predicted.lower().split())
        exp_words = set(expected.lower().split())

        if not exp_words:
            return 0.0

        overlap = len(pred_words.intersection(exp_words))
        return overlap / len(exp_words)
```

#### 4.4.3 Monitoring Dashboard Integration
```python
# app/rag/monitoring.py
from typing import Dict, Any, List
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger(__name__)

class RAGMonitoringDashboard:
    """Monitoring dashboard for RAG system performance"""

    def __init__(self, langsmith_manager: LangSmithManager):
        self.langsmith = langsmith_manager
        self.metrics = {
            'total_queries': 0,
            'avg_response_time': 0,
            'avg_confidence_score': 0,
            'error_rate': 0,
            'top_queries': [],
            'performance_trends': []
        }

    def record_query(self, query: str, response_time: float, confidence_score: float, error: bool = False):
        """Record a RAG query for monitoring"""
        self.metrics['total_queries'] += 1

        if error:
            self.metrics['error_rate'] = (self.metrics['error_rate'] * (self.metrics['total_queries'] - 1) + 1) / self.metrics['total_queries']
        else:
            # Update average response time
            self.metrics['avg_response_time'] = (
                self.metrics['avg_response_time'] * (self.metrics['total_queries'] - 1) + response_time
            ) / self.metrics['total_queries']

            # Update average confidence score
            self.metrics['avg_confidence_score'] = (
                self.metrics['avg_confidence_score'] * (self.metrics['total_queries'] - 1) + confidence_score
            ) / self.metrics['total_queries']

        # Track top queries (simplified)
        if len(self.metrics['top_queries']) < 10:
            self.metrics['top_queries'].append({
                'query': query[:100],
                'timestamp': datetime.utcnow().isoformat(),
                'confidence': confidence_score
            })

        logger.info("RAG query recorded", query=query[:50], confidence=confidence_score, response_time=response_time)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get monitoring dashboard data"""
        return {
            'metrics': self.metrics,
            'timestamp': datetime.utcnow().isoformat(),
            'langsmith_enabled': self.langsmith.is_enabled()
        }

    def get_langsmith_runs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent LangSmith runs for RAG operations"""
        if not self.langsmith.is_enabled():
            return []

        try:
            runs = self.langsmith.client.list_runs(
                project_name=self.langsmith.project_name,
                start_time=datetime.utcnow() - timedelta(hours=hours)
            )

            return [
                {
                    'run_id': run.id,
                    'name': run.name,
                    'status': run.status,
                    'start_time': run.start_time.isoformat() if run.start_time else None,
                    'execution_time': (run.end_time - run.start_time).total_seconds() if run.end_time and run.start_time else None,
                    'error': run.error
                }
                for run in runs
            ]
        except Exception as e:
            logger.error("Failed to get LangSmith runs", error=str(e))
            return []
```

### 4.5 Integration with Agent System

#### 4.5.1 Enhanced Content Creator Agent
```python
# Update app/agents/content_creator.py
class ContentCreatorAgent(BaseAgent):
    """AI-powered content creation with enhanced RAG"""

    def __init__(self, llm: ChatOpenAI):
        super().__init__("content_creator", llm, self.get_content_tools())
        self.rag_service = get_rag_service()
        self.confidence_scorer = RAGConfidenceScorer()
        self.monitoring = RAGMonitoringDashboard(get_langsmith_manager())

    def generate_content_with_rag(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using enhanced RAG system"""

        start_time = time.time()

        try:
            # Query knowledge base with advanced retrieval
            context_docs = self.rag_service.query_with_advanced_retrieval(
                question=f"What are best practices for {requirements.get('content_type', 'content')}?",
                strategy="ensemble_rerank"
            )

            # Generate content using RAG chain
            content = self.rag_service.generate_with_citations(
                question=f"Create {requirements.get('content_type')} about {requirements.get('topic')}",
                context_docs=context_docs
            )

            # Calculate confidence score
            confidence = self.confidence_scorer.score_response(
                question=requirements.get('topic', ''),
                retrieved_docs=context_docs,
                response=content
            )

            # Record metrics
            response_time = time.time() - start_time
            self.monitoring.record_query(
                query=requirements.get('topic', ''),
                response_time=response_time,
                confidence_score=confidence['confidence_score']
            )

            return {
                'content': content,
                'confidence': confidence,
                'sources_used': len(context_docs),
                'generation_time': response_time
            }

        except Exception as e:
            # Record error
            response_time = time.time() - start_time
            self.monitoring.record_query(
                query=requirements.get('topic', ''),
                response_time=response_time,
                confidence_score=0.0,
                error=True
            )
            raise e
```

#### 4.5.2 RAG Service Integration
```python
# app/rag/advanced_rag.py
from .vectorstore import VectorStoreManager
from .retrievers import MarketingMultiQueryRetriever, MarketingEnsembleRetriever
from .contextual_compression import MarketingContextualCompressionRetriever
from .chains import MarketingRAGChain, CitationRAGChain
from .confidence_scorer import RAGConfidenceScorer
from .monitoring import RAGMonitoringDashboard

class AdvancedRAGService:
    """Advanced RAG service with multiple retrieval strategies"""

    def __init__(self):
        self.vector_store_manager = VectorStoreManager()
        self.retrievers = {}
        self.chains = {}
        self.confidence_scorer = RAGConfidenceScorer()
        self.monitoring = RAGMonitoringDashboard(get_langsmith_manager())

        self._initialize_retrievers()
        self._initialize_chains()

    def _initialize_retrievers(self):
        """Initialize different retrieval strategies"""
        marketing_collection = self.vector_store_manager.get_or_create_collection("marketing_knowledge")

        # Multi-query retriever
        self.retrievers['multi_query'] = MarketingMultiQueryRetriever(
            marketing_collection, get_llm_router().get_primary_llm()
        )

        # Ensemble retriever
        self.retrievers['ensemble'] = MarketingEnsembleRetriever(marketing_collection)

        # Contextual compression retriever
        self.retrievers['ensemble_rerank'] = MarketingContextualCompressionRetriever(
            self.retrievers['ensemble'].retriever,
            settings.cohere.api_key
        )

    def _initialize_chains(self):
        """Initialize RAG chains"""
        llm = get_llm_router().get_primary_llm()

        self.chains['basic_rag'] = MarketingRAGChain(
            self.retrievers['ensemble'].retriever, llm
        )

        self.chains['citation_rag'] = CitationRAGChain(
            self.retrievers['ensemble_rerank'].retriever, llm
        )

    def query_with_advanced_retrieval(self, question: str, strategy: str = "ensemble") -> List[Document]:
        """Query using specified retrieval strategy"""
        if strategy not in self.retrievers:
            strategy = "ensemble"

        return self.retrievers[strategy].get_relevant_documents(question)

    def generate_with_citations(self, question: str, context_docs: List[Document] = None) -> str:
        """Generate response with citations"""
        if context_docs:
            # Use provided context
            retriever = self._create_temporary_retriever(context_docs)
            chain = CitationRAGChain(retriever, get_llm_router().get_primary_llm())
            return chain.invoke(question)
        else:
            # Use default citation chain
            return self.chains['citation_rag'].invoke(question)

    def _create_temporary_retriever(self, documents: List[Document]):
        """Create temporary retriever from documents"""
        # Implementation for creating retriever from specific documents
        pass

    def evaluate_response_quality(self, question: str, response: str, context_docs: List[Document]) -> Dict[str, Any]:
        """Evaluate quality of generated response"""
        return self.confidence_scorer.score_response(question, context_docs, response)

# Global RAG service instance
_rag_service = None

def get_advanced_rag_service() -> AdvancedRAGService:
    """Get the global advanced RAG service instance"""
    global _rag_service
    if _rag_service is None:
        _rag_service = AdvancedRAGService()
    return _rag_service
```

## Testing and Validation

### 4.6 RAG System Testing
```python
# tests/test_rag_system.py
import pytest
from app.rag.advanced_rag import get_advanced_rag_service

class TestAdvancedRAGSystem:
    """Test suite for advanced RAG system"""

    @pytest.fixture
    def rag_service(self):
        return get_advanced_rag_service()

    def test_multi_query_retrieval(self, rag_service):
        """Test multi-query retrieval strategy"""
        question = "What are effective lead generation strategies?"
        docs = rag_service.query_with_advanced_retrieval(question, "multi_query")

        assert len(docs) > 0
        assert all(isinstance(doc, Document) for doc in docs)

    def test_ensemble_retrieval(self, rag_service):
        """Test ensemble retrieval strategy"""
        question = "How to optimize content for SEO?"
        docs = rag_service.query_with_advanced_retrieval(question, "ensemble")

        assert len(docs) > 0
        # Verify both semantic and keyword results are included

    def test_contextual_compression(self, rag_service):
        """Test contextual compression with reranking"""
        question = "What are the best practices for email marketing?"
        docs = rag_service.query_with_advanced_retrieval(question, "ensemble_rerank")

        assert len(docs) <= 5  # Should be compressed to top 5
        # Verify reranking has occurred

    def test_rag_chain_generation(self, rag_service):
        """Test RAG chain response generation"""
        question = "Explain A/B testing in marketing"
        response = rag_service.chains['basic_rag'].invoke(question)

        assert len(response) > 50
        assert "A/B" in response or "split" in response.lower()

    def test_citation_chain(self, rag_service):
        """Test citation-enabled response generation"""
        question = "What is customer acquisition cost?"
        response = rag_service.generate_with_citations(question)

        assert "[Document" in response or "Source:" in response
        assert len(response) > 100

    def test_confidence_scoring(self, rag_service):
        """Test confidence scoring for responses"""
        question = "Marketing funnel stages"
        docs = rag_service.query_with_advanced_retrieval(question)
        response = rag_service.chains['basic_rag'].invoke(question)

        confidence = rag_service.evaluate_response_quality(question, response, docs)

        assert 'confidence_score' in confidence
        assert 'confidence_level' in confidence
        assert 0 <= confidence['confidence_score'] <= 1

    @pytest.mark.integration
    def test_langsmith_integration(self, rag_service):
        """Test LangSmith integration for observability"""
        # This would require LangSmith to be configured
        dashboard_data = rag_service.monitoring.get_dashboard_data()

        assert 'metrics' in dashboard_data
        assert 'langsmith_enabled' in dashboard_data
```

## Performance Optimization

### 4.7 RAG Performance Tuning
```python
# app/rag/performance.py
from typing import Dict, Any, List
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

class RAGPerformanceOptimizer:
    """Optimizes RAG system performance"""

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.cache = {}  # Simple in-memory cache
        self.cache_ttl = 3600  # 1 hour

    async def parallel_retrieval(self, question: str, strategies: List[str]) -> Dict[str, List[Document]]:
        """Execute multiple retrieval strategies in parallel"""
        tasks = []

        for strategy in strategies:
            task = asyncio.get_event_loop().run_in_executor(
                self.executor,
                self._execute_retrieval,
                question,
                strategy
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        return dict(zip(strategies, results))

    def _execute_retrieval(self, question: str, strategy: str) -> List[Document]:
        """Execute single retrieval strategy"""
        rag_service = get_advanced_rag_service()
        return rag_service.query_with_advanced_retrieval(question, strategy)

    def get_cached_response(self, question: str) -> str:
        """Get cached response if available"""
        cache_key = hash(question)

        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item['timestamp'] < self.cache_ttl:
                return cached_item['response']

        return None

    def cache_response(self, question: str, response: str):
        """Cache response for future use"""
        cache_key = hash(question)
        self.cache[cache_key] = {
            'response': response,
            'timestamp': time.time()
        }

    def optimize_chunk_size(self, document_length: int) -> int:
        """Dynamically optimize chunk size based on document length"""
        if document_length < 1000:
            return 500
        elif document_length < 10000:
            return 1000
        else:
            return 1500

    def batch_process_documents(self, documents: List[Document], batch_size: int = 10) -> List[List[Document]]:
        """Process documents in batches for efficiency"""
        return [documents[i:i + batch_size] for i in range(0, len(documents), batch_size)]
```

## Deployment Considerations

### 4.8 Production Deployment
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  rag-service:
    build:
      context: .
      dockerfile: Dockerfile.rag
    environment:
      - CHROMA_SERVER_HOST=chroma
      - CHROMA_SERVER_HTTP_PORT=8000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - COHERE_API_KEY=${COHERE_API_KEY}
    depends_on:
      - chroma
    volumes:
      - chroma_data:/chroma/chroma

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_AUTHN_CREDENTIALS=${CHROMA_AUTH}
      - CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider

volumes:
  chroma_data:
```

### 4.9 Monitoring and Scaling
```python
# app/rag/scaling.py
from typing import Dict, Any
import psutil
import threading
import time

class RAGScaler:
    """Handles scaling decisions for RAG system"""

    def __init__(self):
        self.metrics = {
            'cpu_usage': 0,
            'memory_usage': 0,
            'query_queue_length': 0,
            'avg_response_time': 0
        }
        self.monitoring_thread = threading.Thread(target=self._monitor_system, daemon=True)
        self.monitoring_thread.start()

    def _monitor_system(self):
        """Continuously monitor system resources"""
        while True:
            self.metrics['cpu_usage'] = psutil.cpu_percent()
            self.metrics['memory_usage'] = psutil.virtual_memory().percent
            time.sleep(30)  # Monitor every 30 seconds

    def should_scale_up(self) -> bool:
        """Determine if system should scale up"""
        return (
            self.metrics['cpu_usage'] > 80 or
            self.metrics['memory_usage'] > 85 or
            self.metrics['avg_response_time'] > 5.0  # seconds
        )

    def get_scaling_recommendations(self) -> Dict[str, Any]:
        """Get scaling recommendations"""
        recommendations = {
            'scale_up': self.should_scale_up(),
            'target_instances': 1,
            'reason': []
        }

        if self.metrics['cpu_usage'] > 80:
            recommendations['reason'].append('High CPU usage')
            recommendations['target_instances'] = 2

        if self.metrics['memory_usage'] > 85:
            recommendations['reason'].append('High memory usage')
            recommendations['target_instances'] = max(recommendations['target_instances'], 2)

        if self.metrics['avg_response_time'] > 5.0:
            recommendations['reason'].append('Slow response times')
            recommendations['target_instances'] = max(recommendations['target_instances'], 3)

        return recommendations
```

## Summary

Phase 4 implements a comprehensive Advanced RAG system with:

1. **Vector Database Setup**: ChromaDB with OpenAI embeddings for semantic search
2. **Advanced Retrieval Strategies**: MultiQuery, Ensemble, and Contextual Compression retrievers
3. **RAG Chains**: LCEL-based chains with citation support and confidence scoring
4. **LangSmith Integration**: Full observability and evaluation framework
5. **Performance Optimization**: Parallel processing, caching, and dynamic scaling
6. **Production Deployment**: Docker configuration and monitoring

The implementation provides high-accuracy, contextually relevant responses for marketing agents while maintaining observability and performance optimization capabilities.
