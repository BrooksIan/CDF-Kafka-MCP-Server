#!/usr/bin/env python3
"""
Check topics on CDP Cloud environment
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def check_cdp_cloud_topics():
    """Check what topics exist on CDP Cloud environment."""
    print("🔍 Checking CDP Cloud environment...")
    print("=" * 50)
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    print(f"📋 Config path: {config_path}")
    
    try:
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # List all topics
        print("\n📋 Listing topics on CDP Cloud...")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ Topics: {result.content[0].text}")
        
        # Check if cursortest exists
        print("\n🔍 Checking if cursortest exists on CDP Cloud...")
        request = CallToolRequest(params={'name': 'topic_exists', 'arguments': {'name': 'cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ cursortest exists: {result.content[0].text}")
        
        # Test connection
        print("\n🔌 Testing connection to CDP Cloud...")
        request = CallToolRequest(params={'name': 'test_connection', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ Connection test: {result.content[0].text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_cdp_cloud_topics())
