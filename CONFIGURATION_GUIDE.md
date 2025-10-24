# CDF Kafka MCP Server Configuration Guide

## Overview

The CDF Kafka MCP Server supports multiple configuration methods to work with different environments and deployment scenarios. All endpoints are configurable and no hard-coded values are used.

## Configuration Methods

### 1. Claude Desktop Configuration (Recommended for AI Agent Studio)

Create a `claude_desktop_config.json` file in your Claude Desktop configuration directory:

```json
{
  "mcpServers": {
    "cdf-kafka-mcp-server": {
      "command": "uv",
      "args": [
        "run",
        "python",
        "-m",
        "cdf_kafka_mcp_server.mcp_server"
      ],
      "env": {
        "KAFKA_BOOTSTRAP_SERVERS": "your-kafka-cluster.example.com:9092",
        "KAFKA_SECURITY_PROTOCOL": "SASL_SSL",
        "KAFKA_SASL_MECHANISM": "PLAIN",
        "KAFKA_SASL_USERNAME": "your-username",
        "KAFKA_SASL_PASSWORD": "your-password",
        "KAFKA_VERIFY_SSL": "false",
        "KAFKA_CLUSTER_ID": "your-cluster-id",
        "KNOX_GATEWAY": "https://your-knox-gateway.example.com:8443/gateway",
        "KNOX_USERNAME": "your-username",
        "KNOX_PASSWORD": "your-password",
        "CDP_URL": "https://your-cdp-cluster.example.com:443",
        "CDP_USERNAME": "your-username",
        "CDP_PASSWORD": "your-password",
        "CDP_REST_BASE_URL": "https://your-cdp-cluster.example.com:443",
        "CDP_REST_USERNAME": "your-username",
        "CDP_REST_PASSWORD": "your-password",
        "CDP_REST_CLUSTER_ID": "your-cluster-id",
        "KAFKA_CONNECT_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-token/kafka-connect",
        "KAFKA_REST_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/kafka-rest",
        "KAFKA_TOPICS_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/kafka-topics",
        "SMM_API_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/smm-api",
        "ADMIN_API_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/admin",
        "CDP_API_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-api",
        "TARGET_BASE_URL": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-token",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 2. YAML Configuration File

Create a `kafka_config.yaml` file:

```yaml
kafka:
  bootstrap_servers:
    - "your-kafka-cluster.example.com:9092"
  security_protocol: "SASL_SSL"
  sasl_mechanism: "PLAIN"
  sasl_username: "your-username"
  sasl_password: "your-password"
  verify_ssl: true
  cluster_id: "your-cluster-id"

knox:
  gateway: "https://your-knox-gateway.example.com:8443/gateway"
  username: "your-username"
  password: "your-password"
  verify_ssl: true

cdp:
  url: "https://your-cdp-cluster.example.com:443"
  username: "your-username"
  password: "your-password"
  cluster_id: "your-cluster-id"

cdp_rest:
  base_url: "https://your-cdp-cluster.example.com:443"
  username: "your-username"
  password: "your-password"
  cluster_id: "your-cluster-id"
  
  # Individual endpoint configurations (optional)
  kafka_connect_endpoint: "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-token/kafka-connect"
  kafka_rest_endpoint: "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/kafka-rest"
  kafka_topics_endpoint: "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/kafka-topics"
  smm_api_endpoint: "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/smm-api"
  admin_api_endpoint: "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/admin"
  cdp_api_endpoint: "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-api"

target_base_url: "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-token"
log_level: "INFO"
```

### 3. Environment Variables

Set environment variables:

```bash
export KAFKA_BOOTSTRAP_SERVERS="your-kafka-cluster.example.com:9092"
export KAFKA_SECURITY_PROTOCOL="SASL_SSL"
export KAFKA_SASL_MECHANISM="PLAIN"
export KAFKA_SASL_USERNAME="your-username"
export KAFKA_SASL_PASSWORD="your-password"
export KAFKA_VERIFY_SSL="true"
export KAFKA_CLUSTER_ID="your-cluster-id"
export KNOX_GATEWAY="https://your-knox-gateway.example.com:8443/gateway"
export KNOX_USERNAME="your-username"
export KNOX_PASSWORD="your-password"
export CDP_URL="https://your-cdp-cluster.example.com:443"
export CDP_USERNAME="your-username"
export CDP_PASSWORD="your-password"
export CDP_REST_BASE_URL="https://your-cdp-cluster.example.com:443"
export CDP_REST_USERNAME="your-username"
export CDP_REST_PASSWORD="your-password"
export CDP_REST_CLUSTER_ID="your-cluster-id"
export KAFKA_CONNECT_ENDPOINT="https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-token/kafka-connect"
export KAFKA_REST_ENDPOINT="https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/kafka-rest"
export KAFKA_TOPICS_ENDPOINT="https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/kafka-topics"
export SMM_API_ENDPOINT="https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/smm-api"
export ADMIN_API_ENDPOINT="https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/admin"
export CDP_API_ENDPOINT="https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-api"
export TARGET_BASE_URL="https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-token"
export LOG_LEVEL="INFO"
```

## Environment-Specific Examples

### Cloudera AI Agent Studio

For Cloudera AI Agent Studio, use the Claude Desktop configuration with your specific CDP environment:

```json
{
  "mcpServers": {
    "cdf-kafka-mcp-server": {
      "command": "uv",
      "args": ["run", "python", "-m", "cdf_kafka_mcp_server.mcp_server"],
      "env": {
        "KAFKA_BOOTSTRAP_SERVERS": "your-cdp-cluster.example.com:443",
        "KAFKA_SECURITY_PROTOCOL": "SASL_SSL",
        "KAFKA_SASL_MECHANISM": "PLAIN",
        "KAFKA_SASL_USERNAME": "your-username",
        "KAFKA_SASL_PASSWORD": "your-password",
        "KAFKA_VERIFY_SSL": "false",
        "KAFKA_CLUSTER_ID": "your-cluster-id",
        "KAFKA_CONNECT_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-token/kafka-connect",
        "KAFKA_REST_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/kafka-rest",
        "KAFKA_TOPICS_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/kafka-topics",
        "SMM_API_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/smm-api",
        "ADMIN_API_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy/admin",
        "CDP_API_ENDPOINT": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-api",
        "TARGET_BASE_URL": "https://your-cdp-cluster.example.com:443/your-cluster/cdp-proxy-token",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Local Development

For local development with a local Kafka cluster:

```yaml
kafka:
  bootstrap_servers:
    - "localhost:9092"
  security_protocol: "PLAINTEXT"
  sasl_mechanism: "PLAIN"
  verify_ssl: false

log_level: "DEBUG"
```

### Production Environment

For production with Knox Gateway:

```yaml
kafka:
  bootstrap_servers:
    - "kafka-prod.example.com:9092"
  security_protocol: "SASL_SSL"
  sasl_mechanism: "PLAIN"
  sasl_username: "prod-user"
  sasl_password: "secure-password"
  verify_ssl: true
  cluster_id: "prod-cluster"

knox:
  gateway: "https://knox-prod.example.com:8443/gateway"
  username: "prod-user"
  password: "secure-password"
  verify_ssl: true

log_level: "INFO"
```

## Configuration Priority

The configuration system follows this priority order:

1. **Environment Variables** (highest priority)
2. **YAML Configuration File**
3. **Default Values** (lowest priority)

## Endpoint Configuration

### Default Endpoint Construction

If individual endpoints are not specified, they are constructed using the base URL + default paths:

- `kafka_connect`: `{base_url}/kafka-connect`
- `kafka_rest`: `{base_url}/kafka-rest`
- `kafka_topics`: `{base_url}/kafka-topics`
- `smm_api`: `{base_url}/smm-api`
- `admin_api`: `{base_url}/admin`
- `cdp_api`: `{base_url}/cdp-proxy-api`

### Custom Endpoint Configuration

You can override individual endpoints using:

- **Environment Variables**: `KAFKA_CONNECT_ENDPOINT`, `KAFKA_REST_ENDPOINT`, etc.
- **YAML Configuration**: `cdp_rest.kafka_connect_endpoint`, `cdp_rest.kafka_rest_endpoint`, etc.

## Security Considerations

1. **Never hard-code credentials** in configuration files
2. **Use environment variables** for sensitive information
3. **Use secure authentication methods** (SASL_SSL, TLS)
4. **Verify SSL certificates** in production environments
5. **Use least-privilege access** for service accounts

## Troubleshooting

### Common Issues

1. **Connection Failures**: Check bootstrap servers and security protocol
2. **Authentication Errors**: Verify credentials and authentication method
3. **SSL Errors**: Check certificate configuration and verify_ssl setting
4. **Endpoint Not Found**: Verify endpoint URLs and cluster configuration

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL="DEBUG"
```

### Health Checks

Use the built-in health check tools:

- `test_connection`: Test basic connectivity
- `get_health_status`: Get comprehensive health status
- `test_authentication`: Test authentication mechanisms

## Migration Guide

### From Hard-coded Configuration

1. **Identify hard-coded values** in your current setup
2. **Create environment-specific configuration** using templates
3. **Set environment variables** or create YAML files
4. **Test configuration** with health check tools
5. **Deploy to target environment**

### Between Environments

1. **Copy configuration template** for new environment
2. **Update endpoint URLs** for new environment
3. **Update credentials** for new environment
4. **Test configuration** before deployment
5. **Deploy and verify** functionality

## Best Practices

1. **Use configuration templates** for consistency
2. **Version control configuration templates** (not actual credentials)
3. **Use environment-specific configurations** for different deployments
4. **Test configurations** before production deployment
5. **Monitor and log** configuration changes
6. **Use secure credential management** systems
7. **Document environment-specific requirements**
