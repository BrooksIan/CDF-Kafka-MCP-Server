"""
Apache Knox Gateway client for authentication and metadata discovery.
"""

import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential

from .config import KnoxConfig


class KnoxError(Exception):
    """Knox Gateway error."""
    pass


class KnoxClient:
    """Client for Apache Knox Gateway authentication and metadata discovery."""

    def __init__(self, config: KnoxConfig):
        """
        Initialize Knox client.

        Args:
            config: Knox configuration
        """
        self.config = config
        self.session = self._create_session()
        self._token: Optional[str] = None
        self._token_expiry: Optional[float] = None

    def _create_session(self) -> requests.Session:
        """Create configured requests session."""
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Configure SSL verification
        session.verify = self.config.verify_ssl
        if self.config.ca_bundle:
            session.verify = self.config.ca_bundle

        # Set timeout
        session.timeout = 30

        return session

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_token(self) -> str:
        """
        Get authentication token from Knox Gateway.

        Returns:
            str: Authentication token

        Raises:
            KnoxError: If authentication fails
        """
        # Return cached token if still valid
        if self._token and self._token_expiry and time.time() < self._token_expiry:
            return self._token

        # If we have a token configured directly, use it
        if self.config.token:
            self._token = self.config.token
            self._token_expiry = time.time() + 24 * 3600  # Assume long-lived token
            return self._token

        # Otherwise, authenticate with username/password
        return self._authenticate_with_credentials()

    def _authenticate_with_credentials(self) -> str:
        """Authenticate with Knox using username/password."""
        token_url = urljoin(self.config.gateway, f"gateway/{self.config.service}/oauth/token")

        data = {
            'grant_type': 'password',
            'username': self.config.username,
            'password': self.config.password,
            'scope': 'kafka'
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }

        try:
            response = self.session.post(
                token_url,
                data=data,
                headers=headers,
                auth=(self.config.username, self.config.password)
            )
            response.raise_for_status()

            token_data = response.json()
            self._token = token_data['access_token']

            # Set token expiry
            if 'expires_in' in token_data:
                self._token_expiry = time.time() + token_data['expires_in']
            else:
                self._token_expiry = time.time() + 3600  # Default to 1 hour

            return self._token

        except requests.exceptions.RequestException as e:
            raise KnoxError(f"Failed to authenticate with Knox Gateway: {e}")
        except KeyError as e:
            raise KnoxError(f"Invalid token response from Knox Gateway: missing {e}")
        except json.JSONDecodeError as e:
            raise KnoxError(f"Invalid JSON response from Knox Gateway: {e}")

    def get_authenticated_request(self, method: str, path: str, **kwargs) -> requests.Request:
        """
        Create an authenticated HTTP request to Knox Gateway.

        Args:
            method: HTTP method
            path: Request path
            **kwargs: Additional request arguments

        Returns:
            requests.Request: Authenticated request
        """
        token = self.get_token()

        # Build the full URL
        full_url = urljoin(self.config.gateway, f"gateway/{self.config.service}/{path}")

        # Set default headers
        headers = kwargs.get('headers', {})
        headers.update({
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json'
        })
        kwargs['headers'] = headers

        return requests.Request(method, full_url, **kwargs)

    def test_connection(self) -> bool:
        """
        Test the connection to Knox Gateway.

        Returns:
            bool: True if connection successful
        """
        try:
            self.get_token()
            return True
        except KnoxError:
            return False

    def get_kafka_metadata(self) -> Dict[str, Any]:
        """
        Get Kafka metadata from Knox Gateway.

        Returns:
            Dict[str, Any]: Kafka metadata

        Raises:
            KnoxError: If metadata retrieval fails
        """
        try:
            req = self.get_authenticated_request('GET', 'api/v1/metadata')
            response = self.session.send(req.prepare())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise KnoxError(f"Failed to get Kafka metadata: {e}")
        except json.JSONDecodeError as e:
            raise KnoxError(f"Invalid JSON response from Knox Gateway: {e}")

    def get_kafka_bootstrap_servers(self) -> List[str]:
        """
        Get Kafka bootstrap servers through Knox Gateway.

        Returns:
            List[str]: List of bootstrap servers
        """
        try:
            metadata = self.get_kafka_metadata()

            # Extract bootstrap servers from metadata
            # The actual structure depends on your Knox configuration
            if 'bootstrap_servers' in metadata:
                servers = metadata['bootstrap_servers']
                if isinstance(servers, list):
                    return servers
                elif isinstance(servers, str):
                    return [server.strip() for server in servers.split(',')]

            # Fallback: return empty list - should not use gateway URL as bootstrap server
            # The actual Kafka bootstrap servers should be provided in the configuration
            return []

        except KnoxError:
            # Fallback: return empty list - should not use gateway URL as bootstrap server
            return []

    def close(self) -> None:
        """Close the Knox client session."""
        self.session.close()
