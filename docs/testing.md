# Testing Strategy

## Overview

The AI Marketing Agents system implements a comprehensive testing strategy covering unit tests, integration tests, end-to-end tests, and performance benchmarks. The testing approach emphasizes AI-specific validation, real-time system reliability, and production readiness.

## Testing Pyramid

```
┌─────────────────────────────────────┐
│         End-to-End Tests            │
│    (Full workflow validation)       │
│                                     │
│  ┌─────────────────────────────────┐ │
│  │    Integration Tests           │ │
│  │  (Component interaction)       │ │
│  │                                 │ │
│  │  ┌─────────────────────────────┐ │ │
│  │  │     Unit Tests             │ │ │
│  │  │   (Individual functions)   │ │ │
│  │  └─────────────────────────────┘ │ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Unit Testing

### Agent Logic Testing
```python
# tests/test_agents.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.lead_gen import LeadGenerationAgent
from app.agents.content_creator import ContentCreatorAgent

class TestLeadGenerationAgent:
    @pytest.fixture
    async def agent(self):
        agent = LeadGenerationAgent()
        agent.llm = AsyncMock()
        agent.scraper = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_identify_audience(self, agent):
        """Test audience identification logic"""
        campaign_config = {
            "target_industry": "technology",
            "company_size": "50-200",
            "job_titles": ["CTO", "VP Engineering"]
        }

        audience = await agent.identify_audience(campaign_config)

        assert "industry" in audience
        assert audience["industry"] == "technology"
        assert len(audience["job_titles"]) > 0

    @pytest.mark.asyncio
    async def test_qualify_lead_scoring(self, agent):
        """Test lead scoring algorithm"""
        lead = {
            "company": "TechCorp",
            "job_title": "CTO",
            "industry": "technology",
            "company_size": 150
        }

        scored_lead = await agent.qualify_lead(lead)

        assert "score" in scored_lead
        assert 0 <= scored_lead["score"] <= 1
        assert scored_lead["qualified"] == (scored_lead["score"] > 0.7)

class TestContentCreatorAgent:
    @pytest.fixture
    async def agent(self):
        agent = ContentCreatorAgent()
        agent.llm = AsyncMock()
        agent.rag = AsyncMock()
        return agent

    @pytest.mark.asyncio
    async def test_content_generation_with_rag(self, agent):
        """Test content generation with RAG context"""
        agent.rag.retrieve.return_value = "Relevant marketing context..."
        agent.llm.generate.return_value = "Generated blog post content"

        result = await agent.generate_content(
            content_type="blog_post",
            topic="AI Marketing Trends",
            context="B2B technology audience"
        )

        assert "content" in result
        assert "metadata" in result
        agent.rag.retrieve.assert_called_once()
        agent.llm.generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_ab_variant_generation(self, agent):
        """Test A/B testing variant generation"""
        base_content = "Original blog post content"

        variants = await agent.generate_variants(base_content, count=3)

        assert len(variants) == 3
        for variant in variants:
            assert variant != base_content  # Variants should differ
            assert len(variant) > 0
```

### RAG System Testing
```python
# tests/test_rag.py
import pytest
from app.rag.system import AdvancedRAGSystem

class TestAdvancedRAG:
    @pytest.fixture
    async def rag_system(self):
        system = AdvancedRAGSystem()
        system.vectorstore = AsyncMock()
        system.llm = AsyncMock()
        return system

    @pytest.mark.asyncio
    async def test_multi_query_retrieval(self, rag_system):
        """Test multi-query retrieval expansion"""
        query = "marketing automation"

        # Mock the multi-query expansion
        rag_system.multi_query_retriever.aget_relevant_documents.return_value = [
            MagicMock(page_content="Content 1", metadata={"source": "doc1"}),
            MagicMock(page_content="Content 2", metadata={"source": "doc2"})
        ]

        results = await rag_system.multi_query_retrieve(query)

        assert len(results) >= 2
        rag_system.multi_query_retriever.aget_relevant_documents.assert_called()

    @pytest.mark.asyncio
    async def test_contextual_compression(self, rag_system):
        """Test document compression and reranking"""
        docs = [
            MagicMock(page_content="Long irrelevant content..."),
            MagicMock(page_content="Short relevant content")
        ]

        compressed = await rag_system.compress_documents(docs, query="marketing")

        assert len(compressed) <= len(docs)  # Should compress
        # Most relevant docs should be prioritized

    @pytest.mark.asyncio
    async def test_response_synthesis(self, rag_system):
        """Test final response generation with citations"""
        context = "Marketing automation context..."
        query = "What is marketing automation?"

        rag_system.llm.ainvoke.return_value = MagicMock(
            content="Marketing automation is...",
            usage_metadata={"total_tokens": 150}
        )

        response = await rag_system.synthesize_response(context, query)

        assert "answer" in response
        assert "citations" in response
        assert "confidence" in response
```

### Behavioral Intelligence Testing
```python
# tests/test_personalization.py
import pytest
from app.personalization.engine import BehavioralEngine

class TestBehavioralEngine:
    @pytest.fixture
    async def engine(self):
        engine = BehavioralEngine()
        engine.db = AsyncMock()
        engine.redis = AsyncMock()
        return engine

    @pytest.mark.asyncio
    async def test_event_processing(self, engine):
        """Test real-time event processing"""
        event = {
            "user_id": "user_123",
            "event": "page_view",
            "properties": {"page": "/pricing"}
        }

        await engine.process_event(event)

        # Verify event stored
        engine.db.execute.assert_called()

        # Verify profile updated
        engine.redis.hset.assert_called_with(
            "user_profile:user_123",
            mapping={"last_page": "/pricing", "page_views": 1}
        )

    @pytest.mark.asyncio
    async def test_intent_prediction(self, engine):
        """Test user intent prediction"""
        user_events = [
            {"event": "page_view", "properties": {"page": "/pricing"}},
            {"event": "page_view", "properties": {"page": "/demo"}},
            {"event": "form_start", "properties": {"form": "contact"}}
        ]

        intent = await engine.predict_intent("user_123", user_events)

        assert intent in ["purchase", "demo_request", "contact", "browsing"]
        assert isinstance(intent, str)

    @pytest.mark.asyncio
    async def test_personalization_recommendations(self, engine):
        """Test personalized recommendations"""
        user_profile = {
            "segment": "enterprise",
            "interests": ["automation", "analytics"],
            "last_activity": "2024-01-01"
        }

        recommendations = await engine.get_recommendations(
            "user_123",
            user_profile,
            context="homepage"
        )

        assert "recommendations" in recommendations
        assert len(recommendations["recommendations"]) > 0

        for rec in recommendations["recommendations"]:
            assert "type" in rec
            assert "id" in rec
            assert "relevance_score" in rec
```

## Integration Testing

### API Integration Tests
```python
# tests/test_api_integration.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
class TestAPIIntegration:
    @pytest.fixture
    async def client(self):
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            yield client

    async def test_event_tracking_pipeline(self, client):
        """Test complete event tracking pipeline"""
        event_data = {
            "user_id": "test_user",
            "event": "page_view",
            "properties": {"page": "/test"}
        }

        response = await client.post(
            "/api/v1/events/track",
            json=event_data,
            headers={"X-API-Key": "test_key"}
        )

        assert response.status_code == 201
        data = response.json()

        assert "event_id" in data
        assert data["status"] == "tracked"

        # Verify event stored in database
        # Verify behavioral profile updated
        # Verify real-time processing triggered

    async def test_campaign_creation_workflow(self, client):
        """Test campaign creation with agent coordination"""
        campaign_data = {
            "name": "Test Campaign",
            "type": "lead_gen",
            "budget": 1000,
            "channels": ["google_ads"],
            "target_audience": {
                "industry": "technology",
                "company_size": "50-200"
            }
        }

        response = await client.post(
            "/api/v1/campaigns/create",
            json=campaign_data,
            headers={"X-API-Key": "test_key"}
        )

        assert response.status_code == 201
        data = response.json()

        assert "campaign_id" in data
        assert data["status"] == "created"

        # Verify campaign stored
        # Verify agents assigned
        # Verify tasks queued

    async def test_content_generation_with_rag(self, client):
        """Test content generation with RAG integration"""
        content_request = {
            "type": "blog_post",
            "topic": "AI Marketing",
            "audience": "marketers"
        }

        response = await client.post(
            "/api/v1/content/generate",
            json=content_request,
            headers={"X-API-Key": "test_key"}
        )

        assert response.status_code == 200
        data = response.json()

        assert "content" in data
        assert "metadata" in data
        assert len(data["content"]) > 0

        # Verify RAG retrieval called
        # Verify LLM generation with context
        # Verify content stored in library
```

### Agent Coordination Tests
```python
# tests/test_agent_coordination.py
import pytest
from app.agents.orchestrator import AgentOrchestrator

class TestAgentOrchestration:
    @pytest.fixture
    async def orchestrator(self):
        orch = AgentOrchestrator()
        # Mock all agents
        orch.agents = {
            'lead_gen': AsyncMock(),
            'content': AsyncMock(),
            'ad_manager': AsyncMock()
        }
        return orch

    @pytest.mark.asyncio
    async def test_campaign_execution_flow(self, orchestrator):
        """Test complete campaign execution flow"""
        campaign_config = {
            "name": "Test Campaign",
            "budget": 1000,
            "audience": {"industry": "tech"}
        }

        # Execute campaign
        result = await orchestrator.execute_campaign(campaign_config)

        # Verify agent execution order
        orchestrator.agents['lead_gen'].execute.assert_called_once()
        orchestrator.agents['content'].execute.assert_called_once()
        orchestrator.agents['ad_manager'].execute.assert_called_once()

        # Verify state transitions
        assert "campaign_id" in result
        assert "status" in result

    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, orchestrator):
        """Test error handling in agent orchestration"""
        # Make lead gen agent fail
        orchestrator.agents['lead_gen'].execute.side_effect = Exception("API Error")

        campaign_config = {"name": "Test Campaign"}

        # Should handle error gracefully
        result = await orchestrator.execute_campaign(campaign_config)

        # Verify error logged
        # Verify fallback behavior
        # Verify campaign marked as failed
        assert result["status"] == "failed"
        assert "error" in result
```

## End-to-End Testing

### Campaign Workflow E2E Test
```python
# tests/test_e2e_campaign.py
import pytest
from tests.utils import TestClient, TestDatabase

@pytest.mark.e2e
class TestCampaignE2E:
    @pytest.fixture
    async def test_setup(self):
        """Setup test environment with real dependencies"""
        client = TestClient()
        db = TestDatabase()

        # Setup test data
        await db.setup_test_user()
        await db.setup_test_knowledge_base()

        yield client, db

        # Cleanup
        await db.cleanup()

    @pytest.mark.asyncio
    async def test_complete_campaign_workflow(self, test_setup):
        """Test complete campaign from creation to execution"""
        client, db = test_setup

        # 1. Create campaign
        campaign_response = await client.post("/api/v1/campaigns/create", {
            "name": "E2E Test Campaign",
            "type": "lead_gen",
            "budget": 500,
            "channels": ["google_ads"],
            "target_audience": {
                "industry": "technology",
                "company_size": "50-200"
            }
        })

        campaign_id = campaign_response.json()["campaign_id"]

        # 2. Verify campaign created
        campaign = await db.get_campaign(campaign_id)
        assert campaign["status"] == "created"

        # 3. Wait for agent execution (or trigger manually in test)
        await client.post(f"/api/v1/campaigns/{campaign_id}/execute")

        # 4. Monitor execution
        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = await client.get(f"/api/v1/campaigns/{campaign_id}")
            status = status_response.json()["status"]

            if status == "completed":
                break
            elif status == "failed":
                pytest.fail("Campaign execution failed")

            await asyncio.sleep(2)

        # 5. Verify results
        final_status = await client.get(f"/api/v1/campaigns/{campaign_id}")
        campaign_data = final_status.json()

        assert campaign_data["status"] == "completed"
        assert "leads_generated" in campaign_data["performance"]
        assert "content_created" in campaign_data["performance"]

        # 6. Verify data persistence
        leads = await db.get_leads_by_campaign(campaign_id)
        assert len(leads) > 0

        content = await db.get_content_by_campaign(campaign_id)
        assert len(content) > 0
```

### Real-time Personalization E2E Test
```python
# tests/test_e2e_personalization.py
import pytest
import asyncio

@pytest.mark.e2e
class TestPersonalizationE2E:
    @pytest.mark.asyncio
    async def test_realtime_personalization_flow(self, client):
        """Test real-time personalization from event to recommendation"""
        user_id = "test_user_e2e"

        # 1. Track user behavior
        events = [
            {"user_id": user_id, "event": "page_view", "properties": {"page": "/pricing"}},
            {"user_id": user_id, "event": "page_view", "properties": {"page": "/demo"}},
            {"user_id": user_id, "event": "form_start", "properties": {"form": "contact"}},
        ]

        for event in events:
            response = await client.post("/api/v1/events/track", json=event)
            assert response.status_code == 201

        # 2. Wait for processing
        await asyncio.sleep(2)

        # 3. Get personalized recommendations
        rec_response = await client.get(f"/api/v1/recommendations/{user_id}?context=homepage")
        assert rec_response.status_code == 200

        recommendations = rec_response.json()

        # 4. Verify personalization
        assert len(recommendations["recommendations"]) > 0

        # Should recommend demo-related content based on behavior
        demo_recs = [r for r in recommendations["recommendations"]
                    if "demo" in r.get("title", "").lower()]
        assert len(demo_recs) > 0

        # 5. Verify user profile updated
        profile_response = await client.get(f"/api/v1/users/{user_id}")
        profile = profile_response.json()

        assert profile["segment"] is not None
        assert profile["last_seen"] is not None
```

## Performance Testing

### Load Testing
```python
# tests/test_performance.py
import pytest
import asyncio
import time
from locust import HttpUser, task, between

class APIPerformanceTest:
    @pytest.mark.performance
    def test_api_throughput(self):
        """Test API can handle 1000+ events/second"""
        import aiohttp
        import asyncio

        async def send_event(session, event_id):
            event = {
                "user_id": f"user_{event_id % 100}",  # 100 test users
                "event": "page_view",
                "properties": {"page": f"/page_{event_id % 10}"}
            }

            async with session.post(
                "http://localhost:8000/api/v1/events/track",
                json=event,
                headers={"X-API-Key": "test_key"}
            ) as response:
                return response.status == 201

        async def run_load_test():
            async with aiohttp.ClientSession() as session:
                tasks = []
                start_time = time.time()

                # Send 1000 events
                for i in range(1000):
                    tasks.append(send_event(session, i))

                results = await asyncio.gather(*tasks)
                end_time = time.time()

                success_rate = sum(results) / len(results)
                total_time = end_time - start_time
                throughput = len(results) / total_time

                assert success_rate > 0.99  # 99% success rate
                assert throughput > 100  # 100+ events/second
                assert total_time < 15  # Complete within 15 seconds

        asyncio.run(run_load_test())

class LocustLoadTest(HttpUser):
    wait_time = between(0.1, 1)

    @task
    def track_event(self):
        self.client.post("/api/v1/events/track", json={
            "user_id": "load_test_user",
            "event": "page_view",
            "properties": {"page": "/test"}
        }, headers={"X-API-Key": "test_key"})

    @task(3)
    def get_recommendations(self):
        self.client.get("/api/v1/recommendations/load_test_user")
```

### RAG Performance Testing
```python
# tests/test_rag_performance.py
import pytest
import time
import asyncio

class TestRAGPerformance:
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_rag_query_latency(self, rag_system):
        """Test RAG query response time"""
        queries = [
            "What is marketing automation?",
            "How to optimize Google Ads campaigns?",
            "Lead generation strategies for B2B",
            "Content marketing best practices"
        ]

        latencies = []

        for query in queries:
            start_time = time.time()
            result = await rag_system.retrieve_and_generate(query)
            end_time = time.time()

            latency = end_time - start_time
            latencies.append(latency)

            # Each query should complete within 2 seconds
            assert latency < 2.0
            assert "answer" in result
            assert len(result["answer"]) > 0

        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 1.5  # Average under 1.5 seconds

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_rag_throughput(self, rag_system):
        """Test RAG can handle concurrent queries"""
        async def single_query(query_id):
            query = f"Marketing query {query_id}"
            start_time = time.time()
            result = await rag_system.retrieve_and_generate(query)
            end_time = time.time()
            return end_time - start_time

        # Run 10 concurrent queries
        tasks = [single_query(i) for i in range(10)]
        latencies = await asyncio.gather(*tasks)

        # All should complete within reasonable time
        max_latency = max(latencies)
        assert max_latency < 3.0

        # Average latency should be acceptable
        avg_latency = sum(latencies) / len(latencies)
        assert avg_latency < 2.0
```

## AI-Specific Testing

### RAG Quality Evaluation
```python
# tests/test_rag_quality.py
import pytest
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision
)

class TestRAGQuality:
    @pytest.mark.asyncio
    async def test_rag_answer_quality(self, rag_system):
        """Evaluate RAG answer quality using RAGAS"""
        test_cases = [
            {
                "question": "What are the benefits of marketing automation?",
                "ground_truth": "Marketing automation benefits include increased efficiency, better lead nurturing, improved customer segmentation, and higher conversion rates through personalized campaigns."
            },
            {
                "question": "How does behavioral targeting work?",
                "ground_truth": "Behavioral targeting analyzes user actions, preferences, and patterns to deliver relevant ads and content, improving engagement and conversion rates."
            }
        ]

        for test_case in test_cases:
            # Generate answer
            result = await rag_system.retrieve_and_generate(test_case["question"])

            # Evaluate with RAGAS
            evaluation = evaluate(
                predictions=[result["answer"]],
                references=[test_case["ground_truth"]],
                questions=[test_case["question"]],
                metrics=[faithfulness, answer_relevancy]
            )

            # Assert quality thresholds
            assert evaluation["faithfulness"] > 0.8
            assert evaluation["answer_relevancy"] > 0.8

    @pytest.mark.asyncio
    async def test_retrieval_accuracy(self, rag_system):
        """Test retrieval accuracy with known documents"""
        # Insert test documents
        test_docs = [
            {"content": "Google Ads is a pay-per-click advertising platform.", "id": "test_doc_1"},
            {"content": "LinkedIn Ads targets professional audiences.", "id": "test_doc_2"},
            {"content": "Content marketing builds brand authority.", "id": "test_doc_3"}
        ]

        await rag_system.add_documents(test_docs)

        # Test retrieval
        query = "advertising platforms for professionals"
        retrieved = await rag_system.retrieve(query, top_k=3)

        # Should retrieve LinkedIn doc
        linkedin_retrieved = any("LinkedIn" in doc["content"] for doc in retrieved)
        assert linkedin_retrieved

        # Should not retrieve irrelevant content marketing doc for this query
        content_marketing_retrieved = any("Content marketing" in doc["content"] for doc in retrieved)
        assert not content_marketing_retrieved
```

### Agent Behavior Testing
```python
# tests/test_agent_behavior.py
import pytest

class TestAgentBehavior:
    @pytest.mark.asyncio
    async def test_lead_scoring_consistency(self, lead_agent):
        """Test lead scoring produces consistent results"""
        lead = {
            "company": "TestCorp",
            "job_title": "CTO",
            "industry": "technology",
            "company_size": 100
        }

        # Score multiple times
        scores = []
        for _ in range(10):
            scored_lead = await lead_agent.qualify_lead(lead.copy())
            scores.append(scored_lead["score"])

        # Scores should be consistent (within small variance)
        avg_score = sum(scores) / len(scores)
        variance = max(scores) - min(scores)
        assert variance < 0.05  # Less than 5% variance

    @pytest.mark.asyncio
    async def test_content_generation_creativity(self, content_agent):
        """Test content generation produces varied outputs"""
        prompt = "Write a blog post about AI marketing"

        # Generate multiple variants
        variants = []
        for _ in range(5):
            content = await content_agent.generate_content("blog_post", prompt)
            variants.append(content["content"])

        # Check variety (simple heuristic)
        unique_sentences = set()
        for variant in variants:
            sentences = variant.split('.')
            unique_sentences.update(sentences[:3])  # First 3 sentences

        # Should have reasonable variety
        assert len(unique_sentences) > len(variants) * 2
```

## Test Infrastructure

### Test Configuration
```python
# tests/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.config import Settings
from app.database import get_db
from app.main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_settings():
    """Test-specific settings"""
    return Settings(
        database_url="postgresql+asyncpg://test:test@localhost:5433/test_db",
        redis_url="redis://localhost:6380",
        environment="test"
    )

@pytest.fixture(scope="session")
async def test_db_engine(test_settings):
    """Test database engine"""
    engine = create_async_engine(test_settings.database_url, echo=False)

    # Create test database schema
    async with engine.begin() as conn:
        # Create tables
        pass

    yield engine

    # Cleanup
    await engine.dispose()

@pytest.fixture
async def test_db_session(test_db_engine):
    """Test database session"""
    async with AsyncSession(test_db_engine) as session:
        yield session
        await session.rollback()

@pytest.fixture
async def test_client(test_settings):
    """Test HTTP client"""
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        # Override dependencies for testing
        app.dependency_overrides[get_db] = lambda: test_db_session
        yield client
        app.dependency_overrides.clear()
```

### Test Data Management
```python
# tests/utils.py
import json
from pathlib import Path

class TestDataManager:
    @staticmethod
    def load_test_events():
        """Load test event data"""
        with open(Path(__file__).parent / "data" / "test_events.json") as f:
            return json.load(f)

    @staticmethod
    def load_test_campaigns():
        """Load test campaign data"""
        with open(Path(__file__).parent / "data" / "test_campaigns.json") as f:
            return json.load(f)

    @staticmethod
    def create_mock_user(user_id="test_user"):
        """Create mock user data"""
        return {
            "user_id": user_id,
            "email": f"{user_id}@example.com",
            "traits": {"plan": "pro", "company": "TestCorp"},
            "segment": "enterprise"
        }

class TestDatabase:
    def __init__(self, session):
        self.session = session

    async def setup_test_user(self):
        """Setup test user in database"""
        # Implementation

    async def setup_test_knowledge_base(self):
        """Setup test knowledge base"""
        # Implementation

    async def cleanup(self):
        """Clean up test data"""
        # Implementation
```

## CI/CD Testing

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7-alpine

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Run unit tests
        run: pytest tests/unit/ -v --cov=app --cov-report=xml

      - name: Run integration tests
        run: pytest tests/integration/ -v

      - name: Run performance tests
        run: pytest tests/performance/ -v --durations=10

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
```

### Performance Regression Testing
```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  performance:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run performance tests
        run: pytest tests/performance/ -v --benchmark-json=output.json

      - name: Store benchmark results
        uses: benchmark-action/github-action-benchmark@v1
        with:
          name: AI Marketing Agents Performance
          tool: 'pytest'
          output-file-path: output.json
          github-token: ${{ secrets.GITHUB_TOKEN }}
          auto-push: true
```

This comprehensive testing strategy ensures the AI Marketing Agents system is reliable, performant, and ready for production deployment while showcasing advanced AI engineering capabilities.