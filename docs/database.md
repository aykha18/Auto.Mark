# Database Design

## Overview

The AI Marketing Agents system uses PostgreSQL as the primary database with Redis for caching and message queuing. The schema is designed for high-performance analytics, real-time personalization, and scalable multi-tenant operations.

## Database Architecture

### Primary Database: PostgreSQL 15+
- **Purpose**: Persistent data storage, complex queries, analytics
- **Features**: JSONB for flexible schemas, advanced indexing, ACID compliance
- **Extensions**: uuid-ossp, pg_stat_statements, pg_buffercache

### Cache & Queue: Redis 7+
- **Purpose**: Session management, real-time data, message queuing
- **Features**: Pub/Sub, sorted sets, hyperloglog for unique counts
- **Persistence**: RDB snapshots + AOF for durability

### Vector Database: Pinecone
- **Purpose**: Semantic search, RAG retrieval, embeddings storage
- **Features**: HNSW indexing, metadata filtering, real-time updates

## Core Tables

### users
Primary user profile and segmentation table.

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE,
    traits JSONB,
    segment VARCHAR(50),
    ltv_prediction DECIMAL(10,2),
    churn_risk DECIMAL(3,2),
    -- Indexes
    INDEX idx_users_email (email),
    INDEX idx_users_segment (segment),
    INDEX idx_users_created_at (created_at),
    INDEX idx_users_last_seen (last_seen),
    -- Partial indexes for active users
    INDEX idx_users_active ON users (last_seen) WHERE last_seen > NOW() - INTERVAL '30 days',
    -- GIN index for JSONB queries
    INDEX idx_users_traits ON users USING GIN (traits)
);

-- Partitioning by month for large datasets
-- CREATE TABLE users_y2024m01 PARTITION OF users FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

**Key Fields:**
- `user_id`: UUID primary key for global uniqueness
- `traits`: JSONB for flexible user attributes (name, company, preferences)
- `segment`: Pre-computed segment for fast filtering
- `ltv_prediction`: ML-predicted lifetime value
- `churn_risk`: ML-predicted churn probability (0.0-1.0)

### events
Behavioral event tracking with high write throughput.

```sql
CREATE TABLE events (
    event_id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    event_name VARCHAR(100) NOT NULL,
    properties JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id UUID,
    ip_address INET,
    user_agent TEXT,
    -- Indexes
    INDEX idx_events_user_timestamp (user_id, timestamp DESC),
    INDEX idx_events_event_name (event_name),
    INDEX idx_events_timestamp (timestamp DESC),
    INDEX idx_events_session (session_id),
    -- Partial indexes for common events
    INDEX idx_events_page_view ON events (user_id, timestamp) WHERE event_name = 'page_view',
    INDEX idx_events_signup ON events (user_id, timestamp) WHERE event_name = 'user_signup',
    -- GIN index for property queries
    INDEX idx_events_properties ON events USING GIN (properties),
    -- BRIN index for time-series data (better than B-tree for large tables)
    INDEX idx_events_timestamp_brin ON events USING BRIN (timestamp) WHERE timestamp > '2024-01-01'
);

-- Partitioning by day for high-volume event data
-- CREATE TABLE events_y2024m01d01 PARTITION OF events FOR VALUES FROM ('2024-01-01') TO ('2024-01-02');
```

**Key Fields:**
- `event_id`: BigSerial for high-volume inserts
- `properties`: JSONB for event-specific data (product_id, page_url, etc.)
- `session_id`: Groups events within user sessions
- `ip_address`: For geo-analytics and fraud detection

### campaigns
Marketing campaign management and tracking.

```sql
CREATE TABLE campaigns (
    campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL CHECK (type IN ('lead_gen', 'content', 'retention', 'ad')),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed', 'stopped')),
    config JSONB,
    budget DECIMAL(10,2),
    spent DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(50),
    -- Indexes
    INDEX idx_campaigns_status (status),
    INDEX idx_campaigns_type (type),
    INDEX idx_campaigns_created_at (created_at),
    INDEX idx_campaigns_created_by (created_by),
    -- GIN index for config queries
    INDEX idx_campaigns_config ON campaigns USING GIN (config)
);
```

**Key Fields:**
- `config`: JSONB with campaign settings (audience, channels, goals)
- `budget/spent`: Financial tracking for ROI calculations
- `created_by`: Agent or user who created the campaign

### ad_campaigns
Platform-specific ad campaign tracking.

```sql
CREATE TABLE ad_campaigns (
    ad_campaign_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(campaign_id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL CHECK (platform IN ('google_ads', 'linkedin', 'producthunt')),
    platform_campaign_id VARCHAR(255),
    audience_config JSONB,
    creatives JSONB,
    performance_metrics JSONB,
    last_optimized TIMESTAMP WITH TIME ZONE,
    -- Indexes
    INDEX idx_ad_campaigns_campaign (campaign_id),
    INDEX idx_ad_campaigns_platform (platform),
    INDEX idx_ad_campaigns_last_optimized (last_optimized),
    -- GIN indexes for complex queries
    INDEX idx_ad_campaigns_audience ON ad_campaigns USING GIN (audience_config),
    INDEX idx_ad_campaigns_performance ON ad_campaigns USING GIN (performance_metrics)
);
```

### leads
Lead generation and qualification tracking.

```sql
CREATE TABLE leads (
    lead_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255),
    phone VARCHAR(50),
    name VARCHAR(255),
    company VARCHAR(255),
    job_title VARCHAR(100),
    source VARCHAR(100),
    score DECIMAL(3,2) CHECK (score >= 0 AND score <= 1),
    qualified BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'lost')),
    properties JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_contacted TIMESTAMP WITH TIME ZONE,
    converted_at TIMESTAMP WITH TIME ZONE,
    -- Indexes
    INDEX idx_leads_email (email),
    INDEX idx_leads_score (score DESC),
    INDEX idx_leads_status (status),
    INDEX idx_leads_source (source),
    INDEX idx_leads_qualified (qualified),
    INDEX idx_leads_created_at (created_at),
    -- Compound indexes for common queries
    INDEX idx_leads_score_status (score DESC, status) WHERE qualified = true,
    INDEX idx_leads_source_score (source, score DESC),
    -- GIN index for property searches
    INDEX idx_leads_properties ON leads USING GIN (properties)
);
```

**Key Fields:**
- `score`: ML-computed lead quality score (0.0-1.0)
- `qualified`: Boolean flag for sales-ready leads
- `properties`: JSONB with enrichment data (company size, industry, social profiles)

### content_library
AI-generated content storage and performance tracking.

```sql
CREATE TABLE content_library (
    content_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content_type VARCHAR(50) NOT NULL CHECK (content_type IN ('blog', 'social', 'email', 'ad_copy', 'landing_page')),
    title VARCHAR(500),
    content TEXT,
    metadata JSONB,
    performance_score DECIMAL(3,2),
    generated_by VARCHAR(50),
    campaign_id UUID REFERENCES campaigns(campaign_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    published_at TIMESTAMP WITH TIME ZONE,
    -- Indexes
    INDEX idx_content_type (content_type),
    INDEX idx_content_created_at (created_at),
    INDEX idx_content_campaign (campaign_id),
    INDEX idx_content_generated_by (generated_by),
    INDEX idx_content_performance (performance_score DESC),
    -- Full-text search index
    INDEX idx_content_fts ON content_library USING GIN (to_tsvector('english', title || ' ' || content)),
    -- GIN index for metadata
    INDEX idx_content_metadata ON content_library USING GIN (metadata)
);
```

**Key Fields:**
- `metadata`: JSONB with SEO data, word count, reading time, etc.
- `performance_score`: Engagement/completion rate
- `generated_by`: Agent name for attribution

## Redis Data Structures

### Session Management
```redis
# User sessions with TTL
SET session:user_123:session_456 '{"user_id": "user_123", "start_time": 1640995200, "page_views": 5}'
EXPIRE session:user_123:session_456 3600

# Real-time user profile cache
HSET user_profile:user_123 email "user@example.com"
HSET user_profile:user_123 segment "enterprise"
HSET user_profile:user_123 last_event_time 1640995200
```

### Event Buffering
```redis
# Buffer events for batch processing
LPUSH event_buffer:user_123 '{"event": "page_view", "timestamp": 1640995200}'
LTRIM event_buffer:user_123 0 99  # Keep last 100 events

# Rate limiting
SET rate_limit:api_key:abc123 45
EXPIRE rate_limit:api_key:abc123 3600
```

### Real-time Analytics
```redis
# HyperLogLog for unique counts
PFADD unique_users_today user_123
PFADD unique_users_today user_456
PFCOUNT unique_users_today

# Sorted sets for leaderboards
ZADD campaign_performance 95.5 campaign_123
ZADD campaign_performance 87.2 campaign_456
ZRANGE campaign_performance 0 -1 WITHSCORES
```

### Message Queuing
```redis
# Task queues for agents
LPUSH agent_tasks:lead_gen '{"task": "generate_leads", "campaign_id": "123"}'
LPUSH agent_tasks:content_creator '{"task": "create_blog", "topic": "AI trends"}'

# Pub/Sub for real-time updates
PUBLISH campaign_updates '{"campaign_id": "123", "status": "completed"}'
```

## Pinecone Collections

### marketing_knowledge
Primary knowledge base for RAG.

```python
collection_config = {
    "name": "marketing-knowledge",
    "dimension": 1536,  # text-embedding-3-large
    "metric": "cosine",
    "metadata_config": {
        "source": {"type": "string"},
        "category": {"type": "string"},
        "last_updated": {"type": "timestamp"},
        "tags": {"type": "string[]"}
    }
}
```

**Metadata Schema:**
- `source`: document | web_scraped | user_generated
- `category`: product_docs | market_trends | competitor_intel | campaign_history
- `last_updated`: timestamp for freshness scoring
- `tags`: searchable keywords

### user_behavior_patterns
Behavioral pattern embeddings for personalization.

```python
behavior_patterns_config = {
    "name": "user-behavior-patterns",
    "dimension": 1536,
    "metric": "cosine",
    "metadata_config": {
        "segment": {"type": "string"},
        "frequency": {"type": "numeric"},
        "conversion_rate": {"type": "numeric"},
        "pattern_type": {"type": "string"}
    }
}
```

### campaign_history
Past campaign performance embeddings.

```python
campaign_history_config = {
    "name": "campaign-history",
    "dimension": 1536,
    "metric": "cosine",
    "metadata_config": {
        "platform": {"type": "string"},
        "performance_score": {"type": "numeric"},
        "audience_size": {"type": "numeric"},
        "conversion_rate": {"type": "numeric"}
    }
}
```

## Data Models

### SQLAlchemy Models

```python
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    last_seen = Column(DateTime(timezone=True))
    traits = Column(JSONB)
    segment = Column(String(50), index=True)
    ltv_prediction = Column(Float)
    churn_risk = Column(Float)

    # Relationships
    events = relationship("Event", back_populates="user")
    leads = relationship("Lead", back_populates="user")

class Event(Base):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    event_name = Column(String(100), nullable=False, index=True)
    properties = Column(JSONB)
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    session_id = Column(UUID(as_uuid=True), index=True)

    # Relationships
    user = relationship("User", back_populates="events")

class Campaign(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    status = Column(String(20), default="draft")
    config = Column(JSONB)
    budget = Column(Float)
    spent = Column(Float, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    ad_campaigns = relationship("AdCampaign", back_populates="campaign")
    content = relationship("Content", back_populates="campaign")

class Lead(Base):
    __tablename__ = "leads"

    lead_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    email = Column(String(255), index=True)
    score = Column(Float)
    qualified = Column(Boolean, default=False)
    status = Column(String(50), default="new")
    properties = Column(JSONB)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="leads")

class Content(Base):
    __tablename__ = "content_library"

    content_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_type = Column(String(50), nullable=False)
    title = Column(String(500))
    content = Column(Text)
    metadata = Column(JSONB)
    performance_score = Column(Float)
    generated_by = Column(String(50))
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaign_id"))
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # Relationships
    campaign = relationship("Campaign", back_populates="content")
```

### Pydantic Schemas

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    traits: Optional[Dict[str, Any]] = None
    segment: Optional[str] = None

class UserCreate(UserBase):
    user_id: UUID

class User(UserBase):
    user_id: UUID
    created_at: datetime
    last_seen: Optional[datetime] = None
    ltv_prediction: Optional[float] = None
    churn_risk: Optional[float] = None

    class Config:
        from_attributes = True

class EventBase(BaseModel):
    user_id: UUID
    event_name: str = Field(..., max_length=100)
    properties: Optional[Dict[str, Any]] = None
    timestamp: Optional[datetime] = None
    session_id: Optional[UUID] = None

class EventCreate(EventBase):
    pass

class Event(EventBase):
    event_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class CampaignBase(BaseModel):
    name: str = Field(..., max_length=255)
    type: str = Field(..., pattern="^(lead_gen|content|retention|ad)$")
    config: Optional[Dict[str, Any]] = None
    budget: Optional[float] = None

class CampaignCreate(CampaignBase):
    pass

class Campaign(CampaignBase):
    campaign_id: UUID
    status: str = "draft"
    spent: float = 0
    created_at: datetime
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LeadBase(BaseModel):
    email: Optional[EmailStr] = None
    score: Optional[float] = Field(None, ge=0, le=1)
    qualified: bool = False
    status: str = "new"
    properties: Optional[Dict[str, Any]] = None

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    lead_id: UUID
    created_at: datetime
    last_contacted: Optional[datetime] = None
    converted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

## Indexing Strategy

### Performance Optimization

1. **Composite Indexes**: For common query patterns
   ```sql
   CREATE INDEX idx_events_user_timestamp ON events (user_id, timestamp DESC);
   CREATE INDEX idx_leads_score_status ON leads (score DESC, status) WHERE qualified = true;
   ```

2. **Partial Indexes**: For filtered queries
   ```sql
   CREATE INDEX idx_users_active ON users (last_seen) WHERE last_seen > NOW() - INTERVAL '30 days';
   ```

3. **GIN Indexes**: For JSONB and full-text search
   ```sql
   CREATE INDEX idx_users_traits ON users USING GIN (traits);
   CREATE INDEX idx_content_fts ON content_library USING GIN (to_tsvector('english', title || ' ' || content));
   ```

4. **BRIN Indexes**: For time-series data
   ```sql
   CREATE INDEX idx_events_timestamp_brin ON events USING BRIN (timestamp);
   ```

### Partitioning Strategy

For high-volume tables, implement partitioning:

```sql
-- Events table partitioning by month
CREATE TABLE events_y2024m01 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

-- Users table partitioning by creation year
CREATE TABLE users_y2024 PARTITION OF users
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
```

## Data Retention & Archiving

### Retention Policies
- **Events**: 2 years active, 5 years archived
- **Users**: Indefinite (GDPR compliance)
- **Campaigns**: 3 years active, 7 years archived
- **Content**: Indefinite (IP protection)

### Archival Strategy
```sql
-- Move old events to archive table
INSERT INTO events_archive SELECT * FROM events WHERE timestamp < NOW() - INTERVAL '2 years';
DELETE FROM events WHERE timestamp < NOW() - INTERVAL '2 years';
```

## Backup & Recovery

### Backup Strategy
- **Daily**: Full PostgreSQL backup
- **Hourly**: WAL archiving for point-in-time recovery
- **Real-time**: Redis RDB snapshots

### Recovery Procedures
- **RTO**: 4 hours for full recovery
- **RPO**: 5 minutes data loss tolerance
- **Testing**: Monthly recovery drills

## Migration Strategy

### Alembic Migrations
```python
# migrations/versions/001_initial_schema.py
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        # ... other columns
        sa.PrimaryKeyConstraint('user_id')
    )
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'], unique=True)
    op.create_index('idx_users_segment', 'users', ['segment'])

def downgrade():
    op.drop_index('idx_users_segment', table_name='users')
    op.drop_index('idx_users_email', table_name='users')
    op.drop_table('users')
```

This database design provides the foundation for a scalable, high-performance AI marketing system with efficient querying, real-time capabilities, and comprehensive analytics support.