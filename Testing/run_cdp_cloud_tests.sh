#!/bin/bash

# CDP Cloud MCP Tools Test Runner
# Runs comprehensive tests for all MCP tools against CDP Cloud configuration

set -e

echo "🚀 CDP Cloud MCP Tools Test Suite"
echo "=================================="
echo "Testing all MCP tools against CDP Cloud with Knox Gateway authentication"
echo ""

# Check if we're in the right directory
if [ ! -f "test_cdp_cloud_mcp_tools.py" ]; then
    echo "❌ Error: test_cdp_cloud_mcp_tools.py not found"
    echo "Please run this script from the Testing/ directory"
    exit 1
fi

# Check if CDP Cloud configuration is set up
if [ ! -f "../config/kafka_config.yaml" ]; then
    echo "❌ Error: kafka_config.yaml not found"
    echo "Please run: ../setup_cloud.sh cdp-cloud"
    exit 1
fi

echo "📋 Configuration check:"
echo "  - CDP Cloud config: $(ls -la ../config/kafka_config.yaml | awk '{print $5}' | xargs -I {} echo "{} bytes")"
echo "  - Knox Gateway: $(grep 'gateway:' ../config/kafka_config.yaml | cut -d'"' -f2)"
echo "  - Security Protocol: $(grep 'security_protocol:' ../config/kafka_config.yaml | cut -d'"' -f2)"
echo ""

# Set environment variables for CDP Cloud
echo "🔧 Setting up CDP Cloud environment..."
export KAFKA_BOOTSTRAP_SERVERS="irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443"
export KAFKA_SECURITY_PROTOCOL="SASL_SSL"
export KAFKA_SASL_MECHANISM="PLAIN"
export KNOX_GATEWAY="https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443/irb-kakfa-only/cdp-proxy-token"
export KNOX_SERVICE="kafka"
export KNOX_VERIFY_SSL="true"
export KAFKA_CONFIG_FILE="../config/kafka_config.yaml"

# Optional: Set CDP Cloud credentials if provided
if [ ! -z "$KAFKA_SASL_USERNAME" ] && [ ! -z "$KAFKA_SASL_PASSWORD" ]; then
    echo "✅ CDP Cloud credentials provided"
else
    echo "⚠️  CDP Cloud credentials not set (using Knox token only)"
    echo "   To set credentials: export KAFKA_SASL_USERNAME='your-username'"
    echo "   To set credentials: export KAFKA_SASL_PASSWORD='your-password'"
fi

echo ""
echo "🧪 Starting MCP tools test suite..."
echo ""

# Run the test script
if command -v uv &> /dev/null; then
    echo "Using UV to run tests..."
    uv run python test_cdp_cloud_mcp_tools.py
else
    echo "Using Python to run tests..."
    python3 test_cdp_cloud_mcp_tools.py
fi

echo ""
echo "🎉 CDP Cloud MCP Tools test completed!"
echo "Check the generated JSON file for detailed results."
