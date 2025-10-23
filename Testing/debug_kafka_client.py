#!/usr/bin/env python3
"""
Debug Kafka Client Initialization
Debug script to see what's being passed to the Kafka client.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.config import load_config
from cdf_kafka_mcp_server.kafka_client import KafkaClient

def debug_kafka_client():
    """Debug Kafka client initialization."""
    print("🔍 Debugging Kafka Client Initialization")
    print("=" * 50)
    
    # Get config path
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    print(f"📋 Config path: {config_path}")
    
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
        
        # Try to initialize Kafka client
        print(f"\n🧪 Testing Kafka Client Initialization:")
        try:
            kafka_client = KafkaClient(config)
            print("✅ Kafka client initialized successfully")
            
            # Test connection
            print("🔌 Testing connection...")
            if kafka_client.test_connection():
                print("✅ Connection test passed")
            else:
                print("❌ Connection test failed")
                
        except Exception as e:
            print(f"❌ Kafka client initialization failed: {e}")
            import traceback
            traceback.print_exc()
        
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_kafka_client()
