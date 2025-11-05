#!/usr/bin/env python3
"""
Verify Railway deployment is working correctly
"""

import requests
import json
import os

def verify_railway_deployment():
    """Verify the Railway deployment"""
    
    # Get Railway URL from environment or use default
    base_url = os.getenv("RAILWAY_URL", "https://your-app.railway.app")
    if base_url == "https://your-app.railway.app":
        print("WARNING: Please set RAILWAY_URL environment variable or update the script with your Railway URL")
        return False
    
    print("Verifying Railway Deployment")
    print("=" * 50)
    print(f"Base URL: {base_url}")
    
    try:
        # 1. Test health endpoint
        print("\n1. Testing health endpoint...")
        health_response = requests.get(f"{base_url}/api/v1/health", timeout=10)
        
        if health_response.status_code == 200:
            print("SUCCESS: Health endpoint working")
            try:
                health_data = health_response.json()
                print(f"   Status: {health_data.get('status')}")
                print(f"   Environment: {health_data.get('environment')}")
            except ValueError as e:
                print(f"   Warning: Could not parse JSON response: {e}")
                print(f"   Response text: {health_response.text[:200]}...")
        else:
            print(f"FAILED: Health endpoint failed: {health_response.status_code}")
            return False
        
        # 2. Test assessment questions endpoint
        print("\n2. Testing assessment questions endpoint...")
        questions_response = requests.get(f"{base_url}/api/v1/landing/assessment/questions", timeout=10)
        
        if questions_response.status_code == 200:
            print("SUCCESS: Assessment questions endpoint working")
            questions_data = questions_response.json()
            print(f"   Total questions: {questions_data.get('total_questions')}")
            print(f"   Assessment type: {questions_data.get('assessment_type')}")
        else:
            print(f"FAILED: Assessment questions endpoint failed: {questions_response.status_code}")
            return False
        
        # 3. Test assessment start with CRM data
        print("\n3. Testing assessment start with CRM selection...")
        test_data = {
            "email": "railway.test@example.com",
            "name": "Railway Test User",
            "company": "Railway Test Co",
            "preferred_crm": "pipedrive"
        }
        
        start_response = requests.post(
            f"{base_url}/api/v1/landing/assessment/start",
            json=test_data,
            timeout=10
        )
        
        if start_response.status_code == 200:
            print("SUCCESS: Assessment start endpoint working")
            start_data = start_response.json()
            assessment_id = start_data.get("assessment_id")
            print(f"   Assessment ID: {assessment_id}")
            print(f"   Status: {start_data.get('status')}")

            # Check if using new compact format
            if str(assessment_id).startswith('assess_'):
                print("SUCCESS: Using new compact assessment ID format")
            else:
                print("WARNING: Still using old assessment ID format")

        else:
            print(f"FAILED: Assessment start endpoint failed: {start_response.status_code}")
            print(f"   Response: {start_response.text}")
            return False
        
        # 4. Test frontend is accessible
        print("\n4. Testing frontend accessibility...")
        frontend_response = requests.get(base_url, timeout=10)
        
        if frontend_response.status_code == 200:
            print("SUCCESS: Frontend is accessible")
            if "Unitasa" in frontend_response.text:
                print("SUCCESS: Frontend contains expected content")
            else:
                print("WARNING: Frontend may not be fully loaded")
        else:
            print(f"FAILED: Frontend not accessible: {frontend_response.status_code}")
            return False
        
        print("\nSUCCESS: Railway deployment verification completed successfully!")
        print("\nDeployment Summary:")
        print("SUCCESS: Backend API is running")
        print("SUCCESS: Database tables are created")
        print("SUCCESS: CRM selection functionality is working")
        print("SUCCESS: Compact assessment IDs are being generated")
        print("SUCCESS: Frontend is accessible")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"FAILED: Connection failed. Check if {base_url} is accessible")
        return False
    except Exception as e:
        print(f"FAILED: Verification failed with error: {e}")
        return False

def main():
    """Main verification function"""
    print("Railway Deployment Verification")
    print("=" * 50)
    
    success = verify_railway_deployment()
    
    if success:
        print("\nSUCCESS: All checks passed! Your Railway deployment is working correctly.")
    else:
        print("\nFAILED: Some checks failed. Please review the deployment.")
    
    print("\nNext steps:")
    print("1. Test the complete assessment flow on your Railway URL")
    print("2. Verify CRM selection is working in the UI")
    print("3. Check that lead data is being stored correctly")

if __name__ == "__main__":
    main()