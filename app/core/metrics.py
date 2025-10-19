"""
Metrics and monitoring for AI Marketing Agents
Uses Prometheus client for metrics collection
"""

import time
from typing import Callable, Any
from functools import wraps
import prometheus_client as prom
from prometheus_client import Counter, Histogram, Gauge, Summary

from app.config import settings


# API Metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total number of API requests',
    ['method', 'endpoint', 'status_code']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

api_requests_active = Gauge(
    'api_requests_active',
    'Number of active API requests'
)

# Agent Metrics
agent_task_total = Counter(
    'agent_task_total',
    'Total number of agent tasks executed',
    ['agent_type', 'status']
)

agent_task_duration = Histogram(
    'agent_task_duration_seconds',
    'Agent task duration in seconds',
    ['agent_type'],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0]
)

agent_active_tasks = Gauge(
    'agent_active_tasks',
    'Number of currently active agent tasks',
    ['agent_type']
)

# RAG Metrics
rag_queries_total = Counter(
    'rag_queries_total',
    'Total number of RAG queries',
    ['query_type', 'status']
)

rag_query_duration = Histogram(
    'rag_query_duration_seconds',
    'RAG query duration in seconds',
    ['query_type'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

rag_retrieval_results = Histogram(
    'rag_retrieval_results_count',
    'Number of documents retrieved in RAG queries',
    ['query_type'],
    buckets=[0, 1, 5, 10, 25, 50, 100]
)

# Database Metrics
db_connections_active = Gauge(
    'db_connections_active',
    'Number of active database connections'
)

db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0]
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total number of cache hits'
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total number of cache misses'
)

cache_hit_ratio = Gauge(
    'cache_hit_ratio',
    'Cache hit ratio (0.0 to 1.0)'
)

# External API Metrics
external_api_calls_total = Counter(
    'external_api_calls_total',
    'Total number of external API calls',
    ['api_name', 'status']
)

external_api_duration = Histogram(
    'external_api_duration_seconds',
    'External API call duration in seconds',
    ['api_name'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

# Circuit Breaker Metrics
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=open, 2=half_open)',
    ['service_name']
)

circuit_breaker_failures = Counter(
    'circuit_breaker_failures_total',
    'Total number of circuit breaker failures',
    ['service_name']
)

# Business Metrics
leads_generated_total = Counter(
    'leads_generated_total',
    'Total number of leads generated',
    ['source', 'quality']
)

campaigns_created_total = Counter(
    'campaigns_created_total',
    'Total number of campaigns created',
    ['type', 'status']
)

content_generated_total = Counter(
    'content_generated_total',
    'Total number of content pieces generated',
    ['type', 'status']
)


def setup_metrics():
    """
    Initialize metrics collection
    """
    # Custom metrics registry if needed
    pass


def measure_api_request(method: str, endpoint: str):
    """
    Decorator to measure API request metrics

    Args:
        method: HTTP method
        endpoint: API endpoint
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            api_requests_active.inc()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                status_code = getattr(result, 'status_code', 200)
                api_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()

                return result

            except Exception as e:
                # Extract status code from exception if available
                status_code = getattr(e, 'status_code', 500)
                api_requests_total.labels(
                    method=method,
                    endpoint=endpoint,
                    status_code=status_code
                ).inc()
                raise

            finally:
                duration = time.time() - start_time
                api_request_duration.labels(
                    method=method,
                    endpoint=endpoint
                ).observe(duration)
                api_requests_active.dec()

        return wrapper
    return decorator


def measure_agent_task(agent_type: str):
    """
    Decorator to measure agent task metrics

    Args:
        agent_type: Type of agent (lead_gen, content_creator, etc.)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            agent_active_tasks.labels(agent_type=agent_type).inc()
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                agent_task_total.labels(
                    agent_type=agent_type,
                    status='success'
                ).inc()
                return result

            except Exception as e:
                agent_task_total.labels(
                    agent_type=agent_type,
                    status='error'
                ).inc()
                raise

            finally:
                duration = time.time() - start_time
                agent_task_duration.labels(agent_type=agent_type).observe(duration)
                agent_active_tasks.labels(agent_type=agent_type).dec()

        return wrapper
    return decorator


def measure_rag_query(query_type: str = 'general'):
    """
    Decorator to measure RAG query metrics

    Args:
        query_type: Type of RAG query
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                rag_queries_total.labels(
                    query_type=query_type,
                    status='success'
                ).inc()

                # Count retrieved results if available
                if hasattr(result, 'source_nodes'):
                    result_count = len(result.source_nodes)
                    rag_retrieval_results.labels(query_type=query_type).observe(result_count)

                return result

            except Exception as e:
                rag_queries_total.labels(
                    query_type=query_type,
                    status='error'
                ).inc()
                raise

            finally:
                duration = time.time() - start_time
                rag_query_duration.labels(query_type=query_type).observe(duration)

        return wrapper
    return decorator


def update_cache_metrics(hits: int, misses: int):
    """
    Update cache hit/miss metrics

    Args:
        hits: Number of cache hits
        misses: Number of cache misses
    """
    cache_hits_total.inc(hits)
    cache_misses_total.inc(misses)

    total = hits + misses
    if total > 0:
        hit_ratio = hits / total
        cache_hit_ratio.set(hit_ratio)


def measure_external_api(api_name: str):
    """
    Decorator to measure external API call metrics

    Args:
        api_name: Name of the external API
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                external_api_calls_total.labels(
                    api_name=api_name,
                    status='success'
                ).inc()
                return result

            except Exception as e:
                external_api_calls_total.labels(
                    api_name=api_name,
                    status='error'
                ).inc()
                raise

            finally:
                duration = time.time() - start_time
                external_api_duration.labels(api_name=api_name).observe(duration)

        return wrapper
    return decorator