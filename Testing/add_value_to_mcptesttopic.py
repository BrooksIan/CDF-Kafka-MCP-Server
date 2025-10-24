#!/usr/bin/env python3
"""
Add a value to mcptesttopic using CDP Kafka client
"""

import asyncio
import sys
import os
import json
import time
from typing import Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.cdp_kafka_client import CDPKafkaClient
from cdf_kafka_mcp_server.config import load_config

async def add_value_to_topic():
    """Add a value to mcptesttopic."""
    print("🚀 Adding value to mcptesttopic")
    print("=" * 50)
    
    try:
        # Load configuration
        config = load_config('../config/kafka_config_cdp_optimized.yaml')
        
        # Initialize CDP Kafka client
        print("🔧 Initializing CDP Kafka client...")
        client = CDPKafkaClient(config)
        
        # Test connection
        print("🔍 Testing connection...")
        connection_result = client.test_connection()
        print(f"Connection: {connection_result.get('connected', False)}")
        print(f"Message: {connection_result.get('message', 'No message')}")
        
        # Create topic if it doesn't exist
        print("\n🔧 Creating topic if it doesn't exist...")
        try:
            topic_result = await client.create_topic(
                name='mcptesttopic',
                partitions=1,
                replication_factor=1
            )
            print(f"Topic creation result: {topic_result}")
        except Exception as e:
            print(f"Topic creation failed (may already exist): {e}")
        
        # List topics to verify
        print("\n🔍 Listing topics...")
        try:
            topics = await client.list_topics()
            print(f"Available topics: {topics}")
        except Exception as e:
            print(f"Failed to list topics: {e}")
        
        # Produce message
        print("\n📝 Producing message to mcptesttopic...")
        try:
            message_data = {
                'topic': 'mcptesttopic',
                'key': 'test-key-1',
                'value': f'Hello from MCP Server! Timestamp: {int(time.time())}',
                'headers': {
                    'source': 'mcp-server',
                    'timestamp': str(int(time.time())),
                    'version': '1.0'
                }
            }
            
            result = await client.produce_message(
                topic='mcptesttopic',
                key='test-key-1',
                value=f'Hello from MCP Server! Timestamp: {int(time.time())}',
                headers={
                    'source': 'mcp-server',
                    'timestamp': str(int(time.time())),
                    'version': '1.0'
                }
            )
            
            print(f"✅ Message produced successfully!")
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"❌ Failed to produce message: {e}")
            
            # Try with minimal parameters
            print("\n🔄 Trying with minimal parameters...")
            try:
                result = await client.produce_message(
                    topic='mcptesttopic',
                    value=f'Simple message from MCP Server at {int(time.time())}'
                )
                print(f"✅ Simple message produced: {result}")
            except Exception as e2:
                print(f"❌ Simple message also failed: {e2}")
        
        # Consume messages to verify
        print("\n🔍 Consuming messages to verify...")
        try:
            messages = await client.consume_messages(
                topic='mcptesttopic',
                max_messages=5
            )
            print(f"Consumed messages: {len(messages)}")
            for i, msg in enumerate(messages):
                print(f"  Message {i+1}: {msg}")
        except Exception as e:
            print(f"Failed to consume messages: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(add_value_to_topic())
