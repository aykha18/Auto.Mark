"""
Database configuration for Unitasa
Supports both local development and Railway PostgreSQL
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Railway provides DATABASE_URL, but we need to ensure it's async
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
elif not DATABASE_URL:
    # Temporary fallback for debugging - use SQLite
    print("WARNING: DATABASE_URL not set, using SQLite fallback for debugging")
    DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine
if DATABASE_URL.startswith("sqlite"):
    # SQLite doesn't support connection pooling
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL logging in development
    )
else:
    # PostgreSQL with connection pooling
    engine = create_async_engine(
        DATABASE_URL,
        echo=False,  # Set to True for SQL logging in development
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

# Create declarative base
Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)