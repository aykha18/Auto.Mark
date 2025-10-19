"""
AI Marketing Agents - FastAPI Application
Main entry point for the microservice
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
from prometheus_client import make_asgi_app

from app.config import settings, get_settings
from app.core.logging import setup_logging
from app.core.metrics import setup_metrics
from app.core.database import create_tables, get_db
from app.core.cache import setup_redis
from app.api.v1.api import api_router
from app.core.circuit_breaker import setup_circuit_breakers


# Setup structured logging
setup_logging()

# Setup metrics
metrics_app = make_asgi_app()

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager
    Handles startup and shutdown events
    """
    logger.info("Starting AI Marketing Agents", version=settings.version)

    # Startup
    try:
        # Create database tables
        await create_tables()

        # Setup Redis connection
        await setup_redis()

        # Setup circuit breakers
        setup_circuit_breakers()

        # Setup metrics
        setup_metrics()

        logger.info("Application startup complete")

    except Exception as e:
        logger.error("Application startup failed", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Marketing Agents")


def create_application() -> FastAPI:
    """
    Create and configure FastAPI application
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Autonomous AI marketing platform with advanced RAG and multi-agent orchestration",
        openapi_url="/api/v1/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Set up CORS
    if settings.api.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.api.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add trusted host middleware
    if not settings.is_development():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.api.allowed_hosts,
        )

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(
            "Unhandled exception",
            exc_info=exc,
            path=request.url.path,
            method=request.method,
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                }
            },
        )

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "version": settings.version,
            "environment": settings.environment,
        }

    # Metrics endpoint
    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        return metrics_app

    # API routes
    app.include_router(api_router, prefix="/api/v1")

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information"""
        return {
            "name": settings.app_name,
            "version": settings.version,
            "description": "Autonomous AI marketing platform",
            "docs": "/docs",
            "health": "/health",
            "metrics": "/metrics",
        }

    return app


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api.host,
        port=settings.api.port,
        reload=settings.api.debug,
        log_level=settings.log_level.lower(),
    )