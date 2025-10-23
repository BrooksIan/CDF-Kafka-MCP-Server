"""
MCP server implementation for CDF Kafka MCP Server.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

from .config import load_config
from .kafka_client import KafkaClient, ProduceMessageRequest, ConsumeMessageRequest
from .knox_client import KnoxError


class CDFKafkaMCPServer:
    """CDF Kafka MCP Server implementation."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MCP server.

        Args:
            config_path: Path to configuration file
        """
        self.config = load_config(config_path)
        self.kafka_client: Optional[KafkaClient] = None
        self.logger = self._setup_logging()

        # Initialize Kafka client
        try:
            self.kafka_client = KafkaClient(self.config)
            self.logger.info("Kafka client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Kafka client: {e}")
            raise

    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration."""
        logger = logging.getLogger("cdf_kafka_mcp_server")
        logger.setLevel(getattr(logging, self.config.log_level))

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    async def list_tools(self, request: ListToolsRequest) -> ListToolsResult:
        """List available MCP tools."""
        tools = [
            # Topic Management Tools
            Tool(
                name="list_topics",
                description="List all Kafka topics",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="create_topic",
                description="Create a new Kafka topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Topic name"},
                        "partitions": {"type": "integer", "description": "Number of partitions", "default": 1},
                        "replication_factor": {"type": "integer", "description": "Replication factor", "default": 1},
                        "config": {"type": "object", "description": "Topic configuration", "additionalProperties": {"type": "string"}}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="describe_topic",
                description="Get detailed information about a topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Topic name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="delete_topic",
                description="Delete a Kafka topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Topic name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="topic_exists",
                description="Check if a topic exists",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Topic name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="get_topic_partitions",
                description="Get the number of partitions for a topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Topic name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="update_topic_config",
                description="Update topic configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Topic name"},
                        "config": {"type": "object", "description": "Configuration to update", "additionalProperties": {"type": "string"}}
                    },
                    "required": ["name", "config"]
                }
            ),

            # Message Operations
            Tool(
                name="produce_message",
                description="Produce a message to a topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic name"},
                        "key": {"type": "string", "description": "Message key"},
                        "value": {"type": "string", "description": "Message value"},
                        "headers": {"type": "object", "description": "Message headers", "additionalProperties": {"type": "string"}}
                    },
                    "required": ["topic", "value"]
                }
            ),
            Tool(
                name="consume_messages",
                description="Consume messages from a topic",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic name"},
                        "partition": {"type": "integer", "description": "Partition number"},
                        "offset": {"type": "integer", "description": "Starting offset", "default": 0},
                        "max_count": {"type": "integer", "description": "Maximum number of messages", "default": 10},
                        "timeout": {"type": "integer", "description": "Timeout in seconds", "default": 5}
                    },
                    "required": ["topic"]
                }
            ),
            Tool(
                name="get_topic_offsets",
                description="Get earliest and latest offsets for a topic partition",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic name"},
                        "partition": {"type": "integer", "description": "Partition number"}
                    },
                    "required": ["topic", "partition"]
                }
            ),

            # System Information
            Tool(
                name="get_broker_info",
                description="Get information about Kafka brokers",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="get_cluster_metadata",
                description="Get cluster metadata",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="test_connection",
                description="Test the connection to Kafka",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),

            # Kafka Connect Management Tools
            Tool(
                name="list_connectors",
                description="List all Kafka Connect connectors",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="create_connector",
                description="Create a new Kafka Connect connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"},
                        "config": {"type": "object", "description": "Connector configuration", "additionalProperties": {"type": "string"}}
                    },
                    "required": ["name", "config"]
                }
            ),
            Tool(
                name="get_connector",
                description="Get information about a specific connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="get_connector_status",
                description="Get the status of a specific connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="get_connector_config",
                description="Get the configuration of a specific connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="update_connector_config",
                description="Update the configuration of a specific connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"},
                        "config": {"type": "object", "description": "New connector configuration", "additionalProperties": {"type": "string"}}
                    },
                    "required": ["name", "config"]
                }
            ),
            Tool(
                name="delete_connector",
                description="Delete a specific connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="pause_connector",
                description="Pause a specific connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="resume_connector",
                description="Resume a paused connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="restart_connector",
                description="Restart a specific connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="get_connector_tasks",
                description="Get information about connector tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="get_connector_active_topics",
                description="Get active topics for a connector",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "Connector name"}
                    },
                    "required": ["name"]
                }
            ),
            Tool(
                name="list_connector_plugins",
                description="List available connector plugins",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="validate_connector_config",
                description="Validate connector configuration",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "plugin_name": {"type": "string", "description": "Plugin name"},
                        "config": {"type": "object", "description": "Configuration to validate", "additionalProperties": {"type": "string"}}
                    },
                    "required": ["plugin_name", "config"]
                }
            ),
            Tool(
                name="get_connect_server_info",
                description="Get Kafka Connect server information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
        ]

        # Add Knox-specific tools if enabled
        if self.config.is_knox_enabled():
            tools.extend([
                Tool(
                    name="test_knox_connection",
                    description="Test the connection to Knox Gateway",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_knox_metadata",
                    description="Get metadata from Knox Gateway",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
            ])

        return ListToolsResult(tools=tools)

    async def call_tool(self, request: CallToolRequest) -> CallToolResult:
        """Handle tool calls."""
        try:
            # Extract tool name and arguments from request
            tool_name = request.params.name
            arguments = request.params.arguments or {}
            
            self.logger.info(f"Calling tool: {tool_name}")

            # Route to appropriate handler
            if tool_name == "list_topics":
                result = await self._handle_list_topics(arguments)
            elif tool_name == "create_topic":
                result = await self._handle_create_topic(arguments)
            elif tool_name == "describe_topic":
                result = await self._handle_describe_topic(arguments)
            elif tool_name == "delete_topic":
                result = await self._handle_delete_topic(arguments)
            elif tool_name == "topic_exists":
                result = await self._handle_topic_exists(arguments)
            elif tool_name == "get_topic_partitions":
                result = await self._handle_get_topic_partitions(arguments)
            elif tool_name == "update_topic_config":
                result = await self._handle_update_topic_config(arguments)
            elif tool_name == "produce_message":
                result = await self._handle_produce_message(arguments)
            elif tool_name == "consume_messages":
                result = await self._handle_consume_messages(arguments)
            elif tool_name == "get_topic_offsets":
                result = await self._handle_get_topic_offsets(arguments)
            elif tool_name == "get_broker_info":
                result = await self._handle_get_broker_info(arguments)
            elif tool_name == "get_cluster_metadata":
                result = await self._handle_get_cluster_metadata(arguments)
            elif tool_name == "test_connection":
                result = await self._handle_test_connection(arguments)
            elif tool_name == "list_connectors":
                result = await self._handle_list_connectors(arguments)
            elif tool_name == "create_connector":
                result = await self._handle_create_connector(arguments)
            elif tool_name == "get_connector":
                result = await self._handle_get_connector(arguments)
            elif tool_name == "get_connector_status":
                result = await self._handle_get_connector_status(arguments)
            elif tool_name == "get_connector_config":
                result = await self._handle_get_connector_config(arguments)
            elif tool_name == "update_connector_config":
                result = await self._handle_update_connector_config(arguments)
            elif tool_name == "delete_connector":
                result = await self._handle_delete_connector(arguments)
            elif tool_name == "pause_connector":
                result = await self._handle_pause_connector(arguments)
            elif tool_name == "resume_connector":
                result = await self._handle_resume_connector(arguments)
            elif tool_name == "restart_connector":
                result = await self._handle_restart_connector(arguments)
            elif tool_name == "get_connector_tasks":
                result = await self._handle_get_connector_tasks(arguments)
            elif tool_name == "get_connector_active_topics":
                result = await self._handle_get_connector_active_topics(arguments)
            elif tool_name == "list_connector_plugins":
                result = await self._handle_list_connector_plugins(arguments)
            elif tool_name == "validate_connector_config":
                result = await self._handle_validate_connector_config(arguments)
            elif tool_name == "get_connect_server_info":
                result = await self._handle_get_connect_server_info(arguments)
            elif tool_name == "test_knox_connection":
                result = await self._handle_test_knox_connection(arguments)
            elif tool_name == "get_knox_metadata":
                result = await self._handle_get_knox_metadata(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps(result, indent=2))]
            )

        except Exception as e:
            self.logger.error(f"Error in tool {tool_name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]
            )

    # Tool Handlers

    async def _handle_list_topics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_topics tool."""
        topics = self.kafka_client.list_topics()
        return {"topics": topics, "count": len(topics)}

    async def _handle_create_topic(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_topic tool."""
        name = arguments["name"]
        partitions = arguments.get("partitions", 1)
        replication_factor = arguments.get("replication_factor", 1)
        config = arguments.get("config", {})

        self.kafka_client.create_topic(name, partitions, replication_factor, config)
        return {
            "message": f"Topic '{name}' created successfully",
            "topic": name,
            "partitions": partitions,
            "replication_factor": replication_factor
        }

    async def _handle_describe_topic(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle describe_topic tool."""
        name = arguments["name"]
        topic_info = self.kafka_client.describe_topic(name)

        return {
            "name": topic_info.name,
            "partitions": topic_info.partitions,
            "replication_factor": topic_info.replication_factor,
            "config": topic_info.config,
            "partition_details": topic_info.partition_details
        }

    async def _handle_delete_topic(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_topic tool."""
        name = arguments["name"]
        self.kafka_client.delete_topic(name)
        return {"message": f"Topic '{name}' deleted successfully", "topic": name}

    async def _handle_topic_exists(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle topic_exists tool."""
        name = arguments["name"]
        exists = self.kafka_client.topic_exists(name)
        return {"topic": name, "exists": exists}

    async def _handle_get_topic_partitions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_topic_partitions tool."""
        name = arguments["name"]
        partitions = self.kafka_client.get_topic_partitions(name)
        return {"topic": name, "partitions": partitions}

    async def _handle_update_topic_config(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_topic_config tool."""
        name = arguments["name"]
        config = arguments["config"]
        self.kafka_client.update_topic_config(name, config)
        return {
            "message": f"Topic '{name}' configuration updated successfully",
            "topic": name,
            "config": config
        }

    async def _handle_produce_message(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle produce_message tool."""
        request = ProduceMessageRequest(
            topic=arguments["topic"],
            key=arguments.get("key"),
            value=arguments["value"],
            headers=arguments.get("headers")
        )

        message = self.kafka_client.produce_message(request)
        return {
            "topic": message.topic,
            "partition": message.partition,
            "offset": message.offset,
            "key": message.key,
            "value": message.value,
            "headers": message.headers,
            "timestamp": message.timestamp.isoformat()
        }

    async def _handle_consume_messages(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle consume_messages tool."""
        request = ConsumeMessageRequest(
            topic=arguments["topic"],
            partition=arguments.get("partition"),
            offset=arguments.get("offset", 0),
            max_count=arguments.get("max_count", 10),
            timeout=arguments.get("timeout", 5)
        )

        messages = self.kafka_client.consume_messages(request)
        return {
            "messages": [
                {
                    "topic": msg.topic,
                    "partition": msg.partition,
                    "offset": msg.offset,
                    "key": msg.key,
                    "value": msg.value,
                    "headers": msg.headers,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in messages
            ],
            "count": len(messages)
        }

    async def _handle_get_topic_offsets(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_topic_offsets tool."""
        topic = arguments["topic"]
        partition = arguments["partition"]

        earliest, latest = self.kafka_client.get_topic_offsets(topic, partition)
        return {
            "topic": topic,
            "partition": partition,
            "earliest": earliest,
            "latest": latest
        }

    async def _handle_get_broker_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_broker_info tool."""
        brokers = self.kafka_client.get_brokers()
        return {
            "brokers": brokers,
            "client_id": self.config.kafka.client_id,
            "security_protocol": self.config.kafka.security_protocol,
            "knox_enabled": self.kafka_client.is_knox_enabled()
        }

    async def _handle_get_cluster_metadata(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_cluster_metadata tool."""
        brokers = self.kafka_client.get_brokers()
        return {
            "brokers": brokers,
            "client_id": self.config.kafka.client_id,
            "security_protocol": self.config.kafka.security_protocol,
            "knox_enabled": self.kafka_client.is_knox_enabled(),
            "version": "1.0.0"
        }

    async def _handle_test_connection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle test_connection tool."""
        connected = self.kafka_client.test_connection()
        return {
            "connected": connected,
            "message": "Successfully connected to Kafka" if connected else "Failed to connect to Kafka"
        }

    async def _handle_test_knox_connection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle test_knox_connection tool."""
        if not self.config.is_knox_enabled():
            return {
                "connected": False,
                "error": "Knox authentication is not enabled"
            }

        connected = self.kafka_client.knox_client.test_connection()
        return {
            "connected": connected,
            "message": "Successfully connected to Knox Gateway" if connected else "Failed to connect to Knox Gateway"
        }

    async def _handle_get_knox_metadata(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_knox_metadata tool."""
        if not self.config.is_knox_enabled():
            return {"error": "Knox authentication is not enabled"}

        try:
            metadata = self.kafka_client.knox_client.get_kafka_metadata()
            return {
                "metadata": metadata,
                "message": "Successfully retrieved metadata from Knox Gateway"
            }
        except KnoxError as e:
            return {"error": str(e)}

    # Kafka Connect Tool Handlers

    async def _handle_list_connectors(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_connectors tool."""
        connectors = self.kafka_client.list_connectors()
        return {"connectors": connectors, "count": len(connectors)}

    async def _handle_create_connector(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_connector tool."""
        name = arguments["name"]
        config = arguments["config"]

        result = self.kafka_client.create_connector(name, config)
        return {
            "message": f"Connector '{name}' created successfully",
            "connector": name,
            "config": config,
            "result": result
        }

    async def _handle_get_connector(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_connector tool."""
        name = arguments["name"]
        connector_info = self.kafka_client.get_connector(name)
        return connector_info

    async def _handle_get_connector_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_connector_status tool."""
        name = arguments["name"]
        status = self.kafka_client.get_connector_status(name)
        return {"connector": name, "status": status}

    async def _handle_get_connector_config(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_connector_config tool."""
        name = arguments["name"]
        config = self.kafka_client.get_connector_config(name)
        return {"connector": name, "config": config}

    async def _handle_update_connector_config(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_connector_config tool."""
        name = arguments["name"]
        config = arguments["config"]

        result = self.kafka_client.update_connector_config(name, config)
        return {
            "message": f"Connector '{name}' configuration updated successfully",
            "connector": name,
            "config": config,
            "result": result
        }

    async def _handle_delete_connector(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle delete_connector tool."""
        name = arguments["name"]
        self.kafka_client.delete_connector(name)
        return {"message": f"Connector '{name}' deleted successfully", "connector": name}

    async def _handle_pause_connector(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pause_connector tool."""
        name = arguments["name"]
        self.kafka_client.pause_connector(name)
        return {"message": f"Connector '{name}' paused successfully", "connector": name}

    async def _handle_resume_connector(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle resume_connector tool."""
        name = arguments["name"]
        self.kafka_client.resume_connector(name)
        return {"message": f"Connector '{name}' resumed successfully", "connector": name}

    async def _handle_restart_connector(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle restart_connector tool."""
        name = arguments["name"]
        self.kafka_client.restart_connector(name)
        return {"message": f"Connector '{name}' restarted successfully", "connector": name}

    async def _handle_get_connector_tasks(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_connector_tasks tool."""
        name = arguments["name"]
        tasks = self.kafka_client.get_connector_tasks(name)
        return {"connector": name, "tasks": tasks}

    async def _handle_get_connector_active_topics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_connector_active_topics tool."""
        name = arguments["name"]
        topics = self.kafka_client.get_connector_active_topics(name)
        return {"connector": name, "active_topics": topics}

    async def _handle_list_connector_plugins(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_connector_plugins tool."""
        plugins = self.kafka_client.list_connector_plugins()
        return {"plugins": plugins, "count": len(plugins)}

    async def _handle_validate_connector_config(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validate_connector_config tool."""
        plugin_name = arguments["plugin_name"]
        config = arguments["config"]

        validation_result = self.kafka_client.validate_connector_config(plugin_name, config)
        return {
            "plugin_name": plugin_name,
            "config": config,
            "validation": validation_result
        }

    async def _handle_get_connect_server_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_connect_server_info tool."""
        server_info = self.kafka_client.get_connect_server_info()
        return {"server_info": server_info}

    async def run(self) -> None:
        """Run the MCP server."""
        self.logger.info("Starting CDF Kafka MCP Server...")

        # Create MCP server
        server = Server("cdf-kafka-mcp-server")

        # Register handlers
        server.list_tools = self.list_tools
        server.call_tool = self.call_tool

        # Run server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="cdf-kafka-mcp-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )
