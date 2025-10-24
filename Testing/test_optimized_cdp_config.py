#!/usr/bin/env python3
"""
Test optimized CDP configuration with MCP server
"""

import asyncio
import sys
import os
import json
import time
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

class OptimizedCDPConfigTester:
    """Test optimized CDP configuration with MCP server."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or '../config/kafka_config_cdp_optimized.yaml'
        self.server = None
        self.test_results = {}
    
    async def initialize_server(self) -> bool:
        """Initialize the MCP server with optimized configuration."""
        try:
            print("🔧 Initializing MCP server with optimized CDP configuration...")
            self.server = CDFKafkaMCPServer(self.config_path)
            print("✅ MCP server initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize MCP server: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test connection with optimized configuration."""
        print("\n🔍 Test 1: Connection Test")
        try:
            request = CallToolRequest(params={
                'name': 'test_connection',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            print(f"   Status: {data.get('connected', False)}")
            print(f"   Message: {data.get('message', 'No message')}")
            print(f"   Method: {data.get('method', 'Unknown')}")
            
            self.test_results['connection'] = data.get('connected', False)
            return data.get('connected', False)
            
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            self.test_results['connection'] = False
            return False
    
    async def test_list_topics(self) -> bool:
        """Test listing topics with optimized configuration."""
        print("\n🔍 Test 2: List Topics")
        try:
            request = CallToolRequest(params={
                'name': 'list_topics',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            topics = data.get('topics', [])
            count = data.get('count', 0)
            method = data.get('method', 'Unknown')
            
            print(f"   Topics found: {count}")
            print(f"   Method: {method}")
            if topics:
                print(f"   Topics: {topics[:5]}{'...' if len(topics) > 5 else ''}")
            
            self.test_results['list_topics'] = True
            return True
            
        except Exception as e:
            print(f"❌ List topics test failed: {e}")
            self.test_results['list_topics'] = False
            return False
    
    async def test_connector_operations(self) -> bool:
        """Test connector operations with optimized configuration."""
        print("\n🔍 Test 3: Connector Operations")
        try:
            # Test list connectors
            request = CallToolRequest(params={
                'name': 'list_connectors',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            connectors = data.get('connectors', [])
            method = data.get('method', 'Unknown')
            
            print(f"   Connectors found: {len(connectors)}")
            print(f"   Method: {method}")
            
            self.test_results['connector_operations'] = True
            return True
            
        except Exception as e:
            print(f"❌ Connector operations test failed: {e}")
            self.test_results['connector_operations'] = False
            return False
    
    async def test_health_status(self) -> bool:
        """Test health status with optimized configuration."""
        print("\n🔍 Test 4: Health Status")
        try:
            request = CallToolRequest(params={
                'name': 'get_health_status',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            overall_status = data.get('overall_status', 'unknown')
            services = data.get('services', {})
            
            print(f"   Overall Status: {overall_status}")
            print(f"   Services: {len(services)}")
            for service, status in services.items():
                print(f"     {service}: {status.get('status', 'unknown')}")
            
            self.test_results['health_status'] = overall_status in ['healthy', 'degraded']
            return True
            
        except Exception as e:
            print(f"❌ Health status test failed: {e}")
            self.test_results['health_status'] = False
            return False
    
    async def test_cdp_connection(self) -> bool:
        """Test CDP connection with optimized configuration."""
        print("\n🔍 Test 5: CDP Connection")
        try:
            request = CallToolRequest(params={
                'name': 'test_cdp_connection',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            connected = data.get('connected', False)
            print(f"   CDP Connected: {connected}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            self.test_results['cdp_connection'] = connected
            return connected
            
        except Exception as e:
            print(f"❌ CDP connection test failed: {e}")
            self.test_results['cdp_connection'] = False
            return False
    
    async def test_endpoint_discovery(self) -> bool:
        """Test endpoint discovery with optimized configuration."""
        print("\n🔍 Test 6: Endpoint Discovery")
        try:
            # Test if we can discover endpoints
            if hasattr(self.server, 'cdp_rest_client') and self.server.cdp_rest_client:
                endpoints = self.server.cdp_rest_client.discover_endpoints()
                print(f"   Endpoints discovered: {len(endpoints)}")
                for endpoint, info in endpoints.items():
                    print(f"     {endpoint}: {info.get('status', 'unknown')}")
                self.test_results['endpoint_discovery'] = True
                return True
            else:
                print("   No CDP REST client available")
                self.test_results['endpoint_discovery'] = False
                return False
                
        except Exception as e:
            print(f"❌ Endpoint discovery test failed: {e}")
            self.test_results['endpoint_discovery'] = False
            return False
    
    async def test_message_operations(self) -> bool:
        """Test message operations with optimized configuration."""
        print("\n🔍 Test 7: Message Operations")
        try:
            # Test produce message (this will likely fail but we can test the flow)
            topic_name = f"test-topic-{int(time.time())}"
            request = CallToolRequest(params={
                'name': 'produce_message',
                'arguments': {
                    'topic': topic_name,
                    'key': 'test-key',
                    'value': 'Hello from optimized CDP config!',
                    'method': 'cdp_rest'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            success = 'error' not in data
            print(f"   Topic: {topic_name}")
            print(f"   Success: {success}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            self.test_results['message_operations'] = success
            return success
            
        except Exception as e:
            print(f"❌ Message operations test failed: {e}")
            self.test_results['message_operations'] = False
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests with optimized configuration."""
        print("🚀 Optimized CDP Configuration Test Suite")
        print("=" * 60)
        
        # Initialize server
        if not await self.initialize_server():
            print("❌ Cannot proceed without MCP server initialization")
            return self.test_results
        
        # Run all tests
        tests = [
            self.test_connection,
            self.test_list_topics,
            self.test_connector_operations,
            self.test_health_status,
            self.test_cdp_connection,
            self.test_endpoint_discovery,
            self.test_message_operations
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                print(f"❌ Test failed with exception: {e}")
        
        # Print summary
        self.print_test_summary()
        
        return self.test_results
    
    def print_test_summary(self):
        """Print test results summary."""
        print("\n" + "=" * 60)
        print("📊 OPTIMIZED CDP CONFIGURATION TEST RESULTS")
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
        
        print("\n🔧 Configuration Status:")
        if hasattr(self.server, 'cdp_rest_client') and self.server.cdp_rest_client:
            print("  ✅ CDP REST client initialized")
        else:
            print("  ❌ CDP REST client not available")
        
        if hasattr(self.server, 'kafka_client') and self.server.kafka_client:
            print("  ✅ Kafka client initialized (fallback)")
        else:
            print("  ❌ Kafka client not available")
        
        print("\n🎯 Next Steps:")
        if passed_tests > 0:
            print("1. Some tests passed - configuration is partially working")
            print("2. Review failed tests and adjust configuration")
            print("3. Test with actual CDP services when available")
        else:
            print("1. All tests failed - review configuration")
            print("2. Check CDP service availability")
            print("3. Verify authentication credentials")
            print("4. Consider using fallback Kafka client")

async def main():
    """Main function to run optimized CDP configuration tests."""
    tester = OptimizedCDPConfigTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
