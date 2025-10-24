#!/usr/bin/env python3
"""
Test MCP server create_topic method directly
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def test_mcp_create_topic():
    """Test MCP server create_topic method directly."""
    print("🔍 Testing MCP server create_topic method...")
    print("=" * 50)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # Try to create topic
        print("\n🆕 Creating topic 'cursortest'...")
        request = CallToolRequest(params={'name': 'create_topic', 'arguments': {'name': 'cursortest', 'partitions': 1, 'replication_factor': 1}})
        result = await server.call_tool(request)
        print(f"✅ Create topic result: {result.content[0].text}")
        
        # Check if topic exists
        print("\n🔍 Checking if topic exists...")
        request = CallToolRequest(params={'name': 'topic_exists', 'arguments': {'name': 'cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ Topic exists: {result.content[0].text}")
        
        # List all topics
        print("\n📋 Listing all topics...")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ Topics: {result.content[0].text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mcp_create_topic())
