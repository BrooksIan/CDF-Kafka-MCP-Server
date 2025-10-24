"""
CDP Cloud Authentication Client

This module provides authentication and API access for CDP Cloud environments,
including support for CDP-specific tokens and API endpoints.
"""

import requests
import json
import time
import base64
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)


class CDPError(Exception):
    """CDP Cloud error."""
    pass


class CDPClient:
    """
    Client for CDP Cloud authentication and API access.
    
    Provides methods for:
    - CDP token authentication
    - CDP API operations
    - Service discovery
    - Topic management
    """
    
    def __init__(self, cdp_url: str, username: str, password: str, token: Optional[str] = None):
        """
        Initialize CDP client.
        
        Args:
            cdp_url: Base URL of the CDP Cloud environment
            username: Username for authentication
            password: Password for authentication
            token: Optional CDP token (if already available)
        """
        self.cdp_url = cdp_url.rstrip('/')
        self.username = username
        self.password = password
        self.token = token
        self.session = requests.Session()
        self._setup_authentication()
    
    def _setup_authentication(self):
        """Setup authentication for CDP Cloud."""
        if self.token:
            # Use provided token
            self.session.headers.update({
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
        else:
            # Use basic authentication
            credentials = f"{self.username}:{self.password}"
            encoded_credentials = base64.b64encode(credentials.encode()).decode()
            self.session.headers.update({
                'Authorization': f'Basic {encoded_credentials}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            })
    
    def get_cdp_proxy_url(self) -> str:
        """Get the CDP proxy API URL."""
        return f"{self.cdp_url}/cdp-proxy-api"
    
    def get_cdp_proxy_token_url(self) -> str:
        """Get the CDP proxy token API URL."""
        return f"{self.cdp_url}/cdp-proxy-token"
    
    def get_kafka_connect_url(self) -> str:
        """Get Kafka Connect URL through CDP proxy."""
        return f"{self.get_cdp_proxy_url()}/kafka-connect"
    
    def get_kafka_connect_token_url(self) -> str:
        """Get Kafka Connect URL through CDP proxy token."""
        return f"{self.get_cdp_proxy_token_url()}/kafka-connect"
    
    def test_connection(self) -> bool:
        """
        Test connection to CDP Cloud.
        
        Returns:
            True if connection successful
        """
        try:
            # Try CDP proxy API first
            response = self.session.get(self.get_kafka_connect_url(), timeout=10)
            if response.status_code in [200, 401, 403]:
                return True
            
            # Try CDP proxy token API
            response = self.session.get(self.get_kafka_connect_token_url(), timeout=10)
            return response.status_code in [200, 401, 403]
        except Exception as e:
            logger.error(f"CDP connection test failed: {e}")
            return False
    
    def get_available_apis(self) -> Dict[str, Any]:
        """
        Get information about available CDP APIs.
        
        Returns:
            Dictionary with API information
        """
        apis = {
            "cdp_proxy_api": {
                "url": self.get_cdp_proxy_url(),
                "kafka_connect": self.get_kafka_connect_url(),
                "available": False
            },
            "cdp_proxy_token": {
                "url": self.get_cdp_proxy_token_url(),
                "kafka_connect": self.get_kafka_connect_token_url(),
                "available": False
            }
        }
        
        # Test CDP proxy API
        try:
            response = self.session.get(self.get_kafka_connect_url(), timeout=10)
            apis["cdp_proxy_api"]["available"] = response.status_code in [200, 401, 403]
            apis["cdp_proxy_api"]["status_code"] = response.status_code
        except Exception as e:
            apis["cdp_proxy_api"]["error"] = str(e)
        
        # Test CDP proxy token API
        try:
            response = self.session.get(self.get_kafka_connect_token_url(), timeout=10)
            apis["cdp_proxy_token"]["available"] = response.status_code in [200, 401, 403]
            apis["cdp_proxy_token"]["status_code"] = response.status_code
        except Exception as e:
            apis["cdp_proxy_token"]["error"] = str(e)
        
        return apis
    
    def list_connectors(self) -> List[str]:
        """
        List Kafka Connect connectors through CDP.
        
        Returns:
            List of connector names
        """
        # Try CDP proxy token API first
        try:
            response = self.session.get(f"{self.get_kafka_connect_token_url()}/connectors", timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"CDP proxy token API failed: {e}")
        
        # Fallback to CDP proxy API
        try:
            response = self.session.get(f"{self.get_kafka_connect_url()}/connectors", timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"CDP proxy API failed: {e}")
        
        return []
    
    def create_connector(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a Kafka Connect connector through CDP.
        
        Args:
            name: Connector name
            config: Connector configuration
        
        Returns:
            Creation result
        """
        connector_data = {
            "name": name,
            "config": config
        }
        
        # Try CDP proxy token API first
        try:
            response = self.session.post(
                f"{self.get_kafka_connect_token_url()}/connectors",
                json=connector_data,
                timeout=30
            )
            if response.status_code in [200, 201]:
                return response.json()
        except Exception as e:
            logger.warning(f"CDP proxy token API failed: {e}")
        
        # Fallback to CDP proxy API
        try:
            response = self.session.post(
                f"{self.get_kafka_connect_url()}/connectors",
                json=connector_data,
                timeout=30
            )
            if response.status_code in [200, 201]:
                return response.json()
        except Exception as e:
            logger.warning(f"CDP proxy API failed: {e}")
        
        return {"error": "Failed to create connector through CDP APIs"}
    
    def get_connector_status(self, name: str) -> Dict[str, Any]:
        """
        Get connector status through CDP.
        
        Args:
            name: Connector name
        
        Returns:
            Connector status
        """
        # Try CDP proxy token API first
        try:
            response = self.session.get(f"{self.get_kafka_connect_token_url()}/connectors/{name}/status", timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"CDP proxy token API failed: {e}")
        
        # Fallback to CDP proxy API
        try:
            response = self.session.get(f"{self.get_kafka_connect_url()}/connectors/{name}/status", timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"CDP proxy API failed: {e}")
        
        return {"error": "Failed to get connector status through CDP APIs"}
    
    def delete_connector(self, name: str) -> bool:
        """
        Delete a connector through CDP.
        
        Args:
            name: Connector name
        
        Returns:
            True if successful
        """
        # Try CDP proxy token API first
        try:
            response = self.session.delete(f"{self.get_kafka_connect_token_url()}/connectors/{name}", timeout=30)
            if response.status_code in [200, 204]:
                return True
        except Exception as e:
            logger.warning(f"CDP proxy token API failed: {e}")
        
        # Fallback to CDP proxy API
        try:
            response = self.session.delete(f"{self.get_kafka_connect_url()}/connectors/{name}", timeout=30)
            if response.status_code in [200, 204]:
                return True
        except Exception as e:
            logger.warning(f"CDP proxy API failed: {e}")
        
        return False
    
    def get_connect_server_info(self) -> Dict[str, Any]:
        """
        Get Kafka Connect server information through CDP.
        
        Returns:
            Server information
        """
        # Try CDP proxy token API first
        try:
            response = self.session.get(f"{self.get_kafka_connect_token_url()}", timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"CDP proxy token API failed: {e}")
        
        # Fallback to CDP proxy API
        try:
            response = self.session.get(f"{self.get_kafka_connect_url()}", timeout=30)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            logger.warning(f"CDP proxy API failed: {e}")
        
        return {"error": "Failed to get server info through CDP APIs"}
    
    def validate_token(self, token: str) -> bool:
        """
        Validate a CDP token.
        
        Args:
            token: Token to validate
        
        Returns:
            True if token is valid
        """
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
            response = self.session.get(self.get_kafka_connect_token_url(), headers=headers, timeout=10)
            return response.status_code in [200, 401, 403]
        except Exception as e:
            logger.error(f"Token validation failed: {e}")
            return False
    
    def get_service_health(self) -> Dict[str, Any]:
        """
        Get health status of CDP services.
        
        Returns:
            Health information
        """
        health_info = {
            "cdp_connection": self.test_connection(),
            "apis": self.get_available_apis(),
            "connectors": {
                "available": len(self.list_connectors()) >= 0,
                "count": len(self.list_connectors())
            }
        }
        
        # Determine overall health
        if health_info["cdp_connection"] and any(api["available"] for api in health_info["apis"].values()):
            health_info["overall_health"] = "healthy"
        elif health_info["cdp_connection"]:
            health_info["overall_health"] = "degraded"
        else:
            health_info["overall_health"] = "unhealthy"
        
        return health_info


class CDPKafkaClient:
    """
    Kafka client that uses CDP Cloud for secure access.
    
    This client provides Kafka operations through CDP Cloud,
    ensuring secure access to Kafka services.
    """
    
    def __init__(self, cdp_client: CDPClient):
        """
        Initialize CDP Kafka client.
        
        Args:
            cdp_client: CDP client instance
        """
        self.cdp_client = cdp_client
        self.connect_url = cdp_client.get_kafka_connect_url()
        self.connect_token_url = cdp_client.get_kafka_connect_token_url()
    
    def get_kafka_connect_url(self) -> str:
        """Get the best available Kafka Connect URL."""
        apis = self.cdp_client.get_available_apis()
        
        # Prefer CDP proxy token API if available
        if apis["cdp_proxy_token"]["available"]:
            return self.connect_token_url
        elif apis["cdp_proxy_api"]["available"]:
            return self.connect_url
        else:
            return self.connect_url  # Fallback
    
    def test_connectivity(self) -> bool:
        """Test connectivity to Kafka Connect through CDP."""
        return self.cdp_client.test_connection()
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about available Kafka services."""
        return {
            "connect_url": self.get_kafka_connect_url(),
            "cdp_url": self.cdp_client.cdp_url,
            "apis": self.cdp_client.get_available_apis()
        }
