#!/usr/bin/env python3
"""
Diagnose 404 routing issue on Railway
"""

import requests
import json

def diagnose_404_routing():
    """Diagnose the 404 routing issue"""
    print("🔍 Railway 404 Routing Diagnosis")
    print("=" * 50)
    
    base_url = "https://unitas.up.railway.app"
    
    print("PROGRESS:")
    print("✅ CORS issue resolved")
    print("✅ 500 error resolved (now 404)")
    print("❌ 404 Not Found - routing issue")
    print()
    
    # Test main health endpoint
    print("1️⃣ Testing main health endpoint...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {health_response.status_code}")
        if health_response.status_code == 200:
            print("   ✅ Main health endpoint working")
        else:
            print(f"   ❌ Main health failed: {health_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Main health error: {e}")
    
    print()
    
    # Test landing health endpoint
    print("2️⃣ Testing landing health endpoint...")
    try:
        landing_health_response = requests.get(f"{base_url}/api/v1/landing/health", timeout=10)
        print(f"   Status: {landing_health_response.status_code}")
        if landing_health_response.status_code == 200:
            print("   ✅ Landing health endpoint working")
            data = landing_health_response.json()
            print(f"   Service: {data.get('service')}")
            print(f"   Router: {data.get('router')}")
            print(f"   Endpoints: {data.get('endpoints')}")
        else:
            print(f"   ❌ Landing health failed: {landing_health_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Landing health error: {e}")
    
    print()
    
    # Test new test endpoint
    print("3️⃣ Testing landing test endpoint...")
    try:
        test_response = requests.get(f"{base_url}/api/v1/landing/test", timeout=10)
        print(f"   Status: {test_response.status_code}")
        if test_response.status_code == 200:
            print("   ✅ Landing test endpoint working")
            data = test_response.json()
            print(f"   Message: {data.get('message')}")
        else:
            print(f"   ❌ Landing test failed: {test_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Landing test error: {e}")
    
    print()
    
    # Test assessment questions endpoint
    print("4️⃣ Testing assessment questions endpoint...")
    try:
        questions_response = requests.get(f"{base_url}/api/v1/landing/assessment/questions", timeout=10)
        print(f"   Status: {questions_response.status_code}")
        if questions_response.status_code == 200:
            print("   ✅ Assessment questions working")
            data = questions_response.json()
            print(f"   Total questions: {data.get('total_questions')}")
        else:
            print(f"   ❌ Assessment questions failed: {questions_response.text[:200]}")
    except Exception as e:
        print(f"   ❌ Assessment questions error: {e}")
    
    print()
    
    # Test the problematic assessment start endpoint
    print("5️⃣ Testing assessment start endpoint (the 404 issue)...")
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
        print(f"   Status: {start_response.status_code}")
        if start_response.status_code == 200:
            print("   ✅ Assessment start working!")
            data = start_response.json()
            print(f"   Assessment ID: {data.get('assessment_id')}")
        else:
            print(f"   ❌ Assessment start failed: {start_response.status_code}")
            print(f"   Response: {start_response.text[:300]}")
    except Exception as e:
        print(f"   ❌ Assessment start error: {e}")
    
    print()
    
    # Test alternative paths
    print("6️⃣ Testing alternative endpoint paths...")
    
    alternative_paths = [
        "/api/v1/landing_working/assessment/start",
        "/api/v1/landing_working/health",
        "/landing/assessment/start",
        "/assessment/start"
    ]
    
    for path in alternative_paths:
        try:
            alt_response = requests.get(f"{base_url}{path}", timeout=5)
            print(f"   {path}: {alt_response.status_code}")
        except:
            print(f"   {path}: Connection failed")
    
    print()
    print("🔍 POSSIBLE CAUSES:")
    print("1. Router not properly registered in main.py")
    print("2. Import issue with landing_working module")
    print("3. Route prefix mismatch")
    print("4. Railway deployment using wrong module")
    print("5. FastAPI route registration order issue")
    print()
    
    print("🛠️ NEXT STEPS:")
    print("1. Check Railway deployment logs")
    print("2. Verify which endpoints are actually available")
    print("3. Check if landing_working router is being loaded")
    print("4. Test the new /test endpoint to verify router")

def main():
    """Main function"""
    diagnose_404_routing()

if __name__ == "__main__":
    main()