#!/usr/bin/env python3
"""
CDP Cloud MCP Tools Test Script
Tests all MCP tools against CDP Cloud configuration with Knox Gateway authentication.
"""

import asyncio
import json
import logging
import os
import sys
import time
from typing import Dict, List, Any, Optional

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from cdf_kafka_mcp_server.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CDPCloudMCPTester:
    """Test all MCP tools against CDP Cloud configuration."""
    
    def __init__(self):
        self.server = None
        self.test_results = {}
        self.test_topic_prefix = "cdp-cloud-test-"
        self.test_message_count = 3
        
    async def setup(self):
        """Initialize the MCP server with CDP Cloud configuration."""
        try:
            logger.info("🚀 Initializing MCP server with CDP Cloud configuration...")
            
            # Get config path
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
            logger.info(f"✅ Using config file: {config_path}")
            
            # Load configuration to verify it
            config = load_config(config_path)
            logger.info(f"✅ Configuration loaded: {config.kafka.bootstrap_servers}")
            logger.info(f"✅ Knox Gateway: {config.knox.gateway}")
            logger.info(f"✅ Security Protocol: {config.kafka.security_protocol}")
            
            # Initialize MCP server with config path
            self.server = CDFKafkaMCPServer(config_path)
            
            logger.info("✅ MCP server initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP server: {e}")
            return False
    
    async def test_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> Dict[str, Any]:
        """Test a single MCP tool."""
        if arguments is None:
            arguments = {}
            
        try:
            logger.info(f"🧪 Testing tool: {tool_name}")
            
            # Create a mock request object
            class MockRequest:
                def __init__(self, name: str, args: Dict[str, Any]):
                    self.params = MockParams(name, args)
            
            class MockParams:
                def __init__(self, name: str, args: Dict[str, Any]):
                    self.name = name
                    self.arguments = args
            
            request = MockRequest(tool_name, arguments)
            
            # Call the tool
            start_time = time.time()
            result = await self.server.call_tool(request)
            end_time = time.time()
            
            # Parse result
            if result.content and len(result.content) > 0:
                try:
                    result_data = json.loads(result.content[0].text)
                except json.JSONDecodeError:
                    result_data = {"raw_response": result.content[0].text}
            else:
                result_data = {"error": "No content returned"}
            
            return {
                "success": True,
                "tool": tool_name,
                "arguments": arguments,
                "result": result_data,
                "duration": end_time - start_time,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"❌ Tool {tool_name} failed: {e}")
            return {
                "success": False,
                "tool": tool_name,
                "arguments": arguments,
                "error": str(e),
                "duration": 0,
                "timestamp": time.time()
            }
    
    async def test_connection_tools(self):
        """Test connection and basic functionality tools."""
        logger.info("🔌 Testing connection tools...")
        
        tools = [
            ("test_connection", {}),
            ("get_broker_info", {}),
            ("get_cluster_metadata", {}),
            ("test_knox_connection", {}),
            ("get_knox_metadata", {})
        ]
        
        for tool_name, args in tools:
            result = await self.test_tool(tool_name, args)
            self.test_results[tool_name] = result
    
    async def test_topic_management_tools(self):
        """Test topic management tools."""
        logger.info("📁 Testing topic management tools...")
        
        # Test topic name
        test_topic = f"{self.test_topic_prefix}topic-{int(time.time())}"
        
        tools = [
            ("list_topics", {}),
            ("topic_exists", {"name": test_topic}),
            ("create_topic", {
                "name": test_topic,
                "partitions": 3,
                "replication_factor": 1,
                "config": {"cleanup.policy": "delete"}
            }),
            ("topic_exists", {"name": test_topic}),
            ("describe_topic", {"name": test_topic}),
            ("get_topic_partitions", {"name": test_topic}),
            ("update_topic_config", {
                "name": test_topic,
                "config": {"retention.ms": "3600000"}
            }),
            ("get_topic_offsets", {"name": test_topic}),
            ("delete_topic", {"name": test_topic}),
            ("topic_exists", {"name": test_topic})
        ]
        
        for tool_name, args in tools:
            result = await self.test_tool(tool_name, args)
            self.test_results[tool_name] = result
            # Small delay between topic operations
            await asyncio.sleep(0.5)
    
    async def test_message_operations_tools(self):
        """Test message production and consumption tools."""
        logger.info("💬 Testing message operations tools...")
        
        # Create a test topic for message operations
        test_topic = f"{self.test_topic_prefix}messages-{int(time.time())}"
        
        # Create topic first
        await self.test_tool("create_topic", {
            "name": test_topic,
            "partitions": 2,
            "replication_factor": 1
        })
        
        # Wait a moment for topic creation
        await asyncio.sleep(1)
        
        # Test message production
        for i in range(self.test_message_count):
            await self.test_tool("produce_message", {
                "topic": test_topic,
                "key": f"test-key-{i}",
                "value": f"Test message {i} for CDP Cloud",
                "headers": {
                    "source": "cdp-cloud-test",
                    "timestamp": str(int(time.time())),
                    "message_id": str(i)
                }
            })
            await asyncio.sleep(0.2)  # Small delay between messages
        
        # Test message consumption
        await self.test_tool("consume_messages", {
            "topic": test_topic,
            "max_messages": self.test_message_count,
            "timeout": 10
        })
        
        # Clean up
        await self.test_tool("delete_topic", {"name": test_topic})
    
    async def test_kafka_connect_tools(self):
        """Test Kafka Connect management tools."""
        logger.info("🔗 Testing Kafka Connect tools...")
        
        tools = [
            ("list_connectors", {}),
            ("get_connect_server_info", {}),
            ("list_connector_plugins", {}),
            ("validate_connector_config", {
                "connector_class": "org.apache.kafka.connect.file.FileStreamSourceConnector",
                "config": {
                    "file": "/tmp/test.txt",
                    "topic": "test-topic"
                }
            })
        ]
        
        for tool_name, args in tools:
            result = await self.test_tool(tool_name, args)
            self.test_results[tool_name] = result
    
    async def test_connector_lifecycle_tools(self):
        """Test connector lifecycle management tools."""
        logger.info("🔄 Testing connector lifecycle tools...")
        
        # Create a test connector
        connector_name = f"cdp-cloud-test-connector-{int(time.time())}"
        
        # Test connector creation
        await self.test_tool("create_connector", {
            "name": connector_name,
            "config": {
                "connector.class": "org.apache.kafka.connect.tools.MockSourceConnector",
                "tasks.max": "1",
                "topics": f"{self.test_topic_prefix}connector-test"
            }
        })
        
        # Wait for connector to start
        await asyncio.sleep(2)
        
        # Test connector management tools
        tools = [
            ("get_connector", {"name": connector_name}),
            ("get_connector_status", {"name": connector_name}),
            ("get_connector_config", {"name": connector_name}),
            ("get_connector_tasks", {"name": connector_name}),
            ("get_connector_active_topics", {"name": connector_name}),
            ("pause_connector", {"name": connector_name}),
            ("resume_connector", {"name": connector_name}),
            ("restart_connector", {"name": connector_name}),
            ("update_connector_config", {
                "name": connector_name,
                "config": {
                    "connector.class": "org.apache.kafka.connect.tools.MockSourceConnector",
                    "tasks.max": "2",
                    "topics": f"{self.test_topic_prefix}connector-test-updated"
                }
            })
        ]
        
        for tool_name, args in tools:
            result = await self.test_tool(tool_name, args)
            self.test_results[tool_name] = result
            await asyncio.sleep(0.5)
        
        # Clean up connector
        await self.test_tool("delete_connector", {"name": connector_name})
    
    async def run_all_tests(self):
        """Run all MCP tool tests."""
        logger.info("🚀 Starting CDP Cloud MCP Tools Test Suite")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Initialize server
            if not await self.setup():
                logger.error("❌ Failed to initialize MCP server")
                return False
            
            # Run test suites
            await self.test_connection_tools()
            await self.test_topic_management_tools()
            await self.test_message_operations_tools()
            await self.test_kafka_connect_tools()
            await self.test_connector_lifecycle_tools()
            
            end_time = time.time()
            total_duration = end_time - start_time
            
            # Generate summary
            await self.generate_summary(total_duration)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Test suite failed: {e}")
            return False
    
    async def generate_summary(self, total_duration: float):
        """Generate test summary and save results."""
        logger.info("📊 Generating test summary...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - successful_tests
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Categorize results
        categories = {
            "Connection Tools": ["test_connection", "get_broker_info", "get_cluster_metadata", "test_knox_connection", "get_knox_metadata"],
            "Topic Management": ["list_topics", "create_topic", "describe_topic", "delete_topic", "topic_exists", "get_topic_partitions", "update_topic_config", "get_topic_offsets"],
            "Message Operations": ["produce_message", "consume_messages"],
            "Kafka Connect": ["list_connectors", "get_connect_server_info", "list_connector_plugins", "validate_connector_config"],
            "Connector Lifecycle": ["create_connector", "get_connector", "get_connector_status", "get_connector_config", "get_connector_tasks", "get_connector_active_topics", "pause_connector", "resume_connector", "restart_connector", "update_connector_config", "delete_connector"]
        }
        
        # Print summary
        logger.info("=" * 60)
        logger.info("📊 CDP CLOUD MCP TOOLS TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        logger.info(f"🧪 Total Tests: {total_tests}")
        logger.info(f"✅ Successful: {successful_tests}")
        logger.info(f"❌ Failed: {failed_tests}")
        logger.info(f"📈 Success Rate: {success_rate:.1f}%")
        logger.info("")
        
        # Print category breakdown
        for category, tools in categories.items():
            category_tests = [tool for tool in tools if tool in self.test_results]
            category_success = sum(1 for tool in category_tests if self.test_results[tool]["success"])
            category_total = len(category_tests)
            category_rate = (category_success / category_total * 100) if category_total > 0 else 0
            
            logger.info(f"📁 {category}: {category_success}/{category_total} ({category_rate:.1f}%)")
        
        logger.info("")
        
        # Print failed tests
        failed_tools = [tool for tool, result in self.test_results.items() if not result["success"]]
        if failed_tools:
            logger.info("❌ Failed Tools:")
            for tool in failed_tools:
                error = self.test_results[tool].get("error", "Unknown error")
                logger.info(f"   - {tool}: {error}")
        else:
            logger.info("🎉 All tests passed!")
        
        # Save detailed results
        results_file = f"cdp_cloud_mcp_test_results_{int(time.time())}.json"
        with open(results_file, 'w') as f:
            json.dump({
                "summary": {
                    "total_tests": total_tests,
                    "successful_tests": successful_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "total_duration": total_duration,
                    "timestamp": time.time()
                },
                "results": self.test_results
            }, f, indent=2)
        
        logger.info(f"📄 Detailed results saved to: {results_file}")
        logger.info("=" * 60)

async def main():
    """Main function to run the CDP Cloud MCP tools test."""
    print("🚀 CDP Cloud MCP Tools Test Suite")
    print("=" * 50)
    print("Testing all MCP tools against CDP Cloud configuration")
    print("with Knox Gateway authentication")
    print("=" * 50)
    
    tester = CDPCloudMCPTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Test suite failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
