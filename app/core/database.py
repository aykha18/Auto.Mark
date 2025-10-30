"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.config import get_settings
from app.models.base import Base

settings = get_settings()

# Create database engine
engine = create_engine(
    settings.database.url,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    echo=settings.api.debug,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def create_tables():
    """Create all database tables"""
    # Import all models to ensure they're registered
    from app.models import (
        User, Event, Lead, Campaign, Content,
        Assessment, CoCreatorProgram, CoCreator,
        PaymentTransaction, FounderStory, FounderMilestone
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> Session:
    """Get async database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()