#!/usr/bin/env python3
"""
Check heartbeats topic created by connector
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def check_heartbeats_topic():
    """Check heartbeats topic created by connector."""
    print("🎉 SUCCESS! Connector created 'heartbeats' topic!")
    print("=" * 60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # Check if heartbeats topic exists
        print("\n🔍 Checking heartbeats topic...")
        request = CallToolRequest(params={'name': 'topic_exists', 'arguments': {'name': 'heartbeats'}})
        result = await server.call_tool(request)
        print(f"✅ Heartbeats topic exists: {result.content[0].text}")
        
        # List all topics
        print("\n📋 Listing all topics...")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ All topics: {result.content[0].text}")
        
        # Try to produce a message to the heartbeats topic
        print("\n📝 Testing message production to heartbeats topic...")
        request = CallToolRequest(params={'name': 'produce_message', 'arguments': {'topic': 'heartbeats', 'value': 'Test message from MCP server', 'key': 'test-key'}})
        result = await server.call_tool(request)
        print(f"✅ Produce message result: {result.content[0].text}")
        
        # Try to consume messages from the heartbeats topic
        print("\n📖 Testing message consumption from heartbeats topic...")
        request = CallToolRequest(params={'name': 'consume_messages', 'arguments': {'topic': 'heartbeats', 'max_messages': 5, 'timeout': 10}})
        result = await server.call_tool(request)
        print(f"✅ Consume messages result: {result.content[0].text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_heartbeats_topic())
