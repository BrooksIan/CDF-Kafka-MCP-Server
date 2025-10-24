#!/usr/bin/env python3
"""
Create a topic using Kafka Connect connector
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def create_topic_via_connector():
    """Create a topic using Kafka Connect connector."""
    print("🔧 Creating topic using Kafka Connect connector...")
    print("=" * 60)
    
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    
    try:
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # First, check current topics
        print("\n📋 Current topics:")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"Topics: {result.content[0].text}")
        
        # Try to create a connector that might trigger topic creation
        print("\n🔧 Creating MirrorHeartbeatConnector...")
        request = CallToolRequest(params={
            'name': 'create_connector', 
            'arguments': {
                'name': 'cursortest-creator',
                'config': {
                    'connector.class': 'org.apache.kafka.connect.mirror.MirrorHeartbeatConnector',
                    'topics': 'cursortest',
                    'source.cluster.alias': 'source',
                    'target.cluster.alias': 'target',
                    'source.cluster.bootstrap.servers': 'irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443',
                    'target.cluster.bootstrap.servers': 'irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443',
                    'tasks.max': '1'
                }
            }
        })
        result = await server.call_tool(request)
        print(f"✅ Create connector result: {result.content[0].text}")
        
        # Check connectors
        print("\n📋 Current connectors:")
        request = CallToolRequest(params={'name': 'list_connectors', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"Connectors: {result.content[0].text}")
        
        # Check if topic was created
        print("\n🔍 Checking if cursortest topic exists...")
        request = CallToolRequest(params={'name': 'topic_exists', 'arguments': {'name': 'cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ Topic exists: {result.content[0].text}")
        
        # List topics again to see if anything changed
        print("\n📋 Topics after connector creation:")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"Topics: {result.content[0].text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_topic_via_connector())
