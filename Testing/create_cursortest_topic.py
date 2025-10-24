#!/usr/bin/env python3
"""
Create cursortest topic using MCP server
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def create_cursortest_topic():
    """Create the cursortest topic using MCP server."""
    print("🧪 Creating topic 'cursortest' using MCP server...")
    print("=" * 50)
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    print(f"📋 Config path: {config_path}")
    
    try:
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # Create the topic
        print("\n🔧 Creating topic: cursortest")
        request = CallToolRequest(params={'name': 'create_topic', 'arguments': {'name': 'cursortest', 'partitions': 1, 'replication_factor': 1}})
        result = await server.call_tool(request)
        print(f"✅ Create result: {result.content[0].text}")
        
        # List all topics to verify
        print("\n📋 Listing all topics to verify...")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ Topics: {result.content[0].text}")
        
        # Check if topic exists
        print("\n🔍 Checking if cursortest exists...")
        request = CallToolRequest(params={'name': 'topic_exists', 'arguments': {'name': 'cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ Topic exists: {result.content[0].text}")
        
        print("\n🎉 Topic creation completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_cursortest_topic())
