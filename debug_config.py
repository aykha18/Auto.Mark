#!/usr/bin/env python3
"""
Debug configuration loading
"""

import os
from app.core.config import get_settings

# Set environment variables
os.environ["WISE_API_KEY"] = "edcc89bf-3ecf-40c9-9686-8f4c90426038"
os.environ["WISE_PROFILE_ID"] = "test_profile_123"
os.environ["WISE_ENVIRONMENT"] = "sandbox"

print("🔍 Environment Variables:")
print(f"   WISE_API_KEY: {os.getenv('WISE_API_KEY')}")
print(f"   WISE_PROFILE_ID: {os.getenv('WISE_PROFILE_ID')}")
print(f"   WISE_ENVIRONMENT: {os.getenv('WISE_ENVIRONMENT')}")

print("\n🔧 Settings Object:")
settings = get_settings()
print(f"   Wise API Key: {settings.wise.api_key}")
print(f"   Wise Profile ID: {settings.wise.profile_id}")
print(f"   Wise Environment: {settings.wise.environment}")

print("\n📁 Direct OS Environment Check:")
print(f"   All env vars: {[k for k in os.environ.keys() if 'WISE' in k]}")