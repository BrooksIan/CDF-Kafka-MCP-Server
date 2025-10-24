#!/usr/bin/env python3
"""
CDP Service Discovery and Configuration Script
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

class CDPServiceDiscovery:
    """Discover and configure CDP services."""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.discovered_services = {}
        
        # Setup authentication
        self._setup_auth()
    
    def _setup_auth(self):
        """Setup authentication for CDP services."""
        import base64
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        self.session.headers.update({
            'Authorization': f'Basic {encoded_credentials}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'User-Agent': 'CDF-Kafka-MCP-Server/1.0'
        })
        
        # Disable SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        self.session.verify = False
    
    def discover_services(self) -> Dict[str, Any]:
        """Discover all available CDP services."""
        print("🔍 Discovering CDP Services...")
        print("=" * 60)
        
        # Test base connectivity
        base_status = self._test_endpoint(self.base_url, "Base URL")
        
        # Discover various service paths
        service_paths = [
            # CDP Proxy API paths
            "/irb-kakfa-only/cdp-proxy-api",
            "/irb-kakfa-only/cdp-proxy",
            "/irb-kakfa-only/cdp-proxy-token",
            
            # Kafka service paths
            "/irb-kakfa-only/kafka",
            "/irb-kakfa-only/kafka-rest",
            "/irb-kakfa-only/kafka-connect",
            "/irb-kakfa-only/kafka-topics",
            
            # Knox Gateway paths
            "/irb-kakfa-only/knox",
            "/irb-kakfa-only/gateway",
            "/irb-kakfa-only/knox-gateway",
            
            # SMM paths
            "/irb-kakfa-only/smm",
            "/irb-kakfa-only/smm-api",
            "/irb-kakfa-only/streams-messaging-manager",
            
            # Admin paths
            "/irb-kakfa-only/admin",
            "/irb-kakfa-only/api",
            "/irb-kakfa-only/management",
            
            # Health and info paths
            "/irb-kakfa-only/health",
            "/irb-kakfa-only/info",
            "/irb-kakfa-only/status",
            
            # Root paths
            "/",
            "/api",
            "/health",
            "/info",
            "/status"
        ]
        
        discovered = {}
        for path in service_paths:
            full_url = urljoin(self.base_url, path)
            status = self._test_endpoint(full_url, path)
            if status['available']:
                discovered[path] = status
        
        self.discovered_services = discovered
        return discovered
    
    def _test_endpoint(self, url: str, name: str) -> Dict[str, Any]:
        """Test a specific endpoint."""
        try:
            response = self.session.get(url, timeout=10)
            
            # Determine if this is a useful endpoint
            content_type = response.headers.get('content-type', '').lower()
            is_json = 'json' in content_type
            is_html = 'html' in content_type
            is_text = 'text' in content_type
            
            # Check for specific indicators
            is_kafka_rest = 'kafka' in url.lower() and (response.status_code == 200 or 'kafka' in response.text.lower())
            is_connect_api = 'connect' in url.lower() and (response.status_code == 200 or 'connect' in response.text.lower())
            is_admin_api = 'admin' in url.lower() and (response.status_code == 200 or 'admin' in response.text.lower())
            
            return {
                'url': url,
                'name': name,
                'status_code': response.status_code,
                'available': response.status_code in [200, 401, 403],  # 401/403 means endpoint exists but needs auth
                'content_type': content_type,
                'is_json': is_json,
                'is_html': is_html,
                'is_text': is_text,
                'is_kafka_rest': is_kafka_rest,
                'is_connect_api': is_connect_api,
                'is_admin_api': is_admin_api,
                'response_size': len(response.text),
                'response_preview': response.text[:200] if response.text else '',
                'headers': dict(response.headers)
            }
        except Exception as e:
            return {
                'url': url,
                'name': name,
                'status_code': 'error',
                'available': False,
                'error': str(e),
                'content_type': '',
                'is_json': False,
                'is_html': False,
                'is_text': False,
                'is_kafka_rest': False,
                'is_connect_api': False,
                'is_admin_api': False,
                'response_size': 0,
                'response_preview': '',
                'headers': {}
            }
    
    def discover_kafka_services(self) -> Dict[str, Any]:
        """Discover Kafka-specific services."""
        print("\n🔍 Discovering Kafka Services...")
        print("=" * 40)
        
        kafka_services = {}
        
        # Test common Kafka REST API patterns
        kafka_patterns = [
            "/irb-kakfa-only/cdp-proxy-api/kafka-rest",
            "/irb-kakfa-only/cdp-proxy/kafka-rest",
            "/irb-kakfa-only/kafka-rest",
            "/irb-kakfa-only/kafka/rest",
            "/irb-kakfa-only/rest",
            "/kafka-rest",
            "/rest"
        ]
        
        for pattern in kafka_patterns:
            full_url = urljoin(self.base_url, pattern)
            status = self._test_endpoint(full_url, f"Kafka REST: {pattern}")
            if status['available']:
                kafka_services[f"kafka_rest_{pattern.replace('/', '_')}"] = status
        
        # Test Kafka Connect patterns
        connect_patterns = [
            "/irb-kakfa-only/cdp-proxy-api/kafka-connect",
            "/irb-kakfa-only/cdp-proxy/kafka-connect",
            "/irb-kakfa-only/kafka-connect",
            "/irb-kakfa-only/kafka/connect",
            "/kafka-connect",
            "/connect"
        ]
        
        for pattern in connect_patterns:
            full_url = urljoin(self.base_url, pattern)
            status = self._test_endpoint(full_url, f"Kafka Connect: {pattern}")
            if status['available']:
                kafka_services[f"kafka_connect_{pattern.replace('/', '_')}"] = status
        
        return kafka_services
    
    def discover_knox_services(self) -> Dict[str, Any]:
        """Discover Knox Gateway services."""
        print("\n🔍 Discovering Knox Gateway Services...")
        print("=" * 40)
        
        knox_services = {}
        
        # Test Knox Gateway patterns
        knox_patterns = [
            "/irb-kakfa-only/cdp-proxy-token",
            "/irb-kakfa-only/knox-gateway",
            "/irb-kakfa-only/knox",
            "/irb-kakfa-only/gateway",
            "/knox-gateway",
            "/knox",
            "/gateway"
        ]
        
        for pattern in knox_patterns:
            full_url = urljoin(self.base_url, pattern)
            status = self._test_endpoint(full_url, f"Knox: {pattern}")
            if status['available']:
                knox_services[f"knox_{pattern.replace('/', '_')}"] = status
        
        return knox_services
    
    def discover_admin_services(self) -> Dict[str, Any]:
        """Discover Admin/Management services."""
        print("\n🔍 Discovering Admin Services...")
        print("=" * 40)
        
        admin_services = {}
        
        # Test Admin API patterns
        admin_patterns = [
            "/irb-kakfa-only/cdp-proxy-api",
            "/irb-kakfa-only/admin",
            "/irb-kakfa-only/api",
            "/irb-kakfa-only/management",
            "/admin",
            "/api",
            "/management"
        ]
        
        for pattern in admin_patterns:
            full_url = urljoin(self.base_url, pattern)
            status = self._test_endpoint(full_url, f"Admin: {pattern}")
            if status['available']:
                admin_services[f"admin_{pattern.replace('/', '_')}"] = status
        
        return admin_services
    
    def generate_configuration(self) -> Dict[str, Any]:
        """Generate configuration based on discovered services."""
        print("\n⚙️ Generating Configuration...")
        print("=" * 40)
        
        config = {
            'base_url': self.base_url,
            'username': self.username,
            'password': '***',  # Hide password in output
            'discovered_services': self.discovered_services,
            'recommended_endpoints': {},
            'configuration_template': {}
        }
        
        # Find best endpoints for each service type
        kafka_rest_candidates = []
        kafka_connect_candidates = []
        knox_candidates = []
        admin_candidates = []
        
        for service_name, service_info in self.discovered_services.items():
            if service_info.get('is_kafka_rest') or 'kafka-rest' in service_name:
                kafka_rest_candidates.append((service_name, service_info))
            elif service_info.get('is_connect_api') or 'connect' in service_name:
                kafka_connect_candidates.append((service_name, service_info))
            elif 'knox' in service_name or 'gateway' in service_name:
                knox_candidates.append((service_name, service_info))
            elif 'admin' in service_name or 'api' in service_name:
                admin_candidates.append((service_name, service_info))
        
        # Select best candidates
        if kafka_rest_candidates:
            best_kafka_rest = max(kafka_rest_candidates, key=lambda x: x[1]['status_code'] if isinstance(x[1]['status_code'], int) else 0)
            config['recommended_endpoints']['kafka_rest'] = best_kafka_rest[1]['url']
        
        if kafka_connect_candidates:
            best_kafka_connect = max(kafka_connect_candidates, key=lambda x: x[1]['status_code'] if isinstance(x[1]['status_code'], int) else 0)
            config['recommended_endpoints']['kafka_connect'] = best_kafka_connect[1]['url']
        
        if knox_candidates:
            best_knox = max(knox_candidates, key=lambda x: x[1]['status_code'] if isinstance(x[1]['status_code'], int) else 0)
            config['recommended_endpoints']['knox_gateway'] = best_knox[1]['url']
        
        if admin_candidates:
            best_admin = max(admin_candidates, key=lambda x: x[1]['status_code'] if isinstance(x[1]['status_code'], int) else 0)
            config['recommended_endpoints']['admin_api'] = best_admin[1]['url']
        
        # Generate configuration template
        config['configuration_template'] = {
            'kafka': {
                'bootstrap_servers': [f"{self.base_url.split('://')[1]}"],
                'security_protocol': 'SASL_SSL',
                'sasl_mechanism': 'PLAIN',
                'sasl_username': self.username,
                'sasl_password': self.password,
                'verify_ssl': False
            },
            'cdp_rest': {
                'base_url': self.base_url,
                'username': self.username,
                'password': self.password,
                'endpoints': {
                    'kafka_rest': config['recommended_endpoints'].get('kafka_rest', ''),
                    'kafka_connect': config['recommended_endpoints'].get('kafka_connect', ''),
                    'knox_gateway': config['recommended_endpoints'].get('knox_gateway', ''),
                    'admin_api': config['recommended_endpoints'].get('admin_api', '')
                }
            }
        }
        
        return config
    
    def print_discovery_report(self):
        """Print comprehensive discovery report."""
        print("\n" + "=" * 80)
        print("📊 CDP SERVICE DISCOVERY REPORT")
        print("=" * 80)
        
        # Summary
        total_services = len(self.discovered_services)
        available_services = sum(1 for s in self.discovered_services.values() if s['available'])
        
        print(f"Total Services Tested: {total_services}")
        print(f"Available Services: {available_services}")
        print(f"Success Rate: {(available_services/total_services*100):.1f}%")
        
        # Available services
        print(f"\n✅ Available Services ({available_services}):")
        for service_name, service_info in self.discovered_services.items():
            if service_info['available']:
                status = service_info['status_code']
                content_type = service_info['content_type']
                print(f"  {service_name}: {status} ({content_type})")
        
        # Unavailable services
        print(f"\n❌ Unavailable Services ({total_services - available_services}):")
        for service_name, service_info in self.discovered_services.items():
            if not service_info['available']:
                error = service_info.get('error', f"Status {service_info['status_code']}")
                print(f"  {service_name}: {error}")
        
        # Recommendations
        print(f"\n🔧 Recommendations:")
        if available_services == 0:
            print("  - Check base URL and authentication credentials")
            print("  - Verify CDP services are running")
            print("  - Check network connectivity")
        else:
            print("  - Use discovered working endpoints")
            print("  - Configure MCP server with recommended endpoints")
            print("  - Test each service individually")

def main():
    """Main function to run CDP service discovery."""
    # Configuration
    base_url = os.getenv("CDP_REST_BASE_URL", "https://your-cdp-cluster.example.com:443")
    username = os.getenv("CDP_REST_USERNAME", "your-username")
    password = os.getenv("CDP_REST_PASSWORD", "your-password")
    
    print("🚀 CDP Service Discovery and Configuration")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Username: {username}")
    print("=" * 60)
    
    # Initialize discovery
    discovery = CDPServiceDiscovery(base_url, username, password)
    
    # Discover services
    discovered = discovery.discover_services()
    
    # Discover specific service types
    kafka_services = discovery.discover_kafka_services()
    knox_services = discovery.discover_knox_services()
    admin_services = discovery.discover_admin_services()
    
    # Generate configuration
    config = discovery.generate_configuration()
    
    # Print report
    discovery.print_discovery_report()
    
    # Save configuration
    config_file = "cdp_discovered_config.json"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Configuration saved to: {config_file}")
    
    # Print recommended configuration
    print(f"\n⚙️ Recommended Configuration:")
    print(json.dumps(config['configuration_template'], indent=2))

if __name__ == "__main__":
    main()
