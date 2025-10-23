# Testing Documentation for CDF Kafka MCP Server

## Overview

This directory contains comprehensive testing suites for the CDF Kafka MCP Server, including MCP tools testing, Docker deployment testing, and Knox Gateway integration testing.

## Test Suites

### 1. MCP Tools Testing (`test_mcp_tools.py`)
Tests all MCP tools functionality including:
- Tool registration verification
- Basic Kafka operations (list, create, delete topics)
- Message production and consumption
- Kafka Connect operations
- Knox Gateway operations

### 2. Docker Deployment Testing (`test_docker_deployment.py`)
Tests Docker Compose services and integration:
- Docker Compose service health
- Kafka connectivity via CLI
- Kafka Connect REST API
- SMM UI accessibility
- MCP server integration
- Service health checks

### 3. Knox Integration Testing (`test_knox_integration.py`)
Tests Knox Gateway authentication:
- Token retrieval
- Token validation
- Token refresh
- Gateway connectivity
- Complete authentication flow

## 🚀 Testing Instructions

### **Step-by-Step Testing Guide**

#### **Step 1: Prerequisites Setup**
```bash
# 1. Navigate to the project root
cd /path/to/CDF-Kafka-MCP-Server

# 2. Start Docker Compose services
docker-compose up -d

# 3. Wait for services to be healthy (about 2-3 minutes)
docker-compose ps

# 4. Navigate to Testing directory
cd Testing

# 5. Install Python dependencies
pip install -r requirements.txt

# 6. Set environment variables
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
```

#### **Step 2: Verify Docker Environment**
```bash
# Check that all services are running and healthy
docker-compose ps

# Expected output should show:
# - kafka: Up (healthy)
# - zookeeper: Up (healthy) 
# - smm: Up (healthy)
# - kafka-connect: Up (healthy)
# - schema-registry: Up (healthy)
# - postgresql: Up (healthy)
# - prometheus: Up (healthy)
```

#### **Step 3: Choose Your Testing Approach**

##### **Option A: Quick Testing (Recommended for Development)**
```bash
# Run essential tests quickly (5-10 minutes)
./run_quick_tests.sh

# This will:
# - Check Docker Compose services
# - Run MCP tools tests
# - Verify basic functionality
```

##### **Option B: Full Test Suite (Comprehensive Testing)**
```bash
# Run comprehensive test suite (15-30 minutes)
./run_full_tests.sh

# This will:
# - Run all test suites
# - Generate detailed reports
# - Save results to test_results.json
```

##### **Option C: Individual Test Suites (Targeted Testing)**
```bash
# Test only MCP tools functionality
python3 test_mcp_tools.py

# Test only Docker deployment
python3 test_docker_deployment.py

# Test only Knox Gateway integration
python3 test_knox_integration.py
```

##### **Option D: Comprehensive Testing (All Suites)**
```bash
# Run all test suites with detailed reporting
python3 run_tests.py

# This will:
# - Run all three test suites
# - Provide comprehensive summary
# - Save detailed results to JSON
```

### **Understanding Test Results**

#### **Test Output Interpretation**
```
🧪 Testing MCP Tools...
✅ MCP server initialized successfully
✅ All 25 expected tools are registered
✅ Successfully listed 3 topics: ['cursortest', 'mcp-test-topic']
✅ Successfully created topic 'mcp-tools-test-topic'
✅ Successfully produced message to 'mcp-tools-test-topic'
✅ Successfully consumed 1 messages from 'mcp-tools-test-topic'

📊 MCP TOOLS TEST RESULTS SUMMARY
====================================
Total Tests: 7
Passed: 7
Failed: 0
Success Rate: 100.0%
```

#### **Success Criteria**
- **✅ PASS**: Test completed successfully
- **❌ FAIL**: Test failed, check logs for details
- **⏭️ SKIP**: Test was skipped (usually due to missing dependencies)

#### **Expected Success Rates**
- **MCP Tools**: 80-100% (some tools may fail due to environment issues)
- **Docker Deployment**: 90-100% (should be very reliable)
- **Knox Integration**: 0-100% (depends on Knox Gateway configuration)

### **Running Tests**

### **Advanced Testing Scenarios**

#### **Testing with Custom Configuration**
```bash
# 1. Copy and modify test configuration
cp test_config.json test_config_custom.json

# 2. Edit test_config_custom.json with your settings
# 3. Run tests with custom config
python3 run_tests.py --config test_config_custom.json
```

#### **Testing Specific MCP Tools**
```bash
# Test only Kafka Connect tools
python3 -c "
import asyncio
from test_mcp_tools import MCPToolsTester
async def test_connect_only():
    tester = MCPToolsTester()
    await tester.setup()
    await tester.test_kafka_connect_tools()
    tester.print_summary()
asyncio.run(test_connect_only())
"
```

#### **Continuous Integration Testing**
```bash
# For CI/CD pipelines
#!/bin/bash
set -e
docker-compose up -d
sleep 60  # Wait for services
cd Testing
pip install -r requirements.txt
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
python3 run_tests.py
# Exit with error code if tests fail
```

### **Performance Testing**

#### **Load Testing MCP Tools**
```bash
# Test with multiple concurrent operations
python3 -c "
import asyncio
from test_mcp_tools import MCPToolsTester

async def load_test():
    tasks = []
    for i in range(5):
        tester = MCPToolsTester()
        await tester.setup()
        tasks.append(tester.test_produce_message_tool())
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(f'Load test completed: {len(results)} concurrent operations')

asyncio.run(load_test())
"
```

#### **Memory and Resource Monitoring**
```bash
# Monitor resource usage during tests
docker stats --no-stream &
python3 run_tests.py
kill %1
```

## Prerequisites

### **System Requirements**
- **Docker**: Version 20.10+ with Docker Compose
- **Python**: Version 3.10+ (required for MCP library)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Disk**: Minimum 2GB free space

### **Environment Setup**
1. **Docker Environment**: Ensure Docker Compose services are running
   ```bash
   docker-compose up -d
   ```

2. **Python Dependencies**: Install testing dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**: Set required environment variables
   ```bash
   export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
   ```

### **Optional Dependencies**
```bash
# For enhanced testing capabilities
pip install pytest-xdist  # Parallel test execution
pip install pytest-html  # HTML test reports
pip install pytest-cov  # Coverage reporting
```

## Configuration

The `test_config.json` file contains configuration for:
- Docker services to test
- MCP tools to verify
- Health check endpoints
- Test timeouts and retry settings

## Test Results

Test results are saved to `test_results.json` and include:
- Timestamp and duration
- Detailed results by test suite
- Pass/fail/skip counts
- Success rates

## 🔧 Troubleshooting Guide

### **Common Issues and Solutions**

#### **1. Docker Services Not Running**
```bash
# Problem: Services fail to start
# Solution: Check Docker Compose status and logs

# Check service status
docker-compose ps

# Check logs for specific service
docker-compose logs kafka
docker-compose logs zookeeper

# Restart services
docker-compose down
docker-compose up -d

# Wait for services to be healthy
sleep 60
docker-compose ps
```

#### **2. MCP Server Connection Issues**
```bash
# Problem: MCP server can't connect to Kafka
# Solution: Verify environment and connectivity

# Check environment variables
echo $KAFKA_BOOTSTRAP_SERVERS

# Test Kafka connectivity directly
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Check MCP server logs
python3 -c "
from src.cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
import os
os.environ['KAFKA_BOOTSTRAP_SERVERS'] = 'localhost:9092'
server = CDFKafkaMCPServer()
print('MCP server initialized successfully')
"
```

#### **3. Knox Gateway Tests Failing**
```bash
# Problem: Knox Gateway tests fail
# Solution: Check Knox configuration

# Check if Knox Gateway is configured
grep -r "knox" ../config/

# Test Knox Gateway connectivity (if configured)
curl -k https://your-knox-gateway:8443/gateway/kafka/api/v1/topics

# Skip Knox tests if not needed
python3 test_mcp_tools.py  # This will skip Knox tests
```

#### **4. Test Dependencies Missing**
```bash
# Problem: ImportError or ModuleNotFoundError
# Solution: Install missing dependencies

# Install all testing dependencies
pip install -r requirements.txt

# Install additional dependencies if needed
pip install requests pytest pytest-asyncio

# Check Python version (must be 3.10+)
python3 --version
```

#### **5. Permission Issues**
```bash
# Problem: Permission denied errors
# Solution: Fix file permissions

# Make scripts executable
chmod +x run_quick_tests.sh
chmod +x run_full_tests.sh

# Fix Docker permissions (if needed)
sudo chown -R $USER:$USER .
```

### **Debug Mode and Verbose Output**

#### **Enable Debug Logging**
```bash
# Run tests with verbose output
python3 -u test_mcp_tools.py 2>&1 | tee test_output.log

# Run with debug environment variable
DEBUG=1 python3 run_tests.py

# Check test output log
tail -f test_output.log
```

#### **Interactive Debugging**
```bash
# Start Python interactive session for debugging
python3 -c "
import sys
sys.path.insert(0, '../src')
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
import os
os.environ['KAFKA_BOOTSTRAP_SERVERS'] = 'localhost:9092'

# Debug MCP server
server = CDFKafkaMCPServer()
print('Available tools:', [tool.name for tool in server.tools])
"
```

### **Performance Issues**

#### **Slow Test Execution**
```bash
# Problem: Tests run slowly
# Solution: Optimize Docker resources

# Increase Docker memory allocation
# In Docker Desktop: Settings > Resources > Memory > 8GB

# Use faster test execution
python3 test_mcp_tools.py  # Skip slower Docker tests

# Run tests in parallel (if supported)
python3 -m pytest test_*.py -n 4
```

#### **Memory Issues**
```bash
# Problem: Out of memory errors
# Solution: Monitor and optimize resource usage

# Monitor Docker resource usage
docker stats

# Clean up Docker resources
docker system prune -f
docker volume prune -f

# Restart Docker services
docker-compose restart
```

### **Test-Specific Troubleshooting**

#### **MCP Tools Test Failures**
```bash
# Common MCP tool test issues:

# 1. Tool registration fails
# Check: MCP server initialization
python3 -c "
from src.cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
server = CDFKafkaMCPServer()
print(f'Tools registered: {len(server.tools)}')
"

# 2. Topic operations fail
# Check: Kafka connectivity
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# 3. Message production/consumption fails
# Check: Topic exists and Kafka is healthy
docker exec kafka /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic test-topic
```

#### **Docker Deployment Test Failures**
```bash
# Common Docker test issues:

# 1. Service health checks fail
# Check: Service logs
docker-compose logs kafka
docker-compose logs zookeeper

# 2. Port conflicts
# Check: Port usage
netstat -tulpn | grep :9092
netstat -tulpn | grep :28083

# 3. Volume mount issues
# Check: Volume permissions
docker volume ls
docker volume inspect cdf-kafka-mcp-server_kafka-data
```

#### **Knox Integration Test Failures**
```bash
# Common Knox test issues:

# 1. Knox Gateway not configured
# Solution: Skip Knox tests or configure Knox
export KNOX_ENABLED=false

# 2. Authentication failures
# Check: Knox credentials and network
curl -k -H "Authorization: Bearer $KNOX_TOKEN" https://knox-gateway:8443/gateway/kafka/api/v1/topics

# 3. SSL/TLS issues
# Check: Certificate validity
openssl s_client -connect knox-gateway:8443
```

### **Getting Help**

#### **Collect Debug Information**
```bash
# Create debug report
cat > debug_report.txt << EOF
=== System Information ===
OS: $(uname -a)
Docker: $(docker --version)
Docker Compose: $(docker-compose --version)
Python: $(python3 --version)

=== Docker Services ===
$(docker-compose ps)

=== Environment Variables ===
KAFKA_BOOTSTRAP_SERVERS: $KAFKA_BOOTSTRAP_SERVERS
KNOX_ENABLED: $KNOX_ENABLED

=== Test Results ===
$(python3 run_tests.py 2>&1 | tail -20)
EOF

echo "Debug report saved to debug_report.txt"
```

#### **Contact Information**
- **Issues**: Create GitHub issue with debug report
- **Documentation**: Check main README.md
- **Configuration**: Review config/ directory
- **Logs**: Check Docker Compose logs for service-specific issues

## Troubleshooting

## 📚 Best Practices and Tips

### **Testing Workflow Recommendations**

#### **Development Workflow**
1. **Start with Quick Tests**: Use `./run_quick_tests.sh` during development
2. **Run Full Tests**: Use `./run_full_tests.sh` before committing changes
3. **Test Specific Features**: Use individual test files for targeted testing
4. **Monitor Resources**: Keep an eye on Docker resource usage

#### **CI/CD Integration**
```bash
# Example GitHub Actions workflow
name: Test CDF Kafka MCP Server
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r Testing/requirements.txt
      - name: Start Docker services
        run: |
          docker-compose up -d
          sleep 60
      - name: Run tests
        run: |
          cd Testing
          export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"
          python3 run_tests.py
```

### **Performance Optimization**

#### **Faster Test Execution**
```bash
# Use parallel execution for independent tests
python3 -m pytest test_*.py -n 4

# Skip slow tests during development
python3 test_mcp_tools.py  # Skip Docker tests

# Use test-specific configurations
python3 run_tests.py --config test_config_fast.json
```

#### **Resource Management**
```bash
# Monitor resource usage
docker stats --no-stream

# Clean up between test runs
docker-compose down
docker system prune -f
docker-compose up -d
```

### **Test Data Management**

#### **Test Topic Management**
```bash
# Clean up test topics after tests
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --delete --topic mcp-tools-test-topic

# List all topics
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
```

#### **Test Configuration Management**
```bash
# Use environment-specific configs
cp test_config.json test_config_local.json
cp test_config.json test_config_ci.json

# Modify configs for different environments
# Local: Use localhost
# CI: Use container names
# Production: Use actual service endpoints
```

### **Debugging Tips**

#### **Effective Debugging**
1. **Start Simple**: Test individual components first
2. **Use Logs**: Enable verbose logging for detailed output
3. **Check Dependencies**: Ensure all services are healthy
4. **Isolate Issues**: Run tests individually to identify problems
5. **Use Interactive Mode**: Use Python interactive sessions for debugging

#### **Common Debug Commands**
```bash
# Check service health
docker-compose ps

# View service logs
docker-compose logs kafka
docker-compose logs zookeeper

# Test connectivity
docker exec kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list

# Check MCP server
python3 -c "
import sys; sys.path.insert(0, '../src')
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
server = CDFKafkaMCPServer()
print('MCP server OK')
"
```

### **Maintenance and Updates**

#### **Regular Maintenance**
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Update Docker images
docker-compose pull
docker-compose up -d

# Clean up old test data
docker system prune -f
docker volume prune -f
```

#### **Test Suite Updates**
When adding new tests:
1. Follow existing test structure
2. Add appropriate error handling
3. Include cleanup procedures
4. Update this documentation
5. Add new tools to `test_config.json`

## Test Coverage