#!/usr/bin/env python3
"""
Cloud Testing Script for CDF Kafka MCP Server

This script tests the MCP server against cloud-based Kafka environments.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, 'src')

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest, CallToolRequestParams


class CloudTester:
    """Cloud testing utility for MCP server."""
    
    def __init__(self):
        self.mcp_server = None
        self.test_results = []
    
    async def initialize(self) -> bool:
        """Initialize MCP server."""
        try:
            print("🔧 Initializing MCP server...")
            self.mcp_server = CDFKafkaMCPServer()
            print(f"✅ MCP server initialized successfully")
            print(f"✅ Knox enabled: {self.mcp_server.config.is_knox_enabled()}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize MCP server: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """Test basic connection to Kafka."""
        try:
            print("\n🔍 Testing basic connection...")
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='test_connection',
                    arguments={}
                )
            )
            result = await self.mcp_server.call_tool(request)
            print(f"✅ Connection test passed: {result.content[0].text}")
            self.test_results.append({"test": "connection", "status": "passed"})
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            self.test_results.append({"test": "connection", "status": "failed", "error": str(e)})
            return False
    
    async def test_topic_operations(self) -> bool:
        """Test topic operations."""
        try:
            print("\n📁 Testing topic operations...")
            
            # List topics
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='list_topics',
                    arguments={}
                )
            )
            result = await self.mcp_server.call_tool(request)
            topics_data = json.loads(result.content[0].text)
            print(f"✅ Topics listed: {len(topics_data.get('topics', []))} topics found")
            
            # Create test topic
            test_topic = "cloud-test-topic"
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='create_topic',
                    arguments={
                        'name': test_topic,
                        'partitions': 1,
                        'replication_factor': 1
                    }
                )
            )
            result = await self.mcp_server.call_tool(request)
            print(f"✅ Test topic created: {test_topic}")
            
            # Check if topic exists
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='topic_exists',
                    arguments={'name': test_topic}
                )
            )
            result = await self.mcp_server.call_tool(request)
            exists_data = json.loads(result.content[0].text)
            print(f"✅ Topic exists check: {exists_data.get('exists', False)}")
            
            self.test_results.append({"test": "topic_operations", "status": "passed"})
            return True
        except Exception as e:
            print(f"❌ Topic operations test failed: {e}")
            self.test_results.append({"test": "topic_operations", "status": "failed", "error": str(e)})
            return False
    
    async def test_message_operations(self) -> bool:
        """Test message operations."""
        try:
            print("\n💬 Testing message operations...")
            
            test_topic = "cloud-test-topic"
            
            # Produce message
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='produce_message',
                    arguments={
                        'topic': test_topic,
                        'key': 'test-key-1',
                        'value': 'Hello from cloud testing!',
                        'headers': {
                            'source': 'cloud-test',
                            'timestamp': '2024-01-01T00:00:00Z'
                        }
                    }
                )
            )
            result = await self.mcp_server.call_tool(request)
            print(f"✅ Message produced successfully")
            
            # Produce another message
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='produce_message',
                    arguments={
                        'topic': test_topic,
                        'key': 'test-key-2',
                        'value': 'Second message from cloud testing!',
                        'headers': {
                            'source': 'cloud-test',
                            'timestamp': '2024-01-01T00:01:00Z'
                        }
                    }
                )
            )
            result = await self.mcp_server.call_tool(request)
            print(f"✅ Second message produced successfully")
            
            # Get topic offsets
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='get_topic_offsets',
                    arguments={
                        'topic': test_topic,
                        'partition': 0
                    }
                )
            )
            result = await self.mcp_server.call_tool(request)
            offsets_data = json.loads(result.content[0].text)
            print(f"✅ Topic offsets: {offsets_data}")
            
            self.test_results.append({"test": "message_operations", "status": "passed"})
            return True
        except Exception as e:
            print(f"❌ Message operations test failed: {e}")
            self.test_results.append({"test": "message_operations", "status": "failed", "error": str(e)})
            return False
    
    async def test_knox_integration(self) -> bool:
        """Test Knox integration."""
        try:
            print("\n🔐 Testing Knox integration...")
            
            # Test Knox connection
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='test_knox_connection',
                    arguments={}
                )
            )
            result = await self.mcp_server.call_tool(request)
            knox_data = json.loads(result.content[0].text)
            print(f"✅ Knox connection test: {knox_data}")
            
            # Get Knox metadata
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='get_knox_metadata',
                    arguments={}
                )
            )
            result = await self.mcp_server.call_tool(request)
            metadata = json.loads(result.content[0].text)
            print(f"✅ Knox metadata: {metadata}")
            
            self.test_results.append({"test": "knox_integration", "status": "passed"})
            return True
        except Exception as e:
            print(f"❌ Knox integration test failed: {e}")
            self.test_results.append({"test": "knox_integration", "status": "failed", "error": str(e)})
            return False
    
    async def test_kafka_connect(self) -> bool:
        """Test Kafka Connect operations."""
        try:
            print("\n🔌 Testing Kafka Connect operations...")
            
            # List connectors
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='list_connectors',
                    arguments={}
                )
            )
            result = await self.mcp_server.call_tool(request)
            connectors_data = json.loads(result.content[0].text)
            print(f"✅ Connectors listed: {len(connectors_data.get('connectors', []))} connectors found")
            
            # List connector plugins
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='list_connector_plugins',
                    arguments={}
                )
            )
            result = await self.mcp_server.call_tool(request)
            plugins_data = json.loads(result.content[0].text)
            print(f"✅ Connector plugins: {len(plugins_data.get('plugins', []))} plugins available")
            
            # Get Connect server info
            request = CallToolRequest(
                params=CallToolRequestParams(
                    name='get_connect_server_info',
                    arguments={}
                )
            )
            result = await self.mcp_server.call_tool(request)
            server_info = json.loads(result.content[0].text)
            print(f"✅ Connect server info: {server_info}")
            
            self.test_results.append({"test": "kafka_connect", "status": "passed"})
            return True
        except Exception as e:
            print(f"❌ Kafka Connect test failed: {e}")
            self.test_results.append({"test": "kafka_connect", "status": "failed", "error": str(e)})
            return False
    
    def print_environment_info(self):
        """Print environment information."""
        print("🌍 Environment Information:")
        print(f"  KAFKA_BOOTSTRAP_SERVERS: {os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'Not set')}")
        print(f"  KAFKA_SECURITY_PROTOCOL: {os.getenv('KAFKA_SECURITY_PROTOCOL', 'Not set')}")
        print(f"  KAFKA_SASL_MECHANISM: {os.getenv('KAFKA_SASL_MECHANISM', 'Not set')}")
        print(f"  KNOX_GATEWAY: {os.getenv('KNOX_GATEWAY', 'Not set')}")
        print(f"  KNOX_TOKEN: {'Set' if os.getenv('KNOX_TOKEN') else 'Not set'}")
        print(f"  MCP_LOG_LEVEL: {os.getenv('MCP_LOG_LEVEL', 'INFO')}")
    
    def print_test_summary(self):
        """Print test summary."""
        print("\n📊 Test Summary:")
        passed = sum(1 for result in self.test_results if result['status'] == 'passed')
        total = len(self.test_results)
        print(f"  Tests passed: {passed}/{total}")
        
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'passed' else "❌"
            print(f"  {status_icon} {result['test']}: {result['status']}")
            if result['status'] == 'failed' and 'error' in result:
                print(f"    Error: {result['error']}")
    
    async def run_all_tests(self):
        """Run all cloud tests."""
        print("🚀 Starting Cloud Testing for CDF Kafka MCP Server")
        print("=" * 60)
        
        self.print_environment_info()
        
        if not await self.initialize():
            return False
        
        # Run tests
        await self.test_connection()
        await self.test_topic_operations()
        await self.test_message_operations()
        await self.test_knox_integration()
        await self.test_kafka_connect()
        
        self.print_test_summary()
        
        return True


async def main():
    """Main function."""
    tester = CloudTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
