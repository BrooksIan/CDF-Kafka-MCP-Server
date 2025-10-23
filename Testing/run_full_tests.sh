#!/bin/bash
# Full Test Runner for CDF Kafka MCP Server
# Runs all test suites comprehensively

set -e

echo "🚀 CDF Kafka MCP Server - Full Test Suite"
echo "=========================================="

# Check if Docker Compose is running
echo "📋 Checking Docker Compose services..."
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Docker Compose services not running. Please run: docker-compose up -d"
    exit 1
fi

echo "✅ Docker Compose services are running"

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Run comprehensive tests
echo ""
echo "🧪 Running comprehensive test suite..."
cd "$(dirname "$0")"
python3 run_tests.py

echo ""
echo "🎉 Full test suite completed!"
echo "Check test_results.json for detailed results"
