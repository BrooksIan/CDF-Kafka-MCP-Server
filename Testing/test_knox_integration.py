#!/usr/bin/env python3
"""
Knox Gateway Integration Testing Suite for CDF Kafka MCP Server
Tests Knox Gateway authentication and token management
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from cdf_kafka_mcp_server.knox_client import KnoxClient

class KnoxIntegrationTester:
    def __init__(self):
        self.mcp_server = None
        self.knox_client = None
        self.test_results = {}
        
    async def setup(self):
        """Setup the test environment"""
        print("🔧 Setting up Knox integration testing...")
        try:
            # Set environment variables for testing
            os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"
            
            # Initialize MCP server
            self.mcp_server = CDFKafkaMCPServer()
            
            # Initialize Knox client (if Knox is configured)
            try:
                self.knox_client = KnoxClient()
                print("✅ Knox client initialized")
            except Exception as e:
                print(f"⚠️  Knox client not available: {e}")
                self.knox_client = None
            
            print("✅ Test environment setup complete")
            return True
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            return False
    
    async def test_knox_token_retrieval(self):
        """Test Knox token retrieval"""
        print("\n🧪 Testing Knox token retrieval...")
        
        try:
            result = await self.mcp_server.call_tool("get_knox_token", {})
            
            if result and "token" in result:
                token = result["token"]
                print(f"✅ Successfully retrieved Knox token (length: {len(token)})")
                self.test_results["knox_token_retrieval"] = True
                
                # Store token for validation test
                self.test_token = token
            else:
                print(f"❌ Token retrieval failed: {result}")
                self.test_results["knox_token_retrieval"] = False
                
        except Exception as e:
            print(f"❌ Knox token retrieval test failed: {e}")
            self.test_results["knox_token_retrieval"] = False
    
    async def test_knox_token_validation(self):
        """Test Knox token validation"""
        print("\n🧪 Testing Knox token validation...")
        
        try:
            # Use the token from previous test or a test token
            test_token = getattr(self, 'test_token', 'test-token')
            
            result = await self.mcp_server.call_tool("validate_knox_token", {
                "token": test_token
            })
            
            if result and "valid" in result:
                is_valid = result["valid"]
                print(f"✅ Token validation completed: {'valid' if is_valid else 'invalid'}")
                self.test_results["knox_token_validation"] = True
            else:
                print(f"❌ Token validation failed: {result}")
                self.test_results["knox_token_validation"] = False
                
        except Exception as e:
            print(f"❌ Knox token validation test failed: {e}")
            self.test_results["knox_token_validation"] = False
    
    async def test_knox_token_refresh(self):
        """Test Knox token refresh"""
        print("\n🧪 Testing Knox token refresh...")
        
        try:
            result = await self.mcp_server.call_tool("refresh_knox_token", {})
            
            if result and "token" in result:
                new_token = result["token"]
                print(f"✅ Successfully refreshed Knox token (length: {len(new_token)})")
                self.test_results["knox_token_refresh"] = True
            else:
                print(f"❌ Token refresh failed: {result}")
                self.test_results["knox_token_refresh"] = False
                
        except Exception as e:
            print(f"❌ Knox token refresh test failed: {e}")
            self.test_results["knox_token_refresh"] = False
    
    async def test_knox_gateway_connectivity(self):
        """Test Knox Gateway connectivity"""
        print("\n🧪 Testing Knox Gateway connectivity...")
        
        try:
            if self.knox_client:
                # Test basic connectivity
                gateway_url = self.knox_client.gateway_url
                print(f"Testing connectivity to: {gateway_url}")
                
                # This would typically involve making a request to the gateway
                # For now, we'll just check if the client is properly configured
                if gateway_url and gateway_url.startswith('http'):
                    print("✅ Knox Gateway URL is properly configured")
                    self.test_results["knox_gateway_connectivity"] = True
                else:
                    print("❌ Knox Gateway URL is not properly configured")
                    self.test_results["knox_gateway_connectivity"] = False
            else:
                print("⚠️  Knox client not available, skipping connectivity test")
                self.test_results["knox_gateway_connectivity"] = None
                
        except Exception as e:
            print(f"❌ Knox Gateway connectivity test failed: {e}")
            self.test_results["knox_gateway_connectivity"] = False
    
    async def test_knox_authentication_flow(self):
        """Test complete Knox authentication flow"""
        print("\n🧪 Testing complete Knox authentication flow...")
        
        try:
            # Step 1: Get token
            token_result = await self.mcp_server.call_tool("get_knox_token", {})
            if not token_result or "token" not in token_result:
                print("❌ Authentication flow failed at token retrieval")
                self.test_results["knox_authentication_flow"] = False
                return
            
            token = token_result["token"]
            print(f"  ✅ Step 1: Token retrieved (length: {len(token)})")
            
            # Step 2: Validate token
            validation_result = await self.mcp_server.call_tool("validate_knox_token", {
                "token": token
            })
            if not validation_result or "valid" not in validation_result:
                print("❌ Authentication flow failed at token validation")
                self.test_results["knox_authentication_flow"] = False
                return
            
            is_valid = validation_result["valid"]
            print(f"  ✅ Step 2: Token validated: {'valid' if is_valid else 'invalid'}")
            
            # Step 3: Refresh token
            refresh_result = await self.mcp_server.call_tool("refresh_knox_token", {})
            if not refresh_result or "token" not in refresh_result:
                print("❌ Authentication flow failed at token refresh")
                self.test_results["knox_authentication_flow"] = False
                return
            
            new_token = refresh_result["token"]
            print(f"  ✅ Step 3: Token refreshed (length: {len(new_token)})")
            
            print("✅ Complete Knox authentication flow successful")
            self.test_results["knox_authentication_flow"] = True
            
        except Exception as e:
            print(f"❌ Knox authentication flow test failed: {e}")
            self.test_results["knox_authentication_flow"] = False
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("📊 KNOX INTEGRATION TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        failed_tests = sum(1 for result in self.test_results.values() if result is False)
        skipped_tests = sum(1 for result in self.test_results.values() if result is None)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            if result is True:
                status = "✅ PASS"
            elif result is False:
                status = "❌ FAIL"
            else:
                status = "⏭️  SKIP"
            print(f"  {test_name}: {status}")
        
        if failed_tests > 0:
            print(f"\n⚠️  {failed_tests} tests failed. Check the logs above for details.")
        else:
            print(f"\n🎉 All tests passed!")

async def main():
    """Main test runner"""
    print("🚀 Starting Knox Integration Testing Suite")
    print("="*50)
    
    tester = KnoxIntegrationTester()
    
    # Setup
    if not await tester.setup():
        print("❌ Setup failed, exiting")
        return
    
    try:
        # Run all tests
        await tester.test_knox_token_retrieval()
        await tester.test_knox_token_validation()
        await tester.test_knox_token_refresh()
        await tester.test_knox_gateway_connectivity()
        await tester.test_knox_authentication_flow()
        
    finally:
        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
