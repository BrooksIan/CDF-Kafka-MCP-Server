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
from .cdp_kafka_client import CDPKafkaClient
from .cdp_rest_client import CDPRestClient
from .knox_client import KnoxError
from .knox_gateway import KnoxGatewayClient, KnoxKafkaClient
from .cdp_client import CDPClient, CDPError
from .monitoring import HealthMonitor, MetricsCollector


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
        self.cdp_kafka_client: Optional[CDPKafkaClient] = None
        self.cdp_rest_client: Optional[CDPRestClient] = None
        self.knox_gateway_client: Optional[KnoxGatewayClient] = None
        self.knox_kafka_client: Optional[KnoxKafkaClient] = None
        self.cdp_client: Optional[CDPClient] = None
        self.health_monitor: Optional[HealthMonitor] = None
        self.metrics_collector: Optional[MetricsCollector] = None
        self.logger = self._setup_logging()

        # Initialize Knox Gateway client if configured
        if hasattr(self.config, 'knox') and self.config.knox.gateway:
            try:
                self.knox_gateway_client = KnoxGatewayClient(
                    gateway_url=self.config.knox.gateway,
                    username=self.config.knox.username,
                    password=self.config.knox.password
                )
                self.knox_kafka_client = KnoxKafkaClient(self.knox_gateway_client)
                self.logger.info("Knox Gateway client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize Knox Gateway client: {e}")

        # Initialize CDP REST client for cloud environments
        if hasattr(self.config, 'kafka') and self.config.kafka.bootstrap_servers:
            try:
                # Extract base URL from bootstrap servers
                bootstrap_server = self.config.kafka.bootstrap_servers[0]
                if ':' in bootstrap_server:
                    base_url = f"https://{bootstrap_server.split(':')[0]}:{bootstrap_server.split(':')[1]}"
                else:
                    base_url = f"https://{bootstrap_server}"
                
                self.cdp_rest_client = CDPRestClient(
                    base_url=base_url,
                    username=getattr(self.config.kafka, 'sasl_username', 'ibrooks'),
                    password=getattr(self.config.kafka, 'sasl_password', 'Admin12345#'),
                    cluster_id=getattr(self.config.kafka, 'cluster_id', 'irb-kakfa-only'),
                    verify_ssl=getattr(self.config.kafka, 'verify_ssl', False),
                    token=getattr(self.config.knox, 'token', None),
                    auth_method=getattr(self.config.kafka, 'auth_method', None)
                )
                self.cdp_kafka_client = CDPKafkaClient(self.config)
                self.logger.info("CDP REST client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize CDP REST client: {e}")

        # Initialize CDP client if configured
        if hasattr(self.config, 'cdp') and self.config.cdp and hasattr(self.config.cdp, 'url') and self.config.cdp.url:
            try:
                self.cdp_client = CDPClient(
                    cdp_url=self.config.cdp.url,
                    username=self.config.cdp.username,
                    password=self.config.cdp.password,
                    token=getattr(self.config.cdp, 'token', None)
                )
                self.logger.info("CDP client initialized successfully")
            except Exception as e:
                self.logger.warning(f"Failed to initialize CDP client: {e}")

        # Initialize Kafka client (fallback for non-cloud environments)
        try:
            self.kafka_client = KafkaClient(self.config)
            self.logger.info("Kafka client initialized successfully")
        except Exception as e:
            self.logger.warning(f"Failed to initialize Kafka client: {e}")
            # Don't raise - allow CDP REST client to handle operations

        # Initialize monitoring
        self.health_monitor = HealthMonitor(
            kafka_client=self.kafka_client,
            knox_gateway_client=self.knox_gateway_client,
            cdp_client=self.cdp_client
        )
        self.metrics_collector = MetricsCollector()
        self.logger.info("Monitoring initialized successfully")
    
    def _get_kafka_client(self) -> Optional[KafkaClient]:
        """Get the appropriate Kafka client."""
        if self.cdp_kafka_client:
            return self.cdp_kafka_client
        elif self.knox_kafka_client:
            return self.knox_kafka_client
        else:
            return self.kafka_client
    
    def _get_cdp_rest_client(self) -> Optional[CDPRestClient]:
        """Get the CDP REST client."""
        return self.cdp_rest_client

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
                    description="Create a new Kafka topic using multiple approaches (Knox, CDP, Connect, Admin)",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "description": "Topic name"},
                            "partitions": {"type": "integer", "description": "Number of partitions", "default": 1},
                            "replication_factor": {"type": "integer", "description": "Replication factor", "default": 1},
                            "config": {"type": "object", "description": "Topic configuration", "additionalProperties": {"type": "string"}},
                            "method": {"type": "string", "description": "Preferred creation method", "enum": ["auto", "knox", "cdp", "connect", "admin"], "default": "auto"}
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
                description="Produce a message to a topic using multiple approaches (Direct, Knox, CDP, Connect)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic": {"type": "string", "description": "Topic name"},
                        "key": {"type": "string", "description": "Message key"},
                        "value": {"type": "string", "description": "Message value"},
                        "headers": {"type": "object", "description": "Message headers", "additionalProperties": {"type": "string"}},
                        "method": {"type": "string", "description": "Preferred production method", "enum": ["auto", "direct", "knox", "cdp", "connect"], "default": "auto"}
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
                Tool(
                    name="get_knox_gateway_info",
                    description="Get Knox Gateway information and status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="list_knox_topologies",
                    description="List all Knox topologies",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_knox_topology",
                    description="Get specific Knox topology configuration",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topology_name": {"type": "string", "description": "Name of the topology"}
                        },
                        "required": ["topology_name"]
                    }
                ),
                Tool(
                    name="create_knox_topology",
                    description="Create a new Knox topology for Kafka services",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topology_name": {"type": "string", "description": "Name for the topology"},
                            "kafka_brokers": {"type": "array", "items": {"type": "string"}, "description": "List of Kafka broker addresses"},
                            "kafka_connect_url": {"type": "string", "description": "Optional Kafka Connect URL"}
                        },
                        "required": ["topology_name", "kafka_brokers"]
                    }
                ),
                Tool(
                    name="get_knox_service_health",
                    description="Get health status of Knox services",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topology": {"type": "string", "description": "Topology name", "default": "default"}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_knox_service_urls",
                    description="Get service URLs through Knox Gateway",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "topology": {"type": "string", "description": "Topology name", "default": "default"}
                        },
                        "required": []
                    }
                ),
                # CDP Cloud Tools
                Tool(
                    name="test_cdp_connection",
                    description="Test connection to CDP Cloud",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_cdp_apis",
                    description="Get information about available CDP APIs",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_cdp_service_health",
                    description="Get health status of CDP services",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="validate_cdp_token",
                    description="Validate a CDP token",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "token": {"type": "string", "description": "CDP token to validate"}
                        },
                        "required": ["token"]
                    }
                ),
                # Monitoring and Health Check Tools
                Tool(
                    name="get_health_status",
                    description="Get comprehensive health status of all services",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_health_summary",
                    description="Get a summary of health status",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="get_health_history",
                    description="Get health check history",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "limit": {"type": "integer", "description": "Number of health checks to return", "default": 10}
                        },
                        "required": []
                    }
                ),
                Tool(
                    name="get_service_metrics",
                    description="Get service performance metrics",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="run_health_check",
                    description="Run a specific health check",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "check_name": {"type": "string", "description": "Name of the health check to run", 
                                         "enum": ["kafka", "knox", "cdp", "mcp_server", "topics", "connect"]}
                        },
                        "required": ["check_name"]
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
            elif tool_name == "get_knox_gateway_info":
                result = await self._handle_get_knox_gateway_info(arguments)
            elif tool_name == "list_knox_topologies":
                result = await self._handle_list_knox_topologies(arguments)
            elif tool_name == "get_knox_topology":
                result = await self._handle_get_knox_topology(arguments)
            elif tool_name == "create_knox_topology":
                result = await self._handle_create_knox_topology(arguments)
            elif tool_name == "get_knox_service_health":
                result = await self._handle_get_knox_service_health(arguments)
            elif tool_name == "get_knox_service_urls":
                result = await self._handle_get_knox_service_urls(arguments)
            elif tool_name == "test_cdp_connection":
                result = await self._handle_test_cdp_connection(arguments)
            elif tool_name == "get_cdp_apis":
                result = await self._handle_get_cdp_apis(arguments)
            elif tool_name == "get_cdp_service_health":
                result = await self._handle_get_cdp_service_health(arguments)
            elif tool_name == "validate_cdp_token":
                result = await self._handle_validate_cdp_token(arguments)
            elif tool_name == "get_health_status":
                result = await self._handle_get_health_status(arguments)
            elif tool_name == "get_health_summary":
                result = await self._handle_get_health_summary(arguments)
            elif tool_name == "get_health_history":
                result = await self._handle_get_health_history(arguments)
            elif tool_name == "get_service_metrics":
                result = await self._handle_get_service_metrics(arguments)
            elif tool_name == "run_health_check":
                result = await self._handle_run_health_check(arguments)
            elif tool_name == "test_authentication":
                result = await self._handle_test_authentication(arguments)
            elif tool_name == "discover_auth_endpoints":
                result = await self._handle_discover_auth_endpoints(arguments)
            elif tool_name == "refresh_authentication":
                result = await self._handle_refresh_authentication(arguments)
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
        # Try CDP REST client first
        cdp_rest_client = self._get_cdp_rest_client()
        if cdp_rest_client:
            try:
                topics = cdp_rest_client.get_topics()
                if isinstance(topics, list):
                    topic_names = [topic.get('name', topic) if isinstance(topic, dict) else str(topic) for topic in topics]
                elif isinstance(topics, dict) and 'topics' in topics:
                    topic_names = [topic.get('name', topic) if isinstance(topic, dict) else str(topic) for topic in topics['topics']]
                else:
                    topic_names = []
                return {"topics": topic_names, "count": len(topic_names), "method": "cdp_rest_api"}
            except Exception as e:
                self.logger.warning(f"CDP REST client list_topics failed: {e}")
        
        # Fallback to Kafka client
        if self.kafka_client:
            try:
                topics = self.kafka_client.list_topics()
                return {"topics": topics, "count": len(topics), "method": "kafka_client"}
            except Exception as e:
                self.logger.warning(f"Kafka client list_topics failed: {e}")
        
        return {"topics": [], "count": 0, "method": "none", "error": "No available client"}

    async def _handle_create_topic(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_topic tool."""
        name = arguments["name"]
        partitions = arguments.get("partitions", 1)
        replication_factor = arguments.get("replication_factor", 1)
        config = arguments.get("config", {})
        method = arguments.get("method", "auto")

        # Create topic using the enhanced method
        self.kafka_client.create_topic(name, partitions, replication_factor, config)
        
        return {
            "message": f"Topic '{name}' created successfully using {method} method",
            "topic": name,
            "partitions": partitions,
            "replication_factor": replication_factor,
            "method": method,
            "config": config
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
        
        # Try CDP REST client first
        cdp_rest_client = self._get_cdp_rest_client()
        if cdp_rest_client:
            try:
                topics = cdp_rest_client.get_topics()
                if isinstance(topics, list):
                    topic_names = [topic.get('name', topic) if isinstance(topic, dict) else str(topic) for topic in topics]
                elif isinstance(topics, dict) and 'topics' in topics:
                    topic_names = [topic.get('name', topic) if isinstance(topic, dict) else str(topic) for topic in topics['topics']]
                else:
                    topic_names = []
                exists = name in topic_names
                return {
                    "topic": name,
                    "exists": exists,
                    "method": "cdp_rest_api"
                }
            except Exception as e:
                self.logger.warning(f"CDP REST client topic_exists failed: {e}")
        
        # Fallback to Kafka client
        if self.kafka_client:
            try:
                exists = self.kafka_client.topic_exists(name)
                return {
                    "topic": name,
                    "exists": exists,
                    "method": "kafka_client"
                }
            except Exception as e:
                self.logger.warning(f"Kafka client topic_exists failed: {e}")
        
        return {
            "topic": name,
            "exists": False,
            "method": "none",
            "error": "No available client for topic existence check"
        }

    async def _handle_get_topic_partitions(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_topic_partitions tool."""
        name = arguments["name"]
        
        # Try CDP REST client first
        cdp_rest_client = self._get_cdp_rest_client()
        if cdp_rest_client:
            try:
                topic_info = cdp_rest_client.get_topic(name)
                if isinstance(topic_info, dict):
                    partitions = topic_info.get('partitions', 1)
                else:
                    partitions = 1
                return {
                    "topic": name,
                    "partitions": partitions,
                    "method": "cdp_rest_api"
                }
            except Exception as e:
                self.logger.warning(f"CDP REST client get_topic_partitions failed: {e}")
        
        # Fallback to Kafka client
        if self.kafka_client:
            try:
                partitions = self.kafka_client.get_topic_partitions(name)
                return {
                    "topic": name,
                    "partitions": partitions,
                    "method": "kafka_client"
                }
            except Exception as e:
                self.logger.warning(f"Kafka client get_topic_partitions failed: {e}")
        
        return {
            "topic": name,
            "partitions": 0,
            "method": "none",
            "error": "No available client for topic partitions check"
        }

    async def _handle_update_topic_config(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_topic_config tool."""
        name = arguments["name"]
        config = arguments["config"]
        
        # Try CDP REST client first
        cdp_rest_client = self._get_cdp_rest_client()
        if cdp_rest_client:
            try:
                # CDP REST API doesn't support topic config updates directly
                # This would need to be implemented via CDP Data Hub APIs
                return {
                    "message": f"Topic '{name}' configuration update not supported via CDP REST API",
                    "topic": name,
                    "config": config,
                    "method": "cdp_rest_api",
                    "error": "Not supported"
                }
            except Exception as e:
                self.logger.warning(f"CDP REST client update_topic_config failed: {e}")
        
        # Fallback to Kafka client
        if self.kafka_client:
            try:
                self.kafka_client.update_topic_config(name, config)
                return {
                    "message": f"Topic '{name}' configuration updated successfully",
                    "topic": name,
                    "config": config,
                    "method": "kafka_client"
                }
            except Exception as e:
                self.logger.warning(f"Kafka client update_topic_config failed: {e}")
        
        return {
            "message": f"Topic '{name}' configuration update failed",
            "topic": name,
            "config": config,
            "method": "none",
            "error": "No available client for topic config update"
        }

    async def _handle_produce_message(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle produce_message tool."""
        topic = arguments["topic"]
        key = arguments.get("key")
        value = arguments["value"]
        headers = arguments.get("headers")
        method = arguments.get("method", "auto")

        # Try CDP REST client first
        cdp_rest_client = self._get_cdp_rest_client()
        if cdp_rest_client:
            try:
                result = cdp_rest_client.produce_message(
                    topic_name=topic,
                    message=value,
                    key=key
                )
                return {
                    "topic": topic,
                    "key": key,
                    "value": value,
                    "headers": headers,
                    "method": "cdp_rest_api",
                    "message": "Message produced successfully using CDP REST API",
                    "result": result
                }
            except Exception as e:
                self.logger.warning(f"CDP REST client produce_message failed: {e}")

        # Fallback to Kafka client
        if self.kafka_client:
            try:
                request = ProduceMessageRequest(
                    topic=topic,
                    key=key,
                    value=value,
                    headers=headers
                )
                message = self.kafka_client.produce_message(request)
                return {
                    "topic": message.topic,
                    "partition": message.partition,
                    "offset": message.offset,
                    "key": message.key,
                    "value": message.value,
                    "headers": message.headers,
                    "timestamp": message.timestamp.isoformat(),
                    "method": "kafka_client",
                    "message": f"Message produced successfully using Kafka client"
                }
            except Exception as e:
                self.logger.warning(f"Kafka client produce_message failed: {e}")

        return {
            "error": "No available client for message production",
            "topic": topic,
            "method": "none"
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
        # Try CDP REST client first
        cdp_rest_client = self._get_cdp_rest_client()
        if cdp_rest_client:
            try:
                result = cdp_rest_client.test_connection()
                return {
                    "connected": result.get("status") == "connected",
                    "message": result.get("message", "CDP connection test"),
                    "method": "cdp_rest_api"
                }
            except Exception as e:
                self.logger.warning(f"CDP REST client test failed: {e}")
        
        # Fallback to Kafka client
        if self.kafka_client:
            try:
                connected = self.kafka_client.test_connection()
                return {
                    "connected": connected,
                    "message": "Successfully connected to Kafka" if connected else "Failed to connect to Kafka",
                    "method": "kafka_client"
                }
            except Exception as e:
                self.logger.warning(f"Kafka client test failed: {e}")
        
        return {
            "connected": False,
            "message": "No available connection method",
            "method": "none"
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

    # Enhanced Knox Gateway Tool Handlers

    async def _handle_get_knox_gateway_info(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_knox_gateway_info tool."""
        if not self.knox_gateway_client:
            return {"error": "Knox Gateway client not available"}

        try:
            gateway_info = self.knox_gateway_client.get_gateway_info()
            return {
                "gateway_info": gateway_info,
                "message": "Successfully retrieved Knox Gateway information"
            }
        except Exception as e:
            return {"error": f"Failed to get Knox Gateway info: {e}"}

    async def _handle_list_knox_topologies(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_knox_topologies tool."""
        if not self.knox_gateway_client:
            return {"error": "Knox Gateway client not available"}

        try:
            topologies = self.knox_gateway_client.list_topologies()
            return {
                "topologies": topologies,
                "count": len(topologies),
                "message": "Successfully listed Knox topologies"
            }
        except Exception as e:
            return {"error": f"Failed to list Knox topologies: {e}"}

    async def _handle_get_knox_topology(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_knox_topology tool."""
        if not self.knox_gateway_client:
            return {"error": "Knox Gateway client not available"}

        topology_name = arguments.get("topology_name", "default")
        try:
            topology = self.knox_gateway_client.get_topology(topology_name)
            return {
                "topology": topology,
                "topology_name": topology_name,
                "message": f"Successfully retrieved topology '{topology_name}'"
            }
        except Exception as e:
            return {"error": f"Failed to get topology '{topology_name}': {e}"}

    async def _handle_create_knox_topology(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_knox_topology tool."""
        if not self.knox_gateway_client:
            return {"error": "Knox Gateway client not available"}

        topology_name = arguments["topology_name"]
        kafka_brokers = arguments["kafka_brokers"]
        kafka_connect_url = arguments.get("kafka_connect_url")

        try:
            success = self.knox_gateway_client.create_kafka_topology(
                topology_name, kafka_brokers, kafka_connect_url
            )
            if success:
                return {
                    "message": f"Successfully created topology '{topology_name}'",
                    "topology_name": topology_name,
                    "kafka_brokers": kafka_brokers,
                    "kafka_connect_url": kafka_connect_url
                }
            else:
                return {"error": f"Failed to create topology '{topology_name}'"}
        except Exception as e:
            return {"error": f"Failed to create topology '{topology_name}': {e}"}

    async def _handle_get_knox_service_health(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_knox_service_health tool."""
        if not self.knox_gateway_client:
            return {"error": "Knox Gateway client not available"}

        topology = arguments.get("topology", "default")
        try:
            health = self.knox_gateway_client.get_service_health(topology)
            return {
                "health": health,
                "topology": topology,
                "message": f"Successfully retrieved health status for topology '{topology}'"
            }
        except Exception as e:
            return {"error": f"Failed to get service health for topology '{topology}': {e}"}

    async def _handle_get_knox_service_urls(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_knox_service_urls tool."""
        if not self.knox_gateway_client:
            return {"error": "Knox Gateway client not available"}

        topology = arguments.get("topology", "default")
        try:
            kafka_url = self.knox_gateway_client.get_kafka_service_url(topology)
            connect_url = self.knox_gateway_client.get_kafka_connect_service_url(topology)
            
            return {
                "service_urls": {
                    "kafka": kafka_url,
                    "kafka_connect": connect_url
                },
                "topology": topology,
                "message": f"Successfully retrieved service URLs for topology '{topology}'"
            }
        except Exception as e:
            return {"error": f"Failed to get service URLs for topology '{topology}': {e}"}

    # CDP Cloud Tool Handlers

    async def _handle_test_cdp_connection(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle test_cdp_connection tool."""
        if not self.cdp_client:
            return {"error": "CDP client not available"}

        try:
            connected = self.cdp_client.test_connection()
            return {
                "connected": connected,
                "message": "CDP connection test completed",
                "cdp_url": self.cdp_client.cdp_url
            }
        except Exception as e:
            return {"error": f"Failed to test CDP connection: {e}"}

    async def _handle_get_cdp_apis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_cdp_apis tool."""
        if not self.cdp_client:
            return {"error": "CDP client not available"}

        try:
            apis = self.cdp_client.get_available_apis()
            return {
                "apis": apis,
                "message": "Successfully retrieved CDP API information"
            }
        except Exception as e:
            return {"error": f"Failed to get CDP APIs: {e}"}

    async def _handle_get_cdp_service_health(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_cdp_service_health tool."""
        if not self.cdp_client:
            return {"error": "CDP client not available"}

        try:
            health = self.cdp_client.get_service_health()
            return {
                "health": health,
                "message": "Successfully retrieved CDP service health"
            }
        except Exception as e:
            return {"error": f"Failed to get CDP service health: {e}"}

    async def _handle_validate_cdp_token(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle validate_cdp_token tool."""
        if not self.cdp_client:
            return {"error": "CDP client not available"}

        token = arguments["token"]
        try:
            valid = self.cdp_client.validate_token(token)
            return {
                "valid": valid,
                "token": token[:20] + "..." if len(token) > 20 else token,
                "message": "CDP token validation completed"
            }
        except Exception as e:
            return {"error": f"Failed to validate CDP token: {e}"}

    # Monitoring and Health Check Tool Handlers

    async def _handle_get_health_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_health_status tool."""
        if not self.health_monitor:
            return {"error": "Health monitor not available"}

        try:
            health_status = self.health_monitor.run_all_health_checks()
            return {
                "health_status": health_status.to_dict(),
                "message": "Health status retrieved successfully"
            }
        except Exception as e:
            return {"error": f"Failed to get health status: {e}"}

    async def _handle_get_health_summary(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_health_summary tool."""
        if not self.health_monitor:
            return {"error": "Health monitor not available"}

        try:
            summary = self.health_monitor.get_health_summary()
            return {
                "summary": summary,
                "message": "Health summary retrieved successfully"
            }
        except Exception as e:
            return {"error": f"Failed to get health summary: {e}"}

    async def _handle_get_health_history(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_health_history tool."""
        if not self.health_monitor:
            return {"error": "Health monitor not available"}

        limit = arguments.get("limit", 10)
        try:
            history = self.health_monitor.get_health_history(limit)
            return {
                "history": history,
                "limit": limit,
                "message": f"Health history retrieved successfully (last {limit} checks)"
            }
        except Exception as e:
            return {"error": f"Failed to get health history: {e}"}

    async def _handle_get_service_metrics(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_service_metrics tool."""
        if not self.health_monitor or not self.metrics_collector:
            return {"error": "Monitoring not available"}

        try:
            health_metrics = self.health_monitor.get_service_metrics()
            performance_metrics = self.metrics_collector.get_metrics()
            
            return {
                "health_metrics": health_metrics,
                "performance_metrics": performance_metrics,
                "message": "Service metrics retrieved successfully"
            }
        except Exception as e:
            return {"error": f"Failed to get service metrics: {e}"}

    async def _handle_run_health_check(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Handle run_health_check tool."""
        if not self.health_monitor:
            return {"error": "Health monitor not available"}

        check_name = arguments["check_name"]
        try:
            if check_name == "kafka":
                result = self.health_monitor.check_kafka_health()
            elif check_name == "knox":
                result = self.health_monitor.check_knox_health()
            elif check_name == "cdp":
                result = self.health_monitor.check_cdp_health()
            elif check_name == "mcp_server":
                result = self.health_monitor.check_mcp_server_health()
            elif check_name == "topics":
                result = self.health_monitor.check_topic_operations()
            elif check_name == "connect":
                result = self.health_monitor.check_connect_operations()
            else:
                return {"error": f"Unknown health check: {check_name}"}

            return {
                "check_result": result.to_dict(),
                "check_name": check_name,
                "message": f"Health check '{check_name}' completed successfully"
            }
        except Exception as e:
            return {"error": f"Failed to run health check '{check_name}': {e}"}

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
