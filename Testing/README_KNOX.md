# Knox Gateway Integration Testing

## Quick Start

```bash
cd Testing
./run_knox_tests.sh
```

## Overview

This directory contains comprehensive testing tools for MCP server integration with Apache Knox Gateway. The test suite validates Knox Gateway configuration, tests all integration features, and provides detailed troubleshooting guidance.

## Files

### Core Test Files
- **`test_knox_integration.py`** - Main integration test suite
- **`validate_knox_setup.py`** - Pre-test validation script
- **`run_knox_tests.sh`** - Automated test runner

### Documentation
- **`KNOX_INTEGRATION_TESTING.md`** - Detailed testing guide
- **`README_KNOX.md`** - This file

## Prerequisites

### 1. Knox Gateway Configuration
- Knox Gateway must be running and accessible
- Admin UI available at: https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/manager/admin-ui/
- Authentication: `ibrooks` / `Admin12345#`
- Kafka services properly configured in topology

### 2. Required Files
- `../config/kafka_config_knox_enhanced.yaml` - Knox configuration
- `../src/` - MCP server source code
- Python 3.12+ with UV package manager

## Test Categories

### 1. Setup Validation
- Configuration file validation
- Authentication verification
- Knox Gateway accessibility
- Topology configuration
- Service mapping validation

### 2. Knox Gateway Features
- Gateway information retrieval
- Topology management
- Service health checks
- URL validation
- Authentication flow

### 3. Kafka Operations
- Topic creation via Knox
- Message production via Knox
- Error handling and fallbacks
- Service integration

### 4. Health Monitoring
- Overall system health
- Service-specific health checks
- Metrics collection
- Performance monitoring

### 5. CDP Integration
- CDP Cloud connectivity
- API accessibility
- Token validation
- Service integration

## Running Tests

### Automated Testing (Recommended)

```bash
# Run complete test suite
./run_knox_tests.sh

# Check exit code
echo $?  # 0 = success, 1 = failure
```

### Manual Testing

```bash
# Validate setup first
uv run python validate_knox_setup.py

# Run integration tests
uv run python test_knox_integration.py
```

### Custom Configuration

```bash
# Use custom config file
CONFIG_PATH="../config/your_config.yaml" uv run python test_knox_integration.py
```

## Test Results

### Success Indicators ✅
- All validation checks pass
- Knox Gateway accessible and configured
- Kafka services working through Knox
- MCP server integration functional

### Warning Indicators ⚠️
- Some tests fail but others pass
- Authentication issues
- Service configuration problems
- Network connectivity issues

### Failure Indicators ❌
- All tests fail
- Knox Gateway not accessible
- Configuration file missing
- Authentication credentials invalid

## Troubleshooting

### Common Issues

#### 1. Knox Gateway Not Accessible
**Symptoms**: Connection errors, timeouts
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

#### 4. Configuration File Issues
**Symptoms**: Missing configuration errors
**Solutions**:
- Ensure config file exists
- Verify YAML syntax
- Check required fields
- Update configuration

### Validation Steps

1. **Check Knox Gateway Status**
   ```bash
   curl -u ibrooks:Admin12345# \
     https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/admin/api/v1/topologies
   ```

2. **Test Kafka Services**
   ```bash
   curl -u ibrooks:Admin12345# \
     https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/cdp-proxy/kafka
   ```

3. **Validate Configuration**
   ```bash
   uv run python validate_knox_setup.py
   ```

## Configuration Requirements

### Knox Gateway Topology
The `cdp-proxy` topology must include:

```xml
<service>
    <role>KAFKA</role>
    <name>kafka</name>
    <url>http://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443</url>
</service>

<service>
    <role>KAFKA_CONNECT</role>
    <name>kafka-connect</name>
    <url>http://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443</url>
</service>
```

### MCP Server Configuration
The `kafka_config_knox_enhanced.yaml` must include:

```yaml
knox:
  gateway: "https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only"
  username: "ibrooks"
  password: "Admin12345#"
  verify_ssl: false
```

## Performance Expectations

### Test Execution Time
- **Setup Validation**: 10-30 seconds
- **Integration Tests**: 30-60 seconds
- **With Issues**: 2-5 minutes (timeout)

### Resource Usage
- **Memory**: ~100MB peak
- **CPU**: Low during tests
- **Network**: Moderate (API calls)

## Continuous Integration

### CI/CD Integration
```bash
# In CI/CD pipeline
cd Testing
if ./run_knox_tests.sh; then
    echo "✅ Knox integration tests passed"
    exit 0
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

## Support

### Log Files
- MCP server logs: `../logs/mcp_server.log`
- Test logs: Console output
- Knox Gateway logs: Check Knox installation

### Documentation
- [Knox Gateway Configuration Guide](../KNOX_GATEWAY_CONFIGURATION.md)
- [CDP Cloud Testing Guide](CDP_CLOUD_TESTING.md)
- [Main README](../README.md)

### Version Compatibility
- Test with different Knox Gateway versions
- Verify MCP server compatibility
- Update tests for new features

## Next Steps

After successful testing:

1. **Use MCP Server**: Deploy and use the MCP server for Kafka operations
2. **Monitor Health**: Set up health monitoring and alerting
3. **Scale Configuration**: Add more services and topologies as needed
4. **Performance Tuning**: Optimize based on test results

## References

- [Apache Knox Gateway Documentation](https://knox.apache.org/)
- [MCP Server Documentation](../README.md)
- [Knox Gateway Configuration Guide](../KNOX_GATEWAY_CONFIGURATION.md)
- [CDP Cloud Integration Guide](CDP_CLOUD_TESTING.md)
