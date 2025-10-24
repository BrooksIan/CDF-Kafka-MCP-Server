#!/usr/bin/env python3
"""
Check if topic was created by connector
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def check_topic_creation():
    """Check if topic was created by connector."""
    print("🔍 Checking if cursortest topic was created...")
    print("=" * 50)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # Check if topic exists
        print("\n🔍 Checking if cursortest topic exists...")
        request = CallToolRequest(params={'name': 'topic_exists', 'arguments': {'name': 'cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ Topic exists: {result.content[0].text}")
        
        # List all topics
        print("\n📋 Listing all topics...")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ All topics: {result.content[0].text}")
        
        # Check connector status
        print("\n📊 Checking connector status...")
        request = CallToolRequest(params={'name': 'get_connector_status', 'arguments': {'name': 'simple-data-generator'}})
        result = await server.call_tool(request)
        print(f"✅ Connector status: {result.content[0].text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_topic_creation())
