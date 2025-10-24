# Knox Gateway Integration Testing

## Overview

This document describes how to test the MCP server integration with Apache Knox Gateway for Kafka operations. The test suite validates all Knox Gateway features and ensures proper configuration.

## Prerequisites

### 1. Knox Gateway Configuration

Before running tests, ensure Knox Gateway is properly configured:

- **Admin UI Access**: https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/manager/admin-ui/
- **Authentication**: `ibrooks` / `Admin12345#`
- **Kafka Services**: Properly mapped in topology
- **Kafka Connect API**: Accessible through Knox Gateway

### 2. Required Configuration Files

- `config/kafka_config_knox_enhanced.yaml` - Knox Gateway configuration
- `config/kafka_config_cdp_cloud.yaml` - CDP Cloud configuration (optional)

### 3. Dependencies

- Python 3.12+
- UV package manager
- MCP server dependencies
- Network access to Knox Gateway

## Test Suite Components

### 1. Core Test File: `test_knox_integration.py`

Comprehensive test suite covering:

- **Knox Gateway Information**: Gateway version, status, configuration
- **Topology Management**: List, get details, service mapping
- **Service Health**: Health checks for Kafka and Connect services
- **Service URLs**: Kafka and Connect API endpoint validation
- **Kafka Operations**: Topic creation and message production via Knox
- **Health Monitoring**: Overall system health and metrics
- **CDP Integration**: CDP Cloud connectivity and APIs

### 2. Test Runner: `run_knox_tests.sh`

Automated test execution with:

- Environment validation
- Knox Gateway accessibility checks
- Timeout handling (5 minutes)
- Comprehensive error reporting
- Troubleshooting guidance

## Running Tests

### Quick Start

```bash
cd Testing
./run_knox_tests.sh
```

### Manual Execution

```bash
cd Testing
uv run python test_knox_integration.py
```

### With Custom Configuration

```bash
cd Testing
CONFIG_PATH="../config/your_config.yaml" uv run python test_knox_integration.py
```

## Test Results Interpretation

### ✅ Success Indicators

- All tests pass without errors
- Knox Gateway information retrieved successfully
- Topologies listed and accessible
- Service health checks return healthy status
- Kafka operations complete successfully

### ⚠️ Warning Indicators

- Some tests fail but others pass
- Authentication issues
- Service configuration problems
- Network connectivity issues

### ❌ Failure Indicators

- All tests fail
- Knox Gateway not accessible
- Configuration file missing
- Authentication credentials invalid

## Troubleshooting

### Common Issues

#### 1. Knox Gateway Not Accessible

**Symptoms**: 404 or connection errors
**Solutions**:
- Check Knox Gateway service status
- Verify network connectivity
- Confirm URL and port accessibility
- Check firewall settings

#### 2. Authentication Failures

**Symptoms**: 401 Unauthorized errors
**Solutions**:
- Verify username/password credentials
- Check authentication provider configuration
- Test with Knox Admin UI
- Review authentication logs

#### 3. Service Mapping Issues

**Symptoms**: 404 errors for Kafka services
**Solutions**:
- Configure Kafka services in topology
- Verify service URLs and ports
- Check service role mappings
- Update topology configuration

#### 4. Kafka Connect API Issues

**Symptoms**: 404 errors for Connect endpoints
**Solutions**:
- Add Kafka Connect service to topology
- Verify Connect service URL
- Check Connect service configuration
- Test Connect service directly

### Configuration Validation

#### Check Topology Configuration

```bash
# List topologies
curl -u ibrooks:Admin12345# \
  https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/admin/api/v1/topologies

# Get specific topology details
curl -u ibrooks:Admin12345# \
  https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/admin/api/v1/topologies/cdp-proxy
```

#### Test Service Endpoints

```bash
# Test Kafka service
curl -u ibrooks:Admin12345# \
  https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/cdp-proxy/kafka

# Test Kafka Connect API
curl -u ibrooks:Admin12345# \
  https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/cdp-proxy/kafka-connect/connectors
```

## Expected Test Flow

### 1. Initialization Phase
- MCP server initialization
- Configuration validation
- Client setup

### 2. Knox Gateway Tests
- Gateway information retrieval
- Topology listing and details
- Service health checks
- URL validation

### 3. Kafka Operations Tests
- Topic creation via Knox
- Message production via Knox
- Error handling and fallbacks

### 4. Integration Tests
- Health monitoring
- CDP Cloud integration
- End-to-end workflows

### 5. Results and Reporting
- Test result summary
- Success/failure counts
- Troubleshooting recommendations

## Performance Expectations

### Test Execution Time
- **Normal**: 30-60 seconds
- **With Issues**: 2-5 minutes (timeout)
- **Network Problems**: Immediate failure

### Resource Usage
- **Memory**: ~100MB peak
- **CPU**: Low during tests
- **Network**: Moderate (API calls)

## Continuous Integration

### Automated Testing

```bash
# Run tests in CI/CD pipeline
cd Testing
./run_knox_tests.sh

# Check exit code
if [ $? -eq 0 ]; then
    echo "✅ Knox integration tests passed"
else
    echo "❌ Knox integration tests failed"
    exit 1
fi
```

### Monitoring Integration

- Test results can be integrated with monitoring systems
- Health checks can be automated
- Alerts can be configured for test failures

## Best Practices

### 1. Regular Testing
- Run tests after Knox Gateway configuration changes
- Test before deploying MCP server updates
- Monitor test results over time

### 2. Configuration Management
- Keep configuration files in version control
- Document configuration changes
- Test with different environments

### 3. Error Handling
- Review error messages carefully
- Check logs for detailed information
- Use troubleshooting steps systematically

### 4. Performance Monitoring
- Track test execution times
- Monitor resource usage
- Identify performance regressions

## Support and Maintenance

### Log Files
- MCP server logs: `logs/mcp_server.log`
- Test logs: Console output
- Knox Gateway logs: Check Knox installation

### Documentation Updates
- Update this document when adding new tests
- Document new troubleshooting steps
- Keep configuration examples current

### Version Compatibility
- Test with different Knox Gateway versions
- Verify MCP server compatibility
- Update tests for new features

## References

- [Apache Knox Gateway Documentation](https://knox.apache.org/)
- [MCP Server Documentation](../README.md)
- [Knox Gateway Configuration Guide](../KNOX_GATEWAY_CONFIGURATION.md)
- [CDP Cloud Integration Guide](../CDP_CLOUD_TESTING.md)
