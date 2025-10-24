# AI Marketing Agents - Phase 3 Implementation

## 🎯 Overview

This document describes the complete Phase 3 implementation of advanced AI marketing agents using LangChain, LangGraph, and LangSmith for autonomous marketing campaign orchestration.

## 🏗️ Architecture

### Core Components

1. **BaseAgent** - Abstract base class for all marketing agents
2. **MarketingAgentState** - Shared state management using TypedDict
3. **Specialized Agents**:
   - LeadGenerationAgent - Autonomous lead discovery and qualification
   - ContentCreatorAgent - RAG-enhanced content generation
   - AdManagerAgent - Multi-platform ad campaign management
4. **Orchestrator** - LangGraph-based workflow coordination
5. **Communication** - Inter-agent messaging protocol
6. **Monitoring** - LangSmith integration for observability
7. **Resilience** - Circuit breakers and retry strategies

### Key Features

- **Multi-Agent Orchestration**: Agents work together through LangGraph workflows
- **Shared State Management**: Type-safe state sharing across all agents
- **RAG Integration**: Content creation enhanced with marketing knowledge base
- **LangSmith Observability**: Complete tracing and monitoring capabilities
- **Resilience Patterns**: Circuit breakers and retry logic for production reliability
- **Inter-Agent Communication**: Standardized messaging between agents
- **Extensibility**: Easy to add new agents and tools

## 🚀 Quick Start

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables (.env)
OPENAI_API_KEY=your_openai_key
GROK_API_KEY=your_grok_key
LANGCHAIN_TRACING_V2=true  # Optional: for LangSmith
LANGCHAIN_API_KEY=your_langsmith_key
```

### Basic Usage

```python
import asyncio
from app.agents.orchestrator import run_marketing_campaign

# Define campaign configuration
campaign_config = {
    'name': 'AI Marketing Campaign',
    'target_audience': {
        'industry': 'technology',
        'company_size': '50-200',
        'job_titles': ['CTO', 'VP Engineering']
    },
    'content_required': True,
    'content_requirements': {
        'type': 'blog_post',
        'topic': 'AI Marketing Strategies',
        'tone': 'professional'
    },
    'ad_platforms': ['google_ads', 'linkedin'],
    'budget': 2000.0
}

# Run the campaign
async def main():
    final_state = await run_marketing_campaign(campaign_config)
    print(f"Campaign completed with {len(final_state['qualified_leads'])} qualified leads")

asyncio.run(main())
```

## 🧪 Testing

### Direct Testing (No Server Required)

```bash
python simple_agent_test.py
```

This tests:
- Individual agent execution
- Full workflow orchestration
- Agent communication
- Monitoring and metrics

### API Testing (Server Required)

```bash
# Terminal 1: Start server
python -m app.main

# Terminal 2: Run API tests
python test_agents_api.py
```

### API Endpoints

- `POST /api/v1/campaigns/run` - Execute marketing campaigns
- `GET /api/v1/agents` - List available agents
- `GET /api/v1/agents/{agent}/metrics` - Agent performance metrics
- `GET /api/v1/health` - System health status
- `POST /api/v1/messages/send` - Send inter-agent messages
- `GET /api/v1/test/*` - Individual agent testing

## 📊 Monitoring & Observability

### LangSmith Integration

When configured, all agent executions are traced in LangSmith:

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=ai-marketing-agents
```

### Metrics Available

- Agent execution times
- Success/failure rates
- Campaign performance scores
- Error tracking and debugging
- Inter-agent communication logs

## 🤖 Agent Details

### Lead Generation Agent

**Purpose**: Discover and qualify potential leads from multiple sources

**Tools**:
- Web scraping (BeautifulSoup, Selenium)
- LinkedIn API integration
- Company database enrichment
- Email validation services

**Key Methods**:
- `discover_leads()` - Multi-source lead discovery
- `qualify_leads()` - Score-based lead qualification
- `calculate_lead_score()` - ML-based scoring algorithm

### Content Creator Agent

**Purpose**: Generate high-quality marketing content using RAG

**Tools**:
- RAG knowledge base querying
- SEO optimization
- Brand guideline checking
- Content performance analysis

**Key Methods**:
- `generate_content()` - AI-powered content creation
- `optimize_content()` - SEO and tone optimization
- `check_brand_guidelines()` - Compliance validation

### Ad Manager Agent

**Purpose**: Manage and optimize multi-channel ad campaigns

**Tools**:
- Google Ads API integration
- LinkedIn Campaign Manager
- Facebook Ads API
- Performance analytics

**Key Methods**:
- `deploy_campaign()` - Multi-platform campaign deployment
- `analyze_performance()` - Campaign metrics analysis
- `optimize_campaigns()` - Automated optimization

## 🔧 Configuration

### Environment Variables

```env
# LLM Configuration
OPENAI_API_KEY=your_key
GROK_API_KEY=your_key
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.7

# LangSmith (Optional)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_key
LANGCHAIN_PROJECT=ai-marketing-agents

# External APIs
SERPAPI_KEY=your_key
GOOGLE_ADS_CLIENT_ID=your_client_id
LINKEDIN_API_KEY=your_key

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db

# Redis (Optional)
REDIS_URL=redis://localhost:6379
```

## 🏃‍♂️ Development Workflow

1. **Agent Development**:
   - Extend `BaseAgent` class
   - Implement required abstract methods
   - Add agent-specific tools

2. **Testing**:
   - Use `simple_agent_test.py` for unit testing
   - Use `test_agents_api.py` for integration testing
   - Monitor LangSmith traces for debugging

3. **Deployment**:
   - Configure environment variables
   - Set up LangSmith project
   - Deploy with monitoring enabled

## 📈 Performance Benchmarks

- **Agent Response Time**: <5 seconds for typical operations
- **Campaign Execution Time**: <30 minutes for complete workflow
- **Concurrent Agents**: Support 10+ simultaneous agent operations
- **Memory Usage**: <500MB per agent instance
- **Error Rate**: <5% for agent operations

## 🔒 Security & Resilience

- **Circuit Breakers**: Automatic failure detection and recovery
- **Rate Limiting**: API rate limit protection
- **Error Handling**: Comprehensive error tracking and recovery
- **Authentication**: API key-based authentication
- **Input Validation**: Pydantic-based request validation

## 🚀 Production Deployment

### Docker Configuration

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app/ ./app/
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "from app.agents.monitoring import get_agent_health; import asyncio; asyncio.run(get_agent_health())"

CMD ["python", "-m", "app.main"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marketing-agents
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: agent
        image: marketing-agents:latest
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        - name: LANGCHAIN_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: langsmith
```

## 📚 API Reference

### Campaign Execution

```python
from app.agents.orchestrator import run_marketing_campaign

campaign_config = {
    "name": "My Campaign",
    "target_audience": {"industry": "tech"},
    "budget": 1000.0
}

result = await run_marketing_campaign(campaign_config)
```

### Individual Agent Usage

```python
from app.agents.lead_generation import LeadGenerationAgent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4")
agent = LeadGenerationAgent(llm)

state = create_initial_state({"target_audience": {"industry": "tech"}})
result = await agent.execute(state)
```

### Monitoring

```python
from app.agents.monitoring import get_agent_metrics

metrics = get_agent_metrics("lead_generation")
print(f"Success rate: {metrics['success_rate']:.2f}")
```

## 🤝 Contributing

1. Follow the existing agent pattern
2. Add comprehensive tests
3. Update documentation
4. Ensure LangSmith tracing works
5. Test with circuit breakers

## 📄 License

This implementation is part of the AI Marketing Agents project.

---

**Note**: This implementation provides a solid foundation for autonomous marketing operations. Each component is designed to be understandable, maintainable, and extensible for future enhancements.