#!/usr/bin/env python3
"""
Test CDP REST API integration with MCP server
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

class CDPRestIntegrationTester:
    """Test CDP REST API integration with MCP server."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or '../config/kafka_config.yaml'
        self.server = None
        self.test_results = {}
    
    async def initialize_server(self) -> bool:
        """Initialize the MCP server."""
        try:
            print("🔧 Initializing MCP server with CDP REST API integration...")
            self.server = CDFKafkaMCPServer(self.config_path)
            print("✅ MCP server initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize MCP server: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test connection via CDP REST API."""
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
        """Test listing topics via CDP REST API."""
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
    
    async def test_create_topic(self) -> bool:
        """Test creating a topic via CDP REST API."""
        print("\n🔍 Test 3: Create Topic")
        try:
            topic_name = f"cdp-rest-test-topic-{int(time.time())}"
            request = CallToolRequest(params={
                'name': 'create_topic',
                'arguments': {
                    'name': topic_name,
                    'partitions': 1,
                    'replication_factor': 1,
                    'method': 'cdp_rest'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            success = 'error' not in data
            print(f"   Topic: {topic_name}")
            print(f"   Success: {success}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            self.test_results['create_topic'] = success
            return success
            
        except Exception as e:
            print(f"❌ Create topic test failed: {e}")
            self.test_results['create_topic'] = False
            return False
    
    async def test_produce_message(self) -> bool:
        """Test producing a message via CDP REST API."""
        print("\n🔍 Test 4: Produce Message")
        try:
            topic_name = f"cdp-rest-test-topic-{int(time.time())}"
            request = CallToolRequest(params={
                'name': 'produce_message',
                'arguments': {
                    'topic': topic_name,
                    'key': 'test-key',
                    'value': 'Hello from CDP REST API!',
                    'method': 'cdp_rest'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            success = 'error' not in data
            print(f"   Topic: {topic_name}")
            print(f"   Success: {success}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            self.test_results['produce_message'] = success
            return success
            
        except Exception as e:
            print(f"❌ Produce message test failed: {e}")
            self.test_results['produce_message'] = False
            return False
    
    async def test_connector_operations(self) -> bool:
        """Test connector operations via CDP REST API."""
        print("\n🔍 Test 5: Connector Operations")
        try:
            # Test list connectors
            request = CallToolRequest(params={
                'name': 'list_connectors',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            connectors = data.get('connectors', [])
            print(f"   Connectors found: {len(connectors)}")
            print(f"   Method: {data.get('method', 'Unknown')}")
            
            self.test_results['connector_operations'] = True
            return True
            
        except Exception as e:
            print(f"❌ Connector operations test failed: {e}")
            self.test_results['connector_operations'] = False
            return False
    
    async def test_health_status(self) -> bool:
        """Test health status via CDP REST API."""
        print("\n🔍 Test 6: Health Status")
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
    
    async def test_endpoint_discovery(self) -> bool:
        """Test endpoint discovery via CDP REST API."""
        print("\n🔍 Test 7: Endpoint Discovery")
        try:
            # Test CDP connection
            request = CallToolRequest(params={
                'name': 'test_cdp_connection',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            connected = data.get('connected', False)
            print(f"   CDP Connected: {connected}")
            print(f"   Message: {data.get('message', 'No message')}")
            
            self.test_results['endpoint_discovery'] = connected
            return connected
            
        except Exception as e:
            print(f"❌ Endpoint discovery test failed: {e}")
            self.test_results['endpoint_discovery'] = False
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all CDP REST API integration tests."""
        print("🚀 CDP REST API Integration Test Suite")
        print("=" * 60)
        
        # Initialize server
        if not await self.initialize_server():
            print("❌ Cannot proceed without MCP server initialization")
            return self.test_results
        
        # Run all tests
        tests = [
            self.test_connection,
            self.test_list_topics,
            self.test_create_topic,
            self.test_produce_message,
            self.test_connector_operations,
            self.test_health_status,
            self.test_endpoint_discovery
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
        print("📊 CDP REST API INTEGRATION TEST RESULTS")
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
        
        print("\n🔧 Recommendations:")
        if failed_tests > 0:
            print("1. Check CDP REST API endpoints are accessible")
            print("2. Verify authentication credentials")
            print("3. Ensure CDP services are properly configured")
            print("4. Review CDP REST API documentation")
        else:
            print("1. All tests passed! CDP REST API integration is working")
            print("2. You can now use the MCP server for CDP Cloud operations")
            print("3. Monitor service health regularly")

async def main():
    """Main function to run CDP REST API integration tests."""
    tester = CDPRestIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
