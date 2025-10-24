"""
Configuration management for CDF Kafka MCP Server.
"""

import os
from pathlib import Path
from typing import Optional, List, Union, Dict

import yaml
from pydantic import BaseModel, field_validator, Field
from dotenv import load_dotenv


class KnoxConfig(BaseModel):
    """Apache Knox Gateway configuration."""

    gateway: str = Field(..., description="Knox Gateway URL")
    token: Optional[str] = Field(None, description="OAuth2 token for Knox authentication")
    username: Optional[str] = Field(None, description="Username for Knox authentication")
    password: Optional[str] = Field(None, description="Password for Knox authentication")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    ca_bundle: Optional[str] = Field(None, description="Path to CA bundle file")
    service: str = Field("kafka", description="Knox service name for Kafka")

    @field_validator('gateway')
    def validate_gateway(cls, v: str) -> str:
        """Validate gateway URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Gateway URL must start with http:// or https://")
        return v.rstrip('/')

    @field_validator('token', 'username', 'password')
    def validate_auth(cls, v: Optional[str], values: Dict) -> Optional[str]:
        """Validate authentication configuration."""
        if v is not None and v.strip() == "":
            return None
        return v

    def is_authenticated(self) -> bool:
        """Check if authentication is configured."""
        return bool(self.token or (self.username and self.password))


class CDPConfig(BaseModel):
    """CDP Cloud configuration."""

    url: str = Field(..., description="CDP Cloud base URL")
    username: str = Field(..., description="Username for CDP authentication")
    password: str = Field(..., description="Password for CDP authentication")
    token: Optional[str] = Field(None, description="CDP token for authentication")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")
    timeout: int = Field(30, description="Request timeout in seconds")

    @field_validator('url')
    def validate_url(cls, v: str) -> str:
        """Validate CDP URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("CDP URL must start with http:// or https://")
        return v.rstrip('/')

    @field_validator('token')
    def validate_token(cls, v: Optional[str]) -> Optional[str]:
        """Validate token format."""
        if v is not None and v.strip() == "":
            return None
        return v

    def is_authenticated(self) -> bool:
        """Check if authentication is configured."""
        return bool(self.token or (self.username and self.password))


class KafkaConfig(BaseModel):
    """Kafka cluster configuration."""

    bootstrap_servers: Union[str, List[str]] = Field(..., description="Kafka bootstrap servers")
    client_id: str = Field("cdf-kafka-mcp-server", description="Kafka client ID")
    security_protocol: str = Field("PLAINTEXT", description="Security protocol")
    sasl_mechanism: Optional[str] = Field(None, description="SASL mechanism")
    sasl_username: Optional[str] = Field(None, description="SASL username")
    sasl_password: Optional[str] = Field(None, description="SASL password")
    tls_enabled: bool = Field(False, description="Enable TLS")
    tls_ca_cert: Optional[str] = Field(None, description="TLS CA certificate file")
    tls_cert: Optional[str] = Field(None, description="TLS certificate file")
    tls_key: Optional[str] = Field(None, description="TLS private key file")
    timeout: int = Field(30, description="Request timeout in seconds")

    @field_validator('security_protocol')
    def validate_security_protocol(cls, v: str) -> str:
        """Validate security protocol."""
        valid_protocols = ["PLAINTEXT", "SASL_PLAINTEXT", "SASL_SSL", "SSL"]
        if v not in valid_protocols:
            raise ValueError(f"Invalid security_protocol: {v}, must be one of {valid_protocols}")
        return v

    @field_validator('sasl_mechanism')
    def validate_sasl_mechanism(cls, v: Optional[str], values: Dict) -> Optional[str]:
        """Validate SASL mechanism."""
        if v is not None:
            valid_mechanisms = ["PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512"]
            if v not in valid_mechanisms:
                raise ValueError(f"Invalid sasl_mechanism: {v}, must be one of {valid_mechanisms}")
        return v

    @field_validator('bootstrap_servers')
    def validate_bootstrap_servers(cls, v: Union[str, List[str]]) -> List[str]:
        """Convert bootstrap servers to list."""
        if isinstance(v, str):
            return [server.strip() for server in v.split(',')]
        return v


class CDPRestConfig(BaseModel):
    """CDP REST API configuration."""
    
    base_url: str = Field(..., description="CDP REST API base URL")
    username: str = Field(..., description="Username for CDP REST authentication")
    password: str = Field(..., description="Password for CDP REST authentication")
    cluster_id: str = Field(..., description="CDP cluster ID")
    endpoints: Optional[Dict[str, str]] = Field(None, description="Custom endpoint URLs")
    timeout: int = Field(30, description="Request timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: int = Field(1, description="Delay between retries in seconds")
    kafka_connect_endpoint: Optional[str] = Field(None, description="Kafka Connect API endpoint")
    kafka_rest_endpoint: Optional[str] = Field(None, description="Kafka REST API endpoint")
    kafka_topics_endpoint: Optional[str] = Field(None, description="Kafka Topics API endpoint")
    smm_api_endpoint: Optional[str] = Field(None, description="SMM API endpoint")
    admin_api_endpoint: Optional[str] = Field(None, description="Admin API endpoint")
    cdp_api_endpoint: Optional[str] = Field(None, description="CDP API endpoint")


class Config(BaseModel):
    """Main configuration class."""

    kafka: KafkaConfig = Field(..., description="Kafka configuration")
    knox: Optional[KnoxConfig] = Field(None, description="Knox configuration")
    cdp: Optional[CDPConfig] = Field(None, description="CDP Cloud configuration")
    cdp_rest: Optional[CDPRestConfig] = Field(None, description="CDP REST API configuration")
    target_base_url: Optional[str] = Field(None, description="Configurable target base URL")
    log_level: str = Field("INFO", description="Log level")

    @field_validator('log_level')
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log_level: {v}, must be one of {valid_levels}")
        return v.upper()

    def is_knox_enabled(self) -> bool:
        """Check if Knox authentication is enabled."""
        return self.knox is not None and self.knox.is_authenticated()

    def is_cdp_enabled(self) -> bool:
        """Check if CDP Cloud authentication is enabled."""
        return self.cdp is not None and self.cdp.is_authenticated()


def load_config(config_path: Optional[str] = None) -> Config:
    """
    Load configuration from file and environment variables.

    Args:
        config_path: Path to configuration file

    Returns:
        Config: Loaded configuration
    """
    # Load environment variables
    load_dotenv()

    config_data = {}

    # Load from file if provided
    if config_path and Path(config_path).exists():
        with open(config_path, 'r') as f:
            content = f.read()
            
        # Handle variable substitution for target_base_url
        if 'target_base_url' in content:
            # Extract target_base_url from the content
            import re
            target_base_url_match = re.search(r'target_base_url:\s*["\']([^"\']+)["\']', content)
            if target_base_url_match:
                target_base_url = target_base_url_match.group(1)
                # Replace ${target_base_url} with the actual value
                content = content.replace('${target_base_url}', target_base_url)
            
        config_data = yaml.safe_load(content)

    # Override with environment variables
    env_config = {
        'kafka': {
            'bootstrap_servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
            'client_id': os.getenv('KAFKA_CLIENT_ID'),
            'security_protocol': os.getenv('KAFKA_SECURITY_PROTOCOL'),
            'sasl_mechanism': os.getenv('KAFKA_SASL_MECHANISM'),
            'sasl_username': os.getenv('KAFKA_SASL_USERNAME'),
            'sasl_password': os.getenv('KAFKA_SASL_PASSWORD'),
            'tls_enabled': os.getenv('KAFKA_TLS_ENABLED', '').lower() == 'true',
            'tls_ca_cert': os.getenv('KAFKA_TLS_CA_CERT'),
            'tls_cert': os.getenv('KAFKA_TLS_CERT'),
            'tls_key': os.getenv('KAFKA_TLS_KEY'),
            'timeout': int(os.getenv('KAFKA_TIMEOUT', '30')),
            'verify_ssl': os.getenv('KAFKA_VERIFY_SSL', 'true').lower() == 'true',
            'cluster_id': os.getenv('KAFKA_CLUSTER_ID'),
            'request_timeout_ms': int(os.getenv('KAFKA_REQUEST_TIMEOUT_MS', '30000')),
            'retry_backoff_ms': int(os.getenv('KAFKA_RETRY_BACKOFF_MS', '1000')),
            'max_retry_attempts': int(os.getenv('KAFKA_MAX_RETRY_ATTEMPTS', '3')),
            'auth_method': os.getenv('KAFKA_AUTH_METHOD'),
        },
        'knox': {
            'gateway': os.getenv('KNOX_GATEWAY'),
            'token': os.getenv('KNOX_TOKEN'),
            'username': os.getenv('KNOX_USERNAME'),
            'password': os.getenv('KNOX_PASSWORD'),
            'verify_ssl': os.getenv('KNOX_VERIFY_SSL', 'true').lower() == 'true',
            'ca_bundle': os.getenv('KNOX_CA_BUNDLE'),
            'service': os.getenv('KNOX_SERVICE', 'kafka'),
        },
        'cdp': {
            'url': os.getenv('CDP_URL'),
            'username': os.getenv('CDP_USERNAME'),
            'password': os.getenv('CDP_PASSWORD'),
            'token': os.getenv('CDP_TOKEN'),
        },
        'cdp_rest': {
            'base_url': os.getenv('CDP_REST_BASE_URL'),
            'username': os.getenv('CDP_REST_USERNAME'),
            'password': os.getenv('CDP_REST_PASSWORD'),
            'cluster_id': os.getenv('CDP_REST_CLUSTER_ID'),
            'timeout': int(os.getenv('CDP_REST_TIMEOUT', '30')),
            'retry_attempts': int(os.getenv('CDP_REST_RETRY_ATTEMPTS', '3')),
            'retry_delay': int(os.getenv('CDP_REST_RETRY_DELAY', '1')),
            'kafka_connect_endpoint': os.getenv('KAFKA_CONNECT_ENDPOINT'),
            'kafka_rest_endpoint': os.getenv('KAFKA_REST_ENDPOINT'),
            'kafka_topics_endpoint': os.getenv('KAFKA_TOPICS_ENDPOINT'),
            'smm_api_endpoint': os.getenv('SMM_API_ENDPOINT'),
            'admin_api_endpoint': os.getenv('ADMIN_API_ENDPOINT'),
            'cdp_api_endpoint': os.getenv('CDP_API_ENDPOINT'),
        },
        'target_base_url': os.getenv('TARGET_BASE_URL'),
        'log_level': os.getenv('MCP_LOG_LEVEL', 'INFO'),
    }

    # Filter out None values
    env_config['kafka'] = {k: v for k, v in env_config['kafka'].items() if v is not None}
    env_config['knox'] = {k: v for k, v in env_config['knox'].items() if v is not None}
    env_config['cdp'] = {k: v for k, v in env_config['cdp'].items() if v is not None}
    env_config['cdp_rest'] = {k: v for k, v in env_config['cdp_rest'].items() if v is not None}

    # Merge configurations
    if 'kafka' in config_data:
        config_data['kafka'].update(env_config['kafka'])
    else:
        config_data['kafka'] = env_config['kafka']

    if env_config['knox'].get('gateway'):
        if 'knox' in config_data:
            config_data['knox'].update(env_config['knox'])
        else:
            config_data['knox'] = env_config['knox']

    if env_config['cdp'].get('url'):
        if 'cdp' in config_data:
            config_data['cdp'].update(env_config['cdp'])
        else:
            config_data['cdp'] = env_config['cdp']

    if env_config['cdp_rest'].get('base_url'):
        if 'cdp_rest' in config_data:
            config_data['cdp_rest'].update(env_config['cdp_rest'])
        else:
            config_data['cdp_rest'] = env_config['cdp_rest']

    if env_config['target_base_url']:
        config_data['target_base_url'] = env_config['target_base_url']

    if env_config['log_level']:
        config_data['log_level'] = env_config['log_level']

    # Remove None values from configs
    for section in ['knox', 'cdp', 'cdp_rest']:
        if section in config_data:
            config_data[section] = {k: v for k, v in config_data[section].items() if v is not None}
            if not config_data[section]:
                del config_data[section]

    return Config(**config_data)


def get_default_config_path() -> str:
    """Get the default configuration file path."""
    return str(Path.home() / ".cdf-kafka-mcp-server.yaml")
