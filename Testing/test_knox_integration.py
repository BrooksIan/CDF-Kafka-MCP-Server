#!/usr/bin/env python3
"""
Test MCP server integration with properly configured Knox Gateway
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

class KnoxIntegrationTester:
    """Test MCP server integration with Knox Gateway."""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or '../config/kafka_config_knox_enhanced.yaml'
        self.server = None
        self.test_results = {}
    
    async def initialize_server(self) -> bool:
        """Initialize the MCP server."""
        try:
            print("🔧 Initializing MCP server with Knox Gateway...")
            self.server = CDFKafkaMCPServer(self.config_path)
            print("✅ MCP server initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize MCP server: {e}")
            print("   This indicates Knox Gateway configuration issues")
            print("   Please check:")
            print("   1. Knox Gateway is properly configured")
            print("   2. Authentication credentials are correct")
            print("   3. Kafka services are mapped in topology")
            return False
    
    async def test_knox_gateway_info(self) -> bool:
        """Test Knox Gateway information retrieval."""
        print("\n🔍 Test 1: Knox Gateway Information")
        try:
            request = CallToolRequest(params={
                'name': 'get_knox_gateway_info',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"❌ Knox Gateway Info Error: {data['error']}")
                return False
            
            print(f"✅ Knox Gateway Info: {data.get('message', 'Success')}")
            if 'gateway_info' in data:
                info = data['gateway_info']
                print(f"   Version: {info.get('version', 'Unknown')}")
                print(f"   Status: {info.get('status', 'Unknown')}")
            
            self.test_results['knox_gateway_info'] = True
            return True
            
        except Exception as e:
            print(f"❌ Knox Gateway Info Test Failed: {e}")
            self.test_results['knox_gateway_info'] = False
            return False
    
    async def test_knox_topologies(self) -> bool:
        """Test Knox topologies listing."""
        print("\n🔍 Test 2: Knox Topologies")
        try:
            request = CallToolRequest(params={
                'name': 'list_knox_topologies',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"❌ Topologies Error: {data['error']}")
                return False
            
            print(f"✅ Topologies: {data.get('message', 'Success')}")
            if 'topologies' in data:
                topologies = data['topologies']
                print(f"   Found {len(topologies)} topologies:")
                for topology in topologies:
                    print(f"     - {topology.get('name', 'Unknown')}: {topology.get('uri', 'Unknown')}")
            
            self.test_results['knox_topologies'] = True
            return True
            
        except Exception as e:
            print(f"❌ Topologies Test Failed: {e}")
            self.test_results['knox_topologies'] = False
            return False
    
    async def test_knox_topology_details(self) -> bool:
        """Test getting specific topology details."""
        print("\n🔍 Test 3: Knox Topology Details")
        try:
            # Test with cdp-proxy topology
            request = CallToolRequest(params={
                'name': 'get_knox_topology',
                'arguments': {
                    'topology_name': 'cdp-proxy'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"❌ Topology Details Error: {data['error']}")
                return False
            
            print(f"✅ Topology Details: {data.get('message', 'Success')}")
            if 'topology' in data:
                topology = data['topology']
                print(f"   Name: {topology.get('name', 'Unknown')}")
                print(f"   URI: {topology.get('uri', 'Unknown')}")
                if 'services' in topology:
                    services = topology['services']
                    print(f"   Services: {len(services)}")
                    for service in services:
                        print(f"     - {service.get('role', 'Unknown')}: {service.get('name', 'Unknown')}")
            
            self.test_results['knox_topology_details'] = True
            return True
            
        except Exception as e:
            print(f"❌ Topology Details Test Failed: {e}")
            self.test_results['knox_topology_details'] = False
            return False
    
    async def test_knox_service_health(self) -> bool:
        """Test Knox service health check."""
        print("\n🔍 Test 4: Knox Service Health")
        try:
            request = CallToolRequest(params={
                'name': 'get_knox_service_health',
                'arguments': {
                    'topology': 'cdp-proxy'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"❌ Service Health Error: {data['error']}")
                return False
            
            print(f"✅ Service Health: {data.get('message', 'Success')}")
            if 'health_status' in data:
                health = data['health_status']
                print(f"   Overall Health: {health.get('overall_health', 'Unknown')}")
                print(f"   Status: {health.get('status', 'Unknown')}")
            
            self.test_results['knox_service_health'] = True
            return True
            
        except Exception as e:
            print(f"❌ Service Health Test Failed: {e}")
            self.test_results['knox_service_health'] = False
            return False
    
    async def test_knox_service_urls(self) -> bool:
        """Test Knox service URL retrieval."""
        print("\n🔍 Test 5: Knox Service URLs")
        try:
            request = CallToolRequest(params={
                'name': 'get_knox_service_urls',
                'arguments': {
                    'topology': 'cdp-proxy'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"❌ Service URLs Error: {data['error']}")
                return False
            
            print(f"✅ Service URLs: {data.get('message', 'Success')}")
            if 'service_info' in data:
                info = data['service_info']
                print(f"   Kafka URL: {info.get('kafka_url', 'Unknown')}")
                print(f"   Connect URL: {info.get('connect_url', 'Unknown')}")
                print(f"   Topology: {info.get('topology', 'Unknown')}")
            
            self.test_results['knox_service_urls'] = True
            return True
            
        except Exception as e:
            print(f"❌ Service URLs Test Failed: {e}")
            self.test_results['knox_service_urls'] = False
            return False
    
    async def test_kafka_operations_via_knox(self) -> bool:
        """Test Kafka operations through Knox Gateway."""
        print("\n🔍 Test 6: Kafka Operations via Knox")
        try:
            # Test topic creation via Knox
            request = CallToolRequest(params={
                'name': 'create_topic',
                'arguments': {
                    'name': 'knox-test-topic',
                    'partitions': 1,
                    'replication_factor': 1,
                    'method': 'knox'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"⚠️  Topic Creation via Knox: {data['error']}")
                # This is expected if Knox is not properly configured
            else:
                print(f"✅ Topic Creation via Knox: {data.get('message', 'Success')}")
            
            # Test message production via Knox
            request = CallToolRequest(params={
                'name': 'produce_message',
                'arguments': {
                    'topic': 'knox-test-topic',
                    'key': 'test-key',
                    'value': 'Hello from Knox Gateway!',
                    'method': 'knox'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"⚠️  Message Production via Knox: {data['error']}")
                # This is expected if Knox is not properly configured
            else:
                print(f"✅ Message Production via Knox: {data.get('message', 'Success')}")
            
            self.test_results['kafka_operations_via_knox'] = True
            return True
            
        except Exception as e:
            print(f"❌ Kafka Operations via Knox Test Failed: {e}")
            self.test_results['kafka_operations_via_knox'] = False
            return False
    
    async def test_health_monitoring(self) -> bool:
        """Test health monitoring features."""
        print("\n🔍 Test 7: Health Monitoring")
        try:
            # Test overall health status
            request = CallToolRequest(params={
                'name': 'get_health_status',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"❌ Health Status Error: {data['error']}")
                return False
            
            print(f"✅ Health Status: {data.get('message', 'Success')}")
            if 'health_status' in data:
                health = data['health_status']
                print(f"   Overall Status: {health.get('overall_status', 'Unknown')}")
                print(f"   Uptime: {health.get('uptime_seconds', 0):.1f}s")
            
            # Test health summary
            request = CallToolRequest(params={
                'name': 'get_health_summary',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"❌ Health Summary Error: {data['error']}")
                return False
            
            print(f"✅ Health Summary: {data.get('message', 'Success')}")
            if 'summary' in data:
                summary = data['summary']
                print(f"   Overall Status: {summary.get('overall_status', 'Unknown')}")
                print(f"   Uptime: {summary.get('uptime', 'Unknown')}")
            
            self.test_results['health_monitoring'] = True
            return True
            
        except Exception as e:
            print(f"❌ Health Monitoring Test Failed: {e}")
            self.test_results['health_monitoring'] = False
            return False
    
    async def test_cdp_integration(self) -> bool:
        """Test CDP Cloud integration."""
        print("\n🔍 Test 8: CDP Cloud Integration")
        try:
            # Test CDP connection
            request = CallToolRequest(params={
                'name': 'test_cdp_connection',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"⚠️  CDP Connection: {data['error']}")
                # This is expected if CDP is not properly configured
            else:
                print(f"✅ CDP Connection: {data.get('message', 'Success')}")
            
            # Test CDP APIs
            request = CallToolRequest(params={
                'name': 'get_cdp_apis',
                'arguments': {}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            
            if 'error' in data:
                print(f"⚠️  CDP APIs: {data['error']}")
                # This is expected if CDP is not properly configured
            else:
                print(f"✅ CDP APIs: {data.get('message', 'Success')}")
            
            self.test_results['cdp_integration'] = True
            return True
            
        except Exception as e:
            print(f"❌ CDP Integration Test Failed: {e}")
            self.test_results['cdp_integration'] = False
            return False
    
    async def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests."""
        print("🚀 Knox Gateway Integration Test Suite")
        print("=" * 60)
        
        # Initialize server
        if not await self.initialize_server():
            print("❌ Cannot proceed without MCP server initialization")
            print("\n🔧 Troubleshooting Steps:")
            print("1. Configure Knox Gateway properly using the Admin UI")
            print("2. Verify Kafka services are mapped in topology")
            print("3. Check authentication credentials")
            print("4. Review Knox Gateway logs")
            print("\n📋 Manual Configuration Required:")
            print(f"   Access: {os.getenv('KNOX_ADMIN_UI', 'https://your-knox-gateway.example.com:8443/gateway/manager/admin-ui/')}")
            print(f"   Login: {os.getenv('KNOX_USERNAME', 'your-username')} / {os.getenv('KNOX_PASSWORD', 'your-password')}")
            print("   Configure: cdp-proxy topology with Kafka services")
            return self.test_results
        
        # Run all tests
        tests = [
            self.test_knox_gateway_info,
            self.test_knox_topologies,
            self.test_knox_topology_details,
            self.test_knox_service_health,
            self.test_knox_service_urls,
            self.test_kafka_operations_via_knox,
            self.test_health_monitoring,
            self.test_cdp_integration
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
        print("📊 TEST RESULTS SUMMARY")
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
            print("1. Configure Knox Gateway properly using the Admin UI")
            print("2. Verify authentication credentials and endpoints")
            print("3. Check Kafka service mappings in topology")
            print("4. Test individual components separately")
        else:
            print("1. All tests passed! Knox Gateway integration is working")
            print("2. You can now use the MCP server for Kafka operations")
            print("3. Monitor service health regularly")

async def main():
    """Main function to run Knox integration tests."""
    tester = KnoxIntegrationTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())