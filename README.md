# AI Marketing Agents MVP

A pluggable, autonomous AI marketing system that integrates with any application to automate lead generation, content creation, and behavioral personalization using advanced RAG and multi-agent orchestration.

## Overview

This MVP implements core requirements 1-6 from the full specification, focusing on showcase-worthy AI engineering features:

- **Advanced RAG System**: Multi-query retrieval, contextual compression, and hybrid search using LangChain + Pinecone + LangSmith
- **Multi-Agent Orchestration**: LangGraph-based agent coordination for marketing tasks
- **Real-time Personalization**: Behavioral intelligence with ML-driven recommendations
- **Pluggable Architecture**: SDK integration for any web framework

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Application                          │
│                (Flask, Django, Node.js, etc.)                │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │             Marketing SDK (Python/JS)                │  │
│  │  - track(event, properties)                          │  │
│  │  - identify(user_id, traits)                         │  │
│  └────────────────────┬─────────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────────┘
                        │ REST API / WebSocket
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            AI Marketing Agents Microservice                 │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            API Gateway (FastAPI)                     │  │
│  │  - Authentication & Rate Limiting                    │  │
│  │  - Request Validation & Circuit Breakers             │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │        Agent Orchestration (LangGraph)              │  │
│  │  - Lead Generation Agent                            │  │
│  │  - Content Creator Agent                            │  │
│  │  - Ad Manager Agent                                 │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │          Advanced RAG System                        │  │
│  │  - Pinecone Vector DB                               │  │
│  │  - Multi-Query Retrieval                            │  │
│  │  - Contextual Compression                           │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │        Behavioral Intelligence Engine               │  │
│  │  - Real-time Event Processing                       │  │
│  │  - ML-based Personalization                         │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│  ┌────────────────────▼─────────────────────────────────┐  │
│  │            Data & Storage Layer                      │  │
│  │  - PostgreSQL (Primary DB)                          │  │
│  │  - Redis (Cache & Queue)                            │  │
│  │  - Pinecone (Vectors)                               │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         External Integrations                        │  │
│  │  - Google Ads API                                    │  │
│  │  - Grok-2 LLM                                        │  │
│  │  - LangSmith (Observability)                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Core Framework
- **FastAPI**: High-performance async API with OpenAPI docs
- **PostgreSQL**: Primary data storage with async SQLAlchemy
- **Redis**: Caching, session management, and message queuing
- **Celery**: Distributed task processing with Redis broker

### AI/ML Stack
- **LangChain**: Agent orchestration and tool integration
- **LangGraph**: Complex multi-agent workflows with state management
- **LangSmith**: LLM observability, debugging, and evaluation
- **Pinecone**: Managed vector database for embeddings
- **Grok-2**: Primary LLM (cost-effective, real-time web access)
- **OpenAI Embeddings**: text-embedding-3-large for vectorization

### External APIs
- **Google Ads API**: Campaign management and optimization
- **Facebook Marketing API**: Multi-platform advertising (Facebook, Instagram, Messenger)
- **LinkedIn Marketing API**: B2B advertising and lead generation
- **ProductHunt API**: Product launch advertising
- **SerpApi/ScrapeBox**: Lead generation and web scraping

## Performance Benchmarks

- **API Latency**: <200ms for event tracking, <2s for content generation
- **Throughput**: 1000+ events/second processing
- **Cost Target**: <$100/month (Grok-2 at moderate usage)
- **Uptime**: 99.5% with graceful degradation
- **RAG Accuracy**: >90% retrieval relevance with hybrid search

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Pinecone account
- Grok-2 API key
- LangSmith account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-marketing-agents.git
cd ai-marketing-agents
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and database URLs
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the application:
```bash
# Start Redis (if not running)
redis-server

# Start Celery worker
celery -A app.tasks worker --loglevel=info

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### SDK Integration

#### Python SDK
```python
from ai_marketing_sdk import MarketingClient

client = MarketingClient(
    api_key="your_api_key",
    base_url="http://localhost:8000"
)

# Track events
client.track(
    user_id="user_123",
    event="product_viewed",
    properties={"product_id": "prod_456", "category": "electronics"}
)

# Identify users
client.identify(
    user_id="user_123",
    traits={"email": "user@example.com", "plan": "pro"}
)

# Get personalized recommendations
recommendations = client.get_recommendations(user_id="user_123")
```

#### JavaScript SDK
```javascript
// Include SDK
<script src="https://cdn.jsdelivr.net/npm/ai-marketing-sdk@1.0.0/dist/sdk.js"></script>

<script>
  const client = new MarketingSDK({
    apiKey: 'your_api_key',
    baseUrl: 'http://localhost:8000'
  });

  // Track events
  client.track('button_clicked', {
    button_id: 'signup_cta',
    page: 'landing'
  });

  // Identify user
  client.identify('user_123', {
    email: 'user@example.com',
    plan: 'pro'
  });
</script>
```

## API Documentation

### Core Endpoints

#### Event Tracking
```http
POST /api/v1/events/track
Content-Type: application/json

{
  "user_id": "string",
  "event": "string",
  "properties": {
    "key": "value"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### User Identification
```http
POST /api/v1/users/identify
Content-Type: application/json

{
  "user_id": "string",
  "traits": {
    "email": "string",
    "name": "string",
    "plan": "string"
  }
}
```

#### Content Generation
```http
POST /api/v1/content/generate
Content-Type: application/json

{
  "type": "blog_post",
  "topic": "AI Marketing Trends 2024",
  "audience": "marketing_professionals",
  "tone": "professional"
}
```

#### Campaign Management
```http
POST /api/v1/campaigns/create
Content-Type: application/json

{
  "name": "Q4 Lead Generation",
  "type": "lead_gen",
  "budget": 5000,
  "target_audience": {
    "industry": "technology",
    "company_size": "50-200",
    "job_titles": ["CTO", "VP Engineering"]
  },
  "channels": ["google_ads", "facebook", "linkedin"]
}
```

## Database Schema

### Core Tables

#### users
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_seen TIMESTAMP,
    traits JSONB,
    segment VARCHAR(50),
    ltv_prediction DECIMAL(10,2),
    churn_risk DECIMAL(3,2)
);
```

#### events
```sql
CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    event_name VARCHAR(100) NOT NULL,
    properties JSONB,
    timestamp TIMESTAMP DEFAULT NOW(),
    session_id UUID,
    INDEX idx_user_timestamp (user_id, timestamp),
    INDEX idx_event_name (event_name)
);
```

#### campaigns
```sql
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50),
    status VARCHAR(20),
    config JSONB,
    budget DECIMAL(10,2),
    spent DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### leads
```sql
CREATE TABLE leads (
    lead_id UUID PRIMARY KEY,
    email VARCHAR(255),
    score DECIMAL(3,2),
    qualified BOOLEAN DEFAULT FALSE,
    status VARCHAR(50),
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### content_library
```sql
CREATE TABLE content_library (
    content_id UUID PRIMARY KEY,
    content_type VARCHAR(50),
    title VARCHAR(500),
    body TEXT,
    metadata JSONB,
    performance_score DECIMAL(3,2),
    created_by VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Code Structure

```
ai-marketing-agents/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── event.py
│   │   ├── campaign.py
│   │   └── lead.py
│   ├── schemas/                # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── event.py
│   │   ├── user.py
│   │   └── campaign.py
│   ├── api/                    # API endpoints
│   │   ├── __init__.py
│   │   ├── events.py
│   │   ├── users.py
│   │   ├── campaigns.py
│   │   └── content.py
│   ├── agents/                 # AI Agents
│   │   ├── __init__.py
│   │   ├── base.py             # BaseAgent class
│   │   ├── lead_gen.py         # Lead Generation Agent
│   │   ├── content_creator.py  # Content Creator Agent
│   │   ├── ad_manager.py       # Ad Manager Agent
│   │   └── orchestrator.py     # Agent Orchestrator
│   ├── rag/                    # Advanced RAG System
│   │   ├── __init__.py
│   │   ├── vectorstore.py      # Pinecone integration
│   │   ├── retrievers.py       # Advanced retrievers
│   │   ├── chains.py           # RAG chains
│   │   └── knowledge_base.py   # Knowledge ingestion
│   ├── personalization/        # Behavioral Intelligence
│   │   ├── __init__.py
│   │   ├── engine.py           # Personalization engine
│   │   ├── models.py           # ML models
│   │   └── realtime.py         # Real-time processing
│   ├── integrations/           # External API integrations
│   │   ├── __init__.py
│   │   ├── google_ads.py
│   │   ├── grok_llm.py
│   │   └── serpapi.py
│   ├── core/                   # Core utilities
│   │   ├── __init__.py
│   │   ├── security.py         # Authentication & security
│   │   ├── cache.py            # Redis caching
│   │   ├── circuit_breaker.py  # Circuit breaker pattern
│   │   ├── metrics.py          # Monitoring & metrics
│   │   └── logger.py           # Logging configuration
│   └── tasks.py                # Celery tasks
├── sdk/
│   ├── python/
│   │   ├── __init__.py
│   │   ├── client.py
│   │   └── setup.py
│   └── javascript/
│       ├── dist/
│       ├── src/
│       └── package.json
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_agents.py
│   ├── test_rag.py
│   └── test_personalization.py
├── docs/
│   ├── api.md
│   ├── architecture.md
│   ├── deployment.md
│   └── monitoring.md
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
├── scripts/
│   ├── setup_db.py
│   ├── ingest_knowledge.py
│   └── benchmark.py
├── requirements.txt
├── .env.example
├── alembic.ini
└── README.md
```

## Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/marketing

# Redis
REDIS_URL=redis://localhost:6379

# Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=marketing-knowledge

# LLM APIs
GROK_API_KEY=your_grok_key
OPENAI_API_KEY=your_openai_key

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=ai-marketing-agents

# Google Ads
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_client_secret
GOOGLE_ADS_DEVELOPER_TOKEN=your_dev_token

# Facebook Ads
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token

# LinkedIn Ads
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret

# Security
SECRET_KEY=your_secret_key
API_KEY_HEADER=X-API-Key

# External APIs
SERPAPI_KEY=your_serpapi_key
```

## Deployment

### Docker Compose (Development)

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/marketing
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  celery_worker:
    build: .
    command: celery -A app.tasks worker --loglevel=info
    depends_on:
      - redis
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=marketing
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

  redis:
    image: redis:7-alpine
```

### Production Deployment

1. **Kubernetes**: Use the provided k8s manifests for production deployment
2. **Monitoring**: Prometheus + Grafana for metrics and alerting
3. **Load Balancing**: Nginx ingress with rate limiting
4. **Scaling**: Horizontal Pod Autoscaling based on CPU/memory

## Monitoring & Observability

### LangSmith Integration
- Real-time LLM call tracing
- Prompt performance analytics
- Agent decision debugging
- Automated evaluation pipelines

### Metrics & Alerting
- API response times and error rates
- Agent task success/failure rates
- Vector database query performance
- External API health checks

### Logging
- Structured JSON logging
- ELK stack integration
- Error tracking with Sentry
- Performance profiling

## Testing Strategy

### Unit Tests
- Agent logic and decision making
- RAG retrieval accuracy
- API endpoint validation
- Database operations

### Integration Tests
- Agent orchestration workflows
- External API integrations
- End-to-end campaign creation
- SDK functionality

### Performance Tests
- Load testing (1000+ concurrent requests)
- RAG query latency benchmarking
- Database throughput testing
- Memory usage profiling

### AI Evaluation
- RAG retrieval relevance scoring
- Content generation quality assessment
- Lead scoring accuracy validation
- Personalization recommendation testing

## Development Workflow

1. **Feature Development**
   - Create feature branch from `main`
   - Implement with comprehensive tests
   - Update documentation
   - Submit pull request

2. **Code Quality**
   - Black for code formatting
   - Flake8 for linting
   - MyPy for type checking
   - Pre-commit hooks

3. **CI/CD Pipeline**
   - GitHub Actions for automated testing
   - Docker image building
   - Security scanning
   - Performance regression testing

## Security Considerations

- API key authentication with rate limiting
- Input validation and sanitization
- SQL injection prevention with SQLAlchemy
- XSS protection in generated content
- Data encryption at rest and in transit
- Regular security audits and updates

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Update documentation
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions or issues:
- GitHub Issues: https://github.com/yourusername/ai-marketing-agents/issues
- Documentation: https://docs.ai-marketing-agents.com
- Email: support@ai-marketing-agents.com

## Roadmap

### MVP (Current)
- ✅ Pluggable architecture with SDK
- ✅ Advanced RAG with Pinecone + LangChain
- ✅ Multi-agent orchestration with LangGraph
- ✅ Behavioral intelligence and personalization
- ✅ Lead generation and content creation
- ✅ Google Ads integration

### Future Enhancements
- Multi-LLM routing (Claude, GPT-4)
- Conversational AI chatbot
- Advanced analytics dashboard
- A/B testing platform
- Multi-tenant white-label support
- Predictive analytics and forecasting

---

**Showcase Features for AI Engineering Jobs:**
- Advanced RAG pipeline with multi-query retrieval and contextual compression
- LangGraph-based multi-agent orchestration with state management
- Real-time behavioral personalization with ML models
- Production-ready observability with LangSmith
- Scalable microservice architecture with async processing
- Comprehensive testing and performance benchmarking