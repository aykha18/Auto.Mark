#!/usr/bin/env python3
"""
Quick diagnostic to check what might have failed
"""

import os
import sys

def check_environment():
    """Check environment variables"""
    print("🔍 Environment Check:")
    print("=" * 30)
    
    # Check Razorpay credentials
    razorpay_key = os.getenv("RAZORPAY_KEY_ID", "")
    razorpay_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
    
    print(f"RAZORPAY_KEY_ID: {'✅ Set' if razorpay_key else '❌ Missing'}")
    if razorpay_key:
        print(f"  Value: {razorpay_key[:8]}...")
    
    print(f"RAZORPAY_KEY_SECRET: {'✅ Set' if razorpay_secret else '❌ Missing'}")
    if razorpay_secret:
        print(f"  Value: {razorpay_secret[:8]}...")
    
    # Check database
    db_url = os.getenv("DATABASE_URL", "")
    print(f"DATABASE_URL: {'✅ Set' if db_url else '❌ Missing'}")
    
    # Check email
    from_email = os.getenv("FROM_EMAIL", "")
    support_email = os.getenv("SUPPORT_EMAIL", "")
    print(f"FROM_EMAIL: {'✅ Set' if from_email else '❌ Missing'} ({from_email})")
    print(f"SUPPORT_EMAIL: {'✅ Set' if support_email else '❌ Missing'} ({support_email})")

def check_imports():
    """Check if required modules can be imported"""
    print("\n📦 Import Check:")
    print("=" * 30)
    
    try:
        import razorpay
        print("✅ razorpay module available")
    except ImportError as e:
        print(f"❌ razorpay module missing: {e}")
    
    try:
        from app.core.razorpay_service import RazorpayPaymentService
        print("✅ RazorpayPaymentService can be imported")
    except ImportError as e:
        print(f"❌ RazorpayPaymentService import failed: {e}")
    
    try:
        from app.core.config import get_settings
        settings = get_settings()
        print("✅ Settings can be loaded")
        print(f"   Razorpay Key ID: {settings.wise.api_key[:8] if hasattr(settings, 'wise') else 'N/A'}...")
    except Exception as e:
        print(f"❌ Settings loading failed: {e}")

def check_server_status():
    """Check if server is running"""
    print("\n🌐 Server Check:")
    print("=" * 30)
    
    try:
        import httpx
        import asyncio
        
        async def test_server():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8000/api/v1/health", timeout=5.0)
                    if response.status_code == 200:
                        print("✅ Server is running and responding")
                        return True
                    else:
                        print(f"⚠️ Server responding but with status: {response.status_code}")
                        return False
            except Exception as e:
                print(f"❌ Server not responding: {e}")
                return False
        
        return asyncio.run(test_server())
        
    except Exception as e:
        print(f"❌ Cannot check server: {e}")
        return False

def main():
    print("🚨 Quick Diagnostic Tool")
    print("=" * 50)
    
    check_environment()
    check_imports()
    server_running = check_server_status()
    
    print("\n📋 Summary:")
    print("=" * 30)
    
    # Check what might be the issue
    razorpay_key = os.getenv("RAZORPAY_KEY_ID", "")
    razorpay_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
    
    if not razorpay_key or not razorpay_secret:
        print("❌ Issue: Razorpay credentials not properly set")
        print("💡 Solution: Check .env file for RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET")
    
    if not server_running:
        print("❌ Issue: Server not running or not responding")
        print("💡 Solution: Start server with: uvicorn app.main:app --reload --port 8000")
    
    db_url = os.getenv("DATABASE_URL", "")
    if not db_url:
        print("⚠️ Warning: DATABASE_URL not set (API endpoints may fail)")
        print("💡 Note: Direct service tests should still work")
    
    print("\n🔧 Quick Fixes:")
    print("1. Check .env file has correct Razorpay credentials")
    print("2. Restart server if needed")
    print("3. Try running: python test_real_razorpay.py")
    print("4. Check Razorpay dashboard for any account issues")

if __name__ == "__main__":
    main()