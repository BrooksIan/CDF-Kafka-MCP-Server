#!/usr/bin/env python3
"""
Debug CDP Cloud Configuration
Simple script to debug configuration loading issues.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.config import load_config

def debug_config():
    """Debug configuration loading."""
    print("🔍 Debugging CDP Cloud Configuration")
    print("=" * 50)
    
    # Get config path
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    print(f"📋 Config path: {config_path}")
    
    # Check if file exists
    if not os.path.exists(config_path):
        print(f"❌ Config file not found: {config_path}")
        return
    
    print(f"✅ Config file exists: {os.path.getsize(config_path)} bytes")
    
    # Load configuration
    try:
        config = load_config(config_path)
        print("✅ Configuration loaded successfully")
        
        # Print Kafka config
        print(f"\n🔧 Kafka Configuration:")
        print(f"  - Bootstrap Servers: {config.kafka.bootstrap_servers}")
        print(f"  - Type: {type(config.kafka.bootstrap_servers)}")
        print(f"  - Security Protocol: {config.kafka.security_protocol}")
        print(f"  - SASL Mechanism: {config.kafka.sasl_mechanism}")
        print(f"  - Client ID: {config.kafka.client_id}")
        
        # Print Knox config
        print(f"\n🔐 Knox Configuration:")
        print(f"  - Gateway: {config.knox.gateway}")
        print(f"  - Service: {config.knox.service}")
        print(f"  - Token: {'***' + config.knox.token[-10:] if config.knox.token else 'None'}")
        
        # Check for any issues
        print(f"\n🔍 Configuration Analysis:")
        
        # Check bootstrap servers
        if isinstance(config.kafka.bootstrap_servers, list):
            for i, server in enumerate(config.kafka.bootstrap_servers):
                print(f"  - Server {i}: {server}")
                if ':' in server:
                    host, port = server.split(':', 1)
                    print(f"    - Host: {host}")
                    print(f"    - Port: {port}")
                    try:
                        port_int = int(port)
                        print(f"    - Port valid: {port_int}")
                    except ValueError as e:
                        print(f"    - Port invalid: {e}")
        else:
            print(f"  - Bootstrap servers is not a list: {type(config.kafka.bootstrap_servers)}")
        
        # Check if Knox URL is somehow in bootstrap servers
        if config.knox.gateway in str(config.kafka.bootstrap_servers):
            print(f"  ⚠️  WARNING: Knox Gateway URL found in bootstrap servers!")
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_config()
