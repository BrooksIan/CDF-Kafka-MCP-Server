#!/bin/bash

# Knox Gateway Integration Test Runner
# This script runs comprehensive tests for MCP server integration with Knox Gateway

set -e

echo "🚀 Knox Gateway Integration Test Runner"
echo "======================================"
echo ""

# Check if we're in the right directory
if [ ! -f "test_knox_integration.py" ]; then
    echo "❌ Error: test_knox_integration.py not found"
    echo "   Please run this script from the Testing/ directory"
    exit 1
fi

# Check if UV is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: UV is not installed or not in PATH"
    echo "   Please install UV: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if configuration file exists
CONFIG_FILE="../config/kafka_config_knox_enhanced.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: Configuration file not found: $CONFIG_FILE"
    echo "   Please ensure the Knox configuration file exists"
    exit 1
fi

echo "✅ Environment check passed"
echo ""

# Function to run tests
run_tests() {
    local test_script="test_knox_integration.py"
    
    echo "🧪 Running Knox Gateway integration tests..."
    echo "   Config: $CONFIG_FILE"
    echo ""
    
    # Run tests directly (timeout not available on macOS)
    if uv run python $test_script; then
        echo ""
        echo "✅ Tests completed successfully"
        return 0
    else
        local exit_code=$?
        echo ""
        echo "❌ Tests failed with exit code: $exit_code"
        return 1
    fi
}

# Function to validate Knox Gateway setup
validate_knox_setup() {
    echo "🔍 Validating Knox Gateway setup..."
    
    if [ ! -f "validate_knox_setup.py" ]; then
        echo "❌ Error: validate_knox_setup.py not found"
        return 1
    fi
    
    if uv run python validate_knox_setup.py; then
        echo "✅ Knox Gateway setup validation passed"
        return 0
    else
        echo "❌ Knox Gateway setup validation failed"
        echo "   Please fix the issues before running integration tests"
        return 1
    fi
}

# Function to show configuration status
show_configuration_status() {
    echo "📋 Configuration Status Check"
    echo "============================"
    
    # Check configuration file
    if [ -f "$CONFIG_FILE" ]; then
        echo "✅ Configuration file exists: $CONFIG_FILE"
        
        # Check for Knox configuration
        if grep -q "knox:" "$CONFIG_FILE"; then
            echo "✅ Knox configuration found in config file"
        else
            echo "⚠️  Knox configuration not found in config file"
        fi
        
        # Check for CDP configuration
        if grep -q "cdp:" "$CONFIG_FILE"; then
            echo "✅ CDP configuration found in config file"
        else
            echo "⚠️  CDP configuration not found in config file"
        fi
    else
        echo "❌ Configuration file missing: $CONFIG_FILE"
    fi
    
    echo ""
}

# Main execution
main() {
    echo "Starting Knox Gateway integration tests..."
    echo ""
    
    # Show configuration status
    show_configuration_status
    
    # Validate Knox Gateway setup
    if ! validate_knox_setup; then
        echo ""
        echo "🔧 Troubleshooting Steps:"
        echo "1. Access Knox Admin UI: https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site/irb-kakfa-only/manager/admin-ui/"
        echo "2. Verify authentication credentials"
        echo "3. Check Knox Gateway service status"
        echo "4. Review Knox Gateway logs"
        echo "5. Configure Kafka services in topology"
        echo ""
        echo "Once Knox Gateway is properly configured, run this script again."
        exit 1
    fi
    
    echo ""
    
    # Run tests
    if run_tests; then
        echo ""
        echo "🎉 All tests completed successfully!"
        echo ""
        echo "📋 Next Steps:"
        echo "1. Use the MCP server for Kafka operations"
        echo "2. Monitor service health regularly"
        echo "3. Test topic creation and message production"
        exit 0
    else
        echo ""
        echo "❌ Some tests failed or timed out"
        echo ""
        echo "🔧 Troubleshooting Steps:"
        echo "1. Check Knox Gateway configuration"
        echo "2. Verify Kafka service mappings"
        echo "3. Test individual components"
        echo "4. Review error messages above"
        exit 1
    fi
}

# Run main function
main "$@"
