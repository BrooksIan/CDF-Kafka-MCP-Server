"""
Main entry point for CDF Kafka MCP Server.
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

import click

from .mcp_server import CDFKafkaMCPServer


@click.command()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, path_type=Path),
    help="Path to configuration file",
)
@click.option(
    "--bootstrap-servers",
    help="Kafka bootstrap servers (comma-separated)",
    envvar="KAFKA_BOOTSTRAP_SERVERS",
)
@click.option(
    "--client-id",
    help="Kafka client ID",
    envvar="KAFKA_CLIENT_ID",
    default="cdf-kafka-mcp-server",
)
@click.option(
    "--security-protocol",
    type=click.Choice(["PLAINTEXT", "SASL_PLAINTEXT", "SASL_SSL", "SSL"]),
    help="Security protocol",
    envvar="KAFKA_SECURITY_PROTOCOL",
    default="PLAINTEXT",
)
@click.option(
    "--sasl-mechanism",
    type=click.Choice(["PLAIN", "SCRAM-SHA-256", "SCRAM-SHA-512"]),
    help="SASL mechanism",
    envvar="KAFKA_SASL_MECHANISM",
)
@click.option(
    "--sasl-username",
    help="SASL username",
    envvar="KAFKA_SASL_USERNAME",
)
@click.option(
    "--sasl-password",
    help="SASL password",
    envvar="KAFKA_SASL_PASSWORD",
)
@click.option(
    "--tls-enabled",
    is_flag=True,
    help="Enable TLS",
    envvar="KAFKA_TLS_ENABLED",
)
@click.option(
    "--tls-ca-cert",
    help="TLS CA certificate file",
    envvar="KAFKA_TLS_CA_CERT",
)
@click.option(
    "--tls-cert",
    help="TLS certificate file",
    envvar="KAFKA_TLS_CERT",
)
@click.option(
    "--tls-key",
    help="TLS private key file",
    envvar="KAFKA_TLS_KEY",
)
@click.option(
    "--timeout",
    type=int,
    help="Request timeout in seconds",
    envvar="KAFKA_TIMEOUT",
    default=30,
)
@click.option(
    "--knox-gateway",
    help="Apache Knox Gateway URL",
    envvar="KNOX_GATEWAY",
)
@click.option(
    "--knox-token",
    help="Apache Knox authentication token",
    envvar="KNOX_TOKEN",
)
@click.option(
    "--knox-username",
    help="Apache Knox username",
    envvar="KNOX_USERNAME",
)
@click.option(
    "--knox-password",
    help="Apache Knox password",
    envvar="KNOX_PASSWORD",
)
@click.option(
    "--knox-verify-ssl",
    is_flag=True,
    default=True,
    help="Verify SSL certificates for Knox",
    envvar="KNOX_VERIFY_SSL",
)
@click.option(
    "--knox-ca-bundle",
    help="CA bundle file for Knox SSL verification",
    envvar="KNOX_CA_BUNDLE",
)
@click.option(
    "--knox-service",
    help="Knox service name for Kafka",
    envvar="KNOX_SERVICE",
    default="kafka",
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    help="Log level",
    envvar="MCP_LOG_LEVEL",
    default="INFO",
)
@click.option(
    "--version",
    is_flag=True,
    help="Show version information",
)
def main(
    config: Optional[Path],
    bootstrap_servers: Optional[str],
    client_id: str,
    security_protocol: str,
    sasl_mechanism: Optional[str],
    sasl_username: Optional[str],
    sasl_password: Optional[str],
    tls_enabled: bool,
    tls_ca_cert: Optional[str],
    tls_cert: Optional[str],
    tls_key: Optional[str],
    timeout: int,
    knox_gateway: Optional[str],
    knox_token: Optional[str],
    knox_username: Optional[str],
    knox_password: Optional[str],
    knox_verify_ssl: bool,
    knox_ca_bundle: Optional[str],
    knox_service: str,
    log_level: str,
    version: bool,
) -> None:
    """
    CDF Kafka MCP Server - A Model Context Protocol server for Apache Kafka with Knox authentication.
    """
    if version:
        from . import __version__
        click.echo(f"CDF Kafka MCP Server version {__version__}")
        return

    # Set up logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("cdf_kafka_mcp_server")

    try:
        # Load configuration
        config_path = str(config) if config else None
        if not config_path:
            default_config = get_default_config_path()
            if Path(default_config).exists():
                config_path = default_config

        # Override with command line arguments
        import os
        if bootstrap_servers:
            os.environ["KAFKA_BOOTSTRAP_SERVERS"] = bootstrap_servers
        if client_id:
            os.environ["KAFKA_CLIENT_ID"] = client_id
        if security_protocol:
            os.environ["KAFKA_SECURITY_PROTOCOL"] = security_protocol
        if sasl_mechanism:
            os.environ["KAFKA_SASL_MECHANISM"] = sasl_mechanism
        if sasl_username:
            os.environ["KAFKA_SASL_USERNAME"] = sasl_username
        if sasl_password:
            os.environ["KAFKA_SASL_PASSWORD"] = sasl_password
        if tls_enabled:
            os.environ["KAFKA_TLS_ENABLED"] = "true"
        if tls_ca_cert:
            os.environ["KAFKA_TLS_CA_CERT"] = tls_ca_cert
        if tls_cert:
            os.environ["KAFKA_TLS_CERT"] = tls_cert
        if tls_key:
            os.environ["KAFKA_TLS_KEY"] = tls_key
        if timeout:
            os.environ["KAFKA_TIMEOUT"] = str(timeout)
        if knox_gateway:
            os.environ["KNOX_GATEWAY"] = knox_gateway
        if knox_token:
            os.environ["KNOX_TOKEN"] = knox_token
        if knox_username:
            os.environ["KNOX_USERNAME"] = knox_username
        if knox_password:
            os.environ["KNOX_PASSWORD"] = knox_password
        if not knox_verify_ssl:
            os.environ["KNOX_VERIFY_SSL"] = "false"
        if knox_ca_bundle:
            os.environ["KNOX_CA_BUNDLE"] = knox_ca_bundle
        if knox_service:
            os.environ["KNOX_SERVICE"] = knox_service
        if log_level:
            os.environ["MCP_LOG_LEVEL"] = log_level

        # Create and run server
        server = CDFKafkaMCPServer(config_path)
        logger.info("Starting CDF Kafka MCP Server...")

        # Run the server
        asyncio.run(server.run())

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
