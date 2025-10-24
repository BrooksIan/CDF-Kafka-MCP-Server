#!/usr/bin/env python3
"""
Check connector status and troubleshoot issues
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def check_connector_status():
    """Check connector status and troubleshoot issues."""
    print("🔍 Checking connector status and troubleshooting...")
    print("=" * 60)
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    
    try:
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # List connectors
        print("\n📋 Current connectors:")
        request = CallToolRequest(params={'name': 'list_connectors', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ Connectors: {result.content[0].text}")
        
        # Get connector status
        print("\n📊 Connector status:")
        request = CallToolRequest(params={'name': 'get_connector_status', 'arguments': {'name': 'cursortest-creator'}})
        result = await server.call_tool(request)
        print(f"✅ Status: {result.content[0].text}")
        
        # Get connector configuration
        print("\n⚙️  Connector configuration:")
        request = CallToolRequest(params={'name': 'get_connector_config', 'arguments': {'name': 'cursortest-creator'}})
        result = await server.call_tool(request)
        print(f"✅ Config: {result.content[0].text}")
        
        # Check if topic was created
        print("\n🔍 Checking if cursortest topic exists:")
        request = CallToolRequest(params={'name': 'topic_exists', 'arguments': {'name': 'cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ Topic exists: {result.content[0].text}")
        
        # List all topics
        print("\n📋 All topics:")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ Topics: {result.content[0].text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_connector_status())
