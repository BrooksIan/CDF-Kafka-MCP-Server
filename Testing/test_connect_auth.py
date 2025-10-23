#!/usr/bin/env python3
"""
Test Kafka Connect Authentication
Test script to verify Connect API authentication with CDP credentials.
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def test_connect_auth():
    """Test Connect API authentication."""
    print("🧪 Testing Kafka Connect Authentication")
    print("=" * 50)
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    print(f"📋 Config path: {config_path}")
    
    try:
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # Test Connect tools
        print("\n🔗 Testing Connect tools...")
        
        # Test list_connectors
        print("🧪 Testing list_connectors...")
        request = CallToolRequest(params={'name': 'list_connectors', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ list_connectors: {result.content[0].text}")
        
        # Test get_connect_server_info
        print("🧪 Testing get_connect_server_info...")
        request = CallToolRequest(params={'name': 'get_connect_server_info', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ get_connect_server_info: {result.content[0].text}")
        
        # Test list_connector_plugins
        print("🧪 Testing list_connector_plugins...")
        request = CallToolRequest(params={'name': 'list_connector_plugins', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ list_connector_plugins: {result.content[0].text}")
        
        print("\n🎉 All Connect API tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_connect_auth())
