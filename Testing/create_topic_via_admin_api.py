#!/usr/bin/env python3
"""
Create topic using Kafka Admin API directly
"""

import os
import sys
import asyncio
from kafka.admin import KafkaAdminClient, ConfigResource, ConfigResourceType
from kafka.admin.new_topic import NewTopic
from kafka.errors import TopicAlreadyExistsError, KafkaError

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.config import load_config

def create_topic_via_admin_api():
    """Create topic using Kafka Admin API directly."""
    print("🚀 Creating topic via Kafka Admin API")
    print("=" * 50)
    
    try:
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'kafka_config.yaml')
        config = load_config(config_path)
        
        print(f"📋 Configuration loaded:")
        print(f"  - Bootstrap servers: {config.kafka.bootstrap_servers}")
        print(f"  - Security protocol: {config.kafka.security_protocol}")
        print(f"  - SASL mechanism: {config.kafka.sasl_mechanism}")
        print(f"  - Username: {config.kafka.sasl_username}")
        
        # Create admin client configuration
        admin_config = {
            'bootstrap_servers': config.kafka.bootstrap_servers,
            'client_id': 'topic-creator-admin',
            'security_protocol': config.kafka.security_protocol,
            'sasl_mechanism': config.kafka.sasl_mechanism,
            'sasl_plain_username': config.kafka.sasl_username,
            'sasl_plain_password': config.kafka.sasl_password,
            'request_timeout_ms': 30000,
            'api_version': (2, 6, 0),
        }
        
        # Add SSL configuration if needed
        if config.kafka.security_protocol in ['SSL', 'SASL_SSL']:
            admin_config['ssl_check_hostname'] = False
        
        print(f"\n🔧 Admin client configuration:")
        for key, value in admin_config.items():
            if 'password' in key.lower():
                print(f"  - {key}: ***")
            else:
                print(f"  - {key}: {value}")
        
        # Create admin client
        print(f"\n🔌 Creating Kafka Admin Client...")
        admin_client = KafkaAdminClient(**admin_config)
        
        # Test connection
        print(f"🔍 Testing connection...")
        metadata = admin_client.list_topics()
        print(f"✅ Connection successful! Found {len(metadata.topics)} topics")
        
        # List existing topics
        print(f"\n📋 Existing topics:")
        for topic in sorted(metadata.topics.keys()):
            print(f"  - {topic}")
        
        # Create new topic
        topic_name = "cursortest"
        print(f"\n🆕 Creating topic: {topic_name}")
        
        new_topic = NewTopic(
            name=topic_name,
            num_partitions=1,
            replication_factor=1,
            topic_configs={
                'cleanup.policy': 'delete',
                'retention.ms': '604800000',  # 7 days
            }
        )
        
        # Create the topic
        result = admin_client.create_topics([new_topic], validate_only=False)
        
        # Check result
        for topic, future in result.items():
            try:
                future.result()  # Wait for the result
                print(f"✅ Topic '{topic}' created successfully!")
            except TopicAlreadyExistsError:
                print(f"⚠️  Topic '{topic}' already exists")
            except KafkaError as e:
                print(f"❌ Failed to create topic '{topic}': {e}")
        
        # Verify topic was created
        print(f"\n🔍 Verifying topic creation...")
        metadata = admin_client.list_topics()
        if topic_name in metadata.topics:
            print(f"✅ Topic '{topic_name}' confirmed to exist!")
            
            # Get topic details
            topic_details = metadata.topics[topic_name]
            print(f"📊 Topic details:")
            print(f"  - Partitions: {len(topic_details.partitions)}")
            print(f"  - Partition details: {topic_details.partitions}")
        else:
            print(f"❌ Topic '{topic_name}' not found after creation")
        
        # Close admin client
        admin_client.close()
        print(f"\n✅ Admin client closed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_topic_via_admin_api()
