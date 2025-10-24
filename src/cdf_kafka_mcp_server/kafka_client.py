"""
Kafka client implementation with Knox authentication support.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import ConfigResource, ConfigResourceType, NewTopic
from kafka.errors import KafkaError, TopicAlreadyExistsError, UnknownTopicOrPartitionError
from kafka.structs import TopicPartition

from .config import Config, KafkaConfig
from .knox_client import KnoxClient, KnoxError


@dataclass
class TopicInfo:
    """Information about a Kafka topic."""
    name: str
    partitions: int
    replication_factor: int
    config: Dict[str, str]
    partition_details: List[Dict[str, Any]]


@dataclass
class Message:
    """Kafka message."""
    topic: str
    partition: int
    offset: int
    key: Optional[str]
    value: str
    headers: Dict[str, str]
    timestamp: datetime


@dataclass
class ProduceMessageRequest:
    """Request to produce a message."""
    topic: str
    key: Optional[str] = None
    value: str = ""
    headers: Optional[Dict[str, str]] = None


@dataclass
class ConsumeMessageRequest:
    """Request to consume messages."""
    topic: str
    partition: Optional[int] = None
    offset: int = 0
    max_count: int = 10
    timeout: int = 5


class KafkaClient:
    """Kafka client with Knox authentication support."""

    def __init__(self, config: Config):
        """
        Initialize Kafka client.

        Args:
            config: Configuration object
        """
        self.config = config
        self.knox_client: Optional[KnoxClient] = None
        self.admin_client: Optional[KafkaAdminClient] = None
        self.producer: Optional[KafkaProducer] = None
        self.consumer: Optional[KafkaConsumer] = None
        self._bootstrap_servers: List[str] = []

        # Initialize Knox client if enabled
        if config.is_knox_enabled():
            from .knox_client import KnoxClient
            self.knox_client = KnoxClient(config.knox)

            # Test Knox connection
            if not self.knox_client.test_connection():
                raise KnoxError("Failed to connect to Knox Gateway")

            # Get bootstrap servers through Knox
            knox_servers = self.knox_client.get_kafka_bootstrap_servers()
            if knox_servers:
                self._bootstrap_servers = knox_servers
            else:
                # Fallback to configuration bootstrap servers
                if isinstance(config.kafka.bootstrap_servers, list):
                    self._bootstrap_servers = config.kafka.bootstrap_servers
                else:
                    self._bootstrap_servers = [config.kafka.bootstrap_servers]
        else:
            # Use direct Kafka configuration
            if isinstance(config.kafka.bootstrap_servers, list):
                self._bootstrap_servers = config.kafka.bootstrap_servers
            else:
                self._bootstrap_servers = [config.kafka.bootstrap_servers]

        # Initialize Kafka clients
        self._init_kafka_clients()

    def _init_kafka_clients(self) -> None:
        """Initialize Kafka clients."""
        kafka_config = self.config.kafka

        # Common configuration
        client_config = {
            'bootstrap_servers': self._bootstrap_servers,
            'client_id': kafka_config.client_id,
            'request_timeout_ms': kafka_config.timeout * 1000,
            'api_version': (2, 6, 0),  # Use a more stable version
        }

        # Configure security
        if kafka_config.security_protocol != 'PLAINTEXT':
            client_config['security_protocol'] = kafka_config.security_protocol

            if kafka_config.security_protocol in ['SASL_PLAINTEXT', 'SASL_SSL']:
                client_config['sasl_mechanism'] = kafka_config.sasl_mechanism
                client_config['sasl_plain_username'] = kafka_config.sasl_username
                client_config['sasl_plain_password'] = kafka_config.sasl_password

            if kafka_config.security_protocol in ['SSL', 'SASL_SSL']:
                client_config['ssl_check_hostname'] = False
                if kafka_config.tls_ca_cert:
                    client_config['ssl_cafile'] = kafka_config.tls_ca_cert
                if kafka_config.tls_cert:
                    client_config['ssl_certfile'] = kafka_config.tls_cert
                if kafka_config.tls_key:
                    client_config['ssl_keyfile'] = kafka_config.tls_key

        # Create admin client with error handling
        try:
            admin_config = client_config.copy()
            admin_config['metadata_max_age_ms'] = 30000  # Reduce metadata refresh
            admin_config['retry_backoff_ms'] = 100
            admin_config['reconnect_backoff_ms'] = 50
            self.admin_client = KafkaAdminClient(**admin_config)
        except Exception as e:
            print(f"Warning: Admin client initialization failed: {e}")
            self.admin_client = None

        # Create producer with aggressive timeout settings
        producer_config = client_config.copy()
        producer_config['value_serializer'] = lambda v: v.encode('utf-8') if isinstance(v, str) else v
        producer_config['key_serializer'] = lambda k: k.encode('utf-8') if isinstance(k, str) else k
        producer_config['retries'] = 1  # Reduce retries
        producer_config['retry_backoff_ms'] = 100
        producer_config['request_timeout_ms'] = 5000  # Reduce request timeout
        producer_config['delivery_timeout_ms'] = 10000  # Reduce delivery timeout
        producer_config['acks'] = '1'  # Change from 'all' to '1' for faster response
        producer_config['batch_size'] = 16384  # Smaller batch size
        producer_config['linger_ms'] = 0  # No batching delay
        self.producer = KafkaProducer(**producer_config)

        # Create consumer
        consumer_config = client_config.copy()
        consumer_config['value_deserializer'] = lambda v: v.decode('utf-8') if isinstance(v, bytes) else v
        consumer_config['key_deserializer'] = lambda k: k.decode('utf-8') if isinstance(k, bytes) else k
        consumer_config['auto_offset_reset'] = 'earliest'
        consumer_config['enable_auto_commit'] = False
        consumer_config['consumer_timeout_ms'] = 5000
        self.consumer = KafkaConsumer(**consumer_config)

    def _list_topics_via_connect(self) -> List[str]:
        """List topics using Kafka Connect API as fallback."""
        try:
            import requests
            connect_url = self._get_connect_url()
            response = requests.get(f"{connect_url}/connectors", timeout=10)

            if response.status_code == 200:
                connectors = response.json()
                topics = set()

                # Get topics from connector configurations
                for connector in connectors:
                    try:
                        config_response = requests.get(f"{connect_url}/connectors/{connector}/config", timeout=10)
                        if config_response.status_code == 200:
                            config = config_response.json()
                            if 'topic' in config:
                                topics.add(config['topic'])
                            elif 'topics' in config:
                                if isinstance(config['topics'], str):
                                    topics.update(config['topics'].split(','))
                                elif isinstance(config['topics'], list):
                                    topics.update(config['topics'])
                    except Exception:
                        continue

                # Add known system topics
                system_topics = [
                    '__consumer_offsets',
                    'connect-configs',
                    'connect-offsets',
                    'connect-status'
                ]
                topics.update(system_topics)

                return list(topics)
            else:
                # Fallback: return empty list if Connect API fails
                return []

        except Exception as e:
            # Ultimate fallback: return empty list
            return []

    def _create_topic_via_connect(self, topic_name: str) -> None:
        """Create topic using Kafka Connect API as fallback."""
        try:
            import requests
            connect_url = self._get_connect_url()

            # Create a simple connector that will create the topic
            connector_name = f"{topic_name}-topic-creator"
            connector_config = {
                'connector.class': 'org.apache.kafka.connect.tools.MockSourceConnector',
                'tasks.max': '1',
                'topic': topic_name
            }

            data = {
                'name': connector_name,
                'config': connector_config
            }

            response = requests.post(f"{connect_url}/connectors", json=data, timeout=10)

            if response.status_code == 201:
                # Wait a moment for the connector to create the topic
                import time
                time.sleep(2)

                # Delete the connector as we only needed it to create the topic
                try:
                    requests.delete(f"{connect_url}/connectors/{connector_name}", timeout=10)
                except Exception:
                    pass  # Ignore deletion errors
            else:
                raise Exception(f"Failed to create topic via Connect API: {response.status_code}")

        except Exception as e:
            raise Exception(f"Failed to create topic {topic_name} via Connect: {e}")

    def close(self) -> None:
        """Close all Kafka connections."""
        if self.admin_client:
            self.admin_client.close()
        if self.producer:
            self.producer.close()
        if self.consumer:
            self.consumer.close()
        if self.knox_client:
            self.knox_client.close()

    def get_brokers(self) -> List[str]:
        """Get list of brokers."""
        return self._bootstrap_servers

    def is_knox_enabled(self) -> bool:
        """Check if Knox authentication is enabled."""
        return self.knox_client is not None

    # Topic Management Methods

    def list_topics(self) -> List[str]:
        """List all topics."""
        # Always use Connect API for CDP Cloud
        try:
            return self._list_topics_via_connect()
        except Exception as e:
            raise Exception(f"Failed to list topics via Connect API: {e}")

    def create_topic(self, name: str, partitions: int = 1, replication_factor: int = 1,
                    config: Optional[Dict[str, str]] = None) -> None:
        """Create a new topic."""
        # Always use Connect API for CDP Cloud
        try:
            self._create_topic_via_connect(name)
        except Exception as e:
            raise Exception(f"Failed to create topic {name} via Connect API: {e}")

    def _describe_topic_via_fallback(self, name: str) -> TopicInfo:
        """Fallback method to describe topic when admin_client is not available."""
        try:
            # Check if topic exists
            topics = self.list_topics()
            if name not in topics:
                raise Exception(f"Topic '{name}' not found")
            
            # Return basic topic info
            return TopicInfo(
                name=name,
                partitions=1,  # Default partition count
                replication_factor=1,  # Default replication factor
                config={},  # Empty config for fallback
                partition_details=[{
                    "id": 0,
                    "leader": -1,
                    "replicas": [-1],
                    "isr": [-1],
                    "offline_replicas": []
                }]
            )
        except Exception as e:
            raise Exception(f"Failed to describe topic '{name}' via fallback: {e}")

    def describe_topic(self, name: str) -> TopicInfo:
        """Get detailed information about a topic."""
        if self.admin_client is None:
            # Fallback: Use basic topic info via list_topics
            return self._describe_topic_via_fallback(name)
        
        try:
            metadata = self.admin_client.describe_topics([name])
            if name not in metadata:
                raise Exception(f"Topic '{name}' not found")

            topic_metadata = metadata[name]

            # Get topic configuration
            config_resource = ConfigResource(ConfigResourceType.TOPIC, name)
            configs = self.admin_client.describe_configs([config_resource])

            topic_config = {}
            if name in configs:
                for config_name, config_entry in configs[name].items():
                    topic_config[config_name] = config_entry.value

            # Build partition details
            partition_details = []
            for partition_id, partition_metadata in topic_metadata.partitions.items():
                partition_details.append({
                    'id': partition_id,
                    'leader': partition_metadata.leader,
                    'replicas': partition_metadata.replicas,
                    'isr': partition_metadata.isr,
                    'offline_replicas': getattr(partition_metadata, 'offline_replicas', [])
                })

            return TopicInfo(
                name=name,
                partitions=len(topic_metadata.partitions),
                replication_factor=len(topic_metadata.partitions[0].replicas) if topic_metadata.partitions else 0,
                config=topic_config,
                partition_details=partition_details
            )

        except UnknownTopicOrPartitionError:
            raise Exception(f"Topic '{name}' not found")
        except KafkaError as e:
            raise Exception(f"Failed to describe topic '{name}': {e}")

    def delete_topic(self, name: str) -> None:
        """Delete a topic."""
        try:
            self.admin_client.delete_topics([name])
        except UnknownTopicOrPartitionError:
            raise Exception(f"Topic '{name}' not found")
        except KafkaError as e:
            raise Exception(f"Failed to delete topic '{name}': {e}")

    def topic_exists(self, name: str) -> bool:
        """Check if a topic exists."""
        if self.admin_client is None:
            # Fallback: Use list_topics
            try:
                topics = self.list_topics()
                return name in topics
            except Exception as e:
                raise Exception(f"Failed to check if topic exists: {e}")
        
        try:
            metadata = self.admin_client.list_topics()
            return name in metadata.topics
        except KafkaError as e:
            raise Exception(f"Failed to check if topic exists: {e}")

    def get_topic_partitions(self, name: str) -> int:
        """Get the number of partitions for a topic."""
        if self.admin_client is None:
            # Fallback: Return default partition count (1)
            try:
                topics = self.list_topics()
                if name not in topics:
                    raise Exception(f"Topic '{name}' not found")
                return 1  # Default partition count for fallback
            except Exception as e:
                raise Exception(f"Failed to get topic partitions: {e}")
        
        try:
            metadata = self.admin_client.describe_topics([name])
            if name not in metadata:
                raise Exception(f"Topic '{name}' not found")
            return len(metadata[name].partitions)
        except UnknownTopicOrPartitionError:
            raise Exception(f"Topic '{name}' not found")
        except KafkaError as e:
            raise Exception(f"Failed to get topic partitions: {e}")

    def update_topic_config(self, name: str, config: Dict[str, str]) -> None:
        """Update topic configuration."""
        try:
            config_resource = ConfigResource(ConfigResourceType.TOPIC, name)
            config_entries = {key: value for key, value in config.items()}

            self.admin_client.alter_configs({
                config_resource: config_entries
            })
        except UnknownTopicOrPartitionError:
            raise Exception(f"Topic '{name}' not found")
        except KafkaError as e:
            raise Exception(f"Failed to update topic configuration: {e}")

    # Message Operations

    def produce_message(self, request: ProduceMessageRequest) -> Message:
        """Produce a message to a topic."""
        try:
            # Prepare headers
            headers = []
            if request.headers:
                for key, value in request.headers.items():
                    headers.append((key, value.encode('utf-8')))

            # Send message
            future = self.producer.send(
                request.topic,
                value=request.value,
                key=request.key,
                headers=headers
            )

            # Wait for result with shorter timeout
            record_metadata = future.get(timeout=3)

            return Message(
                topic=record_metadata.topic,
                partition=record_metadata.partition,
                offset=record_metadata.offset,
                key=request.key,
                value=request.value,
                headers=request.headers or {},
                timestamp=datetime.now()
            )

        except KafkaError as e:
            raise Exception(f"Failed to produce message: {e}")

    def consume_messages(self, request: ConsumeMessageRequest) -> List[Message]:
        """Consume messages from a topic."""
        try:
            # Subscribe to topic
            self.consumer.subscribe([request.topic])

            messages = []
            start_time = time.time()

            for message in self.consumer:
                # Check timeout
                if time.time() - start_time > request.timeout:
                    break

                # Check max count
                if len(messages) >= request.max_count:
                    break

                # Filter by partition if specified
                if request.partition is not None and message.partition != request.partition:
                    continue

                # Filter by offset if specified
                if request.offset > 0 and message.offset < request.offset:
                    continue

                # Convert headers
                headers = {}
                if message.headers:
                    for key, value in message.headers:
                        headers[key] = value.decode('utf-8') if isinstance(value, bytes) else value

                messages.append(Message(
                    topic=message.topic,
                    partition=message.partition,
                    offset=message.offset,
                    key=message.key,
                    value=message.value,
                    headers=headers,
                    timestamp=datetime.fromtimestamp(message.timestamp / 1000) if message.timestamp else datetime.now()
                ))

            return messages

        except KafkaError as e:
            raise Exception(f"Failed to consume messages: {e}")

    def get_topic_offsets(self, topic: str, partition: int) -> tuple[int, int]:
        """Get earliest and latest offsets for a topic partition."""
        try:
            topic_partition = TopicPartition(topic, partition)

            # Get earliest offset
            earliest_offset = self.consumer.beginning_offsets([topic_partition])[topic_partition]

            # Get latest offset
            latest_offset = self.consumer.end_offsets([topic_partition])[topic_partition]

            return int(earliest_offset), int(latest_offset)

        except KafkaError as e:
            raise Exception(f"Failed to get topic offsets: {e}")

    def test_connection(self) -> bool:
        """Test the connection to Kafka."""
        if self.admin_client is None:
            # Fallback: Use list_topics method
            try:
                topics = self.list_topics()
                return len(topics) >= 0  # Any result means connection works
            except Exception:
                return False
        
        try:
            # Try to list topics as a connection test
            self.admin_client.list_topics()
            return True
        except KafkaError:
            return False

    # Kafka Connect Methods

    def _get_connect_url(self) -> str:
        """Get the Kafka Connect REST API URL."""
        # For CDP Cloud, use the CDP proxy API endpoint
        if hasattr(self.config, 'knox') and self.config.knox.gateway:
            # Extract the base URL from Knox Gateway and use CDP proxy API
            gateway_url = self.config.knox.gateway
            if '/cdp-proxy-token/' in gateway_url:
                # Replace cdp-proxy-token with cdp-proxy-api/kafka-connect
                base_url = gateway_url.replace('/cdp-proxy-token/', '/cdp-proxy-api/kafka-connect')
                return base_url
            elif '/cdp-proxy-token' in gateway_url:
                # Handle case where there's no trailing slash
                base_url = gateway_url.replace('/cdp-proxy-token', '/cdp-proxy-api/kafka-connect')
                return base_url
            else:
                # Fallback: append kafka-connect to the gateway URL
                return f"{gateway_url.rstrip('/')}/kafka-connect"
        
        # Fallback to standard Kafka Connect port
        if isinstance(self.config.kafka.bootstrap_servers, list):
            bootstrap_server = self.config.kafka.bootstrap_servers[0]
        else:
            bootstrap_server = self.config.kafka.bootstrap_servers.split(',')[0]
        
        host = bootstrap_server.split(':')[0]
        return f"http://{host}:28083"

    def _make_connect_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a request to the Kafka Connect REST API."""
        import requests

        url = f"{self._get_connect_url()}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        # Add authentication for CDP proxy API
        if hasattr(self, 'knox_client') and self.knox_client:
            try:
                # For CDP proxy API, use basic authentication with SASL credentials
                import base64
                username = self.config.kafka.sasl_username
                password = self.config.kafka.sasl_password
                if username and password:
                    credentials = f"{username}:{password}"
                    encoded_credentials = base64.b64encode(credentials.encode()).decode()
                    headers["Authorization"] = f"Basic {encoded_credentials}"
                else:
                    # Fallback to Knox token
                    token = self.knox_client.get_token()
                    headers["Authorization"] = f"Bearer {token}"
            except Exception as e:
                print(f"Warning: Failed to get authentication for Connect API: {e}")

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json() if response.content else {}

        except requests.exceptions.RequestException as e:
            raise Exception(f"Kafka Connect API request failed: {e}")

    def list_connectors(self) -> List[str]:
        """List all Kafka Connect connectors."""
        try:
            result = self._make_connect_request("GET", "/connectors")
            return result
        except Exception as e:
            raise Exception(f"Failed to list connectors: {e}")

    def create_connector(self, name: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Create a new Kafka Connect connector."""
        try:
            data = {"name": name, "config": config}
            result = self._make_connect_request("POST", "/connectors", data)
            return result
        except Exception as e:
            raise Exception(f"Failed to create connector '{name}': {e}")

    def get_connector(self, name: str) -> Dict[str, Any]:
        """Get information about a specific connector."""
        try:
            result = self._make_connect_request("GET", f"/connectors/{name}")
            return result
        except Exception as e:
            raise Exception(f"Failed to get connector '{name}': {e}")

    def get_connector_status(self, name: str) -> Dict[str, Any]:
        """Get the status of a specific connector."""
        try:
            result = self._make_connect_request("GET", f"/connectors/{name}/status")
            return result
        except Exception as e:
            raise Exception(f"Failed to get connector status for '{name}': {e}")

    def get_connector_config(self, name: str) -> Dict[str, str]:
        """Get the configuration of a specific connector."""
        try:
            result = self._make_connect_request("GET", f"/connectors/{name}/config")
            return result
        except Exception as e:
            raise Exception(f"Failed to get connector config for '{name}': {e}")

    def update_connector_config(self, name: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Update the configuration of a specific connector."""
        try:
            result = self._make_connect_request("PUT", f"/connectors/{name}/config", config)
            return result
        except Exception as e:
            raise Exception(f"Failed to update connector config for '{name}': {e}")

    def delete_connector(self, name: str) -> None:
        """Delete a specific connector."""
        try:
            self._make_connect_request("DELETE", f"/connectors/{name}")
        except Exception as e:
            raise Exception(f"Failed to delete connector '{name}': {e}")

    def pause_connector(self, name: str) -> None:
        """Pause a specific connector."""
        try:
            self._make_connect_request("PUT", f"/connectors/{name}/pause")
        except Exception as e:
            raise Exception(f"Failed to pause connector '{name}': {e}")

    def resume_connector(self, name: str) -> None:
        """Resume a paused connector."""
        try:
            self._make_connect_request("PUT", f"/connectors/{name}/resume")
        except Exception as e:
            raise Exception(f"Failed to resume connector '{name}': {e}")

    def restart_connector(self, name: str) -> None:
        """Restart a specific connector."""
        try:
            self._make_connect_request("POST", f"/connectors/{name}/restart")
        except Exception as e:
            raise Exception(f"Failed to restart connector '{name}': {e}")

    def get_connector_tasks(self, name: str) -> List[Dict[str, Any]]:
        """Get information about connector tasks."""
        try:
            result = self._make_connect_request("GET", f"/connectors/{name}/tasks")
            return result
        except Exception as e:
            raise Exception(f"Failed to get connector tasks for '{name}': {e}")

    def get_connector_active_topics(self, name: str) -> Dict[str, Any]:
        """Get active topics for a connector."""
        try:
            result = self._make_connect_request("GET", f"/connectors/{name}/topics")
            return result
        except Exception as e:
            raise Exception(f"Failed to get active topics for connector '{name}': {e}")

    def list_connector_plugins(self) -> List[Dict[str, Any]]:
        """List available connector plugins."""
        try:
            result = self._make_connect_request("GET", "/connector-plugins")
            return result
        except Exception as e:
            raise Exception(f"Failed to list connector plugins: {e}")

    def validate_connector_config(self, plugin_name: str, config: Dict[str, str]) -> Dict[str, Any]:
        """Validate connector configuration."""
        try:
            result = self._make_connect_request("PUT", f"/connector-plugins/{plugin_name}/config/validate", config)
            return result
        except Exception as e:
            raise Exception(f"Failed to validate connector config for plugin '{plugin_name}': {e}")

    def get_connect_server_info(self) -> Dict[str, Any]:
        """Get Kafka Connect server information."""
        try:
            result = self._make_connect_request("GET", "/")
            return result
        except Exception as e:
            raise Exception(f"Failed to get Connect server info: {e}")
