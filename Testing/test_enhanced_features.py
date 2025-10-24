#!/usr/bin/env python3
"""
Test Enhanced Features

This test validates all the new enhanced features including:
- Knox Gateway integration
- CDP Cloud authentication
- Enhanced topic creation
- Enhanced message production
- Monitoring and health checks
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

def test_enhanced_features():
    """Test all enhanced features."""
    print("🔧 Testing Enhanced Features")
    print("=" * 60)
    
    # Configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    
    try:
        # Initialize MCP server
        print(f"\n🔍 Initializing MCP Server...")
        server = CDFKafkaMCPServer(config_path)
        print("✅ MCP server initialized successfully")
        
        # Test 1: Health Status
        print(f"\n🔍 Test 1: Health Status")
        try:
            request = CallToolRequest(params={'name': 'get_health_status', 'arguments': {}})
            result = asyncio.run(server.call_tool(request))
            health_data = json.loads(result.content[0].text)
            print(f"✅ Health Status: {health_data.get('message', 'Unknown')}")
            if 'health_status' in health_data:
                overall_status = health_data['health_status'].get('overall_status', 'unknown')
                print(f"   Overall Status: {overall_status}")
        except Exception as e:
            print(f"❌ Health Status Error: {e}")
        
        # Test 2: Health Summary
        print(f"\n🔍 Test 2: Health Summary")
        try:
            request = CallToolRequest(params={'name': 'get_health_summary', 'arguments': {}})
            result = asyncio.run(server.call_tool(request))
            summary_data = json.loads(result.content[0].text)
            print(f"✅ Health Summary: {summary_data.get('message', 'Unknown')}")
            if 'summary' in summary_data:
                summary = summary_data['summary']
                print(f"   Overall Status: {summary.get('overall_status', 'unknown')}")
                print(f"   Uptime: {summary.get('uptime_seconds', 0):.1f}s")
        except Exception as e:
            print(f"❌ Health Summary Error: {e}")
        
        # Test 3: Service Metrics
        print(f"\n🔍 Test 3: Service Metrics")
        try:
            request = CallToolRequest(params={'name': 'get_service_metrics', 'arguments': {}})
            result = asyncio.run(server.call_tool(request))
            metrics_data = json.loads(result.content[0].text)
            print(f"✅ Service Metrics: {metrics_data.get('message', 'Unknown')}")
            if 'performance_metrics' in metrics_data:
                perf_metrics = metrics_data['performance_metrics']
                print(f"   Uptime: {perf_metrics.get('uptime_seconds', 0):.1f}s")
                print(f"   Success Rate: {perf_metrics.get('success_rate_percent', 0)}%")
        except Exception as e:
            print(f"❌ Service Metrics Error: {e}")
        
        # Test 4: Knox Gateway Info
        print(f"\n🔍 Test 4: Knox Gateway Info")
        try:
            request = CallToolRequest(params={'name': 'get_knox_gateway_info', 'arguments': {}})
            result = asyncio.run(server.call_tool(request))
            knox_data = json.loads(result.content[0].text)
            print(f"✅ Knox Gateway: {knox_data.get('message', 'Unknown')}")
        except Exception as e:
            print(f"❌ Knox Gateway Error: {e}")
        
        # Test 5: CDP Connection Test
        print(f"\n🔍 Test 5: CDP Connection Test")
        try:
            request = CallToolRequest(params={'name': 'test_cdp_connection', 'arguments': {}})
            result = asyncio.run(server.call_tool(request))
            cdp_data = json.loads(result.content[0].text)
            print(f"✅ CDP Connection: {cdp_data.get('message', 'Unknown')}")
            if 'connected' in cdp_data:
                print(f"   Connected: {cdp_data['connected']}")
        except Exception as e:
            print(f"❌ CDP Connection Error: {e}")
        
        # Test 6: Enhanced Topic Creation
        print(f"\n🔍 Test 6: Enhanced Topic Creation")
        try:
            topic_name = f"enhanced-test-{int(time.time())}"
            request = CallToolRequest(params={
                'name': 'create_topic', 
                'arguments': {
                    'name': topic_name,
                    'partitions': 3,
                    'replication_factor': 1,
                    'method': 'auto'
                }
            })
            result = asyncio.run(server.call_tool(request))
            topic_data = json.loads(result.content[0].text)
            print(f"✅ Topic Creation: {topic_data.get('message', 'Unknown')}")
            print(f"   Topic: {topic_data.get('topic', 'Unknown')}")
            print(f"   Method: {topic_data.get('method', 'Unknown')}")
        except Exception as e:
            print(f"❌ Topic Creation Error: {e}")
        
        # Test 7: Enhanced Message Production
        print(f"\n🔍 Test 7: Enhanced Message Production")
        try:
            request = CallToolRequest(params={
                'name': 'produce_message', 
                'arguments': {
                    'topic': 'enhanced-test-topic',
                    'key': 'test-key',
                    'value': 'Enhanced message production test',
                    'headers': {'source': 'enhanced-test'},
                    'method': 'auto'
                }
            })
            result = asyncio.run(server.call_tool(request))
            message_data = json.loads(result.content[0].text)
            print(f"✅ Message Production: {message_data.get('message', 'Unknown')}")
            print(f"   Method: {message_data.get('method', 'Unknown')}")
        except Exception as e:
            print(f"❌ Message Production Error: {e}")
        
        # Test 8: Individual Health Checks
        print(f"\n🔍 Test 8: Individual Health Checks")
        health_checks = ['kafka', 'knox', 'cdp', 'mcp_server', 'topics', 'connect']
        
        for check_name in health_checks:
            try:
                request = CallToolRequest(params={
                    'name': 'run_health_check', 
                    'arguments': {'check_name': check_name}
                })
                result = asyncio.run(server.call_tool(request))
                check_data = json.loads(result.content[0].text)
                status = check_data.get('check_result', {}).get('status', 'unknown')
                print(f"   {check_name}: {status}")
            except Exception as e:
                print(f"   {check_name}: Error - {e}")
        
        # Test 9: Health History
        print(f"\n🔍 Test 9: Health History")
        try:
            request = CallToolRequest(params={
                'name': 'get_health_history', 
                'arguments': {'limit': 5}
            })
            result = asyncio.run(server.call_tool(request))
            history_data = json.loads(result.content[0].text)
            print(f"✅ Health History: {history_data.get('message', 'Unknown')}")
            print(f"   History Entries: {len(history_data.get('history', []))}")
        except Exception as e:
            print(f"❌ Health History Error: {e}")
        
        # Test 10: List All Tools
        print(f"\n🔍 Test 10: List All Tools")
        try:
            from mcp.types import ListToolsRequest
            request = ListToolsRequest()
            result = asyncio.run(server.list_tools(request))
            tools = result.tools
            print(f"✅ Available Tools: {len(tools)}")
            
            # Categorize tools
            categories = {
                'Topic Management': [],
                'Message Operations': [],
                'Connect Operations': [],
                'Knox Gateway': [],
                'CDP Cloud': [],
                'Monitoring': [],
                'Other': []
            }
            
            for tool in tools:
                name = tool.name
                if any(x in name for x in ['topic', 'create_topic', 'delete_topic', 'describe_topic']):
                    categories['Topic Management'].append(name)
                elif any(x in name for x in ['produce', 'consume', 'message']):
                    categories['Message Operations'].append(name)
                elif any(x in name for x in ['connector', 'connect']):
                    categories['Connect Operations'].append(name)
                elif 'knox' in name:
                    categories['Knox Gateway'].append(name)
                elif 'cdp' in name:
                    categories['CDP Cloud'].append(name)
                elif any(x in name for x in ['health', 'metrics', 'monitor']):
                    categories['Monitoring'].append(name)
                else:
                    categories['Other'].append(name)
            
            for category, tools_list in categories.items():
                if tools_list:
                    print(f"   {category}: {len(tools_list)} tools")
                    for tool in tools_list[:3]:  # Show first 3 tools
                        print(f"     - {tool}")
                    if len(tools_list) > 3:
                        print(f"     ... and {len(tools_list) - 3} more")
        
        except Exception as e:
            print(f"❌ List Tools Error: {e}")
        
        print(f"\n🎉 Enhanced Features Test Completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_features()
