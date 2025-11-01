"""
Unitasa - Unified Marketing Intelligence Platform
Main FastAPI application entry point
"""

import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager

from app.core.database import Base, init_database
from app.core.security_middleware import SecurityHeadersMiddleware

print("Importing API modules...")
try:
    print("Importing health module...")
    from app.api.v1 import health
    print("Health module imported successfully")
    
    print("Importing landing module...")
    from app.api.v1 import landing_working as landing
    print("Landing module imported successfully")
    
    print("Importing chat module...")
    from app.api.v1 import chat
    print("Chat module imported successfully")
    
    print("Importing analytics module...")
    from app.api.v1 import analytics
    print("Analytics module imported successfully")
    
    print("Importing crm_marketplace module...")
    from app.api.v1 import crm_marketplace
    print("CRM marketplace module imported successfully")
    
    print("All API modules imported successfully")
except Exception as e:
    print(f"Error importing API modules: {e}")
    import traceback
    traceback.print_exc()

# Import all models to ensure they are registered with SQLAlchemy
from app.models import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting Unitasa application...")
    try:
        print("Attempting database connection...")
        engine, _ = init_database()
        print(f"Database URL: {engine.url}")
        async with engine.begin() as conn:
            print("Creating database tables...")
            await conn.run_sync(Base.metadata.create_all)
            print(f"Created tables: {list(Base.metadata.tables.keys())}")
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Database connection failed during startup: {e}")
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        print("Application will continue without database initialization")

    print("Application startup complete")
    yield

    # Shutdown
    print("Shutting down application...")
    try:
        engine, _ = init_database()
        await engine.dispose()
        print("Database connection disposed successfully")
    except Exception as e:
        print(f"Error disposing database connection: {e}")


# Create FastAPI application
print("Creating FastAPI application...")
app = FastAPI(
    title="Unitasa API",
    description="Unified Marketing Intelligence Platform - Everything you need IN one platform",
    version="1.0.0",
    lifespan=lifespan
)
print("FastAPI application created")

# Add security middleware (commented out for debugging)
# app.add_middleware(SecurityHeadersMiddleware)

# Add CORS middleware
# Configure CORS for Railway deployment
def get_allowed_origins():
    """Get allowed origins based on environment"""
    # Base allowed origins
    origins = [
        "http://localhost:3000",  # Local development
        "http://localhost:3001",  # Alternative local port
        "https://unitas.up.railway.app",  # Railway frontend
    ]
    
    # Add environment-specific origins
    frontend_url = os.getenv("FRONTEND_URL")
    if frontend_url:
        origins.append(frontend_url)
    
    # In development or if no specific environment, allow all
    environment = os.getenv("ENVIRONMENT", "development")
    railway_env = os.getenv("RAILWAY_ENVIRONMENT")
    
    if environment == "development" and not railway_env:
        return ["*"]
    
    return origins

allowed_origins = get_allowed_origins()
print(f"CORS allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
print("Including API routers...")
try:
    print("Including health router...")
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    print("Health router included successfully")
    
    print("Including landing router...")
    app.include_router(landing.router, prefix="/api/v1/landing", tags=["landing"])
    print("Landing router included successfully")
    
    print("Including chat router...")
    app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
    print("Chat router included successfully")
    
    print("Including analytics router...")
    app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
    print("Analytics router included successfully")
    
    print("Including crm_marketplace router...")
    app.include_router(crm_marketplace.router, prefix="/api/v1", tags=["crm"])
    print("CRM marketplace router included successfully")
    
    print("All API routers included successfully")
except Exception as e:
    print(f"Error including API routers: {e}")
    import traceback
    traceback.print_exc()

# Serve static files from React build
print("Checking for frontend build...")
if os.path.exists("frontend/build"):
    print("Frontend build found, mounting static files")
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

    # Note: This catch-all route will be defined at the end of the file
    # to avoid intercepting API routes
else:
    print("Frontend build not found!")

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    from datetime import datetime
    return {
        "status": "healthy",
        "service": "unitasa-api",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "features": {
            "database": True,
            "co_creator_program": True,
            "assessment_engine": True,
            "payment_processing": True
        }
    }

@app.get("/cors-debug")
async def cors_debug(request: Request):
    """Debug CORS configuration"""
    return {
        "allowed_origins": get_allowed_origins(),
        "request_origin": request.headers.get("origin"),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "railway_environment": os.getenv("RAILWAY_ENVIRONMENT"),
        "frontend_url": os.getenv("FRONTEND_URL"),
        "all_headers": dict(request.headers)
    }

@app.middleware("http")
async def track_conversion_funnel(request, call_next):
    """Middleware to track conversion funnel analytics"""
    from datetime import datetime

    # Track page views and user journey
    path = request.url.path
    user_agent = request.headers.get("user-agent", "")
    referrer = request.headers.get("referer", "")

    # Could store this data for analytics
    # For now, just pass through
    response = await call_next(request)

    # Add tracking headers for analytics
    response.headers["X-Conversion-Stage"] = get_conversion_stage(path)

    return response

def get_conversion_stage(path: str) -> str:
    """Determine conversion stage based on URL path"""
    if path == "/":
        return "landing"
    elif "assessment" in path:
        return "assessment"
    elif "co-creator" in path:
        return "co_creator_interest"
    elif "payment" in path:
        return "payment"
    else:
        return "other"

@app.get("/")
async def root():
    """Root endpoint - serve React app"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    return {"message": "Unitasa API - Unified Marketing Intelligence Platform"}


# TODO: Add catch-all route for React app after API testing is complete


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)