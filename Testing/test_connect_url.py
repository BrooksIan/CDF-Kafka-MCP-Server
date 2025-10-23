#!/usr/bin/env python3
"""
Test Kafka Connect URL Generation
Test script to verify the correct Kafka Connect URL is generated for CDP Cloud.
"""

import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.config import load_config
from cdf_kafka_mcp_server.kafka_client import KafkaClient

def test_connect_url():
    """Test Kafka Connect URL generation."""
    print("🔍 Testing Kafka Connect URL Generation")
    print("=" * 50)
    
    # Get config path
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
    print(f"📋 Config path: {config_path}")
    
    # Load configuration
    try:
        config = load_config(config_path)
        print("✅ Configuration loaded successfully")
        
        # Print Knox config
        print(f"\n🔐 Knox Configuration:")
        print(f"  - Gateway: {config.knox.gateway}")
        print(f"  - Service: {config.knox.service}")
        
        # Initialize Kafka client
        kafka_client = KafkaClient(config)
        
        # Test Connect URL generation
        connect_url = kafka_client._get_connect_url()
        print(f"\n🔗 Generated Connect URL: {connect_url}")
        
        # Expected URL
        expected_url = "https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443/irb-kakfa-only/cdp-proxy-api/kafka-connect"
        print(f"🎯 Expected URL: {expected_url}")
        
        if connect_url == expected_url:
            print("✅ Connect URL is correct!")
        else:
            print("❌ Connect URL doesn't match expected value")
        
        # Test a simple Connect API call
        print(f"\n🧪 Testing Connect API call...")
        try:
            result = kafka_client.list_connectors()
            print(f"✅ Connect API call successful: {result}")
        except Exception as e:
            print(f"⚠️  Connect API call failed (expected): {e}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_connect_url()
