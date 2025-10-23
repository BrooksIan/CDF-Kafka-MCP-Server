# Cloud Testing Setup Guide

## Overview
This guide helps you set up and test the CDF Kafka MCP Server against cloud-based Kafka environments.

## 🚀 Quick Setup

### 1. Choose Your Cloud Provider

#### **AWS MSK (Managed Streaming for Kafka)**
```bash
# Use the AWS MSK configuration
./setup_cloud.sh aws-msk
```

#### **Confluent Cloud**
```bash
# Use the Confluent Cloud configuration
./setup_cloud.sh confluent-cloud
```

#### **Azure Event Hubs for Kafka**
```bash
# Use the Azure Event Hubs configuration
./setup_cloud.sh azure-eventhub
```

#### **Generic Cloud (SASL_SSL)**
```bash
# Use the generic cloud configuration
./setup_cloud.sh generic
```

### 2. Set Environment Variables

#### **AWS MSK**
```bash
export KAFKA_BOOTSTRAP_SERVERS="your-msk-cluster.kafka.us-east-1.amazonaws.com:9092"
export KAFKA_SECURITY_PROTOCOL="SASL_SSL"
export KAFKA_SASL_MECHANISM="SCRAM-SHA-512"
export KAFKA_SASL_USERNAME="your-iam-username"
export KAFKA_SASL_PASSWORD="your-iam-password"
export AWS_ACCESS_KEY_ID="your-aws-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-aws-secret-access-key"
export AWS_REGION="us-east-1"
```

#### **Confluent Cloud**
```bash
export KAFKA_BOOTSTRAP_SERVERS="pkc-xxxxx.us-west-2.aws.confluent.cloud:9092"
export KAFKA_SECURITY_PROTOCOL="SASL_SSL"
export KAFKA_SASL_MECHANISM="PLAIN"
export KAFKA_SASL_USERNAME="your-api-key"
export KAFKA_SASL_PASSWORD="your-api-secret"
```

#### **Azure Event Hubs**
```bash
export KAFKA_BOOTSTRAP_SERVERS="your-eventhub-namespace.servicebus.windows.net:9093"
export KAFKA_SECURITY_PROTOCOL="SASL_SSL"
export KAFKA_SASL_MECHANISM="PLAIN"
export KAFKA_SASL_USERNAME="$ConnectionString"
export KAFKA_SASL_PASSWORD="your-eventhub-connection-string"
```

#### **Generic Cloud (SASL_SSL)**
```bash
export KAFKA_BOOTSTRAP_SERVERS="your-kafka-cluster:9092"
export KAFKA_SECURITY_PROTOCOL="SASL_SSL"
export KAFKA_SASL_MECHANISM="PLAIN"
export KAFKA_SASL_USERNAME="your-username"
export KAFKA_SASL_PASSWORD="your-password"
```

### 3. Test Cloud Connection

```bash
# Test basic connection
uv run python -m cdf_kafka_mcp_server --test-connection

# Test with debug logging
export MCP_LOG_LEVEL="DEBUG"
uv run python -m cdf_kafka_mcp_server
```

## 🔧 Cloud-Specific Configurations

### AWS MSK Configuration

```yaml
# config/kafka_config_aws_msk.yaml
kafka:
  bootstrap_servers: "your-msk-cluster.kafka.us-east-1.amazonaws.com:9092"
  security_protocol: "SASL_SSL"
  sasl_mechanism: "SCRAM-SHA-512"
  sasl_username: "your-iam-username"
  sasl_password: "your-iam-password"
  tls_enabled: true
  timeout: 30

# Knox configuration for AWS MSK
knox:
  gateway: "https://your-knox-gateway:8444"
  token: "your-bearer-token-here"
  service: "kafka"
  verify_ssl: true
```

### Confluent Cloud Configuration

```yaml
# config/kafka_config_confluent_cloud.yaml
kafka:
  bootstrap_servers: "pkc-xxxxx.us-west-2.aws.confluent.cloud:9092"
  security_protocol: "SASL_SSL"
  sasl_mechanism: "PLAIN"
  sasl_username: "your-api-key"
  sasl_password: "your-api-secret"
  tls_enabled: true
  timeout: 30

knox:
  gateway: "https://your-knox-gateway:8444"
  token: "your-bearer-token-here"
  service: "kafka"
  verify_ssl: true
```

### Azure Event Hubs Configuration

```yaml
# config/kafka_config_azure_eventhub.yaml
kafka:
  bootstrap_servers: "your-eventhub-namespace.servicebus.windows.net:9093"
  security_protocol: "SASL_SSL"
  sasl_mechanism: "PLAIN"
  sasl_username: "$ConnectionString"
  sasl_password: "your-eventhub-connection-string"
  tls_enabled: true
  timeout: 30

knox:
  gateway: "https://your-knox-gateway:8444"
  token: "your-bearer-token-here"
  service: "kafka"
  verify_ssl: true
```

## 🧪 Cloud Testing Workflow

### 1. Pre-Test Checklist

- [ ] Cloud Kafka cluster is running and accessible
- [ ] Authentication credentials are valid
- [ ] Network connectivity is established
- [ ] Knox Gateway is configured (if using Knox)
- [ ] Environment variables are set correctly

### 2. Basic Connectivity Test

```bash
# Test 1: Basic connection
uv run python3 -c "
import sys
sys.path.insert(0, 'src')
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest, CallToolRequestParams
import asyncio

async def test_cloud_connection():
    try:
        mcp_server = CDFKafkaMCPServer()
        print('✅ MCP server initialized successfully')
        
        # Test connection
        request = CallToolRequest(
            params=CallToolRequestParams(
                name='test_connection',
                arguments={}
            )
        )
        result = await mcp_server.call_tool(request)
        print(f'✅ Connection test: {result.content[0].text}')
        
    except Exception as e:
        print(f'❌ Connection failed: {e}')

asyncio.run(test_cloud_connection())
"
```

### 3. Topic Operations Test

```bash
# Test 2: Topic operations
uv run python3 -c "
import sys
sys.path.insert(0, 'src')
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest, CallToolRequestParams
import asyncio

async def test_topic_operations():
    try:
        mcp_server = CDFKafkaMCPServer()
        
        # List topics
        request = CallToolRequest(
            params=CallToolRequestParams(
                name='list_topics',
                arguments={}
            )
        )
        result = await mcp_server.call_tool(request)
        print(f'✅ Topics listed: {result.content[0].text}')
        
        # Create test topic
        request = CallToolRequest(
            params=CallToolRequestParams(
                name='create_topic',
                arguments={
                    'name': 'cloud-test-topic',
                    'partitions': 1,
                    'replication_factor': 1
                }
            )
        )
        result = await mcp_server.call_tool(request)
        print(f'✅ Topic created: {result.content[0].text}')
        
    except Exception as e:
        print(f'❌ Topic operations failed: {e}')

asyncio.run(test_topic_operations())
"
```

### 4. Message Operations Test

```bash
# Test 3: Message operations
uv run python3 -c "
import sys
sys.path.insert(0, 'src')
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest, CallToolRequestParams
import asyncio

async def test_message_operations():
    try:
        mcp_server = CDFKafkaMCPServer()
        
        # Produce message
        request = CallToolRequest(
            params=CallToolRequestParams(
                name='produce_message',
                arguments={
                    'topic': 'cloud-test-topic',
                    'key': 'test-key',
                    'value': 'Hello from cloud!',
                    'headers': {
                        'source': 'cloud-test',
                        'timestamp': '2024-01-01T00:00:00Z'
                    }
                }
            )
        )
        result = await mcp_server.call_tool(request)
        print(f'✅ Message produced: {result.content[0].text}')
        
        # Consume messages
        request = CallToolRequest(
            params=CallToolRequestParams(
                name='consume_messages',
                arguments={
                    'topic': 'cloud-test-topic',
                    'partition': 0,
                    'offset': 'earliest',
                    'max_count': 5
                }
            )
        )
        result = await mcp_server.call_tool(request)
        print(f'✅ Messages consumed: {result.content[0].text}')
        
    except Exception as e:
        print(f'❌ Message operations failed: {e}')

asyncio.run(test_message_operations())
"
```

## 🔐 Knox Gateway Cloud Integration

### 1. Knox Gateway Configuration

```bash
# Set Knox Gateway for cloud environment
export KNOX_GATEWAY="https://your-knox-gateway.company.com:8444"
export KNOX_TOKEN="your-bearer-token-here"
export KNOX_SERVICE="kafka"
export KNOX_VERIFY_SSL="true"
```

### 2. Test Knox Integration

```bash
# Test Knox connection
uv run python3 -c "
import sys
sys.path.insert(0, 'src')
from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer
from mcp.types import CallToolRequest, CallToolRequestParams
import asyncio

async def test_knox_integration():
    try:
        mcp_server = CDFKafkaMCPServer()
        print(f'✅ Knox enabled: {mcp_server.config.is_knox_enabled()}')
        
        # Test Knox connection
        request = CallToolRequest(
            params=CallToolRequestParams(
                name='test_knox_connection',
                arguments={}
            )
        )
        result = await mcp_server.call_tool(request)
        print(f'✅ Knox connection: {result.content[0].text}')
        
    except Exception as e:
        print(f'❌ Knox integration failed: {e}')

asyncio.run(test_knox_integration())
"
```

## 🚨 Cloud Testing Troubleshooting

### Common Issues

#### 1. Connection Timeouts
```bash
# Increase timeout settings
export KAFKA_TIMEOUT="60"
export MCP_LOG_LEVEL="DEBUG"
```

#### 2. Authentication Failures
```bash
# Verify credentials
echo $KAFKA_SASL_USERNAME
echo $KAFKA_SASL_PASSWORD
echo $KNOX_TOKEN
```

#### 3. SSL Certificate Issues
```bash
# For testing, disable SSL verification
export KNOX_VERIFY_SSL="false"
export KAFKA_SSL_VERIFY="false"
```

#### 4. Network Connectivity
```bash
# Test network connectivity
ping your-kafka-cluster.com
telnet your-kafka-cluster.com 9092
```

## 📊 Cloud Testing Results

### Test Results Template

```markdown
## Cloud Testing Results

**Date**: 2024-01-01
**Cloud Provider**: AWS MSK / Confluent Cloud / Azure Event Hubs
**Kafka Version**: 2.8.0
**Knox Gateway**: Enabled/Disabled

### Test Results

- [ ] Basic Connection Test
- [ ] Topic Operations Test
- [ ] Message Operations Test
- [ ] Knox Integration Test
- [ ] Performance Test

### Issues Found

1. Issue 1: Description
2. Issue 2: Description

### Recommendations

1. Recommendation 1
2. Recommendation 2
```

## 🎯 Next Steps

1. **Choose Cloud Provider**: Select AWS MSK, Confluent Cloud, or Azure Event Hubs
2. **Set Up Credentials**: Configure authentication credentials
3. **Run Tests**: Execute the cloud testing workflow
4. **Document Results**: Record test results and any issues
5. **Optimize Configuration**: Adjust settings based on test results

## 📚 Additional Resources

- [AWS MSK Documentation](https://docs.aws.amazon.com/msk/)
- [Confluent Cloud Documentation](https://docs.confluent.io/cloud/)
- [Azure Event Hubs Documentation](https://docs.microsoft.com/en-us/azure/event-hubs/)
- [Knox Gateway Documentation](https://knox.apache.org/)
