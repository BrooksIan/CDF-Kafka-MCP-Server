#!/bin/bash

# Cloud Testing Wrapper Script for CDF Kafka MCP Server

set -e

echo "🚀 CDF Kafka MCP Server - Cloud Testing"
echo "========================================"

# Function to display usage
usage() {
    echo "Usage: $0 [cloud-provider] [options]"
    echo ""
    echo "Cloud Providers:"
    echo "  aws-msk          AWS Managed Streaming for Kafka"
    echo "  confluent-cloud  Confluent Cloud"
    echo "  azure-eventhub   Azure Event Hubs for Kafka"
    echo "  cdp-cloud        CDP Cloud (Cloudera Data Platform)"
    echo "  generic          Generic SASL_SSL Kafka"
    echo ""
    echo "Options:"
    echo "  --debug          Enable debug logging"
    echo "  --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 aws-msk --debug"
    echo "  $0 confluent-cloud"
    echo "  $0 generic"
    exit 1
}

# Parse arguments
CLOUD_PROVIDER=""
DEBUG_MODE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        aws-msk|confluent-cloud|azure-eventhub|cdp-cloud|generic)
            CLOUD_PROVIDER="$1"
            shift
            ;;
        --debug)
            DEBUG_MODE="true"
            shift
            ;;
        --help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Check if cloud provider is specified
if [ -z "$CLOUD_PROVIDER" ]; then
    echo "❌ Error: Cloud provider must be specified"
    usage
fi

echo "🌍 Cloud Provider: $CLOUD_PROVIDER"

# Set debug mode if requested
if [ "$DEBUG_MODE" = "true" ]; then
    export MCP_LOG_LEVEL="DEBUG"
    echo "🐛 Debug mode enabled"
fi

# Set up cloud-specific environment variables
case "$CLOUD_PROVIDER" in
    "aws-msk")
        echo "📋 Setting up AWS MSK environment..."
        echo "Please set the following environment variables:"
        echo "  export KAFKA_BOOTSTRAP_SERVERS=\"your-msk-cluster.kafka.us-east-1.amazonaws.com:9092\""
        echo "  export KAFKA_SECURITY_PROTOCOL=\"SASL_SSL\""
        echo "  export KAFKA_SASL_MECHANISM=\"SCRAM-SHA-512\""
        echo "  export KAFKA_SASL_USERNAME=\"your-iam-username\""
        echo "  export KAFKA_SASL_PASSWORD=\"your-iam-password\""
        echo "  export AWS_ACCESS_KEY_ID=\"your-aws-access-key-id\""
        echo "  export AWS_SECRET_ACCESS_KEY=\"your-aws-secret-access-key\""
        echo "  export AWS_REGION=\"us-east-1\""
        echo ""
        echo "Press Enter when ready to continue..."
        read
        ;;
    "confluent-cloud")
        echo "📋 Setting up Confluent Cloud environment..."
        echo "Please set the following environment variables:"
        echo "  export KAFKA_BOOTSTRAP_SERVERS=\"pkc-xxxxx.us-west-2.aws.confluent.cloud:9092\""
        echo "  export KAFKA_SECURITY_PROTOCOL=\"SASL_SSL\""
        echo "  export KAFKA_SASL_MECHANISM=\"PLAIN\""
        echo "  export KAFKA_SASL_USERNAME=\"your-api-key\""
        echo "  export KAFKA_SASL_PASSWORD=\"your-api-secret\""
        echo ""
        echo "Press Enter when ready to continue..."
        read
        ;;
    "azure-eventhub")
        echo "📋 Setting up Azure Event Hubs environment..."
        echo "Please set the following environment variables:"
        echo "  export KAFKA_BOOTSTRAP_SERVERS=\"your-eventhub-namespace.servicebus.windows.net:9093\""
        echo "  export KAFKA_SECURITY_PROTOCOL=\"SASL_SSL\""
        echo "  export KAFKA_SASL_MECHANISM=\"PLAIN\""
        echo "  export KAFKA_SASL_USERNAME=\"\$ConnectionString\""
        echo "  export KAFKA_SASL_PASSWORD=\"your-eventhub-connection-string\""
        echo ""
        echo "Press Enter when ready to continue..."
        read
        ;;
    "cdp-cloud")
        echo "📋 Setting up CDP Cloud environment..."
        echo "The Knox bearer token is already configured in the config file."
        echo "Please set the following environment variables (if needed):"
        echo "  export KAFKA_BOOTSTRAP_SERVERS=\"irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443\""
        echo "  export KAFKA_SECURITY_PROTOCOL=\"SASL_SSL\""
        echo "  export KAFKA_SASL_MECHANISM=\"PLAIN\""
        echo "  export KAFKA_SASL_USERNAME=\"your-cdp-username\""
        echo "  export KAFKA_SASL_PASSWORD=\"your-cdp-password\""
        echo "  export KNOX_GATEWAY=\"https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443/irb-kakfa-only/cdp-proxy-token\""
        echo "  export KNOX_TOKEN=\"your-bearer-token\""
        echo "  export KNOX_SERVICE=\"kafka\""
        echo "  export KNOX_VERIFY_SSL=\"true\""
        echo ""
        echo "Press Enter when ready to continue..."
        read
        ;;
    "generic")
        echo "📋 Setting up Generic SASL_SSL environment..."
        echo "Please set the following environment variables:"
        echo "  export KAFKA_BOOTSTRAP_SERVERS=\"your-kafka-cluster:9092\""
        echo "  export KAFKA_SECURITY_PROTOCOL=\"SASL_SSL\""
        echo "  export KAFKA_SASL_MECHANISM=\"PLAIN\""
        echo "  export KAFKA_SASL_USERNAME=\"your-username\""
        echo "  export KAFKA_SASL_PASSWORD=\"your-password\""
        echo ""
        echo "Press Enter when ready to continue..."
        read
        ;;
esac

# Check if required environment variables are set
echo "🔍 Checking environment variables..."

if [ -z "$KAFKA_BOOTSTRAP_SERVERS" ]; then
    echo "❌ Error: KAFKA_BOOTSTRAP_SERVERS is not set"
    exit 1
fi

if [ -z "$KAFKA_SECURITY_PROTOCOL" ]; then
    echo "❌ Error: KAFKA_SECURITY_PROTOCOL is not set"
    exit 1
fi

if [ -z "$KAFKA_SASL_MECHANISM" ]; then
    echo "❌ Error: KAFKA_SASL_MECHANISM is not set"
    exit 1
fi

if [ -z "$KAFKA_SASL_USERNAME" ]; then
    echo "❌ Error: KAFKA_SASL_USERNAME is not set"
    exit 1
fi

if [ -z "$KAFKA_SASL_PASSWORD" ]; then
    echo "❌ Error: KAFKA_SASL_PASSWORD is not set"
    exit 1
fi

echo "✅ Environment variables are set"

# Optional Knox configuration
if [ -n "$KNOX_GATEWAY" ] && [ -n "$KNOX_TOKEN" ]; then
    echo "🔐 Knox Gateway configuration detected"
    echo "  KNOX_GATEWAY: $KNOX_GATEWAY"
    echo "  KNOX_TOKEN: ${KNOX_TOKEN:0:20}..."
else
    echo "ℹ️  Knox Gateway not configured (optional)"
fi

echo ""
echo "🧪 Starting cloud tests..."

# Run the cloud testing script
uv run python3 test_cloud_connection.py

echo ""
echo "🎉 Cloud testing completed!"
echo ""
echo "📊 Next steps:"
echo "  1. Review test results above"
echo "  2. Check any failed tests"
echo "  3. Adjust configuration if needed"
echo "  4. Run tests again if necessary"
echo ""
echo "📚 For more information, see:"
echo "  - CLOUD_TESTING_SETUP.md"
echo "  - README.md (Usage section)"
echo "  - config/kafka_config_*.yaml files"
