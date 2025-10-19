# System Architecture

## Overview

The AI Marketing Agents system is designed as a pluggable microservice that integrates with any web application to provide autonomous marketing capabilities. The architecture emphasizes scalability, reliability, and showcase-worthy AI engineering features.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Host Application                              │
│                    (Flask, Django, Node.js, etc.)                    │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                 Marketing SDK (Python/JS)                      │  │
│  │  - Event Tracking: track(event, properties)                   │  │
│  │  - User Identification: identify(user_id, traits)             │  │
│  │  - Personalization: getRecommendations(user_id)               │  │
│  └────────────────────┬───────────────────────────────────────────┘  │
└───────────────────────┼───────────────────────────────────────────────┘
                        │ REST API / WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────────────┐
│                AI Marketing Agents Microservice                     │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                API Gateway (FastAPI)                           │  │
│  │  - Authentication & Rate Limiting                             │  │
│  │  - Request Validation & Circuit Breakers                      │  │
│  │  - WebSocket Manager                                          │  │
│  └────────────────────┬───────────────────────────────────────────┘  │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐  │
│  │            Agent Orchestration Layer (LangGraph)              │  │
│  │  - Multi-Agent Coordinator                                    │  │
│  │  - Task Queue Manager (Celery)                                │  │
│  │  - Agent Communication Protocol                               │  │
│  └────────────────────┬───────────────────────────────────────────┘  │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐  │
│  │                 Specialized AI Agents                          │  │
│  │                                                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │  │
│  │  │ Lead Gen    │  │ Content     │  │ Ad Manager  │  │ Analytics│ │  │
│  │  │ Agent       │  │ Creator     │  │ Agent       │  │ Agent    │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘ │  │
│  └────────────────────┬───────────────────────────────────────────┘  │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐  │
│  │              Advanced RAG System                              │  │
│  │  - Pinecone Vector DB                                        │  │
│  │  - Multi-Query Retrieval                                     │  │
│  │  - Contextual Compression                                    │  │
│  │  - LangSmith Observability                                   │  │
│  └────────────────────┬───────────────────────────────────────────┘  │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐  │
│  │            Behavioral Intelligence Engine                     │  │
│  │  - Real-time Event Processing                                │  │
│  │  - ML-based Personalization                                  │  │
│  │  - User Profiling & Segmentation                             │  │
│  └────────────────────┬───────────────────────────────────────────┘  │
│                       │                                              │
│  ┌────────────────────▼──────────────────────────────────────────┐  │
│  │                Data & Storage Layer                           │  │
│  │                                                               │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────┐ │  │
│  │  │ PostgreSQL  │  │ Redis Cache │  │ Pinecone   │  │ MinIO   │ │  │
│  │  │ (Primary)   │  │ & Queue     │  │ (Vectors)  │  │ (Files) │ │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────┘ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │                 External Integrations                          │  │
│  │  - Google Ads API                                             │  │
│  │  - Facebook Marketing API (Facebook, Instagram, Messenger)   │  │
│  │  - LinkedIn Marketing API                                     │  │
│  │  - ProductHunt API                                            │  │
│  │  - Grok-2 LLM                                                 │  │
│  │  - LangSmith (Observability)                                  │  │
│  └────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. SDK Integration Layer

**Purpose**: Provide easy integration for any web framework with minimal code changes.

**Python SDK**:
```python
from ai_marketing_sdk import MarketingClient

client = MarketingClient(
    api_key="your_api_key",
    base_url="https://marketing-api.yourdomain.com"
)

# Event tracking
client.track("user_123", "page_view", {"page": "/pricing"})

# User identification
client.identify("user_123", {"email": "user@example.com", "plan": "pro"})

# Real-time personalization
recommendations = client.get_recommendations("user_123")
```

**JavaScript SDK**:
```javascript
// Auto-injected script
<script src="https://cdn.yourdomain.com/marketing-sdk.js"></script>
<script>
  marketingSDK.init({ apiKey: 'your_api_key' });

  // Automatic event tracking
  marketingSDK.track('page_view', { page: window.location.pathname });

  // User identification
  marketingSDK.identify('user_123', { email: 'user@example.com' });
</script>
```

### 2. API Gateway (FastAPI)

**Core Features**:
- **Authentication**: API key validation with Redis-backed sessions
- **Rate Limiting**: Tier-based limits (Free: 1K/day, Pro: 100K/day)
- **Circuit Breakers**: Automatic failure detection and recovery
- **Request Validation**: Pydantic schemas with comprehensive error messages
- **WebSocket Support**: Real-time updates for campaign monitoring

**Key Endpoints**:
```
POST   /api/v1/events/track          # Event tracking
POST   /api/v1/users/identify        # User identification
POST   /api/v1/campaigns/create      # Campaign creation
GET    /api/v1/analytics/dashboard   # Analytics dashboard
POST   /api/v1/content/generate      # Content generation
WS     /ws/realtime                  # Real-time updates
```

### 3. Agent Orchestration Layer (LangGraph)

**Purpose**: Coordinate multiple AI agents in complex workflows with state management.

**LangGraph Workflow**:
```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class MarketingState(TypedDict):
    messages: Annotated[list, operator.add]
    campaign_config: dict
    audience_data: dict
    content_variants: list
    campaign_results: dict
    next_agent: str

# Define agent nodes
workflow = StateGraph(MarketingState)
workflow.add_node("lead_gen", lead_gen_agent.execute)
workflow.add_node("content_creator", content_agent.execute)
workflow.add_node("ad_manager", ad_agent.execute)
workflow.add_node("analytics", analytics_agent.execute)

# Define workflow edges
workflow.set_entry_point("lead_gen")
workflow.add_edge("lead_gen", "content_creator")
workflow.add_edge("content_creator", "ad_manager")
workflow.add_conditional_edges(
    "ad_manager",
    should_optimize,
    {"analytics": "analytics", END: END}
)

# Compile and execute
graph = workflow.compile()
result = await graph.ainvoke(initial_state)
```

### 4. Advanced RAG System

**Architecture**: Multi-stage retrieval with LangChain + Pinecone + LangSmith

```
Query Input
    │
    ▼
┌─────────────────────────────────────┐
│         Query Rewriting             │
│  - Multi-query expansion            │
│  - Intent clarification             │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│       Vector Retrieval              │
│  - Pinecone semantic search         │
│  - Metadata filtering               │
│  - Hybrid scoring                   │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│    Contextual Compression           │
│  - Cohere reranking                 │
│  - Redundancy removal               │
│  - Relevance filtering              │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│      Response Synthesis             │
│  - LangChain LCEL chains            │
│  - Citation tracking                │
│  - Confidence scoring               │
└─────────────────────────────────────┘
```

**Key Features**:
- **Multi-Query Retrieval**: Generate multiple query variations for better coverage
- **Hybrid Search**: Combine semantic (vector) and keyword-based retrieval
- **Contextual Compression**: Rerank and compress retrieved documents
- **LangSmith Observability**: Trace every LLM call with performance metrics

### 5. Specialized AI Agents

#### Lead Generation Agent
```python
class LeadGenerationAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="lead_gen",
            llm=ChatOpenAI(model="gpt-4-turbo"),
            tools=[
                SerpApiTool(),  # Web scraping
                LinkedInTool(), # Social media monitoring
                EnrichmentTool() # Data enrichment
            ]
        )

    async def execute(self, state: MarketingState):
        # Identify target audience
        audience = await self.identify_audience(state['campaign_config'])

        # Generate leads from multiple sources
        leads = await self.scrape_leads(audience)

        # Score and qualify leads
        qualified_leads = await self.qualify_leads(leads)

        # Update state
        return {
            **state,
            'audience_data': audience,
            'leads': qualified_leads
        }
```

#### Content Creator Agent
```python
class ContentCreatorAgent(BaseAgent):
    def __init__(self):
        self.rag_system = AdvancedRAGSystem()
        self.llm = LLMRouter.route('content_generation', priority='cost')

    async def generate_content(self, content_type, context):
        # Retrieve relevant context
        relevant_context = await self.rag_system.retrieve(
            f"Generate {content_type} for {context}"
        )

        # Generate with RAG-enhanced prompts
        content = await self.llm.generate(
            prompt=self.build_prompt(content_type, context, relevant_context)
        )

        # A/B test variants
        variants = await self.generate_variants(content)

        return {
            'primary': content,
            'variants': variants,
            'metadata': self.extract_metadata(content)
        }
```

#### Ad Manager Agent
```python
class AdManagerAgent(BaseAgent):
    def __init__(self):
        self.google_ads = GoogleAdsClient()
        self.facebook_ads = FacebookAdsClient()
        self.linkedin_ads = LinkedInAdsClient()
        self.producthunt = ProductHuntClient()
        self.budget_optimizer = BudgetOptimizer()

    async def deploy_campaign(self, audience, creatives, config):
        results = {}

        # Deploy to multiple platforms
        if 'google' in config['channels']:
            results['google'] = await self.google_ads.create_campaign(
                audience, creatives, config
            )

        if 'facebook' in config['channels']:
            results['facebook'] = await self.facebook_ads.create_campaign(
                audience, creatives, config
            )

        if 'linkedin' in config['channels']:
            results['linkedin'] = await self.linkedin_ads.create_campaign(
                audience, creatives, config
            )

        if 'producthunt' in config['channels']:
            results['producthunt'] = await self.producthunt.create_launch(
                audience, creatives, config
            )

        # Start performance monitoring
        await self.start_monitoring(results)

        return results

    async def optimize_campaign(self, campaign_id):
        # Get performance data
        performance = await self.get_performance(campaign_id)

        # Identify underperformers
        underperformers = self.identify_underperformers(performance)

        # Reallocate budget
        await self.reallocate_budget(underperformers, performance)

        # Generate new creatives
        new_creatives = await self.content_agent.generate_ad_variants()
        await self.deploy_new_creatives(new_creatives)
```

### 6. Behavioral Intelligence Engine

**Real-time Processing Pipeline**:
```
Raw Events → Validation → Enrichment → Segmentation → Personalization → Storage
     │             │            │            │              │            │
     ▼             ▼            ▼            ▼              ▼            ▼
  Redis       Pydantic     ML Models   Clustering     Recommendations  PostgreSQL
  Buffer      Schemas      Inference   Algorithms       Engine         + Pinecone
```

**Key Components**:
- **Event Ingestion**: High-throughput event processing with Redis buffering
- **User Profiling**: Real-time profile updates with trait aggregation
- **Intent Prediction**: ML models for predicting user next actions
- **Personalization Engine**: Context-aware recommendation generation

### 7. Data Storage Layer

**PostgreSQL**: Primary data store with optimized schemas for analytics
**Redis**: Caching, sessions, real-time data, and message queuing
**Pinecone**: Vector embeddings for semantic search and RAG
**MinIO**: File storage for generated content and assets

## Scalability & Performance

### Horizontal Scaling
- **API Gateway**: Kubernetes HPA based on CPU/memory
- **Agent Workers**: Celery autoscaling with Redis queues
- **Database**: Read replicas for analytics queries

### Performance Optimizations
- **Caching Strategy**: Multi-layer caching (Redis → Application → CDN)
- **Database Indexing**: Composite indexes for common query patterns
- **Async Processing**: Non-blocking I/O for all external API calls
- **Connection Pooling**: Efficient database and Redis connection management

### Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'CLOSED'

    async def call(self, func, *args, **kwargs):
        if self.state == 'OPEN':
            if self._should_attempt_reset():
                self.state = 'HALF_OPEN'
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _should_attempt_reset(self):
        return (time.time() - self.last_failure_time) > self.recovery_timeout
```

## Reliability & Resilience

### Error Handling Strategy
1. **Input Validation**: Comprehensive validation at API boundaries
2. **Graceful Degradation**: Core functionality continues when non-critical services fail
3. **Retry Logic**: Exponential backoff for transient failures
4. **Fallback Mechanisms**: Cached responses when services are unavailable

### Monitoring & Observability
- **LangSmith**: LLM call tracing, prompt performance, agent debugging
- **Prometheus**: System metrics, custom business metrics
- **Grafana**: Real-time dashboards and alerting
- **Sentry**: Error tracking and performance monitoring

### Security Measures
- **API Authentication**: Key-based auth with request signing
- **Data Encryption**: TLS 1.3, encrypted storage
- **Input Sanitization**: XSS prevention, SQL injection protection
- **Rate Limiting**: DDoS protection and fair usage enforcement

## Deployment Architecture

### Development Environment
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/marketing
      - REDIS_URL=redis://redis:6379
    depends_on: [db, redis, pinecone]

  worker:
    build: .
    command: celery -A app.tasks worker
    depends_on: [redis, db]

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=marketing

  redis:
    image: redis:7-alpine
```

### Production Environment
- **Kubernetes**: Container orchestration with Helm charts
- **Load Balancing**: Nginx ingress with SSL termination
- **Service Mesh**: Istio for traffic management and security
- **Monitoring Stack**: Prometheus + Grafana + ELK

## Showcase Features for AI Engineering

### 1. Advanced RAG Pipeline
- Multi-query retrieval with query expansion
- Contextual compression with reranking
- Hybrid search combining semantic and keyword methods
- Response synthesis with citation tracking

### 2. Multi-Agent Orchestration
- LangGraph stateful workflows
- Agent-to-agent communication protocols
- Conditional routing based on agent outputs
- Human-in-the-loop capabilities

### 3. Real-time Personalization
- Behavioral event processing at scale
- ML-based intent prediction
- Dynamic user segmentation
- Context-aware recommendation engine

### 4. Production Observability
- LangSmith integration for LLM monitoring
- Comprehensive metrics and alerting
- Performance profiling and optimization
- Error tracking with actionable insights

This architecture provides a solid foundation for a scalable, AI-powered marketing platform while showcasing cutting-edge engineering practices and technologies.