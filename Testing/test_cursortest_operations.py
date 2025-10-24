#!/usr/bin/env python3
"""
Test operations on cursortest topic
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def test_cursortest_operations():
    """Test various operations on the cursortest topic."""
    print("🔍 Testing cursortest topic operations...")
    print("=" * 50)
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    
    try:
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # Describe topic
        print("\n📋 Describing cursortest topic...")
        request = CallToolRequest(params={'name': 'describe_topic', 'arguments': {'name': 'cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ Describe result: {result.content[0].text}")
        
        # Get topic partitions
        print("\n🔢 Getting topic partitions...")
        request = CallToolRequest(params={'name': 'get_topic_partitions', 'arguments': {'name': 'cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ Partitions: {result.content[0].text}")
        
        # Test producing a message
        print("\n💬 Testing message production...")
        request = CallToolRequest(params={
            'name': 'produce_message', 
            'arguments': {
                'topic': 'cursortest',
                'key': 'test-key',
                'value': 'Hello from cursortest topic!',
                'headers': {'source': 'mcp-test'}
            }
        })
        result = await server.call_tool(request)
        print(f"✅ Produce result: {result.content[0].text}")
        
        print("\n🎉 All cursortest operations completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cursortest_operations())
