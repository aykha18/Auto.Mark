# Phase 2: Database & Authentication - Implementation Guide

## Overview

Phase 2 builds upon the foundation established in Phase 1 by implementing the core data layer and authentication system. This phase focuses on creating the database schema, implementing user management, and setting up secure API access patterns.

## Phase 2 Objectives

- ✅ Implement PostgreSQL database schema with SQLAlchemy models
- ✅ Setup Alembic database migrations
- ✅ Create user management and authentication system
- ✅ Implement API key authentication middleware
- ✅ Add Redis caching for performance
- ✅ Build basic event tracking API
- ✅ Integrate LangSmith for LLM observability

## Step 1: Database Models & Schema

### What We Build
Complete SQLAlchemy models with relationships, indexes, and validation.

### Files Created

#### `app/models/__init__.py`
```python
# Database models package
from app.models.base import Base
from app.models.user import User
from app.models.event import Event
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.models.content import Content

__all__ = ["Base", "User", "Event", "Campaign", "Lead", "Content"]
```

#### `app/models/base.py` - Base Model Class
```python
from datetime import datetime
from sqlalchemy import Column, DateTime, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    """Mixin for automatic timestamp fields"""
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

#### `app/models/user.py` - User Model
```python
from sqlalchemy import Column, String, Integer, Float, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.models.base import Base, TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    last_seen = Column(DateTime(timezone=True))

    # User profile data
    traits = Column(JSON)  # Flexible user attributes
    segment = Column(String(50), index=True)  # Computed segment

    # ML predictions
    ltv_prediction = Column(Float)  # Lifetime value prediction
    churn_risk = Column(Float)  # Churn probability (0.0-1.0)

    # Relationships
    events = relationship("Event", back_populates="user", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="user")

    # Indexes for performance
    __table_args__ = (
        Index('idx_users_segment', 'segment'),
        Index('idx_users_last_seen', 'last_seen'),
        Index('idx_users_active', 'last_seen').where(last_seen.isnot(None)),  # Partial index
    )

    def __repr__(self):
        return f"<User(user_id={self.user_id}, email={self.email})>"
```

#### `app/models/event.py` - Event Tracking Model
```python
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Event(Base, TimestampMixin):
    __tablename__ = "events"

    event_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), index=True)
    event_name = Column(String(100), nullable=False, index=True)
    properties = Column(JSON)  # Event-specific data
    timestamp = Column(DateTime(timezone=True), index=True)
    session_id = Column(UUID(as_uuid=True), index=True)

    # Relationships
    user = relationship("User", back_populates="events")

    # Composite indexes for query performance
    __table_args__ = (
        Index('idx_events_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_events_name_timestamp', 'event_name', 'timestamp'),
    )

    def __repr__(self):
        return f"<Event(event_id={self.event_id}, name={self.event_name})>"
```

#### `app/models/campaign.py` - Marketing Campaign Model
```python
from sqlalchemy import Column, String, Float, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    campaign_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # lead_gen, content, retention, ad
    status = Column(String(20), default="draft")  # draft, active, paused, completed
    config = Column(JSON)  # Campaign configuration
    budget = Column(Float)
    spent = Column(Float, default=0.0)

    # Relationships
    ad_campaigns = relationship("AdCampaign", back_populates="campaign", cascade="all, delete-orphan")
    content = relationship("Content", back_populates="campaign")

    # Indexes
    __table_args__ = (
        Index('idx_campaigns_status', 'status'),
        Index('idx_campaigns_type', 'type'),
    )

class AdCampaign(Base, TimestampMixin):
    __tablename__ = "ad_campaigns"

    ad_campaign_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaign_id"))
    platform = Column(String(50), nullable=False)  # google_ads, linkedin, producthunt
    platform_campaign_id = Column(String(255))
    audience_config = Column(JSON)
    creatives = Column(JSON)
    performance_metrics = Column(JSON)
    last_optimized = Column(DateTime(timezone=True))

    # Relationships
    campaign = relationship("Campaign", back_populates="ad_campaigns")

    # Indexes
    __table_args__ = (
        Index('idx_ad_campaigns_platform', 'platform'),
        Index('idx_ad_campaigns_last_optimized', 'last_optimized'),
    )
```

#### `app/models/lead.py` - Lead Management Model
```python
from sqlalchemy import Column, String, Float, Boolean, JSON, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Lead(Base, TimestampMixin):
    __tablename__ = "leads"

    lead_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))

    # Lead information
    email = Column(String(255), index=True)
    name = Column(String(255))
    company = Column(String(255))
    job_title = Column(String(100))

    # Lead scoring
    score = Column(Float)  # 0.0 to 1.0
    qualified = Column(Boolean, default=False, index=True)
    status = Column(String(50), default="new", index=True)  # new, contacted, qualified, converted

    # Enrichment data
    properties = Column(JSON)  # Additional lead data
    source = Column(String(100), index=True)  # google_ads, linkedin, content

    # Timestamps
    last_contacted = Column(DateTime(timezone=True))
    converted_at = Column(DateTime(timezone=True))

    # Relationships
    user = relationship("User", back_populates="leads")

    # Indexes
    __table_args__ = (
        Index('idx_leads_score_status', 'score', 'status'),
        Index('idx_leads_qualified_score', 'qualified', 'score'),
    )
```

#### `app/models/content.py` - Content Library Model
```python
from sqlalchemy import Column, String, Text, JSON, Float, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class Content(Base, TimestampMixin):
    __tablename__ = "content_library"

    content_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_type = Column(String(50), nullable=False, index=True)  # blog, social, email, ad_copy
    title = Column(String(500))
    content = Column(Text)  # Full content
    metadata = Column(JSON)  # SEO data, word count, etc.
    performance_score = Column(Float)  # Engagement/completion rate
    generated_by = Column(String(50))  # Agent name
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaigns.campaign_id"))

    # Relationships
    campaign = relationship("Campaign", back_populates="content")

    # Indexes
    __table_args__ = (
        Index('idx_content_performance', 'performance_score'),
        Index('idx_content_generated_by', 'generated_by'),
    )
```

## Step 2: Database Connection & Session Management

### Files Created

#### `app/core/database.py` - Database Infrastructure
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import structlog

from app.config import settings
from app.models import Base

logger = structlog.get_logger(__name__)

# Create async engine
engine = create_async_engine(
    settings.database.url,
    echo=settings.database.echo,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    poolclass=NullPool,  # Better for async
)

# Create async session factory
async_session_factory = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncSession:
    """Dependency for getting async database session"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def create_tables():
    """Create all database tables"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error("Failed to create database tables", error=str(e))
        raise

async def drop_tables():
    """Drop all database tables (for testing)"""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error("Failed to drop database tables", error=str(e))
        raise

async def init_db():
    """Initialize database with tables and initial data"""
    await create_tables()
    # Add any initial data seeding here
```

## Step 3: Alembic Database Migrations

### Files Created

#### `alembic.ini` - Alembic Configuration
```ini
[alembic]
script_location = alembic
sqlalchemy.url = driver://user:pass@localhost/dbname

[post_write_hooks]
# Logging
hooks = black
black.type = file
black.location = %(here)s

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### `alembic/env.py` - Migration Environment
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.config import settings
from app.models import Base

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from settings
config.set_main_option("sqlalchemy.url", settings.database.url)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

#### `alembic/versions/001_initial_schema.py` - Initial Migration
```python
"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_seen', sa.DateTime(timezone=True), nullable=True),
        sa.Column('traits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('segment', sa.String(length=50), nullable=True),
        sa.Column('ltv_prediction', sa.Float(), nullable=True),
        sa.Column('churn_risk', sa.Float(), nullable=True),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )

    # Create indexes for users
    op.create_index('idx_users_email', 'users', ['email'], unique=False)
    op.create_index('idx_users_segment', 'users', ['segment'], unique=False)
    op.create_index('idx_users_last_seen', 'users', ['last_seen'], unique=False)

    # Create events table
    op.create_table('events',
        sa.Column('event_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('event_name', sa.String(length=100), nullable=False),
        sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('event_id')
    )

    # Create indexes for events
    op.create_index('idx_events_user_timestamp', 'events', ['user_id', 'timestamp'], unique=False)
    op.create_index('idx_events_event_name', 'events', ['event_name'], unique=False)
    op.create_index('idx_events_timestamp', 'events', ['timestamp'], unique=False)

    # Create campaigns table
    op.create_table('campaigns',
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('budget', sa.Float(), nullable=True),
        sa.Column('spent', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('campaign_id')
    )

    # Create ad_campaigns table
    op.create_table('ad_campaigns',
        sa.Column('ad_campaign_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('platform', sa.String(length=50), nullable=False),
        sa.Column('platform_campaign_id', sa.String(length=255), nullable=True),
        sa.Column('audience_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('creatives', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('performance_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('last_optimized', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.campaign_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('ad_campaign_id')
    )

    # Create leads table
    op.create_table('leads',
        sa.Column('lead_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('job_title', sa.String(length=100), nullable=True),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('qualified', sa.Boolean(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('properties', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_contacted', sa.DateTime(timezone=True), nullable=True),
        sa.Column('converted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
        sa.PrimaryKeyConstraint('lead_id')
    )

    # Create content_library table
    op.create_table('content_library',
        sa.Column('content_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content_type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('performance_score', sa.Float(), nullable=True),
        sa.Column('generated_by', sa.String(length=50), nullable=True),
        sa.Column('campaign_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.campaign_id'], ),
        sa.PrimaryKeyConstraint('content_id')
    )

def downgrade() -> None:
    op.drop_table('content_library')
    op.drop_table('leads')
    op.drop_table('ad_campaigns')
    op.drop_table('campaigns')
    op.drop_table('events')
    op.drop_table('users')
```

## Step 4: Authentication & API Key Management

### Files Created

#### `app/core/security.py` - Security Utilities
```python
import secrets
from datetime import datetime, timedelta
from typing import Optional
import jwt
from passlib.context import CryptContext
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.JWTError as e:
        logger.warning("Token validation failed", error=str(e))
        return None

def generate_api_key() -> str:
    """Generate a secure API key"""
    return secrets.token_urlsafe(32)

def hash_api_key(api_key: str) -> str:
    """Hash an API key for storage"""
    return pwd_context.hash(api_key)

def verify_api_key(plain_api_key: str, hashed_api_key: str) -> bool:
    """Verify an API key against its hash"""
    return pwd_context.verify(plain_api_key, hashed_api_key)
```

#### `app/models/api_key.py` - API Key Model
```python
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import Base, TimestampMixin

class APIKey(Base, TimestampMixin):
    __tablename__ = "api_keys"

    api_key_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    hashed_key = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, index=True)
    expires_at = Column(DateTime(timezone=True))
    last_used_at = Column(DateTime(timezone=True))
    usage_count = Column(Integer, default=0)

    # Rate limiting
    rate_limit_requests = Column(Integer, default=1000)  # requests per window
    rate_limit_window = Column(Integer, default=3600)    # window in seconds

    # Ownership
    created_by = Column(String(100))  # Could be user_id or system

    # Indexes
    __table_args__ = (
        Index('idx_api_keys_active', 'is_active'),
        Index('idx_api_keys_expires', 'expires_at'),
    )

    def is_expired(self) -> bool:
        """Check if API key is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False

    def can_make_request(self) -> bool:
        """Check if request can be made within rate limits"""
        # This would be enhanced with Redis-based rate limiting
        return self.is_active and not self.is_expired()
```

#### `app/core/auth.py` - Authentication Middleware
```python
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.security import verify_api_key
from app.models.api_key import APIKey
from app.core.logging import get_logger

logger = get_logger(__name__)
security = HTTPBearer(auto_error=False)

async def get_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> APIKey:
    """
    Validate API key from request headers

    Args:
        credentials: Bearer token credentials
        db: Database session

    Returns:
        APIKey: Validated API key object

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not credentials:
        logger.warning("No API key provided")
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    api_key = credentials.credentials

    # Query API key from database
    query = await db.execute(
        "SELECT * FROM api_keys WHERE is_active = true AND (expires_at IS NULL OR expires_at > NOW())"
    )
    api_keys = query.fetchall()

    # Check each active API key
    for key_record in api_keys:
        key_obj = APIKey(**key_record)
        if verify_api_key(api_key, key_obj.hashed_key):
            # Update usage statistics
            await db.execute(
                """
                UPDATE api_keys
                SET usage_count = usage_count + 1, last_used_at = NOW()
                WHERE api_key_id = $1
                """,
                key_obj.api_key_id
            )
            await db.commit()

            logger.info("API key authenticated", api_key_id=str(key_obj.api_key_id))
            return key_obj

    logger.warning("Invalid API key provided")
    raise HTTPException(
        status_code=401,
        detail="Invalid API key",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user(api_key: APIKey = Depends(get_api_key)):
    """
    Get current user from API key
    This is a placeholder - in a real app you'd have user association
    """
    # For MVP, we just return the API key info
    # In production, you'd look up the user associated with this API key
    return {
        "api_key_id": api_key.api_key_id,
        "name": api_key.name,
        "permissions": ["read", "write"]  # Basic permissions
    }
```

## Step 5: Redis Caching Layer

### Files Created

#### `app/core/cache.py` - Redis Cache Implementation
```python
import json
from typing import Any, Optional, Union
import redis.asyncio as redis
import structlog

from app.config import settings
from app.core.metrics import cache_hits_total, cache_misses_total, cache_hit_ratio

logger = structlog.get_logger(__name__)

class Cache:
    """Redis-based caching with metrics"""

    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = redis.Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                db=settings.redis.db,
                password=settings.redis.password,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Disconnected from Redis")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            value = await self.redis.get(key)
            if value:
                cache_hits_total.inc()
                return json.loads(value)
            else:
                cache_misses_total.inc()
                return None
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        try:
            json_value = json.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, json_value)
            else:
                await self.redis.set(key, json_value)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.error("Cache exists error", key=key, error=str(e))
            return False

# Global cache instance
cache = Cache()

async def setup_redis():
    """Initialize Redis connection"""
    await cache.connect()

async def get_cache() -> Cache:
    """Dependency for getting cache instance"""
    return cache

# Cache key generators
def user_cache_key(user_id: str) -> str:
    """Generate cache key for user data"""
    return f"user:{user_id}"

def campaign_cache_key(campaign_id: str) -> str:
    """Generate cache key for campaign data"""
    return f"campaign:{campaign_id}"

def recommendations_cache_key(user_id: str, context: str) -> str:
    """Generate cache key for user recommendations"""
    return f"recommendations:{user_id}:{context}"
```

## Step 6: Event Tracking API

### Files Created

#### `app/schemas/event.py` - Event Pydantic Schemas
```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class EventBase(BaseModel):
    user_id: UUID
    event_name: str = Field(..., max_length=100, description="Event name")
    properties: Optional[Dict[str, Any]] = Field(None, description="Event properties")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")
    session_id: Optional[UUID] = Field(None, description="Session identifier")

class EventCreate(EventBase):
    pass

class Event(EventBase):
    event_id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class EventBatchCreate(BaseModel):
    events: list[EventCreate] = Field(..., description="List of events to track")

class EventBatchResponse(BaseModel):
    events_tracked: int
    status: str = "batch_processed"
    processed_at: datetime
```

#### `app/api/v1/events.py` - Event API Endpoints
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.auth import get_api_key
from app.core.metrics import measure_api_request
from app.models.event import Event as EventModel
from app.schemas.event import EventCreate, EventBatchCreate, EventBatchResponse
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/track", response_model=dict)
@measure_api_request("POST", "/api/v1/events/track")
async def track_event(
    event: EventCreate,
    db: AsyncSession = Depends(get_db),
    api_key = Depends(get_api_key)
):
    """
    Track a single user event

    This endpoint records user behavior events for personalization and analytics.
    Events are processed asynchronously and stored in the database.
    """
    try:
        # Create event record
        db_event = EventModel(
            user_id=event.user_id,
            event_name=event.event_name,
            properties=event.properties,
            timestamp=event.timestamp,
            session_id=event.session_id
        )

        db.add(db_event)
        await db.commit()
        await db.refresh(db_event)

        logger.info(
            "Event tracked",
            event_id=db_event.event_id,
            user_id=str(event.user_id),
            event_name=event.event_name
        )

        return {
            "event_id": db_event.event_id,
            "status": "tracked",
            "processed_at": db_event.created_at
        }

    except Exception as e:
        logger.error("Failed to track event", error=str(e), user_id=str(event.user_id))
        raise HTTPException(status_code=500, detail="Failed to track event")

@router.post("/batch", response_model=EventBatchResponse)
@measure_api_request("POST", "/api/v1/events/batch")
async def track_events_batch(
    batch: EventBatchCreate,
    db: AsyncSession = Depends(get_db),
    api_key = Depends(get_api_key)
):
    """
    Track multiple events in a single request

    This endpoint provides better performance for high-volume event tracking
    by batching multiple events into a single database transaction.
    """
    try:
        # Create event records
        db_events = []
        for event in batch.events:
            db_event = EventModel(
                user_id=event.user_id,
                event_name=event.event_name,
                properties=event.properties,
                timestamp=event.timestamp,
                session_id=event.session_id
            )
            db_events.append(db_event)
            db.add(db_event)

        await db.commit()

        # Refresh all events to get IDs
        for event in db_events:
            await db.refresh(event)

        logger.info(
            "Batch events tracked",
            count=len(db_events),
            api_key_id=str(api_key.api_key_id)
        )

        return EventBatchResponse(
            events_tracked=len(db_events),
            processed_at=datetime.utcnow()
        )

    except Exception as e:
        logger.error("Failed to track batch events", error=str(e))
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to track events")
```

## Step 7: User Management API

### Files Created

#### `app/schemas/user.py` - User Pydantic Schemas
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    traits: Optional[Dict[str, Any]] = None

class UserCreate(UserBase):
    user_id: Optional[UUID] = None

class UserUpdate(BaseModel):
    traits: Optional[Dict[str, Any]] = None
    segment: Optional[str] = None

class User(UserBase):
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    last_seen: Optional[datetime] = None
    segment: Optional[str] = None
    ltv_prediction: Optional[float] = None
    churn_risk: Optional[float] = None

    class Config:
        from_attributes = True

class UserProfile(User):
    event_count: int = 0
    campaigns_count: int = 0
    leads_count: int = 0
```

#### `app/api/v1/users.py` - User API Endpoints
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
import structlog

from app.core.database import get_db
from app.core.auth import get_api_key
from app.core.cache import get_cache, user_cache_key
from app.core.metrics import measure_api_request
from app.models.user import User as UserModel
from app.models.event import Event
from app.models.campaign import Campaign
from app.models.lead import Lead
from app.schemas.user import UserCreate, UserUpdate, User, UserProfile
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/identify", response_model=User)
@measure_api_request("POST", "/api/v1/users/identify")
async def identify_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    cache = Depends(get_cache),
    api_key = Depends(get_api_key)
):
    """
    Create or update user profile

    This endpoint manages user identification and profile updates.
    User traits are stored as flexible JSON data.
    """
    try:
        user_id = user.user_id or uuid.uuid4()

        # Check if user exists
        db_user = await db.get(UserModel, user_id)

        if db_user:
            # Update existing user
            for field, value in user.dict(exclude_unset=True).items():
                if field != "user_id":
                    setattr(db_user, field, value)
            db_user.last_seen = datetime.utcnow()
        else:
            # Create new user
            db_user = UserModel(
                user_id=user_id,
                email=user.email,
                traits=user.traits,
                last_seen=datetime.utcnow()
            )
            db.add(db_user)

        await db.commit()
        await db.refresh(db_user)

        # Cache user data
        cache_key = user_cache_key(str(user_id))
        await cache.set(cache_key, db_user.__dict__, ttl=3600)  # 1 hour

        logger.info(
            "User identified",
            user_id=str(user_id),
            email=user.email,
            is_new=not db_user
        )

        return User.from_orm(db_user)

    except Exception as e:
        logger.error("Failed to identify user", error=str(e), email=user.email)
        raise HTTPException(status_code=500, detail="Failed to identify user")

@router.get("/{user_id}", response_model=UserProfile)
@measure_api_request("GET", "/api/v1/users/{user_id}")
async def get_user_profile(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    cache = Depends(get_cache),
    api_key = Depends(get_api_key)
):
    """
    Get user profile with statistics

    Returns user information along with engagement metrics.
    """
    try:
        # Check cache first
        cache_key = user_cache_key(str(user_id))
        cached_user = await cache.get(cache_key)
        if cached_user:
            return UserProfile(**cached_user)

        # Query user from database
        db_user = await db.get(UserModel, user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        # Get user statistics
        event_count = await db.scalar(
            func.count(Event.event_id).filter(Event.user_id == user_id)
        )

        campaigns_count = await db.scalar(
            func.count(Campaign.campaign_id).filter(Campaign.created_by == str(user_id))
        )

        leads_count = await db.scalar(
            func.count(Lead.lead_id).filter(Lead.user_id == user_id)
        )

        user_profile = UserProfile.from_orm(db_user)
        user_profile.event_count = event_count or 0
        user_profile.campaigns_count = campaigns_count or 0
        user_profile.leads_count = leads_count or 0

        # Cache the result
        await cache.set(cache_key, user_profile.dict(), ttl=1800)  # 30 minutes

        return user_profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get user profile", error=str(e), user_id=str(user_id))
        raise HTTPException(status_code=500, detail="Failed to get user profile")
```

## Step 8: LangSmith Integration

### Files Created

#### `app/core/langsmith.py` - LangSmith Observability
```python
import os
from typing import Any, Dict, Optional
from langsmith import Client
import structlog

from app.config import settings

logger = structlog.get_logger(__name__)

class LangSmithTracker:
    """LangSmith integration for LLM observability"""

    def __init__(self):
        if not settings.langsmith.api_key:
            logger.warning("LangSmith API key not configured")
            self.client = None
            return

        try:
            self.client = Client(
                api_key=settings.langsmith.api_key,
                api_url=settings.langsmith.endpoint
            )
            logger.info("LangSmith client initialized")
        except Exception as e:
            logger.error("Failed to initialize LangSmith client", error=str(e))
            self.client = None

    async def log_llm_call(
        self,
        provider: str,
        model: str,
        messages: list,
        response: Any,
        latency: float,
        tokens_used: Optional[Dict[str, int]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log LLM API call to LangSmith"""
        if not self.client:
            return

        try:
            run_data = {
                "name": f"{provider}_{model}",
                "run_type": "llm",
                "inputs": {"messages": messages},
                "outputs": {"response": response},
                "extra": {
                    "metadata": metadata or {},
                    "latency": latency,
                    "tokens": tokens_used or {}
                }
            }

            # Create run in LangSmith
            self.client.create_run(**run_data)

        except Exception as e:
            logger.error("Failed to log LLM call to LangSmith", error=str(e))

    async def log_agent_action(
        self,
        agent_name: str,
        action: str,
        inputs: Dict[str, Any],
        outputs: Dict[str, Any],
        duration: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log agent action to LangSmith"""
        if not self.client:
            return

        try:
            run_data = {
                "name": f"agent_{agent_name}_{action}",
                "run_type": "chain",
                "inputs": inputs,
                "outputs": outputs,
                "extra": {
                    "metadata": metadata or {},
                    "duration": duration
                }
            }

            self.client.create_run(**run_data)

        except Exception as e:
            logger.error("Failed to log agent action to LangSmith", error=str(e))

    async def log_rag_query(
        self,
        query: str,
        retrieved_docs: list,
        response: str,
        latency: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Log RAG query to LangSmith"""
        if not self.client:
            return

        try:
            run_data = {
                "name": "rag_query",
                "run_type": "retriever",
                "inputs": {"query": query},
                "outputs": {
                    "response": response,
                    "retrieved_docs": retrieved_docs
                },
                "extra": {
                    "metadata": metadata or {},
                    "latency": latency,
                    "docs_count": len(retrieved_docs)
                }
            }

            self.client.create_run(**run_data)

        except Exception as e:
            logger.error("Failed to log RAG query to LangSmith", error=str(e))

# Global LangSmith tracker instance
langsmith_tracker = LangSmithTracker()

def get_langsmith_tracker() -> LangSmithTracker:
    """Get LangSmith tracker instance"""
    return langsmith_tracker
```

## Summary

Phase 2 establishes the complete data layer and authentication system:

### ✅ **Database Layer**
- SQLAlchemy async models with proper relationships
- Alembic migrations for schema versioning
- Optimized indexes for query performance
- JSONB fields for flexible data storage

### ✅ **Authentication & Security**
- API key authentication with hashing
- JWT token support for future user sessions
- Rate limiting infrastructure
- Security utilities for password hashing

### ✅ **Caching & Performance**
- Redis integration for session and data caching
- Cache key generators for different data types
- TTL-based cache expiration

### ✅ **API Infrastructure**
- Event tracking API with batch support
- User management endpoints
- Proper error handling and validation
- Request/response logging

### ✅ **Observability**
- LangSmith integration for LLM tracking
- Structured logging throughout
- Performance metrics collection

### 🎯 **Showcase Features for Job Applications**
- Production-ready database design with async SQLAlchemy
- Secure API authentication and authorization
- Redis caching for high-performance data access
- Comprehensive observability with LangSmith
- Type-safe APIs with Pydantic validation

This foundation provides a robust base for implementing the AI agent orchestration and RAG systems in Phase 3.
