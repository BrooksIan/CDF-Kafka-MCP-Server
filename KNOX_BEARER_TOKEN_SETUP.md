# Knox Bearer Token Authentication Setup

## Overview
This guide explains how to configure and use Knox Gateway with bearer token authentication for the CDF Kafka MCP Server.

## ✅ Current Status
- **Knox Gateway**: RUNNING on port 8444
- **Bearer Token Auth**: FULLY IMPLEMENTED and TESTED
- **MCP Integration**: COMPLETE with bearer token support
- **Fallback System**: ROBUST and RELIABLE

## 🔧 Configuration

### 1. Environment Variables (Recommended)
```bash
# Set your Knox Gateway configuration
export KNOX_GATEWAY="https://your-knox-gateway:8444"
export KNOX_TOKEN="your-actual-bearer-token-here"
export KNOX_SERVICE="kafka"
export KNOX_VERIFY_SSL="true"  # Set to false for testing
```

### 2. YAML Configuration File
```yaml
# config/kafka_config.yaml
knox:
  gateway: "https://your-knox-gateway:8444"
  token: "your-actual-bearer-token-here"  # Bearer token (recommended)
  username: ""  # Alternative to token
  password: ""  # Alternative to token
  verify_ssl: true
  service: "kafka"
```

## 🚀 Usage

### 1. Start MCP Server with Bearer Token
```bash
# Set environment variables
export KNOX_GATEWAY="https://localhost:8444"
export KNOX_TOKEN="your-bearer-token-here"
export KNOX_SERVICE="kafka"
export KNOX_VERIFY_SSL="false"

# Start MCP server
uv run python -m cdf_kafka_mcp_server
```

### 2. Test Knox Authentication
```python
import asyncio
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest, CallToolRequestParams

async def test_knox_bearer_token():
    mcp_server = CDFKafkaMCPServer()
    
    # Test MCP tools with Knox authentication
    request = CallToolRequest(
        params=CallToolRequestParams(
            name='list_topics',
            arguments={}
        )
    )
    result = await mcp_server.call_tool(request)
    print(f"Topics: {result.content[0].text}")

asyncio.run(test_knox_bearer_token())
```

## 🔐 Bearer Token Authentication Features

### ✅ Implemented Features
- **Token Caching**: Automatic token caching and refresh
- **SSL Support**: Full SSL/TLS support for Knox Gateway
- **Error Handling**: Comprehensive error handling and recovery
- **Retry Logic**: Robust retry mechanisms with exponential backoff
- **Fallback System**: Graceful fallback when Knox is unavailable

### ✅ MCP Tools with Bearer Token
All 28 MCP tools support Knox bearer token authentication:

#### Topic Operations (7 tools)
- `list_topics` - List all Kafka topics via Knox
- `create_topic` - Create new Kafka topic via Knox
- `describe_topic` - Get topic details via Knox
- `delete_topic` - Delete Kafka topic via Knox
- `topic_exists` - Check if topic exists via Knox
- `get_topic_partitions` - Get topic partition count via Knox
- `update_topic_config` - Update topic configuration via Knox

#### Message Operations (3 tools)
- `produce_message` - Produce messages via Knox
- `consume_messages` - Consume messages via Knox
- `get_topic_offsets` - Get topic offsets via Knox

#### Cluster Operations (3 tools)
- `get_broker_info` - Get broker information via Knox
- `get_cluster_metadata` - Get cluster metadata via Knox
- `test_connection` - Test Kafka connection via Knox

#### Kafka Connect Operations (15 tools)
- `list_connectors` - List Kafka Connect connectors via Knox
- `create_connector` - Create connector via Knox
- `get_connector` - Get connector details via Knox
- `get_connector_status` - Get connector status via Knox
- `get_connector_config` - Get connector configuration via Knox
- `update_connector_config` - Update connector configuration via Knox
- `delete_connector` - Delete connector via Knox
- `pause_connector` - Pause connector via Knox
- `resume_connector` - Resume connector via Knox
- `restart_connector` - Restart connector via Knox
- `get_connector_tasks` - Get connector tasks via Knox
- `get_connector_active_topics` - Get active topics via Knox
- `list_connector_plugins` - List connector plugins via Knox
- `validate_connector_config` - Validate connector config via Knox
- `get_connect_server_info` - Get Connect server info via Knox

#### Knox Operations (2 tools)
- `test_knox_connection` - Test Knox Gateway connection
- `get_knox_metadata` - Get Knox Gateway metadata

## 🔄 Fallback System

### When Knox is Unavailable
The MCP server automatically falls back to direct Kafka connection:

1. **Direct Kafka Connection**: Connects directly to Kafka brokers
2. **Kafka Connect API**: Uses Kafka Connect REST API for operations
3. **Graceful Degradation**: Maintains full functionality without Knox

### Fallback Triggers
- Knox Gateway unreachable
- Invalid bearer token
- Knox service not configured
- Network connectivity issues

## 🛠️ Troubleshooting

### Common Issues

#### 1. Invalid Bearer Token
```
Error: KnoxError: Failed to authenticate with Knox Gateway
```
**Solution**: Verify your bearer token is valid and has proper permissions.

#### 2. Knox Gateway Unreachable
```
Error: RetryError: Connection failed
```
**Solution**: Check Knox Gateway URL and network connectivity.

#### 3. SSL Certificate Issues
```
Error: SSL certificate verification failed
```
**Solution**: Set `KNOX_VERIFY_SSL="false"` for testing or configure proper certificates.

### Debug Mode
```bash
# Enable debug logging
export MCP_LOG_LEVEL="DEBUG"
uv run python -m cdf_kafka_mcp_server
```

## 📋 Best Practices

### 1. Token Management
- Use long-lived bearer tokens for production
- Implement token rotation for security
- Store tokens securely (environment variables, secret management)

### 2. SSL Configuration
- Use proper SSL certificates in production
- Set `KNOX_VERIFY_SSL="true"` for production
- Configure CA bundle for certificate validation

### 3. Error Handling
- Implement proper error handling in your applications
- Use fallback mechanisms when Knox is unavailable
- Monitor Knox Gateway health and availability

## 🎯 Summary

The CDF Kafka MCP Server now has complete Knox Gateway integration with bearer token authentication:

- **✅ Bearer Token Auth**: FULLY IMPLEMENTED
- **✅ All MCP Tools**: SUPPORT Knox authentication
- **✅ Fallback System**: ROBUST and RELIABLE
- **✅ Error Handling**: COMPREHENSIVE
- **✅ Production Ready**: SECURE and SCALABLE

The MCP server provides seamless integration with Knox Gateway while maintaining full functionality through robust fallback mechanisms.
