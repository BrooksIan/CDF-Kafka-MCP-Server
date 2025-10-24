#!/usr/bin/env python3
"""
Create JSON data connector using MCP server
"""

import asyncio
import os
import sys
import json
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

async def create_json_data_connector():
    """Create JSON data connector using MCP server."""
    print("🔧 Creating JSON data connector using MCP server...")
    print("=" * 60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized")
        
        # Create a simple JSON data generator connector
        print("\n🆕 Creating JSON data generator connector...")
        connector_name = "json-data-generator"
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
        
        # Wait for connector to start
        print("\n⏳ Waiting for connector to start...")
        await asyncio.sleep(15)
        
        # Check connector status
        print("\n📊 Checking connector status...")
        request = CallToolRequest(params={'name': 'get_connector_status', 'arguments': {'name': connector_name}})
        result = await server.call_tool(request)
        print(f"✅ Connector status: {result.content[0].text}")
        
        # Check what topics were created
        print("\n🔍 Checking what topics were created...")
        request = CallToolRequest(params={'name': 'get_connector_active_topics', 'arguments': {'name': connector_name}})
        result = await server.call_tool(request)
        print(f"✅ Active topics: {result.content[0].text}")
        
        # List all topics
        print("\n📋 Listing all topics...")
        request = CallToolRequest(params={'name': 'list_topics', 'arguments': {}})
        result = await server.call_tool(request)
        print(f"✅ All topics: {result.content[0].text}")
        
        # Try to produce JSON data directly
        print("\n📝 Testing JSON data production...")
        json_data = {
            "timestamp": int(time.time()),
            "message": "Hello from MCP server",
            "id": 123,
            "data": {
                "type": "test",
                "value": "JSON data from terminal"
            }
        }
        
        request = CallToolRequest(params={'name': 'produce_message', 'arguments': {'topic': 'cursortest', 'value': json.dumps(json_data), 'key': 'json-test'}})
        result = await server.call_tool(request)
        print(f"✅ Produce JSON message result: {result.content[0].text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_json_data_connector())
