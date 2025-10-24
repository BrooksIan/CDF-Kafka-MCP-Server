#!/usr/bin/env python3
"""
Create HTTP source connector using MCP server
"""

import asyncio
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def create_http_source_connector():
    """Create HTTP source connector using MCP server."""
    print("🔧 Creating HTTP source connector using MCP server...")
    print("=" * 60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # Create a simple HTTP source connector
        print("\n🆕 Creating HTTP source connector...")
        connector_name = "http-source-cursortest"
        connector_config = {
            "connector.class": "org.apache.kafka.connect.mirror.MirrorSourceConnector",
            "topics": "cursortest",
            "source.cluster.alias": "source",
            "target.cluster.alias": "target",
            "source.cluster.bootstrap.servers": "irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443",
            "target.cluster.bootstrap.servers": "irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443",
            "tasks.max": "1",
            "producer.override.sasl.mechanism": "PLAIN",
            "producer.override.sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"ibrooks\" password=\"Admin12345#\";",
            "producer.override.security.protocol": "SASL_SSL",
            "consumer.override.sasl.mechanism": "PLAIN",
            "consumer.override.sasl.jaas.config": "org.apache.kafka.common.security.plain.PlainLoginModule required username=\"ibrooks\" password=\"Admin12345#\";",
            "consumer.override.security.protocol": "SASL_SSL"
        }
        
        request = CallToolRequest(params={'name': 'create_connector', 'arguments': {'name': connector_name, 'config': connector_config}})
        result = await server.call_tool(request)
        print(f"✅ Create connector result: {result.content[0].text}")
        
        # Wait a bit for connector to start
        print("\n⏳ Waiting for connector to start...")
        await asyncio.sleep(10)
        
        # Check connector status
        print("\n📊 Checking connector status...")
        request = CallToolRequest(params={'name': 'get_connector_status', 'arguments': {'name': 'http-source-cursortest'}})
        result = await server.call_tool(request)
        print(f"✅ Connector status: {result.content[0].text}")
        
        # Check if topic was created
        print("\n🔍 Checking if cursortest topic exists...")
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
    asyncio.run(create_http_source_connector())
