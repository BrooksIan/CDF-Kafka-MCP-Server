#!/bin/bash

# CDF Kafka MCP Server Example Usage
# This script demonstrates how to use the CDF Kafka MCP Server

set -e

echo "🚀 CDF Kafka MCP Server Example Usage"
echo "======================================"

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.9+ first."
    exit 1
fi

# Check if the package is installed
if ! python -c "import cdf_kafka_mcp_server" 2>/dev/null; then
    echo "❌ Package not installed. Installing first..."
    make install
fi

echo ""
echo "📋 Available MCP Tools:"
echo "======================="

# List topics
echo "1. Listing topics..."
python -m cdf_kafka_mcp_server --help | grep -A 20 "Available commands" || echo "   (Run with --help to see available commands)"

echo ""
echo "🔧 Configuration Examples:"
echo "========================="

echo "1. Direct Kafka connection (no Knox):"
echo "   python -m cdf_kafka_mcp_server --bootstrap-servers localhost:9092"

echo ""
echo "2. Kafka with SASL authentication:"
echo "   python -m cdf_kafka_mcp_server \\"
echo "     --bootstrap-servers localhost:9092 \\"
echo "     --security-protocol SASL_SSL \\"
echo "     --sasl-mechanism SCRAM-SHA-256 \\"
echo "     --sasl-username kafka-user \\"
echo "     --sasl-password kafka-password"

echo ""
echo "3. Kafka with Knox Gateway:"
echo "   python -m cdf_kafka_mcp_server \\"
echo "     --bootstrap-servers kafka-broker:9092 \\"
echo "     --knox-gateway https://knox-gateway.example.com:8443 \\"
echo "     --knox-token your-oauth2-token"

echo ""
echo "4. Using configuration file:"
echo "   python -m cdf_kafka_mcp_server --config config/kafka_config.yaml"

echo ""
echo "🐳 Docker Examples:"
echo "==================="

echo "1. Build and run with Docker Compose:"
echo "   docker-compose up --build"

echo ""
echo "2. Run individual services:"
echo "   docker-compose up kafka zookeeper kafka-ui"

echo ""
echo "📝 MCP Tool Examples:"
echo "====================="

echo "1. List topics:"
echo '   {"tool": "list_topics", "arguments": {}}'

echo ""
echo "2. Create a topic:"
echo '   {"tool": "create_topic", "arguments": {"name": "my-topic", "partitions": 3, "replication_factor": 1}}'

echo ""
echo "3. Produce a message:"
echo '   {"tool": "produce_message", "arguments": {"topic": "my-topic", "key": "key1", "value": "Hello Kafka!"}}'

echo ""
echo "4. Consume messages:"
echo '   {"tool": "consume_messages", "arguments": {"topic": "my-topic", "max_count": 10, "timeout": 5}}'

echo ""
echo "5. Test connection:"
echo '   {"tool": "test_connection", "arguments": {}}'

echo ""
echo "🔍 Debugging:"
echo "============="

echo "1. Enable debug logging:"
echo "   MCP_LOG_LEVEL=DEBUG python -m cdf_kafka_mcp_server"

echo ""
echo "2. Test Knox connection:"
echo '   {"tool": "test_knox_connection", "arguments": {}}'

echo ""
echo "3. Get broker information:"
echo '   {"tool": "get_broker_info", "arguments": {}}'

echo ""
echo "✅ Example completed!"
echo "===================="
echo ""
echo "For more information, see:"
echo "- README.md for detailed documentation"
echo "- config/kafka_config.yaml for configuration options"
echo "- claude_desktop_config.json for Claude Desktop integration"
