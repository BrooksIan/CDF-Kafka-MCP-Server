"""Tests for configuration management."""

import pytest
from cdf_kafka_mcp_server.config import Config, KafkaConfig, KnoxConfig, load_config


def test_kafka_config_validation():
    """Test Kafka configuration validation."""
    # Valid configuration
    config = KafkaConfig(
        bootstrap_servers="localhost:9092",
        client_id="test-client",
        security_protocol="PLAINTEXT"
    )
    assert config.bootstrap_servers == ["localhost:9092"]
    assert config.client_id == "test-client"
    assert config.security_protocol == "PLAINTEXT"
    
    # Test multiple bootstrap servers
    config = KafkaConfig(
        bootstrap_servers="localhost:9092,localhost:9093",
        client_id="test-client"
    )
    assert config.bootstrap_servers == ["localhost:9092", "localhost:9093"]


def test_kafka_config_invalid_security_protocol():
    """Test invalid security protocol validation."""
    with pytest.raises(ValueError, match="Invalid security_protocol"):
        KafkaConfig(
            bootstrap_servers="localhost:9092",
            security_protocol="INVALID"
        )


def test_knox_config_validation():
    """Test Knox configuration validation."""
    # Valid configuration with token
    config = KnoxConfig(
        gateway="https://knox.example.com:8443",
        token="test-token"
    )
    assert config.gateway == "https://knox.example.com:8443"
    assert config.token == "test-token"
    assert config.is_authenticated() is True
    
    # Valid configuration with username/password
    config = KnoxConfig(
        gateway="https://knox.example.com:8443",
        username="user",
        password="pass"
    )
    assert config.is_authenticated() is True
    
    # Invalid configuration - no auth
    with pytest.raises(ValueError, match="either token or username/password"):
        KnoxConfig(gateway="https://knox.example.com:8443")


def test_knox_config_invalid_gateway():
    """Test invalid gateway URL validation."""
    with pytest.raises(ValueError, match="Gateway URL must start with"):
        KnoxConfig(
            gateway="invalid-url",
            token="test-token"
        )


def test_config_creation():
    """Test main configuration creation."""
    config = Config(
        kafka=KafkaConfig(bootstrap_servers="localhost:9092"),
        log_level="INFO"
    )
    assert config.kafka.bootstrap_servers == ["localhost:9092"]
    assert config.log_level == "INFO"
    assert config.is_knox_enabled() is False
    
    # With Knox
    knox_config = KnoxConfig(
        gateway="https://knox.example.com:8443",
        token="test-token"
    )
    config = Config(
        kafka=KafkaConfig(bootstrap_servers="localhost:9092"),
        knox=knox_config,
        log_level="DEBUG"
    )
    assert config.is_knox_enabled() is True
    assert config.log_level == "DEBUG"
