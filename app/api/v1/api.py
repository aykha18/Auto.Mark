"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter

from app.api.agents import router as agents_router
from .landing import router as landing_router
from .crm_marketplace import router as crm_marketplace_router
from .chat import router as chat_router
from .analytics import router as analytics_router

api_router = APIRouter()

# Include existing agents router
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])

# Include new landing page router
api_router.include_router(landing_router, prefix="/landing", tags=["landing"])

# Include CRM marketplace router
api_router.include_router(crm_marketplace_router, prefix="/crm-marketplace", tags=["crm-marketplace"])

# Include chat router
api_router.include_router(chat_router, prefix="/chat", tags=["chat"])

# Include analytics router
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
