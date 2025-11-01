"""
Database configuration for Unitasa
Supports both local development and Railway PostgreSQL
"""

import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create declarative base
Base = declarative_base()

# Global variables for lazy initialization
engine = None
AsyncSessionLocal = None


def get_database_url():
    """Get and validate database URL"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required. For local development, set DATABASE_URL to a PostgreSQL connection string.")
    
    # Railway provides DATABASE_URL, but we need to ensure it's async
    if DATABASE_URL.startswith("postgresql://"):
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    return DATABASE_URL


def init_database():
    """Initialize database engine and session factory (lazy initialization)"""
    global engine, AsyncSessionLocal
    
    if engine is not None:
        return engine, AsyncSessionLocal
    
    try:
        DATABASE_URL = get_database_url()
        
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
        
        return engine, AsyncSessionLocal
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        raise


async def get_db():
    """Dependency to get database session"""
    # Initialize database if not already done
    engine, AsyncSessionLocal = init_database()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    # Initialize database if not already done
    engine, _ = init_database()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)