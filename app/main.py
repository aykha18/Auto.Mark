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

from app.core.database import engine, Base
from app.core.security_middleware import SecurityHeadersMiddleware
from app.api.v1 import landing, chat, analytics, crm_marketplace, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("Starting Unitasa application...")
    try:
        print("Attempting database connection...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Database connection failed during startup: {e}")
        print("Application will continue without database initialization")

    print("Application startup complete")
    yield

    # Shutdown
    print("Shutting down application...")
    try:
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include API routers
print("Including API routers...")
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(landing.router, prefix="/api/v1", tags=["landing"])
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
app.include_router(analytics.router, prefix="/api/v1", tags=["analytics"])
app.include_router(crm_marketplace.router, prefix="/api/v1", tags=["crm"])
print("API routers included")

# Serve static files from React build
print("Checking for frontend build...")
if os.path.exists("frontend/build"):
    print("Frontend build found, mounting static files")
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")

    @app.get("/{full_path:path}")
    async def serve_react_app(request: Request, full_path: str):
        """Serve React app for all non-API routes"""
        print(f"Serving path: {full_path}")
        # API routes should not be caught by this
        if full_path.startswith("api/"):
            return {"error": "API endpoint not found"}

        # Serve static files
        file_path = f"frontend/build/{full_path}"
        if os.path.exists(file_path) and os.path.isfile(file_path):
            print(f"Serving static file: {file_path}")
            return FileResponse(file_path)

        # Serve index.html for all other routes (React Router)
        index_path = "frontend/build/index.html"
        if os.path.exists(index_path):
            print(f"Serving index.html: {index_path}")
            return FileResponse(index_path)
        else:
            print("index.html not found!")
            return {"error": "Frontend not built"}
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
        "version": "1.0.0"
    }

@app.get("/")
async def root():
    """Root endpoint - serve React app"""
    if os.path.exists("frontend/build/index.html"):
        return FileResponse("frontend/build/index.html")
    return {"message": "Unitasa API - Unified Marketing Intelligence Platform"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3000))
    uvicorn.run(app, host="0.0.0.0", port=port)