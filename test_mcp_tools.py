#!/usr/bin/env python3
"""
Test script for MCP tools with environment variables
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import ListToolsRequest

async def test_mcp_tools():
    """Test MCP tools with environment variables."""
    print('🚀 Testing MCP Tools with Environment Variables')
    print('=' * 60)
    
    try:
        # Initialize MCP server
        server = CDFKafkaMCPServer('config/kafka_config_cdp_corrected.yaml')
        print('✅ MCP server initialized successfully')
        
        # Test list_tools
        print('\n🔧 Testing list_tools...')
        try:
            request = ListToolsRequest()
            tools_result = await server.list_tools(request)
            tools = tools_result.tools
            print(f'   ✅ Found {len(tools)} tools')
            for tool in tools[:5]:  # Show first 5 tools
                print(f'      - {tool.name}: {tool.description[:50]}...')
            if len(tools) > 5:
                print(f'      ... and {len(tools) - 5} more')
        except Exception as e:
            print(f'   ❌ list_tools failed: {e}')
        
        # Test basic tools
        tools_to_test = [
            ('test_connection', {}),
            ('list_topics', {}),
            ('get_cdp_clusters', {}),
            ('test_authentication', {}),
            ('discover_auth_endpoints', {}),
        ]
        
        for tool_name, args in tools_to_test:
            try:
                print(f'\n🔧 Testing {tool_name}...')
                
                if tool_name == 'test_connection':
                    result = await server._handle_test_connection(args)
                    print(f'   ✅ Connection test: {result.get("status", "unknown")}')
                    
                elif tool_name == 'list_topics':
                    result = await server._handle_list_topics(args)
                    print(f'   ✅ Topics found: {result.get("count", 0)}')
                    print(f'   📋 Method used: {result.get("method", "unknown")}')
                    
                elif tool_name == 'get_cdp_clusters':
                    result = await server._handle_get_cdp_clusters(args)
                    print(f'   ✅ Clusters found: {result.get("count", 0)}')
                    print(f'   📋 Method used: {result.get("method", "unknown")}')
                    
                elif tool_name == 'test_authentication':
                    result = await server._handle_test_authentication(args)
                    print(f'   ✅ Auth test: {result.get("status", "unknown")}')
                    
                elif tool_name == 'discover_auth_endpoints':
                    result = await server._handle_discover_auth_endpoints(args)
                    print(f'   ✅ Endpoints discovered: {len(result.get("endpoints", {}))}')
                    
            except Exception as e:
                print(f'   ❌ {tool_name} failed: {e}')
        
        print('\n🎉 MCP tools testing completed!')
        
    except Exception as e:
        print(f'❌ Error initializing MCP server: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Load environment variables
    env_file = Path(__file__).parent / "config" / "env_current.txt"
    if env_file.exists():
        print(f"📁 Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # Run the test
    asyncio.run(test_mcp_tools())
