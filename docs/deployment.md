# Deployment Guide

## Overview

This guide covers the deployment of the AI Marketing Agents MVP system across different environments, from local development to production Kubernetes clusters.

## Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **CPU**: 2+ cores (4+ recommended for development)
- **RAM**: 4GB minimum (8GB+ recommended)
- **Storage**: 20GB free space for databases and dependencies

### Software Dependencies
- **Docker**: 20.10+ with Docker Compose
- **Python**: 3.10+ with pip and virtualenv
- **Git**: For version control
- **Make**: For build automation (optional)

### External Services
- **Pinecone Account**: For vector database
- **Grok-2 API Key**: From xAI
- **LangSmith Account**: For LLM observability
- **PostgreSQL**: 15+ (or Docker)
- **Redis**: 7+ (or Docker)

## Local Development Setup

### 1. Clone and Setup Project
```bash
# Clone repository
git clone https://github.com/yourusername/ai-marketing-agents.git
cd ai-marketing-agents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys
nano .env
```

**Required Environment Variables**:
```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/marketing

# Redis
REDIS_URL=redis://localhost:6379

# Pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=marketing-knowledge

# LLM APIs
GROK_API_KEY=your_grok_api_key

# LangSmith
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=ai-marketing-agents

# Security
SECRET_KEY=your_generated_secret_key
API_KEY_HEADER=X-API-Key

# External APIs (for full functionality)
GOOGLE_ADS_CLIENT_ID=your_google_ads_client_id
GOOGLE_ADS_CLIENT_SECRET=your_google_ads_client_secret
SERPAPI_KEY=your_serpapi_key
```

### 3. Database Setup
```bash
# Start PostgreSQL and Redis with Docker
docker run -d --name postgres -p 5432:5432 -e POSTGRES_DB=marketing -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password postgres:15
docker run -d --name redis -p 6379:6379 redis:7-alpine

# Run database migrations
alembic upgrade head

# (Optional) Seed with sample data
python scripts/seed_database.py
```

### 4. Pinecone Setup
```bash
# Install Pinecone CLI
pip install pinecone-cli

# Initialize Pinecone index
python scripts/setup_pinecone.py
```

### 5. Knowledge Base Ingestion
```bash
# Ingest marketing knowledge base
python scripts/ingest_knowledge.py --source docs/ --source web --topics "marketing,AI,automation"
```

### 6. Start Application
```bash
# Start Celery worker (in separate terminal)
celery -A app.tasks worker --loglevel=info

# Start FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or use the development script
make dev
```

### 7. Verify Installation
```bash
# Check API health
curl http://localhost:8000/health

# Test event tracking
curl -X POST http://localhost:8000/api/v1/events/track \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test_key" \
  -d '{"user_id": "test_user", "event": "test_event"}'

# Check LangSmith traces
# Visit https://smith.langchain.com
```

## Docker Development

### Docker Compose Setup
```yaml
# docker-compose.yml
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
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  worker:
    build: .
    command: celery -A app.tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/marketing
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - .:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=marketing
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Build and Run
```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Development Workflow
```bash
# Rebuild after code changes
docker-compose up --build --force-recreate

# Run tests in container
docker-compose exec api pytest

# Access database
docker-compose exec db psql -U user -d marketing

# Clean up
docker-compose down -v  # Remove volumes too
```

## Production Deployment

### Kubernetes Deployment

#### 1. Prerequisites
- Kubernetes cluster (EKS, GKE, AKS, or self-hosted)
- kubectl configured
- Helm 3+
- External PostgreSQL and Redis (AWS RDS, Cloud SQL, etc.)

#### 2. Namespace Setup
```bash
# Create namespace
kubectl create namespace ai-marketing

# Create secrets
kubectl create secret generic ai-marketing-secrets \
  --from-literal=database-url="postgresql+asyncpg://..." \
  --from-literal=redis-url="redis://..." \
  --from-literal=grok-api-key="..." \
  --namespace ai-marketing
```

#### 3. Helm Deployment
```bash
# Add Helm repository
helm repo add ai-marketing https://charts.yourdomain.com
helm repo update

# Install with custom values
helm install ai-marketing ai-marketing/ai-marketing-agents \
  --namespace ai-marketing \
  --values values-prod.yaml
```

**values-prod.yaml**:
```yaml
# Production Helm values
image:
  tag: "v1.0.0"

replicaCount: 3

env:
  - name: ENVIRONMENT
    value: "production"
  - name: LOG_LEVEL
    value: "INFO"

ingress:
  enabled: true
  hosts:
    - host: marketing-api.yourdomain.com
      paths:
        - path: /
          pathType: Prefix

resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "500m"

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

# External database configuration
externalDatabase:
  host: your-postgres-host
  port: 5432
  database: marketing
  secretName: ai-marketing-secrets

externalRedis:
  host: your-redis-host
  port: 6379
  secretName: ai-marketing-secrets
```

#### 4. Database Migration
```bash
# Run migrations in Kubernetes job
kubectl apply -f k8s/jobs/migration-job.yaml

# Check migration status
kubectl logs -f job/ai-marketing-migration
```

### AWS Deployment

#### ECS Fargate
```yaml
# Task definition
{
  "family": "ai-marketing-agents",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "api",
      "image": "your-registry/ai-marketing-agents:v1.0.0",
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "DATABASE_URL", "value": "postgresql+asyncpg://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ],
      "secrets": [
        {
          "name": "GROK_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:grok-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/ai-marketing-agents",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Application Load Balancer
```yaml
# ALB configuration for API Gateway
{
  "listeners": [
    {
      "protocol": "HTTPS",
      "port": 443,
      "sslPolicy": "ELBSecurityPolicy-TLS-1-2-2017-01",
      "certificates": [
        {
          "certificateArn": "arn:aws:acm:us-east-1:123456789012:certificate/12345678-1234-1234-1234-123456789012"
        }
      ],
      "defaultActions": [
        {
          "type": "forward",
          "targetGroupArn": "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/api-targets/1234567890123456"
        }
      ]
    }
  ]
}
```

### Google Cloud Run

#### Cloud Build Configuration
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/ai-marketing-agents:$COMMIT_SHA', '.']

  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/ai-marketing-agents:$COMMIT_SHA']

  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - run
      - deploy
      - ai-marketing-agents
      - --image=gcr.io/$PROJECT_ID/ai-marketing-agents:$COMMIT_SHA
      - --region=us-central1
      - --platform=managed
      - --port=8000
      - --memory=1Gi
      - --cpu=1
      - --max-instances=10
      - --set-env-vars=DATABASE_URL=postgresql+asyncpg://...,REDIS_URL=redis://...
      - --set-secrets=GROK_API_KEY=grok-api-key:latest
```

## Configuration Management

### Environment Variables

#### Development
```bash
# .env.development
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DEBUG=true
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/marketing
REDIS_URL=redis://localhost:6379
```

#### Production
```bash
# .env.production
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db-host:5432/marketing
REDIS_URL=redis://prod-redis-host:6379
```

### Configuration Classes
```python
# app/config.py
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    # Environment
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Redis
    redis_url: str = Field(..., env="REDIS_URL")

    # Pinecone
    pinecone_api_key: str = Field(..., env="PINECONE_API_KEY")
    pinecone_environment: str = Field(..., env="PINECONE_ENVIRONMENT")
    pinecone_index_name: str = Field(default="marketing-knowledge")

    # LLM APIs
    grok_api_key: str = Field(..., env="GROK_API_KEY")

    # LangSmith
    langchain_tracing_v2: bool = Field(default=True, env="LANGCHAIN_TRACING_V2")
    langchain_endpoint: str = Field(..., env="LANGCHAIN_ENDPOINT")
    langchain_api_key: str = Field(..., env="LANGCHAIN_API_KEY")
    langchain_project: str = Field(default="ai-marketing-agents")

    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    api_key_header: str = Field(default="X-API-Key")

    # External APIs
    google_ads_client_id: Optional[str] = Field(None, env="GOOGLE_ADS_CLIENT_ID")
    google_ads_client_secret: Optional[str] = Field(None, env="GOOGLE_ADS_CLIENT_SECRET")
    serpapi_key: Optional[str] = Field(None, env="SERPAPI_KEY")

    # Performance
    max_workers: int = Field(default=4)
    request_timeout: int = Field(default=30)
    rate_limit_requests: int = Field(default=1000)
    rate_limit_window: int = Field(default=3600)

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

## Monitoring Setup

### Prometheus Metrics
```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# API metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['method', 'endpoint']
)

# Agent metrics
agent_task_duration = Histogram(
    'agent_task_duration_seconds',
    'Agent task duration',
    ['agent_name', 'task_type']
)

agent_task_success = Counter(
    'agent_task_success_total',
    'Successful agent tasks',
    ['agent_name', 'task_type']
)

agent_task_failure = Counter(
    'agent_task_failure_total',
    'Failed agent tasks',
    ['agent_name', 'task_type']
)

# RAG metrics
rag_query_duration = Histogram(
    'rag_query_duration_seconds',
    'RAG query duration'
)

rag_retrieval_count = Histogram(
    'rag_retrieval_count',
    'Number of documents retrieved'
)

# Business metrics
leads_generated = Counter(
    'leads_generated_total',
    'Total leads generated'
)

campaigns_created = Counter(
    'campaigns_created_total',
    'Total campaigns created'
)
```

### Grafana Dashboards
```json
// Dashboard configuration
{
  "dashboard": {
    "title": "AI Marketing Agents",
    "tags": ["ai-marketing", "production"],
    "panels": [
      {
        "title": "API Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(api_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Agent Performance",
        "type": "heatmap",
        "targets": [
          {
            "expr": "agent_task_duration_seconds",
            "legendFormat": "{{agent_name}}"
          }
        ]
      }
    ]
  }
}
```

### Health Checks
```python
# app/api/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import redis.asyncio as redis
import pinecone

router = APIRouter()

@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "checks": {}
    }

    # Database check
    try:
        await db.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Redis check
    try:
        await redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Pinecone check
    try:
        pinecone.describe_index(settings.pinecone_index_name)
        health_status["checks"]["pinecone"] = "healthy"
    except Exception as e:
        health_status["checks"]["pinecone"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    return health_status
```

## Backup and Recovery

### Database Backup
```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup_$DATE.sql

# Upload to S3
aws s3 cp backup_$DATE.sql s3://ai-marketing-backups/database/

# Cleanup old backups (keep 30 days)
find /backups -name "backup_*.sql" -mtime +30 -delete
```

### Redis Backup
```bash
# Redis RDB backup
redis-cli BGSAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backups/redis_$DATE.rdb
```

### Recovery Procedures
```bash
# Database recovery
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backup_20240101_120000.sql

# Redis recovery
redis-cli SHUTDOWN
cp /backups/redis_20240101_120000.rdb /var/lib/redis/dump.rdb
redis-server
```

## Scaling Strategies

### Horizontal Scaling
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ai-marketing-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ai-marketing-api
  minReplicas: 3
  maxReplicas: 20
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### Database Scaling
- **Read Replicas**: Route read queries to replicas
- **Connection Pooling**: PgBouncer for connection management
- **Partitioning**: Time-based partitioning for events table

### Caching Strategy
```python
# Multi-level caching
from cachetools import TTLCache
from redis import Redis

class CacheManager:
    def __init__(self):
        self.l1_cache = TTLCache(maxsize=1000, ttl=300)  # 5 min TTL
        self.redis = Redis(host='localhost', port=6379)

    async def get(self, key):
        # Check L1 cache first
        if key in self.l1_cache:
            return self.l1_cache[key]

        # Check Redis
        value = await self.redis.get(key)
        if value:
            self.l1_cache[key] = value
            return value

        return None

    async def set(self, key, value, ttl=3600):
        self.l1_cache[key] = value
        await self.redis.setex(key, ttl, value)
```

## Security Hardening

### API Security
```python
# app/core/security.py
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
import jwt
import time

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(api_key_header)):
    """Verify API key with Redis caching"""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    # Check Redis cache first
    cached_user = await redis.get(f"api_key:{api_key}")
    if cached_user:
        return cached_user

    # Check database
    user = await db.execute(
        "SELECT user_id FROM api_keys WHERE key = $1 AND active = true",
        api_key
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Cache for 1 hour
    await redis.setex(f"api_key:{api_key}", 3600, user.user_id)

    return user.user_id
```

### Rate Limiting
```python
# app/core/rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

limiter = Limiter(key_func=get_remote_address)

# Apply to FastAPI app
app.add_middleware(SlowAPIMiddleware)

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    # Custom rate limiting logic
    client_ip = request.client.host
    api_key = request.headers.get("X-API-Key")

    # Tier-based limits
    if api_key:
        limit = await get_user_limit(api_key)
    else:
        limit = 100  # Free tier

    # Check rate limit in Redis
    current = await redis.incr(f"rate_limit:{client_ip}")
    if current == 1:
        await redis.expire(f"rate_limit:{client_ip}", 3600)

    if current > limit:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    response = await call_next(request)
    return response
```

This deployment guide provides comprehensive instructions for setting up the AI Marketing Agents system in various environments, from local development to production Kubernetes clusters, with proper monitoring, security, and scaling considerations.