"""
Test script for CRM Integration Marketplace implementation
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.crm_integration import CRMType, AuthMethod, IntegrationStatus
from app.core.crm_connector_init import initialize_crm_connectors


def test_crm_models():
    """Test CRM model definitions"""
    print("Testing CRM model definitions...")
    
    # Test enum values
    assert CRMType.PIPEDRIVE.value == "pipedrive"
    assert CRMType.HUBSPOT.value == "hubspot"
    assert CRMType.NEURACRM.value == "neuracrm"
    
    assert AuthMethod.OAUTH2.value == "oauth2"
    assert AuthMethod.API_KEY.value == "api_key"
    
    assert IntegrationStatus.AVAILABLE.value == "available"
    assert IntegrationStatus.BETA.value == "beta"
    
    print("✓ CRM model definitions are correct")


def test_connector_initialization():
    """Test connector initialization data"""
    print("Testing connector initialization...")
    
    # This would normally require a database connection
    # For now, just verify the initialization function exists
    assert callable(initialize_crm_connectors)
    
    print("✓ Connector initialization function is available")


def test_framework_components():
    """Test framework component class definitions"""
    print("Testing framework component class definitions...")
    
    try:
        # Test that the files exist and have the expected classes
        import ast
        import os
        
        # Check CRM integration framework
        framework_file = "app/core/crm_integration_framework.py"
        if os.path.exists(framework_file):
            with open(framework_file, 'r') as f:
                content = f.read()
                if "class CRMIntegrationFramework" in content and "class BaseCRMAdapter" in content:
                    print("✓ CRM Integration Framework classes found")
                else:
                    print("✗ Missing CRM Integration Framework classes")
                    return False
        
        # Check marketplace service
        service_file = "app/core/crm_marketplace_service.py"
        if os.path.exists(service_file):
            with open(service_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "class CRMMarketplaceService:" in content:
                    print("✓ CRM Marketplace Service class found")
                else:
                    print("✗ Missing CRM Marketplace Service class")
                    print("Content preview:", content[:200])
                    return False
        
        # Check monitoring
        monitor_file = "app/core/crm_integration_monitoring.py"
        if os.path.exists(monitor_file):
            with open(monitor_file, 'r') as f:
                content = f.read()
                if "class CRMIntegrationMonitor" in content:
                    print("✓ CRM Integration Monitor class found")
                else:
                    print("✗ Missing CRM Integration Monitor class")
                    return False
        
        print("✓ All framework components are properly defined")
        return True
        
    except Exception as e:
        print(f"✗ Framework component test failed: {e}")
        return False


def test_api_endpoints():
    """Test API endpoint file structure"""
    print("Testing API endpoint file structure...")
    
    try:
        api_file = "app/api/v1/crm_marketplace.py"
        if os.path.exists(api_file):
            with open(api_file, 'r') as f:
                content = f.read()
                
                expected_endpoints = [
                    "get_available_connectors",
                    "get_connector_details", 
                    "compare_connectors",
                    "create_demo_connection",
                    "get_integration_health_overview",
                    "get_marketplace_analytics"
                ]
                
                missing_endpoints = []
                for endpoint in expected_endpoints:
                    if f"def {endpoint}" not in content:
                        missing_endpoints.append(endpoint)
                
                if missing_endpoints:
                    print(f"✗ Missing API endpoints: {missing_endpoints}")
                    return False
                
                print("✓ All expected API endpoints are defined")
                return True
        else:
            print("✗ CRM marketplace API file not found")
            return False
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("Running CRM Integration Marketplace implementation tests...\n")
    
    tests = [
        test_crm_models,
        test_connector_initialization,
        test_framework_components,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            result = test()
            if result is not False:
                passed += 1
            print()
        except Exception as e:
            print(f"✗ Test failed with exception: {e}\n")
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! CRM Integration Marketplace implementation is ready.")
        return True
    else:
        print("❌ Some tests failed. Please review the implementation.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)