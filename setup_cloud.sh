#!/bin/bash
# Cloud Kafka Setup Script for CDF Kafka MCP Server
# This script helps you quickly configure the MCP server for cloud deployments

set -e

echo "🚀 CDF Kafka MCP Server - Cloud Setup"
echo "====================================="

# Function to display usage
usage() {
    echo "Usage: $0 [aws-msk|confluent-cloud|azure-eventhub|cdp-cloud|generic]"
    echo ""
    echo "Options:"
    echo "  aws-msk         Setup for AWS MSK (Managed Streaming for Kafka)"
    echo "  confluent-cloud Setup for Confluent Cloud"
    echo "  azure-eventhub  Setup for Azure Event Hubs for Kafka"
    echo "  cdp-cloud       Setup for CDP Cloud (Cloudera Data Platform)"
    echo "  generic         Setup for generic cloud Kafka deployment"
    echo ""
    echo "Example:"
    echo "  $0 cdp-cloud"
    exit 1
}

# Check if provider is specified
if [ $# -eq 0 ]; then
    usage
fi

PROVIDER=$1

case $PROVIDER in
    "aws-msk")
        echo "📋 Setting up for AWS MSK..."
        cp config/kafka_config_aws_msk.yaml config/kafka_config.yaml
        echo "✅ Configuration copied to config/kafka_config.yaml"
        echo ""
        echo "🔧 Next steps:"
        echo "1. Set your AWS credentials:"
        echo "   export AWS_ACCESS_KEY_ID=\"your-access-key\""
        echo "   export AWS_SECRET_ACCESS_KEY=\"your-secret-key\""
        echo "   export AWS_REGION=\"us-east-1\""
        echo ""
        echo "2. Update the bootstrap servers in config/kafka_config.yaml"
        echo "3. Run: uv run python -m cdf_kafka_mcp_server"
        ;;
    
    "confluent-cloud")
        echo "📋 Setting up for Confluent Cloud..."
        cp config/kafka_config_confluent_cloud.yaml config/kafka_config.yaml
        echo "✅ Configuration copied to config/kafka_config.yaml"
        echo ""
        echo "🔧 Next steps:"
        echo "1. Set your Confluent Cloud credentials:"
        echo "   export CONFLUENT_API_KEY=\"your-api-key\""
        echo "   export CONFLUENT_API_SECRET=\"your-api-secret\""
        echo ""
        echo "2. Update the bootstrap servers in config/kafka_config.yaml"
        echo "3. Run: uv run python -m cdf_kafka_mcp_server"
        ;;
    
    "azure-eventhub")
        echo "📋 Setting up for Azure Event Hubs..."
        cp config/kafka_config_azure_eventhub.yaml config/kafka_config.yaml
        echo "✅ Configuration copied to config/kafka_config.yaml"
        echo ""
        echo "🔧 Next steps:"
        echo "1. Set your Azure Event Hubs connection string:"
        echo "   export AZURE_EVENTHUB_CONNECTION_STRING=\"your-connection-string\""
        echo ""
        echo "2. Update the bootstrap servers in config/kafka_config.yaml"
        echo "3. Run: uv run python -m cdf_kafka_mcp_server"
        ;;
    
    "cdp-cloud")
        echo "📋 Setting up for CDP Cloud (Cloudera Data Platform)..."
        cp config/kafka_config_cdp_cloud.yaml config/kafka_config.yaml
        echo "✅ Configuration copied to config/kafka_config.yaml"
        echo ""
        echo "🔧 Next steps:"
        echo "1. The Knox bearer token is already configured in the config file"
        echo "2. Set your CDP Cloud credentials (if needed):"
        echo "   export KAFKA_SASL_USERNAME=\"your-cdp-username\""
        echo "   export KAFKA_SASL_PASSWORD=\"your-cdp-password\""
        echo ""
        echo "3. Optional: Copy environment template:"
        echo "   cp config/env_cdp_cloud_template.txt .env"
        echo "   # Edit .env with your actual values"
        echo ""
        echo "4. Run: uv run python -m cdf_kafka_mcp_server"
        echo ""
        echo "📝 Note: This configuration uses Knox Gateway authentication"
        echo "   with the provided bearer token for secure access to CDP Cloud."
        ;;
    
    "generic")
        echo "📋 Setting up for generic cloud deployment..."
        cp config/kafka_config_cloud.yaml config/kafka_config.yaml
        echo "✅ Configuration copied to config/kafka_config.yaml"
        echo ""
        echo "🔧 Next steps:"
        echo "1. Set your cloud provider credentials:"
        echo "   export KAFKA_SASL_USERNAME=\"your-username\""
        echo "   export KAFKA_SASL_PASSWORD=\"your-password\""
        echo ""
        echo "2. Update the bootstrap servers in config/kafka_config.yaml"
        echo "3. Run: uv run python -m cdf_kafka_mcp_server"
        ;;
    
    *)
        echo "❌ Unknown provider: $PROVIDER"
        usage
        ;;
esac

echo ""
echo "📚 For more information, see the README.md file"
echo "🎉 Setup complete!"
