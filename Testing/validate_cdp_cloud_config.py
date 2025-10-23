#!/usr/bin/env python3
"""
CDP Cloud Configuration Validator
Quick validation of CDP Cloud configuration and basic connectivity.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def validate_cdp_cloud_config():
    """Validate CDP Cloud configuration and basic connectivity."""
    print("🔍 CDP Cloud Configuration Validator")
    print("=" * 50)
    
    try:
        # Load configuration with explicit path
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
        print(f"📋 Loading configuration from: {config_path}")
        config = load_config(config_path)
        
        # Validate Kafka configuration
        print("\n🔧 Kafka Configuration:")
        print(f"  - Bootstrap Servers: {config.kafka.bootstrap_servers}")
        print(f"  - Security Protocol: {config.kafka.security_protocol}")
        print(f"  - SASL Mechanism: {config.kafka.sasl_mechanism}")
        print(f"  - Client ID: {config.kafka.client_id}")
        print(f"  - Timeout: {config.kafka.timeout}s")
        
        # Validate Knox configuration
        print("\n🔐 Knox Gateway Configuration:")
        print(f"  - Gateway URL: {config.knox.gateway}")
        print(f"  - Service: {config.knox.service}")
        print(f"  - Verify SSL: {config.knox.verify_ssl}")
        print(f"  - Token: {'***' + config.knox.token[-10:] if config.knox.token else 'Not set'}")
        print(f"  - Username: {config.knox.username or 'Not set'}")
        
        # Check for CDP Cloud specific settings
        print("\n☁️  CDP Cloud Specific Settings:")
        is_cdp_cloud = "cgsi-dem.prep-j1tk.a3.cloudera.site" in config.kafka.bootstrap_servers
        print(f"  - CDP Cloud URL detected: {is_cdp_cloud}")
        
        has_knox_token = bool(config.knox.token)
        print(f"  - Knox token configured: {has_knox_token}")
        
        sasl_ssl_enabled = config.kafka.security_protocol == "SASL_SSL"
        print(f"  - SASL_SSL enabled: {sasl_ssl_enabled}")
        
        # Configuration validation
        print("\n✅ Configuration Validation:")
        validation_results = []
        
        # Check required fields
        if not config.kafka.bootstrap_servers:
            validation_results.append(("Bootstrap servers", False, "Missing"))
        else:
            validation_results.append(("Bootstrap servers", True, "OK"))
        
        if config.kafka.security_protocol != "SASL_SSL":
            validation_results.append(("Security protocol", False, f"Expected SASL_SSL, got {config.kafka.security_protocol}"))
        else:
            validation_results.append(("Security protocol", True, "OK"))
        
        if not config.knox.gateway:
            validation_results.append(("Knox gateway", False, "Missing"))
        else:
            validation_results.append(("Knox gateway", True, "OK"))
        
        if not config.knox.token and not config.knox.username:
            validation_results.append(("Knox authentication", False, "No token or username provided"))
        else:
            validation_results.append(("Knox authentication", True, "OK"))
        
        # Print validation results
        for field, valid, message in validation_results:
            status = "✅" if valid else "❌"
            print(f"  {status} {field}: {message}")
        
        # Overall validation
        all_valid = all(result[1] for result in validation_results)
        
        print(f"\n📊 Overall Validation: {'✅ PASSED' if all_valid else '❌ FAILED'}")
        
        if all_valid:
            print("\n🎉 CDP Cloud configuration is valid and ready for testing!")
            print("\nNext steps:")
            print("  1. Run comprehensive tests: ./run_cdp_cloud_tests.sh")
            print("  2. Start MCP server: uv run python -m cdf_kafka_mcp_server")
            print("  3. Test individual tools via MCP client")
        else:
            print("\n⚠️  Configuration issues detected. Please fix before testing.")
            print("\nTroubleshooting:")
            print("  1. Run setup script: ../setup_cloud.sh cdp-cloud")
            print("  2. Check environment variables")
            print("  3. Verify Knox Gateway accessibility")
        
        return all_valid
        
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {e}")
        logger.error(f"Configuration validation error: {e}")
        return False

async def main():
    """Main function."""
    success = await validate_cdp_cloud_config()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
