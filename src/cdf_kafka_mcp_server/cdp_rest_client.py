"""
CDP REST API Client for Kafka operations
"""

import requests
import json
import base64
import logging
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urljoin
import time

from .cdp_auth import CDPAuthenticator, AuthCredentials, AuthMethod, CDPAuthenticationError

logger = logging.getLogger(__name__)

class CDPRestClient:
    """Client for CDP REST API operations."""
    
    def __init__(self, base_url: str, username: str, password: str, 
                 cluster_id: str = None, verify_ssl: bool = False, 
                 token: str = None, auth_method: str = None, 
                 custom_endpoints: Dict[str, str] = None,
                 kafka_connect_endpoint: str = None,
                 kafka_rest_endpoint: str = None,
                 kafka_topics_endpoint: str = None,
                 smm_api_endpoint: str = None,
                 admin_api_endpoint: str = None,
                 cdp_api_endpoint: str = None):
        """
        Initialize CDP REST API client.
        
        Args:
            base_url: CDP base URL (e.g., https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site)
            username: CDP username
            password: CDP password
            cluster_id: CDP cluster ID (optional)
            verify_ssl: Whether to verify SSL certificates
            token: Authentication token (optional)
            auth_method: Authentication method (optional)
            custom_endpoints: Custom endpoint URLs (optional)
        """
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.cluster_id = cluster_id
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        # Store individual endpoint configurations
        self.kafka_connect_endpoint = kafka_connect_endpoint
        self.kafka_rest_endpoint = kafka_rest_endpoint
        self.kafka_topics_endpoint = kafka_topics_endpoint
        self.smm_api_endpoint = smm_api_endpoint
        self.admin_api_endpoint = admin_api_endpoint
        self.cdp_api_endpoint = cdp_api_endpoint
        
        # Initialize authentication
        self.authenticator = self._setup_authentication(token, auth_method)
        
        # API endpoints - use custom endpoints if provided, otherwise use defaults
        if custom_endpoints:
            self.endpoints = custom_endpoints
        else:
            # Build endpoints from individual endpoint configurations or use defaults
            self.endpoints = {
                'kafka_connect': getattr(self, 'kafka_connect_endpoint', None) or f"{self.base_url}/kafka-connect",
                'kafka_rest': getattr(self, 'kafka_rest_endpoint', None) or f"{self.base_url}/kafka-rest",
                'kafka_topics': getattr(self, 'kafka_topics_endpoint', None) or f"{self.base_url}/kafka-topics",
                'smm_api': getattr(self, 'smm_api_endpoint', None) or f"{self.base_url}/smm-api",
                'admin_api': getattr(self, 'admin_api_endpoint', None) or f"{self.base_url}/admin",
                'cdp_api': getattr(self, 'cdp_api_endpoint', None) or f"{self.base_url}/cdp-proxy-api"
            }
        
        logger.info(f"CDP REST client initialized for {self.base_url}")
    
    def _setup_authentication(self, token: str = None, auth_method: str = None) -> CDPAuthenticator:
        """Setup authentication for CDP REST API."""
        # Create credentials
        credentials = AuthCredentials(
            username=self.username,
            password=self.password,
            token=token
        )
        
        # Determine authentication method
        if auth_method:
            try:
                method = AuthMethod(auth_method)
            except ValueError:
                method = None
        else:
            method = None
        
        # Create authenticator
        authenticator = CDPAuthenticator(
            base_url=self.base_url,
            credentials=credentials,
            verify_ssl=self.verify_ssl
        )
        
        # Authenticate
        try:
            authenticator.authenticate(method)
            logger.info(f"CDP authentication successful using {authenticator._auth_method}")
        except Exception as e:
            logger.warning(f"CDP authentication failed: {e}")
            # Fallback to basic auth
            try:
                authenticator.authenticate(AuthMethod.BASIC)
                logger.info("CDP authentication fallback to basic auth successful")
            except Exception as e2:
                logger.error(f"CDP authentication fallback failed: {e2}")
        
        return authenticator
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling and authentication."""
        try:
            # Get authentication headers
            auth_headers = self.authenticator.get_auth_headers()
            
            # Merge with existing headers
            headers = kwargs.get('headers', {})
            headers.update(auth_headers)
            kwargs['headers'] = headers
            
            response = self.session.request(method, endpoint, **kwargs)
            logger.debug(f"{method} {endpoint} -> {response.status_code}")
            
            # Handle authentication errors
            if response.status_code == 401:
                logger.warning("Authentication failed, attempting to refresh token")
                try:
                    self.authenticator.refresh_token()
                    # Retry with new token
                    auth_headers = self.authenticator.get_auth_headers()
                    headers.update(auth_headers)
                    kwargs['headers'] = headers
                    response = self.session.request(method, endpoint, **kwargs)
                    logger.info(f"Request retried with refreshed token: {response.status_code}")
                except Exception as e:
                    logger.error(f"Token refresh failed: {e}")
            
            return response
        except Exception as e:
            logger.error(f"Request failed: {method} {endpoint} - {e}")
            raise
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and return JSON data."""
        try:
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise Exception("Authentication failed - check credentials")
            elif response.status_code == 404:
                raise Exception(f"Endpoint not found: {response.url}")
            elif response.status_code == 500:
                raise Exception(f"Server error: {response.text}")
            else:
                raise Exception(f"API error {response.status_code}: {response.text}")
        except json.JSONDecodeError:
            # Handle HTML responses (authentication forms)
            if "html" in response.headers.get('content-type', '').lower():
                raise Exception("Received HTML response - authentication may be required")
            raise Exception(f"Invalid JSON response: {response.text[:200]}")
    
    # ==================== KAFKA REST API ====================
    
    def get_clusters(self) -> List[Dict[str, Any]]:
        """Get Kafka clusters."""
        endpoint = f"{self.endpoints['kafka_rest']}/clusters"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def get_topics(self, cluster_id: str = None) -> List[Dict[str, Any]]:
        """Get Kafka topics."""
        cluster_id = cluster_id or self.cluster_id
        if not cluster_id:
            # Try to discover cluster ID
            try:
                clusters = self.get_clusters()
                if clusters and len(clusters) > 0:
                    cluster_id = clusters[0].get('cluster_id', 'default')
                else:
                    cluster_id = 'default'
            except Exception:
                cluster_id = 'default'
        
        endpoint = f"{self.endpoints['kafka_rest']}/clusters/{cluster_id}/topics"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def create_topic(self, topic_name: str, partitions: int = 1, 
                    replication_factor: int = 1, config: Dict[str, Any] = None,
                    cluster_id: str = None) -> Dict[str, Any]:
        """Create a Kafka topic."""
        cluster_id = cluster_id or self.cluster_id
        if not cluster_id:
            raise Exception("Cluster ID is required")
        
        endpoint = f"{self.endpoints['kafka_rest']}/clusters/{cluster_id}/topics"
        
        topic_config = {
            "name": topic_name,
            "partitions": partitions,
            "replication_factor": replication_factor,
            "config": config or {}
        }
        
        response = self._make_request('POST', endpoint, json=topic_config)
        return self._handle_response(response)
    
    def get_topic(self, topic_name: str, cluster_id: str = None) -> Dict[str, Any]:
        """Get topic details."""
        cluster_id = cluster_id or self.cluster_id
        if not cluster_id:
            raise Exception("Cluster ID is required")
        
        endpoint = f"{self.endpoints['kafka_rest']}/clusters/{cluster_id}/topics/{topic_name}"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def delete_topic(self, topic_name: str, cluster_id: str = None) -> Dict[str, Any]:
        """Delete a Kafka topic."""
        cluster_id = cluster_id or self.cluster_id
        if not cluster_id:
            raise Exception("Cluster ID is required")
        
        endpoint = f"{self.endpoints['kafka_rest']}/clusters/{cluster_id}/topics/{topic_name}"
        response = self._make_request('DELETE', endpoint)
        return self._handle_response(response)
    
    def produce_message(self, topic_name: str, message: Union[str, Dict], 
                       key: str = None, partition: int = None,
                       cluster_id: str = None) -> Dict[str, Any]:
        """Produce a message to a topic."""
        cluster_id = cluster_id or self.cluster_id
        if not cluster_id:
            raise Exception("Cluster ID is required")
        
        endpoint = f"{self.endpoints['kafka_rest']}/clusters/{cluster_id}/topics/{topic_name}/records"
        
        # Prepare message
        if isinstance(message, dict):
            message_data = message
        else:
            message_data = {"value": message}
        
        if key:
            message_data["key"] = key
        if partition is not None:
            message_data["partition"] = partition
        
        response = self._make_request('POST', endpoint, json=message_data)
        return self._handle_response(response)
    
    def consume_messages(self, topic_name: str, consumer_group: str = "mcp-consumer",
                        max_messages: int = 10, cluster_id: str = None) -> List[Dict[str, Any]]:
        """Consume messages from a topic."""
        cluster_id = cluster_id or self.cluster_id
        if not cluster_id:
            raise Exception("Cluster ID is required")
        
        endpoint = f"{self.endpoints['kafka_rest']}/clusters/{cluster_id}/consumers/{consumer_group}/instances/mcp-instance/records"
        
        # Subscribe to topic
        subscribe_endpoint = f"{self.endpoints['kafka_rest']}/clusters/{cluster_id}/consumers/{consumer_group}/instances/mcp-instance/subscription"
        subscribe_data = {"topics": [topic_name]}
        
        try:
            self._make_request('POST', subscribe_endpoint, json=subscribe_data)
        except Exception as e:
            logger.warning(f"Failed to subscribe to topic: {e}")
        
        # Consume messages
        response = self._make_request('GET', endpoint, params={"max_bytes": max_messages * 1024})
        return self._handle_response(response)
    
    # ==================== KAFKA CONNECT API ====================
    
    def get_connectors(self) -> List[str]:
        """Get list of connectors."""
        endpoint = f"{self.endpoints['kafka_connect']}/connectors"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def get_connector(self, connector_name: str) -> Dict[str, Any]:
        """Get connector details."""
        endpoint = f"{self.endpoints['kafka_connect']}/connectors/{connector_name}"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def create_connector(self, connector_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Create a connector."""
        endpoint = f"{self.endpoints['kafka_connect']}/connectors"
        
        connector_data = {
            "name": connector_name,
            "config": config
        }
        
        response = self._make_request('POST', endpoint, json=connector_data)
        return self._handle_response(response)
    
    def delete_connector(self, connector_name: str) -> Dict[str, Any]:
        """Delete a connector."""
        endpoint = f"{self.endpoints['kafka_connect']}/connectors/{connector_name}"
        response = self._make_request('DELETE', endpoint)
        return self._handle_response(response)
    
    def get_connector_status(self, connector_name: str) -> Dict[str, Any]:
        """Get connector status."""
        endpoint = f"{self.endpoints['kafka_connect']}/connectors/{connector_name}/status"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def pause_connector(self, connector_name: str) -> Dict[str, Any]:
        """Pause a connector."""
        endpoint = f"{self.endpoints['kafka_connect']}/connectors/{connector_name}/pause"
        response = self._make_request('PUT', endpoint)
        return self._handle_response(response)
    
    def resume_connector(self, connector_name: str) -> Dict[str, Any]:
        """Resume a connector."""
        endpoint = f"{self.endpoints['kafka_connect']}/connectors/{connector_name}/resume"
        response = self._make_request('PUT', endpoint)
        return self._handle_response(response)
    
    def restart_connector(self, connector_name: str) -> Dict[str, Any]:
        """Restart a connector."""
        endpoint = f"{self.endpoints['kafka_connect']}/connectors/{connector_name}/restart"
        response = self._make_request('POST', endpoint)
        return self._handle_response(response)
    
    def get_connector_plugins(self) -> List[Dict[str, Any]]:
        """Get available connector plugins."""
        endpoint = f"{self.endpoints['kafka_connect']}/connector-plugins"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def validate_connector_config(self, plugin_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate connector configuration."""
        endpoint = f"{self.endpoints['kafka_connect']}/connector-plugins/{plugin_name}/config/validate"
        response = self._make_request('PUT', endpoint, json=config)
        return self._handle_response(response)
    
    # ==================== SMM API ====================
    
    def get_smm_clusters(self) -> List[Dict[str, Any]]:
        """Get SMM clusters."""
        endpoint = f"{self.endpoints['smm_api']}/api/v1/clusters"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def get_smm_topics(self, cluster_id: str = None) -> List[Dict[str, Any]]:
        """Get SMM topics."""
        cluster_id = cluster_id or self.cluster_id
        if not cluster_id:
            raise Exception("Cluster ID is required")
        
        endpoint = f"{self.endpoints['smm_api']}/api/v1/clusters/{cluster_id}/topics"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    def get_smm_connectors(self, cluster_id: str = None) -> List[Dict[str, Any]]:
        """Get SMM connectors."""
        cluster_id = cluster_id or self.cluster_id
        if not cluster_id:
            raise Exception("Cluster ID is required")
        
        endpoint = f"{self.endpoints['smm_api']}/api/v1/clusters/{cluster_id}/connectors"
        response = self._make_request('GET', endpoint)
        return self._handle_response(response)
    
    # ==================== HEALTH AND MONITORING ====================
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status."""
        health_info = {
            "overall_status": "unknown",
            "services": {},
            "timestamp": time.time()
        }
        
        # Check each service
        for service_name, endpoint in self.endpoints.items():
            try:
                response = self._make_request('GET', endpoint, timeout=5)
                health_info["services"][service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "status_code": response.status_code
                }
            except Exception as e:
                health_info["services"][service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Determine overall status
        healthy_services = sum(1 for s in health_info["services"].values() if s["status"] == "healthy")
        total_services = len(health_info["services"])
        
        if healthy_services == total_services:
            health_info["overall_status"] = "healthy"
        elif healthy_services > 0:
            health_info["overall_status"] = "degraded"
        else:
            health_info["overall_status"] = "unhealthy"
        
        return health_info
    
    def test_connection(self) -> Dict[str, Any]:
        """Test connection to CDP services."""
        try:
            # Test authentication first
            auth_result = self.authenticator.test_authentication()
            
            if auth_result.get('authenticated'):
                return {
                    "status": "connected",
                    "message": "Successfully connected to CDP with authentication",
                    "base_url": self.base_url,
                    "auth_method": auth_result.get('method', 'unknown'),
                    "token_type": auth_result.get('token_type', 'unknown'),
                    "timestamp": time.time()
                }
            else:
                return {
                    "status": "error",
                    "message": f"Authentication failed: {auth_result.get('error', 'Unknown error')}",
                    "base_url": self.base_url,
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "base_url": self.base_url,
                "timestamp": time.time()
            }
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test authentication with CDP services."""
        return self.authenticator.test_authentication()
    
    def discover_auth_endpoints(self) -> Dict[str, Any]:
        """Discover available authentication endpoints."""
        return self.authenticator.discover_auth_endpoints()
    
    def refresh_authentication(self) -> bool:
        """Refresh authentication token."""
        try:
            self.authenticator.refresh_token()
            return True
        except Exception as e:
            logger.error(f"Failed to refresh authentication: {e}")
            return False
    
    def get_knox_token(self) -> str:
        """Get Knox token for Kafka Connect authentication."""
        try:
            # Try to get token from Knox gateway
            token_url = f"{self.base_url}/irb-kakfa-only/cdp-proxy-token/gateway/admin/api/v1/topologies"
            response = self.session.get(token_url, auth=(self.username, self.password), verify=self.verify_ssl)
            
            if response.status_code == 200:
                # Extract token from response (this might need adjustment based on actual response format)
                data = response.json()
                if isinstance(data, dict) and 'token' in data:
                    return data['token']
                elif isinstance(data, list) and len(data) > 0:
                    # Try to extract token from topology data
                    topology = data[0]
                    if isinstance(topology, dict) and 'token' in topology:
                        return topology['token']
            
            # If no token found, return a placeholder for now
            return "knox-token-placeholder"
            
        except Exception as e:
            logger.warning(f"Failed to get Knox token: {e}")
            return "knox-token-placeholder"
    
    def list_connectors(self) -> List[Dict[str, Any]]:
        """List Kafka Connect connectors using Knox token authentication."""
        try:
            # Get Knox token
            token = self.get_knox_token()
            
            # Prepare headers with token authentication
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Try different authentication methods
            auth_methods = [
                # Method 1: Bearer token
                {'Authorization': f'Bearer {token}'},
                # Method 2: Basic auth with token
                {'Authorization': f'Basic {token}'},
                # Method 3: Custom header
                {'X-Auth-Token': token},
                # Method 4: Knox-specific header
                {'X-Knox-Token': token}
            ]
            
            for auth_headers in auth_methods:
                try:
                    headers.update(auth_headers)
                    response = self._make_request('GET', f"{self.endpoints['kafka_connect']}/connectors", headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if isinstance(data, list):
                            return data
                        elif isinstance(data, dict) and 'connectors' in data:
                            return data['connectors']
                        else:
                            return [data] if data else []
                    elif response.status_code != 401:
                        logger.warning(f"Unexpected status code {response.status_code} for connectors: {response.text}")
                        
                except Exception as e:
                    logger.debug(f"Auth method failed: {e}")
                    continue
            
            # If all auth methods failed, try with basic auth as fallback
            response = self._make_request('GET', f"{self.endpoints['kafka_connect']}/connectors", 
                                        auth=(self.username, self.password))
            
            if response.status_code == 200:
                data = response.json()
                return data if isinstance(data, list) else [data] if data else []
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to list connectors: {e}")
            return []
    
    # ==================== UTILITY METHODS ====================
    
    def discover_endpoints(self) -> Dict[str, Any]:
        """Discover available CDP endpoints."""
        discovered = {}
        
        for service_name, endpoint in self.endpoints.items():
            try:
                response = self._make_request('GET', endpoint, timeout=5)
                discovered[service_name] = {
                    "endpoint": endpoint,
                    "status": response.status_code,
                    "available": response.status_code == 200
                }
            except Exception as e:
                discovered[service_name] = {
                    "endpoint": endpoint,
                    "status": "error",
                    "available": False,
                    "error": str(e)
                }
        
        return discovered
    
    def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information."""
        try:
            clusters = self.get_clusters()
            if clusters and len(clusters) > 0:
                cluster = clusters[0]  # Use first cluster
                return {
                    "cluster_id": cluster.get("cluster_id"),
                    "name": cluster.get("name"),
                    "version": cluster.get("version"),
                    "endpoint": cluster.get("endpoint"),
                    "available": True
                }
            else:
                return {
                    "cluster_id": self.cluster_id,
                    "available": False,
                    "message": "No clusters found"
                }
        except Exception as e:
            return {
                "cluster_id": self.cluster_id,
                "available": False,
                "error": str(e)
            }
    
    # Kafka Connect API Methods for Cloudera AI Agent Studio Integration
    
    def get_connect_clusters(self) -> List[Dict[str, Any]]:
        """Get Kafka Connect clusters using the primary endpoint."""
        try:
            response = self._make_request('GET', f"{self.endpoints['kafka_connect']}/")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'clusters' in data:
                    return data['clusters']
                else:
                    return [data] if data else []
            return []
        except Exception as e:
            logger.error(f"Failed to get Connect clusters: {e}")
            return []
    
    def get_connect_topics(self) -> List[Dict[str, Any]]:
        """Get topics via Kafka Connect API."""
        try:
            # Try to get topics through Connect API
            response = self._make_request('GET', f"{self.endpoints['kafka_connect']}/topics")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'topics' in data:
                    return data['topics']
                else:
                    return [data] if data else []
            return []
        except Exception as e:
            logger.error(f"Failed to get topics via Connect API: {e}")
            return []
    
    def create_topic_via_connect(self, name: str, partitions: int = 1, replication_factor: int = 1, config: Dict[str, str] = None) -> Dict[str, Any]:
        """Create topic via Kafka Connect API."""
        try:
            topic_config = {
                "name": name,
                "partitions": partitions,
                "replication_factor": replication_factor,
                "config": config or {}
            }
            
            response = self._make_request('POST', f"{self.endpoints['kafka_connect']}/topics", 
                                        json=topic_config)
            if response.status_code in [200, 201]:
                return {
                    "message": f"Topic '{name}' created successfully via Connect API",
                    "topic": name,
                    "partitions": partitions,
                    "replication_factor": replication_factor,
                    "config": config,
                    "method": "kafka_connect_api"
                }
            else:
                return {
                    "error": f"Failed to create topic: {response.status_code} - {response.text}",
                    "topic": name,
                    "method": "kafka_connect_api"
                }
        except Exception as e:
            logger.error(f"Failed to create topic via Connect API: {e}")
            return {
                "error": str(e),
                "topic": name,
                "method": "kafka_connect_api"
            }
    
    def produce_message_via_connect(self, topic_name: str, message: str, key: str = None, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Produce message via Kafka Connect API."""
        try:
            message_data = {
                "topic": topic_name,
                "value": message,
                "key": key,
                "headers": headers or {}
            }
            
            response = self._make_request('POST', f"{self.endpoints['kafka_connect']}/topics/{topic_name}/messages", 
                                        json=message_data)
            if response.status_code in [200, 201]:
                return {
                    "message": "Message produced successfully via Connect API",
                    "topic": topic_name,
                    "method": "kafka_connect_api"
                }
            else:
                return {
                    "error": f"Failed to produce message: {response.status_code} - {response.text}",
                    "topic": topic_name,
                    "method": "kafka_connect_api"
                }
        except Exception as e:
            logger.error(f"Failed to produce message via Connect API: {e}")
            return {
                "error": str(e),
                "topic": topic_name,
                "method": "kafka_connect_api"
            }
    
    def get_topic_info_via_connect(self, topic_name: str) -> Dict[str, Any]:
        """Get topic information via Kafka Connect API."""
        try:
            response = self._make_request('GET', f"{self.endpoints['kafka_connect']}/topics/{topic_name}")
            if response.status_code == 200:
                data = response.json()
                return {
                    "name": topic_name,
                    "info": data,
                    "method": "kafka_connect_api"
                }
            else:
                return {
                    "name": topic_name,
                    "error": f"Topic not found: {response.status_code}",
                    "method": "kafka_connect_api"
                }
        except Exception as e:
            logger.error(f"Failed to get topic info via Connect API: {e}")
            return {
                "name": topic_name,
                "error": str(e),
                "method": "kafka_connect_api"
            }
    
    def delete_topic_via_connect(self, topic_name: str) -> Dict[str, Any]:
        """Delete topic via Kafka Connect API."""
        try:
            response = self._make_request('DELETE', f"{self.endpoints['kafka_connect']}/topics/{topic_name}")
            if response.status_code in [200, 204]:
                return {
                    "message": f"Topic '{topic_name}' deleted successfully via Connect API",
                    "topic": topic_name,
                    "method": "kafka_connect_api"
                }
            else:
                return {
                    "error": f"Failed to delete topic: {response.status_code} - {response.text}",
                    "topic": topic_name,
                    "method": "kafka_connect_api"
                }
        except Exception as e:
            logger.error(f"Failed to delete topic via Connect API: {e}")
            return {
                "error": str(e),
                "topic": topic_name,
                "method": "kafka_connect_api"
            }
