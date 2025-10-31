#!/usr/bin/env python3
"""
Unitasa deployment verification script
Tests all critical functionality before going live
"""

import asyncio
import httpx
import os
import sys
from pathlib import Path


async def verify_frontend_build():
    """Verify React frontend build exists and is complete"""
    print("🔍 Verifying frontend build...")
    
    build_dir = Path("frontend/build")
    if not build_dir.exists():
        print("❌ Frontend build directory not found!")
        return False
    
    required_files = [
        "index.html",
        "static/js",
        "static/css",
        "manifest.json"
    ]
    
    for file_path in required_files:
        if not (build_dir / file_path).exists():
            print(f"❌ Missing required file: {file_path}")
            return False
    
    print("✅ Frontend build verified")
    return True


async def verify_backend_config():
    """Verify backend configuration"""
    print("🔍 Verifying backend configuration...")
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        
        print(f"✅ App name: {settings.app_name}")
        print(f"✅ Environment: {settings.environment}")
        print(f"✅ Port: {settings.port}")
        
        return True
    except Exception as e:
        print(f"❌ Backend configuration error: {e}")
        return False


async def verify_database_config():
    """Verify database configuration"""
    print("🔍 Verifying database configuration...")
    
    try:
        from app.core.database import engine
        print("✅ Database engine created successfully")
        return True
    except Exception as e:
        print(f"❌ Database configuration error: {e}")
        return False


async def verify_api_structure():
    """Verify API structure"""
    print("🔍 Verifying API structure...")
    
    api_files = [
        "app/main.py",
        "app/api/v1/health.py",
        "app/api/v1/landing.py",
        "app/api/v1/chat.py",
        "app/api/v1/analytics.py",
        "app/api/v1/crm_marketplace.py"
    ]
    
    for file_path in api_files:
        if not Path(file_path).exists():
            print(f"❌ Missing API file: {file_path}")
            return False
    
    print("✅ API structure verified")
    return True


async def verify_environment_template():
    """Verify environment template exists"""
    print("🔍 Verifying environment configuration...")
    
    if not Path(".env.railway").exists():
        print("❌ Railway environment template not found!")
        return False
    
    print("✅ Environment template verified")
    return True


async def verify_railway_config():
    """Verify Railway configuration files"""
    print("🔍 Verifying Railway configuration...")
    
    config_files = [
        "railway.json",
        "nixpacks.toml", 
        "requirements.txt",
        "Procfile"
    ]
    
    for file_path in config_files:
        if not Path(file_path).exists():
            print(f"❌ Missing Railway config: {file_path}")
            return False
    
    print("✅ Railway configuration verified")
    return True


async def test_local_startup():
    """Test if the application can start locally"""
    print("🔍 Testing local application startup...")
    
    try:
        from app.main import app
        print("✅ FastAPI app imports successfully")
        return True
    except Exception as e:
        print(f"❌ Application startup error: {e}")
        return False


async def main():
    """Run all verification checks"""
    print("🚀 Unitasa Deployment Verification")
    print("=" * 50)
    
    checks = [
        verify_frontend_build,
        verify_backend_config,
        verify_database_config,
        verify_api_structure,
        verify_environment_template,
        verify_railway_config,
        test_local_startup
    ]
    
    results = []
    for check in checks:
        try:
            result = await check()
            results.append(result)
        except Exception as e:
            print(f"❌ Check failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Ready for Railway deployment!")
        print()
        print("Next steps:")
        print("1. Push code to GitHub: git push origin main")
        print("2. Create Railway project and connect repository")
        print("3. Add PostgreSQL service")
        print("4. Configure environment variables from .env.railway")
        print("5. Deploy and monitor!")
        return True
    else:
        print("❌ Some checks failed. Please fix issues before deploying.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)