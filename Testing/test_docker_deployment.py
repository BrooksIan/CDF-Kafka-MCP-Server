#!/usr/bin/env python3
"""
Docker Deployment Testing Suite for CDF Kafka MCP Server
Tests Docker Compose services and MCP server integration
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from cdf_kafka_mcp_server.mcp_server import CDFKafkaMCPServer

class DockerDeploymentTester:
    def __init__(self):
        self.compose_file = "../docker-compose.yml"
        self.required_services = ["kafka", "zookeeper", "smm", "kafka-connect", "schema-registry"]
        self.test_results = {}
        
    def run_command(self, command: List[str], timeout: int = 30) -> subprocess.CompletedProcess:
        """Run a command with timeout"""
        try:
            return subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(command, 1, "", "Command timed out")
        except Exception as e:
            return subprocess.CompletedProcess(command, 1, "", str(e))
    
    def test_docker_compose_services(self):
        """Test that all required Docker Compose services are running"""
        print("\n🧪 Testing Docker Compose services...")
        
        try:
            # Check Docker Compose status
            result = self.run_command(["docker-compose", "-f", self.compose_file, "ps"])
            
            if result.returncode != 0:
                print(f"❌ Docker Compose ps failed: {result.stderr}")
                self.test_results["docker_compose_ps"] = False
                return
            
            # Check each required service
            services_running = []
            for service in self.required_services:
                if service in result.stdout and ("Up" in result.stdout or "healthy" in result.stdout):
                    services_running.append(service)
                    print(f"  ✅ {service} is running")
                else:
                    print(f"  ❌ {service} is not running")
            
            if len(services_running) == len(self.required_services):
                print(f"✅ All {len(self.required_services)} required services are running")
                self.test_results["docker_compose_services"] = True
            else:
                print(f"❌ Only {len(services_running)}/{len(self.required_services)} services are running")
                self.test_results["docker_compose_services"] = False
                
        except Exception as e:
            print(f"❌ Docker Compose services test failed: {e}")
            self.test_results["docker_compose_services"] = False
    
    def test_kafka_connectivity(self):
        """Test Kafka connectivity using CLI tools"""
        print("\n🧪 Testing Kafka connectivity...")
        
        try:
            # Test listing topics
            result = self.run_command([
                "docker", "exec", "kafka", 
                "/opt/kafka/bin/kafka-topics.sh", 
                "--bootstrap-server", "localhost:9092", 
                "--list"
            ])
            
            if result.returncode == 0:
                topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
                print(f"✅ Kafka connectivity confirmed, found {len(topics)} topics")
                if topics:
                    print(f"  Topics: {topics}")
                self.test_results["kafka_connectivity"] = True
            else:
                print(f"❌ Kafka connectivity failed: {result.stderr}")
                self.test_results["kafka_connectivity"] = False
                
        except Exception as e:
            print(f"❌ Kafka connectivity test failed: {e}")
            self.test_results["kafka_connectivity"] = False
    
    def test_kafka_connect_api(self):
        """Test Kafka Connect REST API"""
        print("\n🧪 Testing Kafka Connect REST API...")
        
        try:
            import requests
            
            # Test Kafka Connect health
            response = requests.get("http://localhost:28083/", timeout=10)
            
            if response.status_code == 200:
                print("✅ Kafka Connect REST API is accessible")
                
                # Test listing connector plugins
                plugins_response = requests.get("http://localhost:28083/connector-plugins", timeout=10)
                if plugins_response.status_code == 200:
                    plugins = plugins_response.json()
                    print(f"✅ Found {len(plugins)} connector plugins")
                    self.test_results["kafka_connect_api"] = True
                else:
                    print(f"❌ Failed to list connector plugins: {plugins_response.status_code}")
                    self.test_results["kafka_connect_api"] = False
            else:
                print(f"❌ Kafka Connect API not accessible: {response.status_code}")
                self.test_results["kafka_connect_api"] = False
                
        except ImportError:
            print("⚠️  requests library not available, skipping Kafka Connect API test")
            self.test_results["kafka_connect_api"] = None
        except Exception as e:
            print(f"❌ Kafka Connect API test failed: {e}")
            self.test_results["kafka_connect_api"] = False
    
    def test_smm_ui_accessibility(self):
        """Test SMM UI accessibility"""
        print("\n🧪 Testing SMM UI accessibility...")
        
        try:
            import requests
            
            # Test SMM UI
            response = requests.get("http://localhost:9991/", timeout=10)
            
            if response.status_code == 200:
                print("✅ SMM UI is accessible")
                self.test_results["smm_ui"] = True
            else:
                print(f"❌ SMM UI not accessible: {response.status_code}")
                self.test_results["smm_ui"] = False
                
        except ImportError:
            print("⚠️  requests library not available, skipping SMM UI test")
            self.test_results["smm_ui"] = None
        except Exception as e:
            print(f"❌ SMM UI test failed: {e}")
            self.test_results["smm_ui"] = False
    
    async def test_mcp_server_integration(self):
        """Test MCP server integration with Docker services"""
        print("\n🧪 Testing MCP server integration...")
        
        try:
            # Set environment variables
            os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"
            
            # Initialize MCP server
            mcp_server = CDFKafkaMCPServer()
            
            # Test listing topics
            result = await mcp_server.call_tool("list_topics", {})
            
            if result and "topics" in result:
                topics = result["topics"]
                print(f"✅ MCP server integration successful, found {len(topics)} topics")
                self.test_results["mcp_server_integration"] = True
            else:
                print(f"❌ MCP server integration failed: {result}")
                self.test_results["mcp_server_integration"] = False
                
        except Exception as e:
            print(f"❌ MCP server integration test failed: {e}")
            self.test_results["mcp_server_integration"] = False
    
    def test_health_checks(self):
        """Test health checks for all services"""
        print("\n🧪 Testing service health checks...")
        
        health_checks = {
            "kafka": "docker exec kafka ps aux | grep -v grep | grep -q Kafka",
            "zookeeper": "docker exec zookeeper ps aux | grep -v grep | grep -q QuorumPeerMain",
            "kafka-connect": "curl -f http://localhost:28083/",
            "schema-registry": "curl -f http://localhost:7788/api/v1/schemaregistry/schemas",
            "smm": "curl -f http://localhost:9991/"
        }
        
        healthy_services = []
        for service, check in health_checks.items():
            try:
                if "curl" in check:
                    import requests
                    url = check.split()[-1]
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        healthy_services.append(service)
                        print(f"  ✅ {service} health check passed")
                    else:
                        print(f"  ❌ {service} health check failed: {response.status_code}")
                else:
                    result = self.run_command(check.split(), timeout=5)
                    if result.returncode == 0:
                        healthy_services.append(service)
                        print(f"  ✅ {service} health check passed")
                    else:
                        print(f"  ❌ {service} health check failed")
            except Exception as e:
                print(f"  ❌ {service} health check error: {e}")
        
        if len(healthy_services) == len(health_checks):
            print(f"✅ All {len(health_checks)} services are healthy")
            self.test_results["health_checks"] = True
        else:
            print(f"⚠️  {len(healthy_services)}/{len(health_checks)} services are healthy")
            self.test_results["health_checks"] = len(healthy_services) >= len(health_checks) // 2
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "="*60)
        print("📊 DOCKER DEPLOYMENT TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result is True)
        failed_tests = sum(1 for result in self.test_results.values() if result is False)
        skipped_tests = sum(1 for result in self.test_results.values() if result is None)
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Skipped: {skipped_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\n📋 Detailed Results:")
        for test_name, result in self.test_results.items():
            if result is True:
                status = "✅ PASS"
            elif result is False:
                status = "❌ FAIL"
            else:
                status = "⏭️  SKIP"
            print(f"  {test_name}: {status}")
        
        if failed_tests > 0:
            print(f"\n⚠️  {failed_tests} tests failed. Check the logs above for details.")
        else:
            print(f"\n🎉 All tests passed!")

async def main():
    """Main test runner"""
    print("🚀 Starting Docker Deployment Testing Suite")
    print("="*50)
    
    tester = DockerDeploymentTester()
    
    try:
        # Run all tests
        tester.test_docker_compose_services()
        tester.test_kafka_connectivity()
        tester.test_kafka_connect_api()
        tester.test_smm_ui_accessibility()
        await tester.test_mcp_server_integration()
        tester.test_health_checks()
        
    finally:
        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
