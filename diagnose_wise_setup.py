#!/usr/bin/env python3
"""
Diagnose Wise API setup issues
"""

import asyncio
import httpx
import os

async def diagnose_wise_setup():
    """Diagnose Wise API setup"""
    print("🔍 Wise API Setup Diagnosis")
    print("=" * 40)
    
    api_key = os.getenv("WISE_API_KEY", "edcc89bf-3ecf-40c9-9686-8f4c90426038")
    profile_id = os.getenv("WISE_PROFILE_ID", "16746958")
    
    print(f"📋 Current Configuration:")
    print(f"   API Key: {api_key[:8]}...{api_key[-4:] if len(api_key) > 12 else api_key}")
    print(f"   Profile ID: {profile_id}")
    print(f"   Key Length: {len(api_key)} characters")
    
    # Check API key format
    print(f"\n🔑 API Key Analysis:")
    if len(api_key) == 36 and api_key.count('-') == 4:
        print("   ✅ Format looks like UUID (correct format)")
    else:
        print("   ❌ Format doesn't match expected UUID format")
        print("   Expected: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    
    # Test different endpoints to identify the issue
    base_url = "https://api.sandbox.transferwise.tech"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Basic connectivity
        print(f"\n🌐 Testing Basic Connectivity...")
        try:
            response = await client.get(f"{base_url}/v1/currencies")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print("   ✅ Sandbox API is accessible")
            else:
                print(f"   ❌ API returned: {response.text[:200]}")
        except Exception as e:
            print(f"   ❌ Connection error: {e}")
        
        # Test 2: Authentication test
        print(f"\n🔐 Testing Authentication...")
        try:
            response = await client.get(f"{base_url}/v1/profiles", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                profiles = response.json()
                print(f"   ✅ Authentication successful!")
                print(f"   Found {len(profiles)} profiles:")
                for profile in profiles:
                    print(f"     - ID: {profile.get('id')}, Type: {profile.get('type')}")
                    if profile.get('id') == int(profile_id):
                        print(f"       ✅ Your profile ID {profile_id} is valid!")
            elif response.status_code == 401:
                error_data = response.json()
                print(f"   ❌ Authentication failed: {error_data.get('error_description', 'Invalid token')}")
                print(f"   🔧 Possible issues:")
                print(f"      - API key is invalid or expired")
                print(f"      - API key is for production, not sandbox")
                print(f"      - API key doesn't have required permissions")
            else:
                print(f"   ❌ Unexpected response: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Authentication test error: {e}")
        
        # Test 3: Profile-specific test
        print(f"\n👤 Testing Specific Profile Access...")
        try:
            response = await client.get(f"{base_url}/v1/profiles/{profile_id}", headers=headers)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                profile = response.json()
                print(f"   ✅ Profile access successful!")
                print(f"   Profile Type: {profile.get('type')}")
                print(f"   Profile Details: {profile.get('details', {})}")
            else:
                print(f"   ❌ Profile access failed: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Profile test error: {e}")
    
    print(f"\n💡 Recommendations:")
    print(f"   1. Verify your Wise account has API access enabled")
    print(f"   2. Check if your API token is specifically for sandbox")
    print(f"   3. Ensure your business profile is properly set up")
    print(f"   4. Contact Wise support if authentication continues to fail")
    
    print(f"\n📚 Useful Links:")
    print(f"   - Wise API Documentation: https://docs.wise.com/")
    print(f"   - Sandbox Environment: https://sandbox.transferwise.tech/")
    print(f"   - Developer Portal: https://wise.com/help/articles/2958229/")

if __name__ == "__main__":
    asyncio.run(diagnose_wise_setup())