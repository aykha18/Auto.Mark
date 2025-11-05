#!/usr/bin/env python3
"""
Debug configuration loading with fresh import
"""

import os

# Set environment variables BEFORE importing
os.environ["WISE_API_KEY"] = "edcc89bf-3ecf-40c9-9686-8f4c90426038"
os.environ["WISE_PROFILE_ID"] = "test_profile_123"
os.environ["WISE_ENVIRONMENT"] = "sandbox"

print("🔍 Environment Variables (before import):")
print(f"   WISE_API_KEY: {os.getenv('WISE_API_KEY')}")
print(f"   WISE_PROFILE_ID: {os.getenv('WISE_PROFILE_ID')}")
print(f"   WISE_ENVIRONMENT: {os.getenv('WISE_ENVIRONMENT')}")

# Now import and test
from app.core.config import WiseSettings

print("\n🔧 Direct WiseSettings:")
wise_settings = WiseSettings()
print(f"   API Key: '{wise_settings.api_key}'")
print(f"   Profile ID: '{wise_settings.profile_id}'")
print(f"   Environment: '{wise_settings.environment}'")

print("\n🔧 Fresh WiseSettings with explicit env:")
wise_settings2 = WiseSettings(
    api_key=os.getenv("WISE_API_KEY", ""),
    profile_id=os.getenv("WISE_PROFILE_ID", ""),
    environment=os.getenv("WISE_ENVIRONMENT", "sandbox")
)
print(f"   API Key: '{wise_settings2.api_key}'")
print(f"   Profile ID: '{wise_settings2.profile_id}'")
print(f"   Environment: '{wise_settings2.environment}'")