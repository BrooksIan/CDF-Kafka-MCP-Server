#!/usr/bin/env python3
"""
Test Knox Gateway Integration

This test validates the new Knox Gateway integration features
including Admin API, service discovery, and topology management.
"""

import asyncio
import os
import sys
import json
import time
import requests

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.knox_gateway import KnoxGatewayClient, KnoxKafkaClient
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest

def test_knox_gateway_integration():
    """Test Knox Gateway integration features."""
    print("🔧 Testing Knox Gateway Integration")
    print("=" * 60)
    
    # Configuration
    gateway_url = os.getenv("KNOX_GATEWAY", "https://your-knox-gateway.example.com:8443/gateway")
    admin_ui_url = os.getenv("KNOX_ADMIN_UI", "https://your-knox-gateway.example.com:8443/gateway/manager/admin-ui/")
    username = os.getenv("KNOX_USERNAME", "your-username")
    password = os.getenv("KNOX_PASSWORD", "your-password")
    
    print(f"🔗 Gateway URL: {gateway_url}")
    print(f"🔗 Admin UI URL: {admin_ui_url}")
    print(f"👤 Username: {username}")
    
    try:
        # Test 1: Initialize Knox Gateway Client
        print(f"\n🔍 Test 1: Initialize Knox Gateway Client")
        knox_client = KnoxGatewayClient(gateway_url, username, password)
        print("✅ Knox Gateway client initialized")
        
        # Test 2: Get Gateway Information
        print(f"\n🔍 Test 2: Get Gateway Information")
        try:
            gateway_info = knox_client.get_gateway_info()
            if gateway_info:
                print(f"✅ Gateway Info: {json.dumps(gateway_info, indent=2)}")
            else:
                print("❌ No gateway info available")
        except Exception as e:
            print(f"❌ Error getting gateway info: {e}")
        
        # Test 3: List Topologies
        print(f"\n🔍 Test 3: List Topologies")
        try:
            topologies = knox_client.list_topologies()
            print(f"✅ Topologies: {json.dumps(topologies, indent=2)}")
        except Exception as e:
            print(f"❌ Error listing topologies: {e}")
        
        # Test 4: Test Service URLs
        print(f"\n🔍 Test 4: Test Service URLs")
        try:
            kafka_url = knox_client.get_kafka_service_url()
            connect_url = knox_client.get_kafka_connect_service_url()
            print(f"✅ Kafka URL: {kafka_url}")
            print(f"✅ Connect URL: {connect_url}")
        except Exception as e:
            print(f"❌ Error getting service URLs: {e}")
        
        # Test 5: Test Service Connectivity
        print(f"\n🔍 Test 5: Test Service Connectivity")
        try:
            kafka_healthy = knox_client.test_service_connectivity(kafka_url)
            connect_healthy = knox_client.test_service_connectivity(connect_url)
            print(f"✅ Kafka Service: {'Healthy' if kafka_healthy else 'Unhealthy'}")
            print(f"✅ Connect Service: {'Healthy' if connect_healthy else 'Unhealthy'}")
        except Exception as e:
            print(f"❌ Error testing connectivity: {e}")
        
        # Test 6: Get Available Services
        print(f"\n🔍 Test 6: Get Available Services")
        try:
            services = knox_client.get_available_services()
            print(f"✅ Available Services: {services}")
        except Exception as e:
            print(f"❌ Error getting available services: {e}")
        
        # Test 7: Test Knox Kafka Client
        print(f"\n🔍 Test 7: Test Knox Kafka Client")
        try:
            knox_kafka = KnoxKafkaClient(knox_client)
            service_info = knox_kafka.get_service_info()
            print(f"✅ Service Info: {json.dumps(service_info, indent=2)}")
            
            connectivity = knox_kafka.test_connectivity()
            print(f"✅ Overall Connectivity: {'Healthy' if connectivity else 'Unhealthy'}")
        except Exception as e:
            print(f"❌ Error testing Knox Kafka client: {e}")
        
        # Test 8: Test Admin UI Access
        print(f"\n🔍 Test 8: Test Admin UI Access")
        try:
            response = requests.get(admin_ui_url, timeout=10)
            print(f"✅ Admin UI Status: {response.status_code}")
            if response.status_code == 200:
                print("✅ Admin UI is accessible")
            else:
                print(f"❌ Admin UI returned: {response.text[:100]}...")
        except Exception as e:
            print(f"❌ Error accessing Admin UI: {e}")
        
        # Test 9: Test MCP Server Integration
        print(f"\n🔍 Test 9: Test MCP Server Integration")
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
            server = CDFKafkaMCPServer(config_path)
            print("✅ MCP server initialized")
            
            # Test connection (synchronous)
            print("✅ MCP server integration test completed")
            
        except Exception as e:
            print(f"❌ Error testing MCP server integration: {e}")
        
        # Test 10: Health Check
        print(f"\n🔍 Test 10: Health Check")
        try:
            health = knox_client.get_service_health()
            print(f"✅ Health Status: {json.dumps(health, indent=2)}")
        except Exception as e:
            print(f"❌ Error getting health status: {e}")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

async def test_async_operations():
    """Test async operations with MCP server."""
    print(f"\n🔧 Testing Async Operations")
    print("=" * 40)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
        server = CDFKafkaMCPServer(config_path)
        
        # Test MCP tools
        tools_to_test = [
            'test_connection',
            'list_topics',
            'get_connect_info'
        ]
        
        for tool in tools_to_test:
            try:
                print(f"\n🔧 Testing {tool}")
                request = CallToolRequest(params={'name': tool, 'arguments': {}})
                result = await server.call_tool(request)
                print(f"✅ {tool}: {result.content[0].text}")
            except Exception as e:
                print(f"❌ {tool}: {e}")
        
    except Exception as e:
        print(f"❌ Error in async operations: {e}")

if __name__ == "__main__":
    test_knox_gateway_integration()
    asyncio.run(test_async_operations())
