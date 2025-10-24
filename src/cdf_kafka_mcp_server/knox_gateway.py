"""
Knox Gateway Integration Module

This module provides comprehensive integration with Apache Knox Gateway
for secure access to Kafka services through CDP Cloud.
"""

import requests
import json
import time
import base64
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class KnoxGatewayClient:
    """
    Client for interacting with Apache Knox Gateway.
    
    Provides methods for:
    - Admin API operations
    - Service discovery
    - Token management
    - Topology management
    """
    
    def __init__(self, gateway_url: str, username: str, password: str):
        """
        Initialize Knox Gateway client.
        
        Args:
            gateway_url: Base URL of the Knox Gateway
            username: Username for authentication
            password: Password for authentication
        """
        self.gateway_url = gateway_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup basic authentication for Knox Gateway."""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.session.headers.update({
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_admin_api_url(self) -> str:
        """Get the Admin API URL for Knox Gateway."""
        return f"{self.gateway_url}/gateway/admin/api/v1"
    
    def get_service_url(self, topology: str, service: str) -> str:
        """
        Get the service URL through Knox Gateway.
        
        Args:
            topology: Knox topology name
            service: Service name (e.g., 'kafka', 'kafka-connect')
        
        Returns:
            Service URL through Knox Gateway
        """
        return f"{self.gateway_url}/gateway/{topology}/{service}"
    
    def get_gateway_info(self) -> Dict[str, Any]:
        """
        Get Knox Gateway information.
        
        Returns:
            Gateway information including version, status, etc.
        """
        try:
            response = self.session.get(f"{self.gateway_url}/gateway/admin/api/v1/info")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get gateway info: {e}")
            return {}
    
    def list_topologies(self) -> List[Dict[str, Any]]:
        """
        List all Knox topologies.
        
        Returns:
            List of topology configurations
        """
        try:
            response = self.session.get(f"{self.get_admin_api_url()}/topologies")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to list topologies: {e}")
            return []
    
    def get_topology(self, topology_name: str) -> Dict[str, Any]:
        """
        Get specific topology configuration.
        
        Args:
            topology_name: Name of the topology
        
        Returns:
            Topology configuration
        """
        try:
            response = self.session.get(f"{self.get_admin_api_url()}/topologies/{topology_name}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get topology {topology_name}: {e}")
            return {}
    
    def create_kafka_topology(self, topology_name: str, kafka_brokers: List[str], 
                            kafka_connect_url: Optional[str] = None) -> bool:
        """
        Create a Knox topology for Kafka services.
        
        Args:
            topology_name: Name for the topology
            kafka_brokers: List of Kafka broker addresses
            kafka_connect_url: Optional Kafka Connect URL
        
        Returns:
            True if successful, False otherwise
        """
        topology_config = {
            "topology": {
                "name": topology_name,
                "providers": [
                    {
                        "role": "authentication",
                        "name": "ShiroProvider",
                        "enabled": "true",
                        "param": {
                            "urls": "classpath:shiro.ini"
                        }
                    },
                    {
                        "role": "authorization",
                        "name": "AclsAuthz",
                        "enabled": "true"
                    },
                    {
                        "role": "identity-assertion",
                        "name": "Default",
                        "enabled": "true"
                    }
                ],
                "services": [
                    {
                        "role": "KAFKA",
                        "name": "kafka",
                        "url": f"http://{kafka_brokers[0] if kafka_brokers else 'localhost:9092'}"
                    }
                ]
            }
        }
        
        # Add Kafka Connect service if provided
        if kafka_connect_url:
            topology_config["topology"]["services"].append({
                "role": "KAFKACONNECT",
                "name": "kafka-connect",
                "url": kafka_connect_url
            })
        
        try:
            response = self.session.post(
                f"{self.get_admin_api_url()}/topologies/{topology_name}",
                json=topology_config
            )
            response.raise_for_status()
            logger.info(f"Successfully created topology {topology_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to create topology {topology_name}: {e}")
            return False
    
    def get_kafka_service_url(self, topology: str = "default") -> str:
        """
        Get Kafka service URL through Knox Gateway.
        
        Args:
            topology: Knox topology name
        
        Returns:
            Kafka service URL
        """
        return self.get_service_url(topology, "kafka")
    
    def get_kafka_connect_service_url(self, topology: str = "default") -> str:
        """
        Get Kafka Connect service URL through Knox Gateway.
        
        Args:
            topology: Knox topology name
        
        Returns:
            Kafka Connect service URL
        """
        return self.get_service_url(topology, "kafka-connect")
    
    def test_service_connectivity(self, service_url: str) -> bool:
        """
        Test connectivity to a service through Knox Gateway.
        
        Args:
            service_url: Service URL to test
        
        Returns:
            True if service is accessible, False otherwise
        """
        try:
            response = self.session.get(service_url, timeout=10)
            return response.status_code in [200, 401, 403]  # 401/403 means service is up but auth required
        except Exception as e:
            logger.error(f"Service connectivity test failed for {service_url}: {e}")
            return False
    
    def get_available_services(self, topology: str = "default") -> List[str]:
        """
        Get list of available services in a topology.
        
        Args:
            topology: Knox topology name
        
        Returns:
            List of available service names
        """
        try:
            response = self.session.get(f"{self.gateway_url}/gateway/{topology}")
            if response.status_code == 200:
                # Parse HTML response to extract service links
                # This is a simplified implementation
                return ["kafka", "kafka-connect"]  # Default services
            return []
        except Exception as e:
            logger.error(f"Failed to get available services for topology {topology}: {e}")
            return []
    
    def validate_token(self, token: str) -> bool:
        """
        Validate a Knox token.
        
        Args:
            token: Token to validate
        
        Returns:
            True if token is valid, False otherwise
        """
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            response = self.session.get(f"{self.gateway_url}/gateway/admin/api/v1/info", headers=headers)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    def get_service_health(self, topology: str = "default") -> Dict[str, Any]:
        """
        Get health status of services in a topology.
        
        Args:
            topology: Knox topology name
        
        Returns:
            Dictionary with service health information
        """
        health_info = {
            "topology": topology,
            "services": {},
            "overall_health": "unknown"
        }
        
        services = self.get_available_services(topology)
        healthy_services = 0
        
        for service in services:
            service_url = self.get_service_url(topology, service)
            is_healthy = self.test_service_connectivity(service_url)
            health_info["services"][service] = {
                "url": service_url,
                "healthy": is_healthy
            }
            if is_healthy:
                healthy_services += 1
        
        if healthy_services == len(services):
            health_info["overall_health"] = "healthy"
        elif healthy_services > 0:
            health_info["overall_health"] = "degraded"
        else:
            health_info["overall_health"] = "unhealthy"
        
        return health_info


class KnoxKafkaClient:
    """
    Kafka client that uses Knox Gateway for secure access.
    
    This client provides Kafka operations through Knox Gateway,
    ensuring secure access to Kafka services in CDP Cloud.
    """
    
    def __init__(self, knox_client: KnoxGatewayClient, topology: str = "default"):
        """
        Initialize Knox Kafka client.
        
        Args:
            knox_client: Knox Gateway client instance
            topology: Knox topology name
        """
        self.knox_client = knox_client
        self.topology = topology
        self.kafka_url = knox_client.get_kafka_service_url(topology)
        self.connect_url = knox_client.get_kafka_connect_service_url(topology)
    
    def get_kafka_connect_url(self) -> str:
        """Get Kafka Connect URL through Knox Gateway."""
        return self.connect_url
    
    def test_connectivity(self) -> bool:
        """Test connectivity to Kafka services through Knox Gateway."""
        kafka_healthy = self.knox_client.test_service_connectivity(self.kafka_url)
        connect_healthy = self.knox_client.test_service_connectivity(self.connect_url)
        return kafka_healthy and connect_healthy
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about available Kafka services."""
        return {
            "kafka_url": self.kafka_url,
            "connect_url": self.connect_url,
            "topology": self.topology,
            "knox_gateway": self.knox_client.gateway_url
        }
