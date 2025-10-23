#!/usr/bin/env python3
"""
MCP Tools Testing Suite for CDF Kafka MCP Server
Tests all MCP tools functionality including Kafka Connect operations
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from cdf_kafka_mcp_server.config import Config

class MCPToolsTester:
    def __init__(self):
        self.mcp_server = None
        self.test_results = {}
        self.test_topic = "mcp-tools-test-topic"
        
    async def setup(self):
        """Setup the MCP server for testing"""
        print("🔧 Setting up MCP server for testing...")
        try:
            # Set environment variables for testing
            os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"
            
            # Initialize MCP server
            self.mcp_server = CDFKafkaMCPServer()
            print("✅ MCP server initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to setup MCP server: {e}")
            return False
    
    async def test_tool_registration(self):
        """Test that all expected tools are registered"""
        print("\n🧪 Testing tool registration...")
        
        expected_tools = [
            # Basic Kafka tools
            "list_topics", "create_topic", "delete_topic", "describe_topic",
            "produce_message", "consume_messages", "get_topic_info",
            
            # Knox tools
            "get_knox_token", "refresh_knox_token", "validate_knox_token",
            
            # Kafka Connect tools
            "list_connectors", "create_connector", "get_connector", 
            "get_connector_status", "get_connector_config", "update_connector_config",
            "delete_connector", "pause_connector", "resume_connector", 
            "restart_connector", "get_connector_tasks", "get_connector_active_topics",
            "list_connector_plugins", "validate_connector_config", "get_connect_server_info"
        ]
        
        try:
            # Get available tools from MCP server
            available_tools = []
            for tool in self.mcp_server.tools:
                available_tools.append(tool.name)
            
            missing_tools = set(expected_tools) - set(available_tools)
            extra_tools = set(available_tools) - set(expected_tools)
            
            if missing_tools:
                print(f"❌ Missing expected tools: {missing_tools}")
                self.test_results["tool_registration"] = False
            else:
                print(f"✅ All {len(expected_tools)} expected tools are registered")
                self.test_results["tool_registration"] = True
            
            if extra_tools:
                print(f"ℹ️  Extra tools found: {extra_tools}")
                
        except Exception as e:
            print(f"❌ Tool registration test failed: {e}")
            self.test_results["tool_registration"] = False
    
    async def test_list_topics_tool(self):
        """Test the list_topics tool"""
        print("\n🧪 Testing list_topics tool...")
        
        try:
            result = await self.mcp_server.call_tool("list_topics", {})
            
            if result and "topics" in result:
                topics = result["topics"]
                print(f"✅ Successfully listed {len(topics)} topics: {topics}")
                self.test_results["list_topics"] = True
            else:
                print(f"❌ Unexpected result format: {result}")
                self.test_results["list_topics"] = False
                
        except Exception as e:
            print(f"❌ list_topics test failed: {e}")
            self.test_results["list_topics"] = False
    
    async def test_create_topic_tool(self):
        """Test the create_topic tool"""
        print(f"\n🧪 Testing create_topic tool for '{self.test_topic}'...")
        
        try:
            # First, try to delete the topic if it exists
            try:
                await self.mcp_server.call_tool("delete_topic", {"topic_name": self.test_topic})
                time.sleep(1)
            except:
                pass  # Topic might not exist
            
            # Create the topic
            result = await self.mcp_server.call_tool("create_topic", {
                "topic_name": self.test_topic,
                "partitions": 1,
                "replication_factor": 1
            })
            
            if result and "success" in result:
                print(f"✅ Successfully created topic '{self.test_topic}'")
                self.test_results["create_topic"] = True
            else:
                print(f"❌ Unexpected result format: {result}")
                self.test_results["create_topic"] = False
                
        except Exception as e:
            print(f"❌ create_topic test failed: {e}")
            self.test_results["create_topic"] = False
    
    async def test_produce_message_tool(self):
        """Test the produce_message tool"""
        print(f"\n🧪 Testing produce_message tool...")
        
        try:
            test_message = '{"test": "MCP tools test message", "timestamp": "' + str(int(time.time())) + '"}'
            
            result = await self.mcp_server.call_tool("produce_message", {
                "topic_name": self.test_topic,
                "message": test_message,
                "key": "test-key"
            })
            
            if result and "success" in result:
                print(f"✅ Successfully produced message to '{self.test_topic}'")
                self.test_results["produce_message"] = True
            else:
                print(f"❌ Unexpected result format: {result}")
                self.test_results["produce_message"] = False
                
        except Exception as e:
            print(f"❌ produce_message test failed: {e}")
            self.test_results["produce_message"] = False
    
    async def test_consume_messages_tool(self):
        """Test the consume_messages tool"""
        print(f"\n🧪 Testing consume_messages tool...")
        
        try:
            result = await self.mcp_server.call_tool("consume_messages", {
                "topic_name": self.test_topic,
                "max_count": 1,
                "timeout": 5
            })
            
            if result and "messages" in result:
                messages = result["messages"]
                print(f"✅ Successfully consumed {len(messages)} messages from '{self.test_topic}'")
                self.test_results["consume_messages"] = True
            else:
                print(f"❌ Unexpected result format: {result}")
                self.test_results["consume_messages"] = False
                
        except Exception as e:
            print(f"❌ consume_messages test failed: {e}")
            self.test_results["consume_messages"] = False
    
    async def test_kafka_connect_tools(self):
        """Test Kafka Connect related tools"""
        print(f"\n🧪 Testing Kafka Connect tools...")
        
        connect_tools = [
            "list_connectors",
            "list_connector_plugins", 
            "get_connect_server_info"
        ]
        
        for tool_name in connect_tools:
            try:
                print(f"  Testing {tool_name}...")
                result = await self.mcp_server.call_tool(tool_name, {})
                
                if result:
                    print(f"  ✅ {tool_name} succeeded")
                    self.test_results[f"connect_{tool_name}"] = True
                else:
                    print(f"  ❌ {tool_name} returned empty result")
                    self.test_results[f"connect_{tool_name}"] = False
                    
            except Exception as e:
                print(f"  ❌ {tool_name} failed: {e}")
                self.test_results[f"connect_{tool_name}"] = False
    
    async def test_knox_tools(self):
        """Test Knox Gateway related tools"""
        print(f"\n🧪 Testing Knox Gateway tools...")
        
        knox_tools = [
            "get_knox_token",
            "validate_knox_token"
        ]
        
        for tool_name in knox_tools:
            try:
                print(f"  Testing {tool_name}...")
                result = await self.mcp_server.call_tool(tool_name, {})
                
                if result:
                    print(f"  ✅ {tool_name} succeeded")
                    self.test_results[f"knox_{tool_name}"] = True
                else:
                    print(f"  ❌ {tool_name} returned empty result")
                    self.test_results[f"knox_{tool_name}"] = False
                    
            except Exception as e:
                print(f"  ❌ {tool_name} failed: {e}")
                self.test_results[f"knox_{tool_name}"] = False
    
    async def cleanup(self):
        """Cleanup test resources"""
        print(f"\n🧹 Cleaning up test resources...")
        
        try:
            # Delete test topic
            await self.mcp_server.call_tool("delete_topic", {"topic_name": self.test_topic})
            print(f"✅ Cleaned up test topic '{self.test_topic}'")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("📊 MCP TOOLS TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        if failed_tests > 0:
            print(f"\n⚠️  {failed_tests} tests failed. Check the logs above for details.")
        else:
            print(f"\n🎉 All tests passed!")

async def main():
    """Main test runner"""
    print("🚀 Starting MCP Tools Testing Suite")
    print("="*50)
    
    tester = MCPToolsTester()
    
    # Setup
    if not await tester.setup():
        print("❌ Setup failed, exiting")
        return
    
    try:
        # Run all tests
        await tester.test_tool_registration()
        await tester.test_list_topics_tool()
        await tester.test_create_topic_tool()
        await tester.test_produce_message_tool()
        await tester.test_consume_messages_tool()
        await tester.test_kafka_connect_tools()
        await tester.test_knox_tools()
        
    finally:
        # Cleanup
        await tester.cleanup()
        
        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
