#!/usr/bin/env python3
"""
Unitasa application startup script for Railway
"""

import os
import sys
import asyncio
import uvicorn
from app.main import app
from app.core.database import init_db


async def startup():
    """Initialize database and start application"""
    try:
        # Initialize database tables
        await init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        # Don't exit - Railway DB might not be ready yet
        pass


def main():
    """Main startup function"""
    # Get port from environment (Railway sets this)
    port = int(os.getenv("PORT", 8000))
    
    # Initialize database
    asyncio.run(startup())
    
    # Start the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )


if __name__ == "__main__":
    main()