"""
CDP-integrated Kafka client using CDP REST APIs.
"""

import time
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from .config import Config, KafkaConfig
from .cdp_rest_client import CDPRestClient

logger = logging.getLogger(__name__)

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

class CDPKafkaClient:
    """CDP-integrated Kafka client using REST APIs."""
    
    def __init__(self, config: Config):
        """Initialize CDP Kafka client."""
        self.config = config
        self.kafka_config = config.kafka
        
        # Initialize CDP REST client
        self.cdp_client = CDPRestClient(
            base_url=self.kafka_config.bootstrap_servers[0].split(':')[0] + ':' + str(self.kafka_config.bootstrap_servers[0].split(':')[1]),
            username=getattr(self.kafka_config, 'sasl_username', 'ibrooks'),
            password=getattr(self.kafka_config, 'sasl_password', 'Admin12345#'),
            cluster_id=getattr(self.kafka_config, 'cluster_id', None),
            verify_ssl=getattr(self.kafka_config, 'verify_ssl', False)
        )
        
        # Cache for cluster info
        self._cluster_info = None
        self._cluster_id = None
        
        logger.info("CDP Kafka client initialized successfully")
    
    def _get_cluster_id(self) -> str:
        """Get cluster ID, caching the result."""
        if self._cluster_id is None:
            try:
                cluster_info = self.cdp_client.get_cluster_info()
                if cluster_info.get('available'):
                    self._cluster_id = cluster_info.get('cluster_id')
                else:
                    # Fallback to configured cluster ID
                    self._cluster_id = getattr(self.kafka_config, 'cluster_id', 'default')
            except Exception as e:
                logger.warning(f"Failed to get cluster ID: {e}")
                self._cluster_id = getattr(self.kafka_config, 'cluster_id', 'default')
        
        return self._cluster_id
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to CDP services."""
        try:
            result = self.cdp_client.test_connection()
            return {
                "status": "connected" if result["status"] == "connected" else "error",
                "message": result["message"],
                "method": "cdp_rest_api",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"CDP connection failed: {str(e)}",
                "method": "cdp_rest_api",
                "timestamp": time.time()
            }
    
    def get_broker_info(self) -> Dict[str, Any]:
        """Get broker information via CDP REST API."""
        try:
            cluster_info = self.cdp_client.get_cluster_info()
            return {
                "brokers": [self.kafka_config.bootstrap_servers[0]],
                "cluster_id": cluster_info.get('cluster_id'),
                "cluster_name": cluster_info.get('name'),
                "version": cluster_info.get('version'),
                "method": "cdp_rest_api",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "brokers": [],
                "error": str(e),
                "method": "cdp_rest_api",
                "timestamp": time.time()
            }
    
    def get_cluster_metadata(self) -> Dict[str, Any]:
        """Get cluster metadata via CDP REST API."""
        try:
            cluster_info = self.cdp_client.get_cluster_info()
            return {
                "cluster_id": cluster_info.get('cluster_id'),
                "name": cluster_info.get('name'),
                "version": cluster_info.get('version'),
                "endpoint": cluster_info.get('endpoint'),
                "available": cluster_info.get('available', False),
                "method": "cdp_rest_api",
                "timestamp": time.time()
            }
        except Exception as e:
            return {
                "error": str(e),
                "method": "cdp_rest_api",
                "timestamp": time.time()
            }
    
    def list_topics(self) -> List[str]:
        """List topics via CDP REST API."""
        try:
            cluster_id = self._get_cluster_id()
            topics_data = self.cdp_client.get_topics(cluster_id)
            
            if isinstance(topics_data, list):
                return [topic.get('name', topic) if isinstance(topic, dict) else str(topic) for topic in topics_data]
            elif isinstance(topics_data, dict) and 'topics' in topics_data:
                return [topic.get('name', topic) if isinstance(topic, dict) else str(topic) for topic in topics_data['topics']]
            else:
                logger.warning(f"Unexpected topics data format: {type(topics_data)}")
                return []
        except Exception as e:
            logger.error(f"Failed to list topics via CDP REST API: {e}")
            return []
    
    def topic_exists(self, topic_name: str) -> bool:
        """Check if topic exists via CDP REST API."""
        try:
            cluster_id = self._get_cluster_id()
            self.cdp_client.get_topic(topic_name, cluster_id)
            return True
        except Exception:
            return False
    
    def create_topic(self, name: str, partitions: int = 1, 
                    replication_factor: int = 1, config: Dict[str, str] = None) -> bool:
        """Create topic via CDP REST API."""
        try:
            cluster_id = self._get_cluster_id()
            result = self.cdp_client.create_topic(
                topic_name=name,
                partitions=partitions,
                replication_factor=replication_factor,
                config=config or {},
                cluster_id=cluster_id
            )
            logger.info(f"Topic '{name}' created successfully via CDP REST API")
            return True
        except Exception as e:
            logger.error(f"Failed to create topic '{name}' via CDP REST API: {e}")
            return False
    
    def describe_topic(self, topic_name: str) -> Optional[TopicInfo]:
        """Describe topic via CDP REST API."""
        try:
            cluster_id = self._get_cluster_id()
            topic_data = self.cdp_client.get_topic(topic_name, cluster_id)
            
            return TopicInfo(
                name=topic_name,
                partitions=topic_data.get('partitions', 1),
                replication_factor=topic_data.get('replication_factor', 1),
                config=topic_data.get('config', {}),
                partition_details=topic_data.get('partition_details', [])
            )
        except Exception as e:
            logger.error(f"Failed to describe topic '{topic_name}' via CDP REST API: {e}")
            return None
    
    def get_topic_partitions(self, topic_name: str) -> List[Dict[str, Any]]:
        """Get topic partitions via CDP REST API."""
        try:
            topic_info = self.describe_topic(topic_name)
            if topic_info:
                return topic_info.partition_details
            return []
        except Exception as e:
            logger.error(f"Failed to get partitions for topic '{topic_name}' via CDP REST API: {e}")
            return []
    
    def update_topic_config(self, topic_name: str, config: Dict[str, str]) -> bool:
        """Update topic configuration via CDP REST API."""
        try:
            # CDP REST API doesn't support topic config updates directly
            # This would need to be implemented via CDP management APIs
            logger.warning(f"Topic config update not supported via CDP REST API for topic '{topic_name}'")
            return False
        except Exception as e:
            logger.error(f"Failed to update config for topic '{topic_name}' via CDP REST API: {e}")
            return False
    
    def get_topic_offsets(self, topic_name: str) -> Dict[str, Any]:
        """Get topic offsets via CDP REST API."""
        try:
            # CDP REST API doesn't provide direct offset information
            # This would need to be implemented via CDP management APIs
            logger.warning(f"Topic offsets not available via CDP REST API for topic '{topic_name}'")
            return {}
        except Exception as e:
            logger.error(f"Failed to get offsets for topic '{topic_name}' via CDP REST API: {e}")
            return {}
    
    def delete_topic(self, topic_name: str) -> bool:
        """Delete topic via CDP REST API."""
        try:
            cluster_id = self._get_cluster_id()
            self.cdp_client.delete_topic(topic_name, cluster_id)
            logger.info(f"Topic '{topic_name}' deleted successfully via CDP REST API")
            return True
        except Exception as e:
            logger.error(f"Failed to delete topic '{topic_name}' via CDP REST API: {e}")
            return False
    
    def produce_message(self, topic: str, key: Optional[str] = None, 
                       value: str = "", headers: Optional[Dict[str, str]] = None) -> bool:
        """Produce message via CDP REST API."""
        try:
            cluster_id = self._get_cluster_id()
            
            # Prepare message data
            message_data = {"value": value}
            if key:
                message_data["key"] = key
            if headers:
                message_data["headers"] = headers
            
            result = self.cdp_client.produce_message(
                topic_name=topic,
                message=message_data,
                cluster_id=cluster_id
            )
            
            logger.info(f"Message produced successfully to topic '{topic}' via CDP REST API")
            return True
        except Exception as e:
            logger.error(f"Failed to produce message to topic '{topic}' via CDP REST API: {e}")
            return False
    
    def consume_messages(self, topic: str, max_messages: int = 10, 
                        consumer_group: str = "mcp-consumer") -> List[Message]:
        """Consume messages via CDP REST API."""
        try:
            cluster_id = self._get_cluster_id()
            messages_data = self.cdp_client.consume_messages(
                topic_name=topic,
                consumer_group=consumer_group,
                max_messages=max_messages,
                cluster_id=cluster_id
            )
            
            messages = []
            for msg_data in messages_data:
                message = Message(
                    topic=topic,
                    partition=msg_data.get('partition', 0),
                    offset=msg_data.get('offset', 0),
                    key=msg_data.get('key'),
                    value=msg_data.get('value', ''),
                    headers=msg_data.get('headers', {}),
                    timestamp=datetime.now()
                )
                messages.append(message)
            
            logger.info(f"Consumed {len(messages)} messages from topic '{topic}' via CDP REST API")
            return messages
        except Exception as e:
            logger.error(f"Failed to consume messages from topic '{topic}' via CDP REST API: {e}")
            return []
    
    # ==================== KAFKA CONNECT OPERATIONS ====================
    
    def list_connectors(self) -> List[str]:
        """List connectors via CDP REST API."""
        try:
            connectors = self.cdp_client.get_connectors()
            return connectors if isinstance(connectors, list) else []
        except Exception as e:
            logger.error(f"Failed to list connectors via CDP REST API: {e}")
            return []
    
    def get_connect_server_info(self) -> Dict[str, Any]:
        """Get Connect server info via CDP REST API."""
        try:
            # This would need to be implemented via CDP management APIs
            logger.warning("Connect server info not available via CDP REST API")
            return {"error": "Not implemented"}
        except Exception as e:
            logger.error(f"Failed to get Connect server info via CDP REST API: {e}")
            return {"error": str(e)}
    
    def list_connector_plugins(self) -> List[Dict[str, Any]]:
        """List connector plugins via CDP REST API."""
        try:
            plugins = self.cdp_client.get_connector_plugins()
            return plugins if isinstance(plugins, list) else []
        except Exception as e:
            logger.error(f"Failed to list connector plugins via CDP REST API: {e}")
            return []
    
    def validate_connector_config(self, plugin_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate connector configuration via CDP REST API."""
        try:
            result = self.cdp_client.validate_connector_config(plugin_name, config)
            return result
        except Exception as e:
            logger.error(f"Failed to validate connector config via CDP REST API: {e}")
            return {"error": str(e)}
    
    def create_connector(self, name: str, config: Dict[str, Any]) -> bool:
        """Create connector via CDP REST API."""
        try:
            result = self.cdp_client.create_connector(name, config)
            logger.info(f"Connector '{name}' created successfully via CDP REST API")
            return True
        except Exception as e:
            logger.error(f"Failed to create connector '{name}' via CDP REST API: {e}")
            return False
    
    def get_connector(self, name: str) -> Optional[Dict[str, Any]]:
        """Get connector details via CDP REST API."""
        try:
            return self.cdp_client.get_connector(name)
        except Exception as e:
            logger.error(f"Failed to get connector '{name}' via CDP REST API: {e}")
            return None
    
    def get_connector_status(self, name: str) -> Optional[Dict[str, Any]]:
        """Get connector status via CDP REST API."""
        try:
            return self.cdp_client.get_connector_status(name)
        except Exception as e:
            logger.error(f"Failed to get connector status for '{name}' via CDP REST API: {e}")
            return None
    
    def get_connector_config(self, name: str) -> Optional[Dict[str, Any]]:
        """Get connector configuration via CDP REST API."""
        try:
            connector = self.get_connector(name)
            return connector.get('config', {}) if connector else None
        except Exception as e:
            logger.error(f"Failed to get connector config for '{name}' via CDP REST API: {e}")
            return None
    
    def get_connector_tasks(self, name: str) -> List[Dict[str, Any]]:
        """Get connector tasks via CDP REST API."""
        try:
            status = self.get_connector_status(name)
            return status.get('tasks', []) if status else []
        except Exception as e:
            logger.error(f"Failed to get connector tasks for '{name}' via CDP REST API: {e}")
            return []
    
    def get_connector_active_topics(self, name: str) -> List[str]:
        """Get connector active topics via CDP REST API."""
        try:
            # This would need to be implemented via CDP management APIs
            logger.warning(f"Active topics not available via CDP REST API for connector '{name}'")
            return []
        except Exception as e:
            logger.error(f"Failed to get active topics for connector '{name}' via CDP REST API: {e}")
            return []
    
    def pause_connector(self, name: str) -> bool:
        """Pause connector via CDP REST API."""
        try:
            self.cdp_client.pause_connector(name)
            logger.info(f"Connector '{name}' paused successfully via CDP REST API")
            return True
        except Exception as e:
            logger.error(f"Failed to pause connector '{name}' via CDP REST API: {e}")
            return False
    
    def resume_connector(self, name: str) -> bool:
        """Resume connector via CDP REST API."""
        try:
            self.cdp_client.resume_connector(name)
            logger.info(f"Connector '{name}' resumed successfully via CDP REST API")
            return True
        except Exception as e:
            logger.error(f"Failed to resume connector '{name}' via CDP REST API: {e}")
            return False
    
    def restart_connector(self, name: str) -> bool:
        """Restart connector via CDP REST API."""
        try:
            self.cdp_client.restart_connector(name)
            logger.info(f"Connector '{name}' restarted successfully via CDP REST API")
            return True
        except Exception as e:
            logger.error(f"Failed to restart connector '{name}' via CDP REST API: {e}")
            return False
    
    def update_connector_config(self, name: str, config: Dict[str, Any]) -> bool:
        """Update connector configuration via CDP REST API."""
        try:
            # CDP REST API doesn't support direct config updates
            # This would need to be implemented via CDP management APIs
            logger.warning(f"Connector config update not supported via CDP REST API for connector '{name}'")
            return False
        except Exception as e:
            logger.error(f"Failed to update config for connector '{name}' via CDP REST API: {e}")
            return False
    
    def delete_connector(self, name: str) -> bool:
        """Delete connector via CDP REST API."""
        try:
            self.cdp_client.delete_connector(name)
            logger.info(f"Connector '{name}' deleted successfully via CDP REST API")
            return True
        except Exception as e:
            logger.error(f"Failed to delete connector '{name}' via CDP REST API: {e}")
            return False
    
    # ==================== HEALTH AND MONITORING ====================
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status via CDP REST API."""
        try:
            return self.cdp_client.get_health_status()
        except Exception as e:
            logger.error(f"Failed to get health status via CDP REST API: {e}")
            return {
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
    
    def discover_endpoints(self) -> Dict[str, Any]:
        """Discover available CDP endpoints."""
        try:
            return self.cdp_client.discover_endpoints()
        except Exception as e:
            logger.error(f"Failed to discover endpoints via CDP REST API: {e}")
            return {"error": str(e)}
