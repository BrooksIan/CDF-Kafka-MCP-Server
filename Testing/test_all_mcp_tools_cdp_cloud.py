#!/usr/bin/env python3
"""
Comprehensive MCP Tools Testing against CDP Cloud
Tests all available MCP tools with CDP cloud configuration
"""

import asyncio
import sys
import os
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

class CDPCloudMCPTester:
    """Comprehensive tester for all MCP tools against CDP Cloud."""
    
    def __init__(self, config_file: str = '../config/kafka_config_cdp_optimized.yaml'):
        """Initialize the tester."""
        self.config_file = config_file
        self.server = None
        self.test_results = {}
        self.start_time = time.time()
        
    async def initialize_server(self) -> bool:
        """Initialize the MCP server."""
        try:
            print("🔧 Initializing MCP server...")
            self.server = CDFKafkaMCPServer(self.config_file)
            print("✅ MCP server initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize MCP server: {e}")
            return False
    
    async def test_connection_tools(self) -> Dict[str, Any]:
        """Test connection-related tools."""
        print("\n🔍 Testing Connection Tools")
        print("=" * 50)
        
        results = {}
        
        # Test 1: test_connection
        try:
            print("Testing: test_connection")
            request = CallToolRequest(params={'name': 'test_connection', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['test_connection'] = {
                'success': data.get('connected', False),
                'message': data.get('message', 'No message'),
                'method': data.get('method', 'unknown'),
                'data': data
            }
            print(f"  ✅ test_connection: {data.get('connected', False)}")
        except Exception as e:
            results['test_connection'] = {'success': False, 'error': str(e)}
            print(f"  ❌ test_connection failed: {e}")
        
        # Test 2: get_health_status
        try:
            print("Testing: get_health_status")
            request = CallToolRequest(params={'name': 'get_health_status', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['get_health_status'] = {
                'success': data.get('overall_status') != 'unhealthy',
                'status': data.get('overall_status', 'unknown'),
                'data': data
            }
            print(f"  ✅ get_health_status: {data.get('overall_status', 'unknown')}")
        except Exception as e:
            results['get_health_status'] = {'success': False, 'error': str(e)}
            print(f"  ❌ get_health_status failed: {e}")
        
        return results
    
    async def test_topic_tools(self) -> Dict[str, Any]:
        """Test topic-related tools."""
        print("\n📋 Testing Topic Tools")
        print("=" * 50)
        
        results = {}
        
        # Test 1: list_topics
        try:
            print("Testing: list_topics")
            request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['list_topics'] = {
                'success': 'error' not in data,
                'topics': data.get('topics', []),
                'count': data.get('count', 0),
                'method': data.get('method', 'unknown'),
                'data': data
            }
            print(f"  ✅ list_topics: {data.get('count', 0)} topics found")
        except Exception as e:
            results['list_topics'] = {'success': False, 'error': str(e)}
            print(f"  ❌ list_topics failed: {e}")
        
        # Test 2: create_topic
        try:
            print("Testing: create_topic")
            topic_name = f"mcp-test-topic-{int(time.time())}"
            request = CallToolRequest(params={
                'name': 'create_topic',
                'arguments': {
                    'name': topic_name,
                    'partitions': 1,
                    'replication_factor': 1
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['create_topic'] = {
                'success': 'error' not in data,
                'topic': topic_name,
                'data': data
            }
            print(f"  ✅ create_topic: {topic_name}")
        except Exception as e:
            results['create_topic'] = {'success': False, 'error': str(e)}
            print(f"  ❌ create_topic failed: {e}")
        
        # Test 3: get_topic_info
        try:
            print("Testing: get_topic_info")
            request = CallToolRequest(params={
                'name': 'get_topic_info',
                'arguments': {'topic': 'mcptesttopic'}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['get_topic_info'] = {
                'success': 'error' not in data,
                'data': data
            }
            print(f"  ✅ get_topic_info: {data.get('topic', 'unknown')}")
        except Exception as e:
            results['get_topic_info'] = {'success': False, 'error': str(e)}
            print(f"  ❌ get_topic_info failed: {e}")
        
        return results
    
    async def test_message_tools(self) -> Dict[str, Any]:
        """Test message-related tools."""
        print("\n📝 Testing Message Tools")
        print("=" * 50)
        
        results = {}
        
        # Test 1: produce_message
        try:
            print("Testing: produce_message")
            request = CallToolRequest(params={
                'name': 'produce_message',
                'arguments': {
                    'topic': 'mcptesttopic',
                    'value': f'Test message from MCP Cloud Test at {int(time.time())}',
                    'key': 'test-key-cloud'
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['produce_message'] = {
                'success': 'error' not in data,
                'data': data
            }
            print(f"  ✅ produce_message: {data.get('message', 'No message')}")
        except Exception as e:
            results['produce_message'] = {'success': False, 'error': str(e)}
            print(f"  ❌ produce_message failed: {e}")
        
        # Test 2: consume_messages
        try:
            print("Testing: consume_messages")
            request = CallToolRequest(params={
                'name': 'consume_messages',
                'arguments': {
                    'topic': 'mcptesttopic',
                    'max_count': 5
                }
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['consume_messages'] = {
                'success': 'error' not in data,
                'messages': data.get('messages', []),
                'count': data.get('count', 0),
                'data': data
            }
            print(f"  ✅ consume_messages: {data.get('count', 0)} messages consumed")
        except Exception as e:
            results['consume_messages'] = {'success': False, 'error': str(e)}
            print(f"  ❌ consume_messages failed: {e}")
        
        return results
    
    async def test_connector_tools(self) -> Dict[str, Any]:
        """Test connector-related tools."""
        print("\n🔌 Testing Connector Tools")
        print("=" * 50)
        
        results = {}
        
        # Test 1: list_connectors
        try:
            print("Testing: list_connectors")
            request = CallToolRequest(params={'name': 'list_connectors', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['list_connectors'] = {
                'success': 'error' not in data,
                'connectors': data.get('connectors', []),
                'count': data.get('count', 0),
                'data': data
            }
            print(f"  ✅ list_connectors: {data.get('count', 0)} connectors found")
        except Exception as e:
            results['list_connectors'] = {'success': False, 'error': str(e)}
            print(f"  ❌ list_connectors failed: {e}")
        
        # Test 2: get_connector_status
        try:
            print("Testing: get_connector_status")
            request = CallToolRequest(params={
                'name': 'get_connector_status',
                'arguments': {'connector_name': 'test-connector'}
            })
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['get_connector_status'] = {
                'success': 'error' not in data,
                'data': data
            }
            print(f"  ✅ get_connector_status: {data.get('status', 'unknown')}")
        except Exception as e:
            results['get_connector_status'] = {'success': False, 'error': str(e)}
            print(f"  ❌ get_connector_status failed: {e}")
        
        return results
    
    async def test_authentication_tools(self) -> Dict[str, Any]:
        """Test authentication-related tools."""
        print("\n🔐 Testing Authentication Tools")
        print("=" * 50)
        
        results = {}
        
        # Test 1: test_authentication
        try:
            print("Testing: test_authentication")
            request = CallToolRequest(params={'name': 'test_authentication', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['test_authentication'] = {
                'success': data.get('authenticated', False),
                'method': data.get('method', 'unknown'),
                'data': data
            }
            print(f"  ✅ test_authentication: {data.get('authenticated', False)}")
        except Exception as e:
            results['test_authentication'] = {'success': False, 'error': str(e)}
            print(f"  ❌ test_authentication failed: {e}")
        
        # Test 2: discover_auth_endpoints
        try:
            print("Testing: discover_auth_endpoints")
            request = CallToolRequest(params={'name': 'discover_auth_endpoints', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['discover_auth_endpoints'] = {
                'success': 'error' not in data,
                'endpoints': data.get('endpoints', {}),
                'data': data
            }
            print(f"  ✅ discover_auth_endpoints: {len(data.get('endpoints', {}))} endpoints found")
        except Exception as e:
            results['discover_auth_endpoints'] = {'success': False, 'error': str(e)}
            print(f"  ❌ discover_auth_endpoints failed: {e}")
        
        return results
    
    async def test_cdp_specific_tools(self) -> Dict[str, Any]:
        """Test CDP-specific tools."""
        print("\n☁️ Testing CDP-Specific Tools")
        print("=" * 50)
        
        results = {}
        
        # Test 1: get_cdp_clusters
        try:
            print("Testing: get_cdp_clusters")
            request = CallToolRequest(params={'name': 'get_cdp_clusters', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['get_cdp_clusters'] = {
                'success': 'error' not in data,
                'clusters': data.get('clusters', []),
                'count': data.get('count', 0),
                'data': data
            }
            print(f"  ✅ get_cdp_clusters: {data.get('count', 0)} clusters found")
        except Exception as e:
            results['get_cdp_clusters'] = {'success': False, 'error': str(e)}
            print(f"  ❌ get_cdp_clusters failed: {e}")
        
        # Test 2: get_cdp_apis
        try:
            print("Testing: get_cdp_apis")
            request = CallToolRequest(params={'name': 'get_cdp_apis', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['get_cdp_apis'] = {
                'success': 'error' not in data,
                'apis': data.get('apis', []),
                'count': data.get('count', 0),
                'data': data
            }
            print(f"  ✅ get_cdp_apis: {data.get('count', 0)} APIs found")
        except Exception as e:
            results['get_cdp_apis'] = {'success': False, 'error': str(e)}
            print(f"  ❌ get_cdp_apis failed: {e}")
        
        # Test 3: get_cdp_service_health
        try:
            print("Testing: get_cdp_service_health")
            request = CallToolRequest(params={'name': 'get_cdp_service_health', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['get_cdp_service_health'] = {
                'success': 'error' not in data,
                'services': data.get('services', {}),
                'data': data
            }
            print(f"  ✅ get_cdp_service_health: {len(data.get('services', {}))} services checked")
        except Exception as e:
            results['get_cdp_service_health'] = {'success': False, 'error': str(e)}
            print(f"  ❌ get_cdp_service_health failed: {e}")
        
        return results
    
    async def test_monitoring_tools(self) -> Dict[str, Any]:
        """Test monitoring-related tools."""
        print("\n📊 Testing Monitoring Tools")
        print("=" * 50)
        
        results = {}
        
        # Test 1: get_service_metrics
        try:
            print("Testing: get_service_metrics")
            request = CallToolRequest(params={'name': 'get_service_metrics', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['get_service_metrics'] = {
                'success': 'error' not in data,
                'metrics': data.get('metrics', {}),
                'data': data
            }
            print(f"  ✅ get_service_metrics: {len(data.get('metrics', {}))} metrics collected")
        except Exception as e:
            results['get_service_metrics'] = {'success': False, 'error': str(e)}
            print(f"  ❌ get_service_metrics failed: {e}")
        
        # Test 2: run_health_check
        try:
            print("Testing: run_health_check")
            request = CallToolRequest(params={'name': 'run_health_check', 'arguments': {}})
            result = await self.server.call_tool(request)
            data = json.loads(result.content[0].text)
            results['run_health_check'] = {
                'success': 'error' not in data,
                'status': data.get('status', 'unknown'),
                'data': data
            }
            print(f"  ✅ run_health_check: {data.get('status', 'unknown')}")
        except Exception as e:
            results['run_health_check'] = {'success': False, 'error': str(e)}
            print(f"  ❌ run_health_check failed: {e}")
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all MCP tool tests."""
        print("🚀 CDP Cloud MCP Tools Comprehensive Test Suite")
        print("=" * 70)
        print(f"Configuration: {self.config_file}")
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        # Initialize server
        if not await self.initialize_server():
            return {'error': 'Failed to initialize MCP server'}
        
        # Run all test categories
        test_categories = [
            ('Connection Tools', self.test_connection_tools),
            ('Topic Tools', self.test_topic_tools),
            ('Message Tools', self.test_message_tools),
            ('Connector Tools', self.test_connector_tools),
            ('Authentication Tools', self.test_authentication_tools),
            ('CDP-Specific Tools', self.test_cdp_specific_tools),
            ('Monitoring Tools', self.test_monitoring_tools)
        ]
        
        for category_name, test_func in test_categories:
            try:
                category_results = await test_func()
                self.test_results[category_name] = category_results
            except Exception as e:
                print(f"❌ {category_name} failed: {e}")
                self.test_results[category_name] = {'error': str(e)}
        
        # Calculate summary
        self.test_results['summary'] = self.calculate_summary()
        
        # Print final results
        self.print_final_results()
        
        return self.test_results
    
    def calculate_summary(self) -> Dict[str, Any]:
        """Calculate test summary statistics."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        for category, results in self.test_results.items():
            if category == 'summary':
                continue
            if isinstance(results, dict) and 'error' not in results:
                for test_name, test_result in results.items():
                    total_tests += 1
                    if test_result.get('success', False):
                        passed_tests += 1
                    else:
                        failed_tests += 1
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'success_rate': success_rate,
            'duration': time.time() - self.start_time
        }
    
    def print_final_results(self):
        """Print final test results."""
        print("\n" + "=" * 70)
        print("📊 CDP CLOUD MCP TOOLS TEST RESULTS")
        print("=" * 70)
        
        summary = self.test_results.get('summary', {})
        print(f"Total Tests: {summary.get('total_tests', 0)}")
        print(f"Passed: {summary.get('passed_tests', 0)}")
        print(f"Failed: {summary.get('failed_tests', 0)}")
        print(f"Success Rate: {summary.get('success_rate', 0):.1f}%")
        print(f"Duration: {summary.get('duration', 0):.2f} seconds")
        
        print("\n📋 Detailed Results by Category:")
        for category, results in self.test_results.items():
            if category == 'summary':
                continue
            
            print(f"\n{category}:")
            if isinstance(results, dict) and 'error' not in results:
                for test_name, test_result in results.items():
                    status = "✅ PASS" if test_result.get('success', False) else "❌ FAIL"
                    print(f"  {test_name}: {status}")
            else:
                print(f"  ❌ Category failed: {results.get('error', 'Unknown error')}")
        
        print("\n🎯 Recommendations:")
        if summary.get('success_rate', 0) >= 80:
            print("✅ Excellent! Most MCP tools are working well with CDP Cloud")
        elif summary.get('success_rate', 0) >= 60:
            print("⚠️ Good progress! Some tools need attention")
        else:
            print("❌ Several tools need fixes. Check CDP configuration and endpoints")
        
        print("\n💡 Next Steps:")
        print("1. Review failed tests and fix configuration issues")
        print("2. Verify CDP service endpoints are accessible")
        print("3. Check authentication credentials and permissions")
        print("4. Test with different CDP environments if available")

async def main():
    """Main function to run CDP Cloud MCP tools tests."""
    tester = CDPCloudMCPTester()
    results = await tester.run_all_tests()
    
    # Save results to file
    timestamp = int(time.time())
    results_file = f"cdp_cloud_mcp_test_results_{timestamp}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\n💾 Results saved to: {results_file}")

if __name__ == "__main__":
    asyncio.run(main())
