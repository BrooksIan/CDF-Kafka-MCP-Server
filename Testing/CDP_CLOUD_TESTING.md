# CDP Cloud MCP Tools Testing Guide

This guide explains how to test all MCP tools against your CDP Cloud (Cloudera Data Platform) configuration with Knox Gateway authentication.

## Overview

The CDP Cloud testing suite provides comprehensive testing for all 28 MCP tools against your CDP Cloud Kafka cluster. It includes:

- **Connection Tools**: Test basic connectivity and Knox Gateway authentication
- **Topic Management**: Create, describe, update, and delete topics
- **Message Operations**: Produce and consume messages
- **Kafka Connect**: Manage connectors and validate configurations
- **Connector Lifecycle**: Full connector management workflow

## Prerequisites

### 1. CDP Cloud Configuration
Ensure your CDP Cloud configuration is set up:

```bash
# Set up CDP Cloud configuration
./setup_cloud.sh cdp-cloud

# Verify configuration
cat config/kafka_config.yaml | grep -E "(gateway|bootstrap_servers|security_protocol)"
```

### 2. Environment Variables
Set up your CDP Cloud environment:

```bash
# Required CDP Cloud settings
export KAFKA_BOOTSTRAP_SERVERS="irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443"
export KAFKA_SECURITY_PROTOCOL="SASL_SSL"
export KAFKA_SASL_MECHANISM="PLAIN"
export KNOX_GATEWAY="https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443/irb-kakfa-only/cdp-proxy-token"
export KNOX_SERVICE="kafka"
export KNOX_VERIFY_SSL="true"

# Optional: CDP Cloud credentials (if needed)
export KAFKA_SASL_USERNAME="your-cdp-username"
export KAFKA_SASL_PASSWORD="your-cdp-password"
```

### 3. Dependencies
Ensure all dependencies are installed:

```bash
# Install dependencies
uv sync

# Or with pip
pip install -r requirements.txt
```

## Running Tests

### Quick Test
Run the complete test suite:

```bash
cd Testing/
./run_cdp_cloud_tests.sh
```

### Manual Test
Run the Python test script directly:

```bash
cd Testing/
uv run python test_cdp_cloud_mcp_tools.py
```

### Debug Mode
Run with debug logging:

```bash
cd Testing/
export MCP_LOG_LEVEL="DEBUG"
./run_cdp_cloud_tests.sh
```

## Test Categories

### 1. Connection Tools (5 tools)
Tests basic connectivity and authentication:

- `test_connection` - Test Kafka cluster connectivity
- `get_broker_info` - Get broker information
- `get_cluster_metadata` - Get cluster metadata
- `test_knox_connection` - Test Knox Gateway connectivity
- `get_knox_metadata` - Get Knox Gateway metadata

### 2. Topic Management (8 tools)
Tests topic lifecycle management:

- `list_topics` - List all topics
- `create_topic` - Create a new topic
- `describe_topic` - Get topic details
- `delete_topic` - Delete a topic
- `topic_exists` - Check if topic exists
- `get_topic_partitions` - Get partition count
- `update_topic_config` - Update topic configuration
- `get_topic_offsets` - Get topic offset information

### 3. Message Operations (2 tools)
Tests message production and consumption:

- `produce_message` - Send messages to topics
- `consume_messages` - Read messages from topics

### 4. Kafka Connect (4 tools)
Tests Kafka Connect management:

- `list_connectors` - List all connectors
- `get_connect_server_info` - Get Connect server information
- `list_connector_plugins` - List available connector plugins
- `validate_connector_config` - Validate connector configuration

### 5. Connector Lifecycle (9 tools)
Tests connector management workflow:

- `create_connector` - Create a new connector
- `get_connector` - Get connector details
- `get_connector_status` - Get connector status
- `get_connector_config` - Get connector configuration
- `get_connector_tasks` - Get connector tasks
- `get_connector_active_topics` - Get active topics
- `pause_connector` - Pause connector
- `resume_connector` - Resume connector
- `restart_connector` - Restart connector
- `update_connector_config` - Update connector configuration
- `delete_connector` - Delete connector

## Test Results

### Output Format
The test suite generates:

1. **Console Output**: Real-time test progress and results
2. **JSON Report**: Detailed results saved to `cdp_cloud_mcp_test_results_<timestamp>.json`

### Success Metrics
- **Total Tests**: 28 MCP tools
- **Success Rate**: Percentage of successful tests
- **Duration**: Total test execution time
- **Category Breakdown**: Success rate per tool category

### Example Output
```
📊 CDP CLOUD MCP TOOLS TEST SUMMARY
====================================
⏱️  Total Duration: 45.32 seconds
🧪 Total Tests: 28
✅ Successful: 26
❌ Failed: 2
📈 Success Rate: 92.9%

📁 Connection Tools: 5/5 (100.0%)
📁 Topic Management: 8/8 (100.0%)
📁 Message Operations: 2/2 (100.0%)
📁 Kafka Connect: 3/4 (75.0%)
📁 Connector Lifecycle: 8/9 (88.9%)
```

## Troubleshooting

### Common Issues

#### 1. Connection Failures
**Error**: `Connection failed to CDP Cloud`
**Solution**: 
- Verify Knox Gateway URL is correct
- Check bearer token is valid and not expired
- Ensure CDP Cloud cluster is accessible

#### 2. Authentication Errors
**Error**: `Knox authentication failed`
**Solution**:
- Verify bearer token is correctly configured
- Check Knox Gateway is running and accessible
- Ensure SSL certificates are valid

#### 3. Topic Creation Failures
**Error**: `Failed to create topic`
**Solution**:
- Check CDP Cloud permissions
- Verify topic name doesn't conflict with existing topics
- Ensure sufficient cluster resources

#### 4. Connector Failures
**Error**: `Connector creation failed`
**Solution**:
- Verify Kafka Connect is running in CDP Cloud
- Check connector plugin availability
- Validate connector configuration

### Debug Mode
Enable debug logging for detailed troubleshooting:

```bash
export MCP_LOG_LEVEL="DEBUG"
./run_cdp_cloud_tests.sh
```

### Manual Verification
Test individual tools manually:

```bash
# Start MCP server
uv run python -m cdf_kafka_mcp_server

# Test specific tool (in another terminal)
curl -X POST http://localhost:8081/mcp/tools \
  -H "Content-Type: application/json" \
  -d '{"name": "test_connection", "arguments": {}}'
```

## Configuration Files

### Main Configuration
- `config/kafka_config.yaml` - CDP Cloud configuration (generated by setup_cloud.sh)

### Test Configuration
- `Testing/test_cdp_cloud_mcp_tools.py` - Main test script
- `Testing/run_cdp_cloud_tests.sh` - Test runner script
- `Testing/CDP_CLOUD_TESTING.md` - This documentation

### Environment Templates
- `config/env_cdp_cloud_template.txt` - Environment variables template

## Best Practices

### 1. Test Environment
- Use a dedicated test environment when possible
- Avoid testing against production CDP Cloud clusters
- Clean up test topics and connectors after testing

### 2. Security
- Keep bearer tokens secure and rotate regularly
- Use environment variables for sensitive credentials
- Enable SSL verification in production

### 3. Monitoring
- Monitor test results for patterns
- Set up alerts for test failures
- Track performance metrics over time

### 4. Maintenance
- Update test scripts when MCP tools change
- Review and update CDP Cloud configuration regularly
- Keep dependencies up to date

## Support

For issues with CDP Cloud testing:

1. Check the troubleshooting section above
2. Review test logs and JSON reports
3. Verify CDP Cloud cluster status
4. Contact CDP Cloud support if needed

## Related Documentation

- [README.md](../README.md) - Main project documentation
- [CLOUD_TESTING_SETUP.md](../CLOUD_TESTING_SETUP.md) - General cloud testing guide
- [KNOX_BEARER_TOKEN_SETUP.md](../KNOX_BEARER_TOKEN_SETUP.md) - Knox authentication setup
