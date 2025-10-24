#!/usr/bin/env python3
"""
Simple script to add a value to mcptesttopic
"""

import asyncio
import sys
import os
import json
import time
import requests
import base64
from typing import Dict, Any

def add_value_to_topic():
    """Add a value to mcptesttopic using direct HTTP requests."""
    print("🚀 Adding value to mcptesttopic")
    print("=" * 50)
    
    # Configuration
    base_url = os.getenv("CDP_REST_BASE_URL", "https://your-cdp-cluster.example.com:443")
    username = os.getenv("CDP_REST_USERNAME", "your-username")
    password = os.getenv("CDP_REST_PASSWORD", "your-password")
    cluster_id = "irb-kakfa-only"
    topic_name = "mcptesttopic"
    
    # Create session with authentication
    session = requests.Session()
    credentials = f"{username}:{password}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    session.headers.update({
        'Authorization': f'Basic {encoded_credentials}',
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'User-Agent': 'CDF-Kafka-MCP-Server/1.0'
    })
    session.verify = False
    
    # Disable SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    print("🔍 Testing connection...")
    try:
        # Test basic connectivity
        response = session.get(f"{base_url}/api/health", timeout=10)
        print(f"Connection test: {response.status_code}")
        
        if response.status_code in [200, 404]:
            print("✅ Connection successful")
        else:
            print(f"❌ Connection failed: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return
    
    print(f"\n📝 Attempting to add value to topic '{topic_name}'...")
    
    # Try different endpoints for producing messages
    endpoints_to_try = [
        f"{base_url}/irb-kakfa-only/cdp-proxy/kafka-rest/clusters/{cluster_id}/topics/{topic_name}/records",
        f"{base_url}/irb-kakfa-only/cdp-proxy/kafka-rest/clusters/default/topics/{topic_name}/records",
        f"{base_url}/irb-kakfa-only/cdp-proxy/kafka-topics/{topic_name}/records",
        f"{base_url}/irb-kakfa-only/cdp-proxy/kafka/{topic_name}/records"
    ]
    
    message_data = {
        "value": f"Hello from MCP Server! Timestamp: {int(time.time())}",
        "key": "test-key-1",
        "headers": {
            "source": "mcp-server",
            "timestamp": str(int(time.time())),
            "version": "1.0"
        }
    }
    
    success = False
    for i, endpoint in enumerate(endpoints_to_try):
        print(f"\n🔄 Trying endpoint {i+1}: {endpoint}")
        try:
            response = session.post(endpoint, json=message_data, timeout=10)
            print(f"Response status: {response.status_code}")
            print(f"Response headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                print("✅ Message sent successfully!")
                print(f"Response: {response.text}")
                success = True
                break
            elif response.status_code == 201:
                print("✅ Message created successfully!")
                print(f"Response: {response.text}")
                success = True
                break
            elif response.status_code == 404:
                print("❌ Endpoint not found")
            elif response.status_code == 401:
                print("❌ Authentication failed")
            elif response.status_code == 403:
                print("❌ Access forbidden")
            else:
                print(f"❌ Unexpected status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
    
    if not success:
        print("\n❌ All endpoints failed. Trying alternative approach...")
        
        # Try to create the topic first
        print("\n🔧 Attempting to create topic...")
        create_endpoints = [
            f"{base_url}/irb-kakfa-only/cdp-proxy/kafka-rest/clusters/{cluster_id}/topics",
            f"{base_url}/irb-kakfa-only/cdp-proxy/kafka-rest/clusters/default/topics",
            f"{base_url}/irb-kakfa-only/cdp-proxy/kafka-topics"
        ]
        
        topic_config = {
            "name": topic_name,
            "partitions": 1,
            "replication_factor": 1,
            "config": {
                "cleanup.policy": "delete",
                "retention.ms": "604800000"
            }
        }
        
        for i, endpoint in enumerate(create_endpoints):
            print(f"\n🔄 Trying create endpoint {i+1}: {endpoint}")
            try:
                response = session.post(endpoint, json=topic_config, timeout=10)
                print(f"Create response status: {response.status_code}")
                
                if response.status_code in [200, 201, 409]:  # 409 = already exists
                    print("✅ Topic creation/verification successful!")
                    break
                else:
                    print(f"❌ Create failed: {response.status_code} - {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Create request failed: {e}")
    
    print(f"\n🎯 Summary:")
    if success:
        print("✅ Successfully added value to mcptesttopic!")
    else:
        print("❌ Failed to add value to mcptesttopic")
        print("Possible reasons:")
        print("- Topic doesn't exist and couldn't be created")
        print("- Authentication issues")
        print("- CDP REST API endpoints not available")
        print("- Network connectivity issues")

if __name__ == "__main__":
    add_value_to_topic()
