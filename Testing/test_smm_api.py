#!/usr/bin/env python3
"""
Test SMM (Streams Messaging Manager) API endpoint
"""

import requests
import json
import base64
from typing import Dict, List, Any

class SMMAPITester:
    """Test SMM API endpoint for Kafka operations."""
    
    def __init__(self):
        self.base_url = "https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443/irb-kakfa-only/cdp-proxy-api/smm-api"
        self.username = "ibrooks"
        self.password = "Admin12345#"
        
        # Basic auth header
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def test_smm_api_access(self) -> bool:
        """Test basic SMM API access."""
        print("🔍 Testing SMM API access...")
        
        try:
            response = requests.get(self.base_url, headers=self.headers, timeout=10)
            print(f"   SMM API Status: {response.status_code}")
            
            if response.status_code == 200:
                print("   ✅ SMM API is accessible")
                try:
                    data = response.json()
                    print(f"   📊 Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"   📊 Response: {response.text[:200]}...")
                return True
            elif response.status_code == 401:
                print("   🔐 SMM API requires authentication")
                return False
            else:
                print(f"   ⚠️  SMM API returned: {response.text[:100]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ SMM API Error: {e}")
            return False
    
    def test_smm_endpoints(self) -> List[str]:
        """Test various SMM API endpoints."""
        print("\n🔍 Testing SMM API endpoints...")
        
        endpoints = [
            "/",
            "/api/v1",
            "/api/v1/clusters",
            "/api/v1/topics",
            "/api/v1/connectors",
            "/api/v1/health",
            "/api/v1/status",
            "/api/v1/info",
            "/clusters",
            "/topics",
            "/connectors",
            "/health",
            "/status",
            "/info"
        ]
        
        working_endpoints = []
        
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                response = requests.get(url, headers=self.headers, timeout=5)
                print(f"   {endpoint}: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"   ✅ Working endpoint: {endpoint}")
                    working_endpoints.append(endpoint)
                    try:
                        data = response.json()
                        print(f"   📊 Data: {json.dumps(data, indent=2)[:150]}...")
                    except:
                        print(f"   📊 Data: {response.text[:150]}...")
                elif response.status_code == 401:
                    print(f"   🔐 Authentication required: {endpoint}")
                elif response.status_code == 404:
                    print(f"   ❌ Not found: {endpoint}")
                else:
                    print(f"   ⚠️  Other status: {endpoint} - {response.text[:50]}...")
                    
            except Exception as e:
                print(f"   ❌ Error: {endpoint} - {e}")
        
        return working_endpoints
    
    def test_kafka_operations(self) -> bool:
        """Test Kafka operations through SMM API."""
        print("\n🔍 Testing Kafka operations through SMM API...")
        
        # Test topics endpoint
        topics_url = f"{self.base_url}/api/v1/topics"
        try:
            response = requests.get(topics_url, headers=self.headers, timeout=10)
            print(f"   Topics API Status: {response.status_code}")
            
            if response.status_code == 200:
                topics = response.json()
                print(f"   ✅ Topics API working - Found {len(topics)} topics")
                if topics:
                    print(f"   📊 Topics: {topics}")
                return True
            else:
                print(f"   ⚠️  Topics API: {response.text[:100]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ Topics API Error: {e}")
            return False
    
    def test_connector_operations(self) -> bool:
        """Test connector operations through SMM API."""
        print("\n🔍 Testing connector operations through SMM API...")
        
        # Test connectors endpoint
        connectors_url = f"{self.base_url}/api/v1/connectors"
        try:
            response = requests.get(connectors_url, headers=self.headers, timeout=10)
            print(f"   Connectors API Status: {response.status_code}")
            
            if response.status_code == 200:
                connectors = response.json()
                print(f"   ✅ Connectors API working - Found {len(connectors)} connectors")
                if connectors:
                    print(f"   📊 Connectors: {connectors}")
                return True
            else:
                print(f"   ⚠️  Connectors API: {response.text[:100]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ Connectors API Error: {e}")
            return False
    
    def test_topic_creation(self) -> bool:
        """Test topic creation through SMM API."""
        print("\n🔍 Testing topic creation through SMM API...")
        
        # Try to create a test topic
        topic_name = "smm-test-topic"
        create_url = f"{self.base_url}/api/v1/topics"
        
        topic_config = {
            "name": topic_name,
            "partitions": 1,
            "replication_factor": 1,
            "config": {}
        }
        
        try:
            response = requests.post(create_url, json=topic_config, headers=self.headers, timeout=30)
            print(f"   Topic Creation Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ Topic created successfully: {result}")
                return True
            else:
                print(f"   ⚠️  Topic creation failed: {response.text[:100]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ Topic creation error: {e}")
            return False
    
    def test_connector_creation(self) -> bool:
        """Test connector creation through SMM API."""
        print("\n🔍 Testing connector creation through SMM API...")
        
        # Try to create a test connector
        connector_name = f"smm-test-connector-{int(__import__('time').time())}"
        create_url = f"{self.base_url}/api/v1/connectors"
        
        connector_config = {
            "name": connector_name,
            "config": {
                "connector.class": "org.apache.kafka.connect.mirror.MirrorHeartbeatConnector",
                "topics": "smm-test-topic",
                "source.cluster.alias": "source",
                "target.cluster.alias": "target"
            }
        }
        
        try:
            response = requests.post(create_url, json=connector_config, headers=self.headers, timeout=30)
            print(f"   Connector Creation Status: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"   ✅ Connector created successfully: {result}")
                return True
            else:
                print(f"   ⚠️  Connector creation failed: {response.text[:100]}...")
                return False
                
        except Exception as e:
            print(f"   ❌ Connector creation error: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all SMM API tests."""
        print("🚀 SMM API Testing Suite")
        print("=" * 50)
        
        results = {}
        
        # Test basic access
        results['smm_access'] = self.test_smm_api_access()
        
        # Test endpoints
        working_endpoints = self.test_smm_endpoints()
        results['endpoints_discovered'] = len(working_endpoints) > 0
        
        # Test Kafka operations
        results['kafka_operations'] = self.test_kafka_operations()
        
        # Test connector operations
        results['connector_operations'] = self.test_connector_operations()
        
        # Test topic creation
        results['topic_creation'] = self.test_topic_creation()
        
        # Test connector creation
        results['connector_creation'] = self.test_connector_creation()
        
        # Print summary
        self.print_summary(results, working_endpoints)
        
        return results
    
    def print_summary(self, results: Dict[str, bool], working_endpoints: List[str]):
        """Print test results summary."""
        print("\n" + "=" * 50)
        print("📊 SMM API TEST RESULTS SUMMARY")
        print("=" * 50)
        
        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {test_name}: {status}")
        
        print(f"\n🔍 Working Endpoints ({len(working_endpoints)}):")
        for endpoint in working_endpoints:
            print(f"  - {endpoint}")
        
        if passed_tests > 0:
            print("\n🎉 SMM API is working!")
            print("   This could be the key to Kafka operations in CDP Cloud")
            print("   Consider updating MCP server to use SMM API")
        else:
            print("\n❌ SMM API tests failed")
            print("   SMM API may not be available or properly configured")

def main():
    """Main function to run SMM API tests."""
    tester = SMMAPITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
