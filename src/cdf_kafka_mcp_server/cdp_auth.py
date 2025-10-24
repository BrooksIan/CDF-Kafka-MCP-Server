"""
CDP Authentication Module
Comprehensive authentication mechanisms for Cloudera Data Platform
"""

import base64
import json
import time
import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from enum import Enum

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

logger = logging.getLogger(__name__)

class AuthMethod(Enum):
    """Authentication methods supported by CDP."""
    BASIC = "basic"
    BEARER_TOKEN = "bearer_token"
    KNOX_TOKEN = "knox_token"
    OAUTH2 = "oauth2"
    SAML = "saml"
    KERBEROS = "kerberos"

@dataclass
class AuthCredentials:
    """Authentication credentials for CDP."""
    username: str
    password: str
    token: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    realm: Optional[str] = None
    keytab_path: Optional[str] = None
    principal: Optional[str] = None

@dataclass
class AuthToken:
    """Authentication token with metadata."""
    token: str
    token_type: str = "Bearer"
    expires_in: Optional[int] = None
    expires_at: Optional[float] = None
    scope: Optional[str] = None
    refresh_token: Optional[str] = None

class CDPAuthenticationError(Exception):
    """CDP Authentication error."""
    pass

class CDPAuthenticator:
    """Comprehensive CDP authentication handler."""
    
    def __init__(self, base_url: str, credentials: AuthCredentials, 
                 verify_ssl: bool = False, timeout: int = 30):
        """
        Initialize CDP authenticator.
        
        Args:
            base_url: CDP base URL
            credentials: Authentication credentials
            verify_ssl: Whether to verify SSL certificates
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.credentials = credentials
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        
        # Create session
        self.session = self._create_session()
        
        # Authentication state
        self._current_token: Optional[AuthToken] = None
        self._auth_method: Optional[AuthMethod] = None
        self._last_auth_time: Optional[float] = None
        
        # CDP-specific endpoints
        self.auth_endpoints = {
            'oauth2_token': '/oauth2/token',
            'knox_token': '/irb-kakfa-only/cdp-proxy-token/knox-token',
            'saml_sso': '/irb-kakfa-only/cdp-proxy/saml/sso',
            'kerberos_tgt': '/irb-kakfa-only/cdp-proxy/kerberos/tgt',
            'basic_auth': '/irb-kakfa-only/cdp-proxy/auth/basic',
            'cdp_auth': '/irb-kakfa-only/cdp-proxy-api/auth',
            'cdp_token': '/irb-kakfa-only/cdp-proxy-api/token'
        }
        
        logger.info(f"CDP Authenticator initialized for {self.base_url}")
    
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
        
        # SSL verification
        session.verify = self.verify_ssl
        
        # Disable SSL warnings if verification is disabled
        if not self.verify_ssl:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        return session
    
    def authenticate(self, method: Optional[AuthMethod] = None) -> AuthToken:
        """
        Authenticate with CDP using the specified method.
        
        Args:
            method: Authentication method to use (auto-detect if None)
            
        Returns:
            Authentication token
        """
        if method is None:
            method = self._detect_auth_method()
        
        self._auth_method = method
        self._last_auth_time = time.time()
        
        try:
            if method == AuthMethod.BASIC:
                return self._authenticate_basic()
            elif method == AuthMethod.BEARER_TOKEN:
                return self._authenticate_bearer_token()
            elif method == AuthMethod.KNOX_TOKEN:
                return self._authenticate_knox_token()
            elif method == AuthMethod.OAUTH2:
                return self._authenticate_oauth2()
            elif method == AuthMethod.SAML:
                return self._authenticate_saml()
            elif method == AuthMethod.KERBEROS:
                return self._authenticate_kerberos()
            else:
                raise CDPAuthenticationError(f"Unsupported authentication method: {method}")
        except Exception as e:
            logger.error(f"Authentication failed with method {method}: {e}")
            raise CDPAuthenticationError(f"Authentication failed: {e}")
    
    def _detect_auth_method(self) -> AuthMethod:
        """Detect the best authentication method based on available credentials."""
        if self.credentials.token:
            if 'knox' in self.credentials.token.lower() or len(self.credentials.token) > 500:
                return AuthMethod.KNOX_TOKEN
            else:
                return AuthMethod.BEARER_TOKEN
        elif self.credentials.client_id and self.credentials.client_secret:
            return AuthMethod.OAUTH2
        elif self.credentials.keytab_path and self.credentials.principal:
            return AuthMethod.KERBEROS
        else:
            return AuthMethod.BASIC
    
    def _authenticate_basic(self) -> AuthToken:
        """Authenticate using basic authentication."""
        logger.info("Authenticating with basic authentication")
        
        # Create basic auth header
        credentials = f"{self.credentials.username}:{self.credentials.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Test basic auth with a simple endpoint
        test_url = urljoin(self.base_url, '/api/health')
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Accept': 'application/json',
            'User-Agent': 'CDF-Kafka-MCP-Server/1.0'
        }
        
        try:
            response = self.session.get(test_url, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 401, 403]:
                # Basic auth is working (even if endpoint returns 401/403)
                token = AuthToken(
                    token=encoded_credentials,
                    token_type="Basic",
                    expires_in=None,
                    expires_at=None
                )
                self._current_token = token
                return token
            else:
                raise CDPAuthenticationError(f"Basic authentication failed: {response.status_code}")
        except Exception as e:
            raise CDPAuthenticationError(f"Basic authentication failed: {e}")
    
    def _authenticate_bearer_token(self) -> AuthToken:
        """Authenticate using bearer token."""
        logger.info("Authenticating with bearer token")
        
        if not self.credentials.token:
            raise CDPAuthenticationError("Bearer token not provided")
        
        # Test bearer token
        test_url = urljoin(self.base_url, '/api/health')
        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Accept': 'application/json',
            'User-Agent': 'CDF-Kafka-MCP-Server/1.0'
        }
        
        try:
            response = self.session.get(test_url, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 401, 403]:
                token = AuthToken(
                    token=self.credentials.token,
                    token_type="Bearer",
                    expires_in=None,
                    expires_at=None
                )
                self._current_token = token
                return token
            else:
                raise CDPAuthenticationError(f"Bearer token authentication failed: {response.status_code}")
        except Exception as e:
            raise CDPAuthenticationError(f"Bearer token authentication failed: {e}")
    
    def _authenticate_knox_token(self) -> AuthToken:
        """Authenticate using Knox token."""
        logger.info("Authenticating with Knox token")
        
        if not self.credentials.token:
            raise CDPAuthenticationError("Knox token not provided")
        
        # Test Knox token
        test_url = urljoin(self.base_url, '/irb-kakfa-only/cdp-proxy-token/gateway/admin/api/v1/info')
        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Accept': 'application/json',
            'User-Agent': 'CDF-Kafka-MCP-Server/1.0'
        }
        
        try:
            response = self.session.get(test_url, headers=headers, timeout=self.timeout)
            
            if response.status_code in [200, 401, 403]:
                token = AuthToken(
                    token=self.credentials.token,
                    token_type="Bearer",
                    expires_in=None,
                    expires_at=None
                )
                self._current_token = token
                return token
            else:
                raise CDPAuthenticationError(f"Knox token authentication failed: {response.status_code}")
        except Exception as e:
            raise CDPAuthenticationError(f"Knox token authentication failed: {e}")
    
    def _authenticate_oauth2(self) -> AuthToken:
        """Authenticate using OAuth2."""
        logger.info("Authenticating with OAuth2")
        
        if not self.credentials.client_id or not self.credentials.client_secret:
            raise CDPAuthenticationError("OAuth2 client credentials not provided")
        
        # Try different OAuth2 endpoints
        oauth2_endpoints = [
            '/oauth2/token',
            '/irb-kakfa-only/cdp-proxy/oauth2/token',
            '/irb-kakfa-only/cdp-proxy-api/oauth2/token'
        ]
        
        for endpoint in oauth2_endpoints:
            try:
                token_url = urljoin(self.base_url, endpoint)
                
                data = {
                    'grant_type': 'client_credentials',
                    'client_id': self.credentials.client_id,
                    'client_secret': self.credentials.client_secret,
                    'scope': 'api'
                }
                
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                    'User-Agent': 'CDF-Kafka-MCP-Server/1.0'
                }
                
                response = self.session.post(token_url, data=data, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    token_data = response.json()
                    token = AuthToken(
                        token=token_data['access_token'],
                        token_type=token_data.get('token_type', 'Bearer'),
                        expires_in=token_data.get('expires_in'),
                        expires_at=time.time() + token_data.get('expires_in', 3600) if token_data.get('expires_in') else None,
                        scope=token_data.get('scope'),
                        refresh_token=token_data.get('refresh_token')
                    )
                    self._current_token = token
                    return token
            except Exception as e:
                logger.debug(f"OAuth2 endpoint {endpoint} failed: {e}")
                continue
        
        raise CDPAuthenticationError("OAuth2 authentication failed on all endpoints")
    
    def _authenticate_saml(self) -> AuthToken:
        """Authenticate using SAML SSO."""
        logger.info("Authenticating with SAML SSO")
        
        # SAML authentication is complex and typically requires browser interaction
        # This is a simplified implementation
        saml_endpoint = urljoin(self.base_url, '/irb-kakfa-only/cdp-proxy/saml/sso')
        
        try:
            # Get SAML request
            response = self.session.get(saml_endpoint, timeout=self.timeout)
            
            if response.status_code == 200:
                # In a real implementation, you would parse the SAML response
                # and extract the token
                raise CDPAuthenticationError("SAML authentication requires browser interaction")
            else:
                raise CDPAuthenticationError(f"SAML authentication failed: {response.status_code}")
        except Exception as e:
            raise CDPAuthenticationError(f"SAML authentication failed: {e}")
    
    def _authenticate_kerberos(self) -> AuthToken:
        """Authenticate using Kerberos."""
        logger.info("Authenticating with Kerberos")
        
        if not self.credentials.keytab_path or not self.credentials.principal:
            raise CDPAuthenticationError("Kerberos credentials not provided")
        
        # Kerberos authentication requires additional libraries
        try:
            import kerberos
        except ImportError:
            raise CDPAuthenticationError("Kerberos library not available")
        
        try:
            # Get Kerberos TGT
            kerberos.getServerPrincipalDetails('HTTP', self.base_url)
            
            # In a real implementation, you would use the Kerberos TGT
            # to obtain a service ticket and then exchange it for a token
            raise CDPAuthenticationError("Kerberos authentication requires additional implementation")
        except Exception as e:
            raise CDPAuthenticationError(f"Kerberos authentication failed: {e}")
    
    def refresh_token(self) -> AuthToken:
        """Refresh the current authentication token."""
        if not self._current_token:
            raise CDPAuthenticationError("No current token to refresh")
        
        if self._current_token.refresh_token:
            # Use refresh token
            return self._authenticate_oauth2()
        else:
            # Re-authenticate
            return self.authenticate(self._auth_method)
    
    def is_token_valid(self) -> bool:
        """Check if the current token is valid."""
        if not self._current_token:
            return False
        
        # Check if token has expired
        if self._current_token.expires_at and time.time() >= self._current_token.expires_at:
            return False
        
        # Check if token is too old (refresh every hour)
        if self._last_auth_time and time.time() - self._last_auth_time > 3600:
            return False
        
        return True
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for requests."""
        if not self._current_token:
            raise CDPAuthenticationError("Not authenticated")
        
        if self._current_token.token_type == "Basic":
            return {
                'Authorization': f'Basic {self._current_token.token}',
                'Accept': 'application/json',
                'User-Agent': 'CDF-Kafka-MCP-Server/1.0'
            }
        else:
            return {
                'Authorization': f'{self._current_token.token_type} {self._current_token.token}',
                'Accept': 'application/json',
                'User-Agent': 'CDF-Kafka-MCP-Server/1.0'
            }
    
    def test_authentication(self) -> Dict[str, Any]:
        """Test authentication with a simple request."""
        try:
            if not self.is_token_valid():
                self.authenticate()
            
            headers = self.get_auth_headers()
            test_url = urljoin(self.base_url, '/api/health')
            
            response = self.session.get(test_url, headers=headers, timeout=self.timeout)
            
            return {
                'authenticated': response.status_code in [200, 401, 403],
                'status_code': response.status_code,
                'method': self._auth_method.value if self._auth_method else 'unknown',
                'token_type': self._current_token.token_type if self._current_token else 'none',
                'expires_at': self._current_token.expires_at if self._current_token else None
            }
        except Exception as e:
            return {
                'authenticated': False,
                'error': str(e),
                'method': self._auth_method.value if self._auth_method else 'unknown'
            }
    
    def discover_auth_endpoints(self) -> Dict[str, Any]:
        """Discover available authentication endpoints."""
        discovered = {}
        
        for name, endpoint in self.auth_endpoints.items():
            try:
                full_url = urljoin(self.base_url, endpoint)
                response = self.session.get(full_url, timeout=5)
                
                discovered[name] = {
                    'endpoint': full_url,
                    'status_code': response.status_code,
                    'available': response.status_code in [200, 401, 403, 404],
                    'content_type': response.headers.get('content-type', ''),
                    'response_size': len(response.text)
                }
            except Exception as e:
                discovered[name] = {
                    'endpoint': full_url,
                    'status_code': 'error',
                    'available': False,
                    'error': str(e)
                }
        
        return discovered

class CDPAuthManager:
    """Manager for CDP authentication across multiple services."""
    
    def __init__(self, base_url: str, credentials: AuthCredentials, 
                 verify_ssl: bool = False):
        """
        Initialize CDP authentication manager.
        
        Args:
            base_url: CDP base URL
            credentials: Authentication credentials
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url
        self.credentials = credentials
        self.verify_ssl = verify_ssl
        
        # Service-specific authenticators
        self.authenticators = {}
        
        # Initialize authenticators for different services
        self._initialize_authenticators()
    
    def _initialize_authenticators(self):
        """Initialize authenticators for different CDP services."""
        services = ['kafka', 'connect', 'smm', 'admin', 'cdp']
        
        for service in services:
            self.authenticators[service] = CDPAuthenticator(
                base_url=self.base_url,
                credentials=self.credentials,
                verify_ssl=self.verify_ssl
            )
    
    def authenticate_service(self, service: str, method: Optional[AuthMethod] = None) -> AuthToken:
        """Authenticate with a specific CDP service."""
        if service not in self.authenticators:
            raise CDPAuthenticationError(f"Unknown service: {service}")
        
        return self.authenticators[service].authenticate(method)
    
    def get_service_auth_headers(self, service: str) -> Dict[str, str]:
        """Get authentication headers for a specific service."""
        if service not in self.authenticators:
            raise CDPAuthenticationError(f"Unknown service: {service}")
        
        return self.authenticators[service].get_auth_headers()
    
    def test_all_services(self) -> Dict[str, Any]:
        """Test authentication for all services."""
        results = {}
        
        for service, authenticator in self.authenticators.items():
            try:
                results[service] = authenticator.test_authentication()
            except Exception as e:
                results[service] = {
                    'authenticated': False,
                    'error': str(e)
                }
        
        return results
    
    def refresh_all_tokens(self) -> Dict[str, bool]:
        """Refresh authentication tokens for all services."""
        results = {}
        
        for service, authenticator in self.authenticators.items():
            try:
                authenticator.refresh_token()
                results[service] = True
            except Exception as e:
                logger.error(f"Failed to refresh token for {service}: {e}")
                results[service] = False
        
        return results
