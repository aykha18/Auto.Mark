#!/usr/bin/env python3
"""
Diagnose Railway 500 Internal Server Error
"""

import requests
import json

def diagnose_railway_500():
    """Diagnose the 500 error on Railway"""
    print("🔍 Railway 500 Error Diagnosis")
    print("=" * 50)
    
    base_url = "https://unitas.up.railway.app"
    
    print("PROGRESS SO FAR:")
    print("✅ CORS issue resolved")
    print("✅ API calls reaching Railway backend")
    print("❌ 500 Internal Server Error on assessment start")
    print()
    
    # Test health endpoint
    print("1️⃣ Testing health endpoint...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Health endpoint working")
            health_data = health_response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Service: {health_data.get('service')}")
            print(f"   Features: {health_data.get('features', {})}")
        else:
            print(f"❌ Health endpoint failed: {health_response.status_code}")
    except Exception as e:
        print(f"❌ Health endpoint error: {e}")
    
    print()
    
    # Test CORS debug endpoint
    print("2️⃣ Testing CORS debug endpoint...")
    try:
        cors_response = requests.get(f"{base_url}/cors-debug", timeout=10)
        if cors_response.status_code == 200:
            print("✅ CORS debug endpoint working")
            cors_data = cors_response.json()
            print(f"   Allowed origins: {cors_data.get('allowed_origins')}")
            print(f"   Environment: {cors_data.get('environment')}")
            print(f"   Railway env: {cors_data.get('railway_environment')}")
            print(f"   Frontend URL: {cors_data.get('frontend_url')}")
        else:
            print(f"❌ CORS debug endpoint failed: {cors_response.status_code}")
    except Exception as e:
        print(f"❌ CORS debug endpoint error: {e}")
    
    print()
    
    # Test assessment questions endpoint
    print("3️⃣ Testing assessment questions endpoint...")
    try:
        questions_response = requests.get(f"{base_url}/api/v1/landing/assessment/questions", timeout=10)
        if questions_response.status_code == 200:
            print("✅ Assessment questions endpoint working")
            questions_data = questions_response.json()
            print(f"   Total questions: {questions_data.get('total_questions')}")
        else:
            print(f"❌ Assessment questions failed: {questions_response.status_code}")
            print(f"   Response: {questions_response.text[:200]}...")
    except Exception as e:
        print(f"❌ Assessment questions error: {e}")
    
    print()
    
    # Test assessment start with minimal data
    print("4️⃣ Testing assessment start (this should show the 500 error)...")
    test_data = {
        "email": "test@example.com",
        "name": "Test User",
        "company": "Test Company",
        "preferred_crm": "hubspot"
    }
    
    try:
        start_response = requests.post(
            f"{base_url}/api/v1/landing/assessment/start",
            json=test_data,
            timeout=10
        )
        if start_response.status_code == 200:
            print("✅ Assessment start working!")
            start_data = start_response.json()
            print(f"   Assessment ID: {start_data.get('assessment_id')}")
        else:
            print(f"❌ Assessment start failed: {start_response.status_code}")
            print(f"   Response: {start_response.text[:500]}...")
    except Exception as e:
        print(f"❌ Assessment start error: {e}")
    
    print()
    print("🔍 LIKELY CAUSES OF 500 ERROR:")
    print("1. Database connection issues (most common)")
    print("2. Missing DATABASE_URL environment variable")
    print("3. Database tables not created")
    print("4. Missing required environment variables")
    print("5. Import errors in Python modules")
    print()
    
    print("🛠️ RECOMMENDED FIXES:")
    print("1. Check Railway logs for detailed error messages")
    print("2. Verify DATABASE_URL is set in Railway environment")
    print("3. Ensure database tables are created")
    print("4. Check all required environment variables are set")
    print()
    
    print("📋 REQUIRED RAILWAY ENVIRONMENT VARIABLES:")
    print("   DATABASE_URL = (Railway PostgreSQL connection string)")
    print("   ENVIRONMENT = production")
    print("   RAILWAY_ENVIRONMENT = production")
    print("   FRONTEND_URL = https://unitas.up.railway.app")

def main():
    """Main function"""
    diagnose_railway_500()

if __name__ == "__main__":
    main()