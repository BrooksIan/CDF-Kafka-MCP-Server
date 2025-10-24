#!/usr/bin/env python3
"""
Test CDP Authentication Mechanisms
"""

import asyncio
import sys
import os
import json
import time
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.cdp_auth import CDPAuthenticator, AuthCredentials, AuthMethod, CDPAuthManager
from cdf_kafka_mcp_server.cdp_rest_client import CDPRestClient
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

class CDPAuthenticationTester:
    """Test CDP authentication mechanisms."""
    
    def __init__(self):
        self.base_url = "https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443"
        self.username = "ibrooks"
        self.password = "Admin12345#"
        self.token = "eyJqa3UiOiJodHRwczovL2lyYi1rYWtmYS1vbmx5LW1hc3RlcjAuY2dzaS1kZW0ucHJlcC1qMXRrLmEzLmNsb3VkZXJhLnNpdGUvaXJiLWtha2ZhLW9ubHkvaG9tZXBhZ2Uva25veHRva2VuL2FwaS92Mi9qd2tzLmpzb24iLCJraWQiOiJYa1JVQTczLUtwNGs2MVVKSGsxZUJDRGhOeVhwRDdEbUVaQUJ1dnM2cjlRIiwidHlwIjoiSldUIiwiYWxnIjoiUlMyNTYifQ.eyJzdWIiOiJpYnJvb2tzIiwiYXVkIjoiY2RwLXByb3h5LXRva2VuIiwiamt1IjoiaHR0cHM6Ly9pcmIta2FrZmEtb25seS1tYXN0ZXIwLmNnc2ktZGVtLnByZXAtajF0ay5hMy5jbG91ZGVyYS5zaXRlL2lyYi1rYWtmYS1vbmx5L2hvbWVwYWdlL2tub3h0b2tlbi9hcGkvdjIvandrcy5qc29uIiwia2lkIjoiWGtSVUE3My1LcDRrNjFVSGhrMWVCQ0RoTnlYcEQ3RG1FWkFCdXZzNnI5USIsImlzcyI6IktOT1hTU08iLCJleHAiOjE3NjEzNTA5ODMsIm1hbmFnZWQudG9rZW4iOiJ0cnVlIiwia25veC5pZCI6IjdiNTYwZWMxLTRiMjgtNGNlMS05Y2VhLWQ4ODQ5MTA1ZjgzMiJ9.NB_nXwD4xUCAiEFqE7kF_ml3TOS0GzAsTzWtUVYyaEzxr0SI1mucvtTAQL4BrO9iHjl3y8OA19At2lH255A_6NsU1oki2VJWPzdZTLjDYHZtng3YATnc-wd3rFrGXVYFZAIjLdwBpV450ts-axhwssafEbm247MPuBUsCPNREz-NURfdEErt8hzTBIKbo_FoTlYkt-OQ8jMuU6VealOACgvxlLr4BXdN_1iq9OuQ_JxbnvoH1ekRMBuBmrbapAyGmcP_qmHOVbPFErQtVzrv5D_po2LOaxAp2Szk2oiU2KpiV4ffSD1GGvvey3R-sUzh7vI-sPJq1vkpufEg4bmzqA"
        self.test_results = {}
    
    def test_basic_authentication(self) -> bool:
        """Test basic authentication."""
        print("\n🔍 Test 1: Basic Authentication")
        try:
            credentials = AuthCredentials(
                username=self.username,
                password=self.password
            )
            
            authenticator = CDPAuthenticator(
                base_url=self.base_url,
                credentials=credentials,
                verify_ssl=False
            )
            
            result = authenticator.authenticate(AuthMethod.BASIC)
            print(f"   Status: Authenticated")
            print(f"   Token Type: {result.token_type}")
            print(f"   Expires At: {result.expires_at}")
            
            # Test authentication
            auth_test = authenticator.test_authentication()
            print(f"   Auth Test: {auth_test.get('authenticated', False)}")
            print(f"   Method: {auth_test.get('method', 'unknown')}")
            
            self.test_results['basic_auth'] = auth_test.get('authenticated', False)
            return auth_test.get('authenticated', False)
            
        except Exception as e:
            print(f"❌ Basic authentication failed: {e}")
            self.test_results['basic_auth'] = False
            return False
    
    def test_bearer_token_authentication(self) -> bool:
        """Test bearer token authentication."""
        print("\n🔍 Test 2: Bearer Token Authentication")
        try:
            credentials = AuthCredentials(
                username=self.username,
                password=self.password,
                token=self.token
            )
            
            authenticator = CDPAuthenticator(
                base_url=self.base_url,
                credentials=credentials,
                verify_ssl=False
            )
            
            result = authenticator.authenticate(AuthMethod.BEARER_TOKEN)
            print(f"   Status: Authenticated")
            print(f"   Token Type: {result.token_type}")
            print(f"   Expires At: {result.expires_at}")
            
            # Test authentication
            auth_test = authenticator.test_authentication()
            print(f"   Auth Test: {auth_test.get('authenticated', False)}")
            print(f"   Method: {auth_test.get('method', 'unknown')}")
            
            self.test_results['bearer_token'] = auth_test.get('authenticated', False)
            return auth_test.get('authenticated', False)
            
        except Exception as e:
            print(f"❌ Bearer token authentication failed: {e}")
            self.test_results['bearer_token'] = False
            return False
    
    def test_knox_token_authentication(self) -> bool:
        """Test Knox token authentication."""
        print("\n🔍 Test 3: Knox Token Authentication")
        try:
            credentials = AuthCredentials(
                username=self.username,
                password=self.password,
                token=self.token
            )
            
            authenticator = CDPAuthenticator(
                base_url=self.base_url,
                credentials=credentials,
                verify_ssl=False
            )
            
            result = authenticator.authenticate(AuthMethod.KNOX_TOKEN)
            print(f"   Status: Authenticated")
            print(f"   Token Type: {result.token_type}")
            print(f"   Expires At: {result.expires_at}")
            
            # Test authentication
            auth_test = authenticator.test_authentication()
            print(f"   Auth Test: {auth_test.get('authenticated', False)}")
            print(f"   Method: {auth_test.get('method', 'unknown')}")
            
            self.test_results['knox_token'] = auth_test.get('authenticated', False)
            return auth_test.get('authenticated', False)
            
        except Exception as e:
            print(f"❌ Knox token authentication failed: {e}")
            self.test_results['knox_token'] = False
            return False
    
    def test_auto_detection(self) -> bool:
        """Test automatic authentication method detection."""
        print("\n🔍 Test 4: Auto Detection")
        try:
            credentials = AuthCredentials(
                username=self.username,
                password=self.password,
                token=self.token
            )
            
            authenticator = CDPAuthenticator(
                base_url=self.base_url,
                credentials=credentials,
                verify_ssl=False
            )
            
            result = authenticator.authenticate()  # Auto-detect
            print(f"   Status: Authenticated")
            print(f"   Detected Method: {authenticator._auth_method}")
            print(f"   Token Type: {result.token_type}")
            
            # Test authentication
            auth_test = authenticator.test_authentication()
            print(f"   Auth Test: {auth_test.get('authenticated', False)}")
            print(f"   Method: {auth_test.get('method', 'unknown')}")
            
            self.test_results['auto_detection'] = auth_test.get('authenticated', False)
            return auth_test.get('authenticated', False)
            
        except Exception as e:
            print(f"❌ Auto detection failed: {e}")
            self.test_results['auto_detection'] = False
            return False
    
    def test_auth_endpoint_discovery(self) -> bool:
        """Test authentication endpoint discovery."""
        print("\n🔍 Test 5: Auth Endpoint Discovery")
        try:
            credentials = AuthCredentials(
                username=self.username,
                password=self.password
            )
            
            authenticator = CDPAuthenticator(
                base_url=self.base_url,
                credentials=credentials,
                verify_ssl=False
            )
            
            endpoints = authenticator.discover_auth_endpoints()
            print(f"   Endpoints discovered: {len(endpoints)}")
            
            available_endpoints = [name for name, info in endpoints.items() if info.get('available')]
            print(f"   Available endpoints: {len(available_endpoints)}")
            
            for name, info in endpoints.items():
                if info.get('available'):
                    print(f"     {name}: {info.get('status_code')} ({info.get('content_type')})")
            
            self.test_results['endpoint_discovery'] = len(available_endpoints) > 0
            return len(available_endpoints) > 0
            
        except Exception as e:
            print(f"❌ Endpoint discovery failed: {e}")
            self.test_results['endpoint_discovery'] = False
            return False
    
    def test_cdp_rest_client_auth(self) -> bool:
        """Test CDP REST client with authentication."""
        print("\n🔍 Test 6: CDP REST Client Authentication")
        try:
            client = CDPRestClient(
                base_url=self.base_url,
                username=self.username,
                password=self.password,
                token=self.token,
                verify_ssl=False
            )
            
            # Test connection
            connection_result = client.test_connection()
            print(f"   Connection: {connection_result.get('status')}")
            print(f"   Message: {connection_result.get('message')}")
            print(f"   Auth Method: {connection_result.get('auth_method')}")
            
            # Test authentication
            auth_result = client.test_authentication()
            print(f"   Auth Test: {auth_result.get('authenticated', False)}")
            print(f"   Method: {auth_result.get('method', 'unknown')}")
            
            self.test_results['cdp_rest_client'] = auth_result.get('authenticated', False)
            return auth_result.get('authenticated', False)
            
        except Exception as e:
            print(f"❌ CDP REST client authentication failed: {e}")
            self.test_results['cdp_rest_client'] = False
            return False
    
    def test_auth_manager(self) -> bool:
        """Test CDP authentication manager."""
        print("\n🔍 Test 7: CDP Auth Manager")
        try:
            credentials = AuthCredentials(
                username=self.username,
                password=self.password,
                token=self.token
            )
            
            manager = CDPAuthManager(
                base_url=self.base_url,
                credentials=credentials,
                verify_ssl=False
            )
            
            # Test all services
            service_results = manager.test_all_services()
            print(f"   Services tested: {len(service_results)}")
            
            authenticated_services = [name for name, result in service_results.items() if result.get('authenticated')]
            print(f"   Authenticated services: {len(authenticated_services)}")
            
            for service, result in service_results.items():
                status = "✅" if result.get('authenticated') else "❌"
                method = result.get('method', 'unknown')
                print(f"     {service}: {status} ({method})")
            
            self.test_results['auth_manager'] = len(authenticated_services) > 0
            return len(authenticated_services) > 0
            
        except Exception as e:
            print(f"❌ Auth manager test failed: {e}")
            self.test_results['auth_manager'] = False
            return False
    
    async def test_mcp_server_auth(self) -> bool:
        """Test MCP server with enhanced authentication."""
        print("\n🔍 Test 8: MCP Server Authentication")
        try:
            # Test with optimized configuration
            server = CDFKafkaMCPServer('../config/kafka_config_cdp_optimized.yaml')
            
            # Test connection
            request = CallToolRequest(params={
                'name': 'test_connection',
                'arguments': {}
            })
            result = await server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            print(f"   Connection: {data.get('connected', False)}")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Method: {data.get('method', 'unknown')}")
            
            # Test authentication if available
            if hasattr(server, 'cdp_rest_client') and server.cdp_rest_client:
                auth_result = server.cdp_rest_client.test_authentication()
                print(f"   Auth Test: {auth_result.get('authenticated', False)}")
                print(f"   Auth Method: {auth_result.get('method', 'unknown')}")
                
                self.test_results['mcp_server'] = auth_result.get('authenticated', False)
                return auth_result.get('authenticated', False)
            else:
                print("   No CDP REST client available")
                self.test_results['mcp_server'] = False
                return False
            
        except Exception as e:
            print(f"❌ MCP server authentication test failed: {e}")
            self.test_results['mcp_server'] = False
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all authentication tests."""
        print("🚀 CDP Authentication Test Suite")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_basic_authentication,
            self.test_bearer_token_authentication,
            self.test_knox_token_authentication,
            self.test_auto_detection,
            self.test_auth_endpoint_discovery,
            self.test_cdp_rest_client_auth,
            self.test_auth_manager,
            self.test_mcp_server_auth
        ]
        
        for test in tests:
            try:
                if asyncio.iscoroutinefunction(test):
                    await test()
                else:
                    test()
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Print summary
        self.print_test_summary()
        
        return self.test_results
    
    def print_test_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("📊 CDP AUTHENTICATION TEST RESULTS")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        print("\n🔧 Authentication Methods Tested:")
        print("  - Basic Authentication (username/password)")
        print("  - Bearer Token Authentication")
        print("  - Knox Token Authentication")
        print("  - Auto Detection")
        print("  - Endpoint Discovery")
        print("  - CDP REST Client Integration")
        print("  - Auth Manager (Multi-service)")
        print("  - MCP Server Integration")
        
        print("\n🎯 Next Steps:")
        if passed_tests > 0:
            print("1. Some authentication methods are working")
            print("2. Use the working authentication method for production")
            print("3. Configure MCP server with the best authentication method")
        else:
            print("1. All authentication methods failed")
            print("2. Check CDP service configuration")
            print("3. Verify credentials and network connectivity")
            print("4. Review CDP authentication documentation")

async def main():
    """Main function to run CDP authentication tests."""
    tester = CDPAuthenticationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
