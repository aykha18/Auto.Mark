# Monitoring & Observability

## Overview

The AI Marketing Agents system implements comprehensive monitoring and observability using LangSmith for LLM tracing, Prometheus for metrics collection, Grafana for visualization, and Sentry for error tracking. This ensures system reliability, performance optimization, and rapid issue resolution.

## LangSmith Integration

### LLM Observability
LangSmith provides deep visibility into LLM calls, agent decisions, and RAG performance.

**Setup:**
```python
# app/core/langsmith.py
from langsmith import Client
from langchain.callbacks import LangChainTracer
import os

class LangSmithManager:
    def __init__(self):
        self.client = Client(
            api_key=os.getenv("LANGSMITH_API_KEY"),
            api_url=os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        )

        self.tracer = LangChainTracer(
            project_name="ai-marketing-agents",
            client=self.client
        )

    def get_tracer(self):
        return self.tracer

    async def log_agent_execution(self, agent_name, execution_data):
        """Log agent execution for analysis"""
        await self.client.create_run(
            name=f"{agent_name}_execution",
            run_type="chain",
            inputs=execution_data.get("inputs", {}),
            outputs=execution_data.get("outputs", {}),
            extra={
                "agent": agent_name,
                "duration": execution_data.get("duration"),
                "success": execution_data.get("success", False),
                "error": execution_data.get("error")
            }
        )

# Global instance
langsmith_manager = LangSmithManager()
```

**Tracing Implementation:**
```python
# app/agents/base.py
from app.core.langsmith import langsmith_manager

class BaseAgent:
    async def execute(self, state):
        tracer = langsmith_manager.get_tracer()

        with tracer.start_as_current_span(f"{self.name}_execution") as span:
            span.set_attribute("agent.name", self.name)
            span.set_attribute("state.keys", list(state.keys()))

            try:
                start_time = time.time()
                result = await self._execute_impl(state)
                duration = time.time() - start_time

                span.set_attribute("execution.duration", duration)
                span.set_attribute("execution.success", True)
                span.set_attribute("result.keys", list(result.keys()) if result else [])

                # Log to LangSmith
                await langsmith_manager.log_agent_execution(
                    self.name,
                    {
                        "inputs": state,
                        "outputs": result,
                        "duration": duration,
                        "success": True
                    }
                )

                return result

            except Exception as e:
                span.set_attribute("execution.success", False)
                span.set_attribute("error.message", str(e))
                span.record_exception(e)

                await langsmith_manager.log_agent_execution(
                    self.name,
                    {
                        "inputs": state,
                        "error": str(e),
                        "success": False
                    }
                )

                raise
```

### RAG Performance Monitoring
```python
# app/rag/monitoring.py
class RAGMonitor:
    def __init__(self):
        self.client = langsmith_manager.client

    async def log_rag_query(self, query, context, response, metadata):
        """Log RAG query performance"""
        await self.client.create_run(
            name="rag_query",
            run_type="retriever",
            inputs={"query": query, "context": context},
            outputs={"response": response},
            extra={
                "retrieval_time": metadata.get("retrieval_time"),
                "generation_time": metadata.get("generation_time"),
                "documents_retrieved": metadata.get("doc_count"),
                "confidence_score": metadata.get("confidence"),
                "tokens_used": metadata.get("tokens")
            }
        )

    async def evaluate_rag_quality(self, queries_and_responses):
        """Batch evaluation of RAG quality"""
        from langsmith.evaluation import evaluate
        from langsmith.evaluation.metrics import (
            answer_relevancy,
            faithfulness,
            context_recall
        )

        results = evaluate(
            queries_and_responses,
            evaluators=[answer_relevancy, faithfulness, context_recall],
            experiment_name="rag_quality_evaluation"
        )

        return results
```

## Prometheus Metrics

### Application Metrics
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge, Summary
import time

# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

api_active_connections = Gauge(
    'api_active_connections',
    'Number of active API connections'
)

# Agent Metrics
agent_executions_total = Counter(
    'agent_executions_total',
    'Total agent executions',
    ['agent_name', 'status']
)

agent_execution_duration = Histogram(
    'agent_execution_duration_seconds',
    'Agent execution duration',
    ['agent_name'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0]
)

agent_errors_total = Counter(
    'agent_errors_total',
    'Total agent errors',
    ['agent_name', 'error_type']
)

# RAG Metrics
rag_queries_total = Counter(
    'rag_queries_total',
    'Total RAG queries',
    ['query_type']
)

rag_query_duration = Histogram(
    'rag_query_duration_seconds',
    'RAG query duration',
    ['stage'],  # retrieval, generation, compression
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

rag_documents_retrieved = Histogram(
    'rag_documents_retrieved_count',
    'Number of documents retrieved',
    buckets=[1, 5, 10, 20, 50, 100]
)

# Campaign Metrics
campaigns_created_total = Counter(
    'campaigns_created_total',
    'Total campaigns created',
    ['campaign_type']
)

campaign_performance = Gauge(
    'campaign_performance_score',
    'Campaign performance score',
    ['campaign_id']
)

# Lead Metrics
leads_generated_total = Counter(
    'leads_generated_total',
    'Total leads generated',
    ['source', 'quality']
)

lead_score_distribution = Histogram(
    'lead_score_distribution',
    'Lead score distribution',
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9]
)

# Content Metrics
content_generated_total = Counter(
    'content_generated_total',
    'Total content pieces generated',
    ['content_type']
)

content_performance_score = Histogram(
    'content_performance_score',
    'Content performance scores',
    buckets=[0.1, 0.3, 0.5, 0.7, 0.9]
)

# Behavioral Intelligence Metrics
events_processed_total = Counter(
    'events_processed_total',
    'Total events processed',
    ['event_type']
)

user_profiles_active = Gauge(
    'user_profiles_active',
    'Number of active user profiles'
)

personalization_requests_total = Counter(
    'personalization_requests_total',
    'Total personalization requests'
)

# External API Metrics
external_api_calls_total = Counter(
    'external_api_calls_total',
    'Total external API calls',
    ['api_name', 'status']
)

external_api_duration = Histogram(
    'external_api_duration_seconds',
    'External API call duration',
    ['api_name'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Circuit Breaker Metrics
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['service_name']
)

circuit_breaker_failures_total = Counter(
    'circuit_breaker_failures_total',
    'Circuit breaker failures',
    ['service_name']
)

# Business Metrics
revenue_tracked = Counter(
    'revenue_tracked_total',
    'Total revenue tracked',
    ['source']
)

conversion_events_total = Counter(
    'conversion_events_total',
    'Total conversion events',
    ['conversion_type']
)
```

### Metrics Collection Middleware
```python
# app/core/middleware.py
import time
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from app.core.metrics import (
    api_requests_total,
    api_request_duration,
    api_active_connections
)

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self._active_connections = 0

    async def dispatch(self, request: Request, call_next):
        # Track active connections
        self._active_connections += 1
        api_active_connections.set(self._active_connections)

        # Track request
        method = request.method
        endpoint = request.url.path

        start_time = time.time()

        try:
            response = await call_next(request)
            status_code = response.status_code

            # Record metrics
            api_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code
            ).inc()

            api_request_duration.labels(
                method=method,
                endpoint=endpoint
            ).observe(time.time() - start_time)

            return response

        except Exception as e:
            # Record error metrics
            api_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status_code=500
            ).inc()

            raise

        finally:
            # Decrement active connections
            self._active_connections -= 1
            api_active_connections.set(self._active_connections)
```

### Custom Metrics for AI Features
```python
# app/core/ai_metrics.py
from app.core.metrics import rag_query_duration, agent_execution_duration
from langsmith import Client
import time

class AIMetricsCollector:
    def __init__(self):
        self.langsmith = Client()

    async def collect_rag_metrics(self, query, response_metadata):
        """Collect detailed RAG performance metrics"""
        rag_query_duration.labels(stage="retrieval").observe(
            response_metadata.get("retrieval_time", 0)
        )
        rag_query_duration.labels(stage="generation").observe(
            response_metadata.get("generation_time", 0)
        )
        rag_query_duration.labels(stage="compression").observe(
            response_metadata.get("compression_time", 0)
        )

        # Log to LangSmith for detailed analysis
        await self.langsmith.create_run(
            name="rag_performance",
            run_type="llm",
            inputs={"query": query},
            outputs={"metadata": response_metadata},
            extra=response_metadata
        )

    async def collect_agent_metrics(self, agent_name, execution_time, success, error=None):
        """Collect agent performance metrics"""
        agent_execution_duration.labels(agent_name=agent_name).observe(execution_time)

        if success:
            agent_executions_total.labels(agent_name=agent_name, status="success").inc()
        else:
            agent_executions_total.labels(agent_name=agent_name, status="failure").inc()
            agent_errors_total.labels(agent_name=agent_name, error_type=type(error).__name__).inc()

    async def collect_llm_cost_metrics(self, model, tokens_used, cost):
        """Track LLM usage costs"""
        # Custom metric for cost tracking
        llm_cost_total = Counter(
            'llm_cost_total',
            'Total LLM costs',
            ['model']
        )
        llm_cost_total.labels(model=model).inc(cost)

        llm_tokens_total = Counter(
            'llm_tokens_total',
            'Total LLM tokens used',
            ['model']
        )
        llm_tokens_total.labels(model=model).inc(tokens_used)
```

## Grafana Dashboards

### System Health Dashboard
```json
{
  "dashboard": {
    "title": "AI Marketing Agents - System Health",
    "panels": [
      {
        "title": "API Response Times",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      },
      {
        "title": "Active Connections",
        "type": "singlestat",
        "targets": [
          {
            "expr": "api_active_connections",
            "legendFormat": "Active Connections"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_requests_total{status_code=~\"5..\"}[5m]) / rate(api_requests_total[5m]) * 100",
            "legendFormat": "Error Rate %"
          }
        ]
      }
    ]
  }
}
```

### AI Performance Dashboard
```json
{
  "dashboard": {
    "title": "AI Marketing Agents - AI Performance",
    "panels": [
      {
        "title": "Agent Execution Times",
        "type": "heatmap",
        "targets": [
          {
            "expr": "agent_execution_duration_seconds",
            "legendFormat": "{{agent_name}}"
          }
        ]
      },
      {
        "title": "RAG Query Performance",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(rag_query_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile - {{stage}}"
          }
        ]
      },
      {
        "title": "LLM Token Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(llm_tokens_total[5m])",
            "legendFormat": "{{model}}"
          }
        ]
      },
      {
        "title": "Agent Success Rate",
        "type": "bargauge",
        "targets": [
          {
            "expr": "rate(agent_executions_total{status=\"success\"}[1h]) / rate(agent_executions_total[1h]) * 100",
            "legendFormat": "{{agent_name}}"
          }
        ]
      }
    ]
  }
}
```

### Business Metrics Dashboard
```json
{
  "dashboard": {
    "title": "AI Marketing Agents - Business Metrics",
    "panels": [
      {
        "title": "Leads Generated",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(leads_generated_total[1h])",
            "legendFormat": "{{source}}"
          }
        ]
      },
      {
        "title": "Campaign Performance",
        "type": "table",
        "targets": [
          {
            "expr": "campaign_performance_score",
            "legendFormat": "{{campaign_id}}"
          }
        ]
      },
      {
        "title": "Revenue Tracking",
        "type": "singlestat",
        "targets": [
          {
            "expr": "sum(rate(revenue_tracked_total[1h]))",
            "legendFormat": "Revenue/Hour"
          }
        ]
      },
      {
        "title": "Content Performance",
        "type": "heatmap",
        "targets": [
          {
            "expr": "content_performance_score",
            "legendFormat": "{{content_type}}"
          }
        ]
      }
    ]
  }
}
```

## Error Tracking with Sentry

### Sentry Integration
```python
# app/core/sentry.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

def init_sentry():
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        environment=os.getenv("ENVIRONMENT", "development"),
        integrations=[
            FastApiIntegration(),
            RedisIntegration(),
            SqlalchemyIntegration()
        ],
        # Sample rates
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,

        # Custom configuration
        before_send=before_send,
        before_breadcrumb=before_breadcrumb
    )

def before_send(event, hint):
    """Filter and enrich error events"""
    # Add custom context
    if 'request' in event:
        event['tags']['endpoint'] = event['request']['url']

    # Filter out expected errors
    if 'exception' in event:
        exc = event['exception']['values'][0]
        if 'CircuitBreakerError' in exc.get('type', ''):
            return None  # Don't send circuit breaker errors

    return event

def before_breadcrumb(breadcrumb, hint):
    """Filter and enrich breadcrumbs"""
    # Add agent execution context
    if breadcrumb.get('category') == 'agent':
        breadcrumb['data']['agent_name'] = breadcrumb['data'].get('agent')

    return breadcrumb
```

### Custom Error Tracking
```python
# app/core/error_tracking.py
import sentry_sdk
from app.core.metrics import agent_errors_total

class ErrorTracker:
    @staticmethod
    def track_agent_error(agent_name, error, context=None):
        """Track agent execution errors"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("agent", agent_name)
            scope.set_tag("error_type", type(error).__name__)
            scope.set_context("agent_context", context or {})

            # Increment metrics
            agent_errors_total.labels(
                agent_name=agent_name,
                error_type=type(error).__name__
            ).inc()

            sentry_sdk.capture_exception(error)

    @staticmethod
    def track_api_error(endpoint, error, request_data=None):
        """Track API errors"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("endpoint", endpoint)
            scope.set_context("request", request_data or {})

            sentry_sdk.capture_exception(error)

    @staticmethod
    def track_external_api_error(api_name, error, request_data=None):
        """Track external API failures"""
        with sentry_sdk.configure_scope() as scope:
            scope.set_tag("external_api", api_name)
            scope.set_context("api_request", request_data or {})

            sentry_sdk.capture_exception(error)
```

## Alerting Rules

### Prometheus Alerting Rules
```yaml
# alert_rules.yml
groups:
  - name: ai-marketing-agents
    rules:
      # API Alerts
      - alert: HighAPIErrorRate
        expr: rate(api_requests_total{status_code=~"[5][0-9][0-9]"}[5m]) / rate(api_requests_total[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High API error rate detected"
          description: "API error rate is {{ $value | printf \"%.2f\" }}%"

      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m])) > 2.0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency detected"
          description: "95th percentile API latency is {{ $value | printf \"%.2f\" }}s"

      # Agent Alerts
      - alert: AgentExecutionFailures
        expr: rate(agent_executions_total{status="failure"}[5m]) / rate(agent_executions_total[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High agent execution failure rate"
          description: "Agent {{ $labels.agent_name }} failure rate is {{ $value | printf \"%.2f\" }}%"

      - alert: AgentSlowExecution
        expr: histogram_quantile(0.95, rate(agent_execution_duration_seconds_bucket[5m])) > 60
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow agent execution detected"
          description: "Agent {{ $labels.agent_name }} 95th percentile execution time is {{ $value | printf \"%.2f\" }}s"

      # RAG Alerts
      - alert: RAGQueryTimeouts
        expr: rate(rag_query_duration_seconds_bucket{le="5"}[5m]) / rate(rag_queries_total[5m]) < 0.95
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High RAG query timeout rate"
          description: "95% of RAG queries are taking longer than 5 seconds"

      # External API Alerts
      - alert: ExternalAPIFailures
        expr: rate(external_api_calls_total{status="error"}[5m]) / rate(external_api_calls_total[5m]) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High external API failure rate"
          description: "External API {{ $labels.api_name }} failure rate is {{ $value | printf \"%.2f\" }}%"

      # Circuit Breaker Alerts
      - alert: CircuitBreakerOpen
        expr: circuit_breaker_state == 1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Circuit breaker opened"
          description: "Circuit breaker for {{ $labels.service_name }} is OPEN"

      # Business Alerts
      - alert: LowLeadGeneration
        expr: rate(leads_generated_total[1h]) < 5
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Low lead generation rate"
          description: "Only {{ $value | printf \"%.0f\" }} leads generated in the last hour"

      - alert: CampaignPerformanceDrop
        expr: campaign_performance_score < 0.7
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Campaign performance dropped"
          description: "Campaign {{ $labels.campaign_id }} performance score is {{ $value | printf \"%.2f\" }}"
```

## Logging Strategy

### Structured Logging
```python
# app/core/logger.py
import logging
import json
import sys
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)

        # Add custom fields
        log_record['service'] = 'ai-marketing-agents'
        log_record['environment'] = os.getenv('ENVIRONMENT', 'development')

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id

        # Add user context if available
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # JSON formatter for production
    if os.getenv('ENVIRONMENT') == 'production':
        formatter = CustomJsonFormatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler for production
    if os.getenv('ENVIRONMENT') == 'production':
        file_handler = logging.FileHandler('logs/ai-marketing-agents.log')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# Global logger instance
logger = setup_logging()
```

### Log Aggregation with ELK Stack
```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.5.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  logstash:
    image: docker.elastic.co/logstash/logstash:8.5.0
    volumes:
      - ./monitoring/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.5.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

## Health Checks

### Application Health Endpoints
```python
# app/api/health.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import pinecone
from app.database import get_db
from app.config import settings

router = APIRouter()

@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db)
):
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }

    # Database check
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = {
            "status": "healthy",
            "response_time": "< 1s"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    # Redis check
    try:
        redis_client = redis.Redis.from_url(settings.redis_url)
        await redis_client.ping()
        health_status["checks"]["redis"] = {
            "status": "healthy",
            "response_time": "< 100ms"
        }
    except Exception as e:
        health_status["checks"]["redis"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    # Pinecone check
    try:
        pinecone.describe_index(settings.pinecone_index_name)
        health_status["checks"]["pinecone"] = {
            "status": "healthy",
            "response_time": "< 500ms"
        }
    except Exception as e:
        health_status["checks"]["pinecone"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "unhealthy"

    # External APIs check
    external_checks = await check_external_apis()
    health_status["checks"].update(external_checks)

    # Overall status
    if health_status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status

@router.get("/health/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    # Quick check for service readiness
    try:
        redis_client = redis.Redis.from_url(settings.redis_url)
        await redis_client.ping()
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/health/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    # Basic liveness check
    return {"status": "alive"}

async def check_external_apis():
    """Check external API dependencies"""
    checks = {}

    # Grok API check
    try:
        # Quick API call to check connectivity
        checks["grok_api"] = {"status": "healthy"}
    except:
        checks["grok_api"] = {"status": "unhealthy"}

    # Google Ads API check (if configured)
    if settings.google_ads_client_id:
        try:
            checks["google_ads_api"] = {"status": "healthy"}
        except:
            checks["google_ads_api"] = {"status": "unhealthy"}

    return checks
```

This comprehensive monitoring and observability setup ensures the AI Marketing Agents system is reliable, performant, and maintainable in production environments.