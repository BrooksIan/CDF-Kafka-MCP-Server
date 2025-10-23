#!/bin/bash
# Quick Test Runner for CDF Kafka MCP Server
# Runs essential tests quickly for development

set -e

echo "🚀 CDF Kafka MCP Server - Quick Tests"
echo "======================================"

# Check if Docker Compose is running
echo "📋 Checking Docker Compose services..."
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Docker Compose services not running. Please run: docker-compose up -d"
    exit 1
fi

echo "✅ Docker Compose services are running"

# Run MCP Tools tests
echo ""
echo "🧪 Running MCP Tools tests..."
cd "$(dirname "$0")"
python3 test_mcp_tools.py

echo ""
echo "🎉 Quick tests completed!"
echo "For comprehensive testing, run: python3 run_tests.py"
