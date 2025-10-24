#!/usr/bin/env python3
"""
Comprehensive CDP Service Discovery Script
"""

import requests
import json
import time
import sys
import os
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin

class ComprehensiveCDPDiscovery:
    """Comprehensive CDP service discovery."""
    
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
    
    def discover_all_services(self) -> Dict[str, Any]:
        """Discover all possible CDP services."""
        print("🔍 Comprehensive CDP Service Discovery...")
        print("=" * 60)
        
        all_services = {}
        
        # Test comprehensive service patterns
        service_patterns = [
            # Base CDP patterns
            ("/", "Root"),
            ("/api", "API Root"),
            ("/health", "Health Check"),
            ("/info", "Info"),
            ("/status", "Status"),
            
            # CDP Proxy patterns
            ("/irb-kakfa-only", "CDP Base"),
            ("/irb-kakfa-only/", "CDP Base with slash"),
            ("/irb-kakfa-only/cdp-proxy", "CDP Proxy"),
            ("/irb-kakfa-only/cdp-proxy/", "CDP Proxy with slash"),
            ("/irb-kakfa-only/cdp-proxy-api", "CDP Proxy API"),
            ("/irb-kakfa-only/cdp-proxy-api/", "CDP Proxy API with slash"),
            ("/irb-kakfa-only/cdp-proxy-token", "CDP Proxy Token"),
            ("/irb-kakfa-only/cdp-proxy-token/", "CDP Proxy Token with slash"),
            
            # Kafka REST API patterns
            ("/irb-kakfa-only/cdp-proxy-api/kafka-rest", "Kafka REST via CDP Proxy API"),
            ("/irb-kakfa-only/cdp-proxy/kafka-rest", "Kafka REST via CDP Proxy"),
            ("/irb-kakfa-only/kafka-rest", "Kafka REST Direct"),
            ("/irb-kakfa-only/kafka/rest", "Kafka REST Alternative"),
            ("/irb-kakfa-only/rest", "REST Short"),
            ("/kafka-rest", "Kafka REST Root"),
            ("/rest", "REST Root"),
            
            # Kafka Connect patterns
            ("/irb-kakfa-only/cdp-proxy-api/kafka-connect", "Kafka Connect via CDP Proxy API"),
            ("/irb-kakfa-only/cdp-proxy/kafka-connect", "Kafka Connect via CDP Proxy"),
            ("/irb-kakfa-only/kafka-connect", "Kafka Connect Direct"),
            ("/irb-kakfa-only/kafka/connect", "Kafka Connect Alternative"),
            ("/irb-kakfa-only/connect", "Connect Short"),
            ("/kafka-connect", "Kafka Connect Root"),
            ("/connect", "Connect Root"),
            
            # Kafka Topics patterns
            ("/irb-kakfa-only/cdp-proxy-api/kafka-topics", "Kafka Topics via CDP Proxy API"),
            ("/irb-kakfa-only/cdp-proxy/kafka-topics", "Kafka Topics via CDP Proxy"),
            ("/irb-kakfa-only/kafka-topics", "Kafka Topics Direct"),
            ("/irb-kakfa-only/kafka/topics", "Kafka Topics Alternative"),
            ("/irb-kakfa-only/topics", "Topics Short"),
            ("/kafka-topics", "Kafka Topics Root"),
            ("/topics", "Topics Root"),
            
            # Knox Gateway patterns
            ("/irb-kakfa-only/knox-gateway", "Knox Gateway"),
            ("/irb-kakfa-only/knox", "Knox"),
            ("/irb-kakfa-only/gateway", "Gateway"),
            ("/irb-kakfa-only/cdp-proxy-token/knox", "Knox via CDP Proxy Token"),
            ("/irb-kakfa-only/cdp-proxy-token/gateway", "Gateway via CDP Proxy Token"),
            ("/knox-gateway", "Knox Gateway Root"),
            ("/knox", "Knox Root"),
            ("/gateway", "Gateway Root"),
            
            # SMM patterns
            ("/irb-kakfa-only/smm", "SMM"),
            ("/irb-kakfa-only/smm-api", "SMM API"),
            ("/irb-kakfa-only/streams-messaging-manager", "SMM Full"),
            ("/irb-kakfa-only/cdp-proxy-api/smm", "SMM via CDP Proxy API"),
            ("/irb-kakfa-only/cdp-proxy/smm", "SMM via CDP Proxy"),
            ("/smm", "SMM Root"),
            ("/smm-api", "SMM API Root"),
            
            # Admin patterns
            ("/irb-kakfa-only/admin", "Admin"),
            ("/irb-kakfa-only/api", "API"),
            ("/irb-kakfa-only/management", "Management"),
            ("/irb-kakfa-only/cdp-proxy-api/admin", "Admin via CDP Proxy API"),
            ("/irb-kakfa-only/cdp-proxy/admin", "Admin via CDP Proxy"),
            ("/admin", "Admin Root"),
            ("/api", "API Root"),
            ("/management", "Management Root"),
            
            # CDP specific patterns
            ("/irb-kakfa-only/cdp", "CDP"),
            ("/irb-kakfa-only/cdp-api", "CDP API"),
            ("/irb-kakfa-only/cdp-management", "CDP Management"),
            ("/cdp", "CDP Root"),
            ("/cdp-api", "CDP API Root"),
            
            # Cloudera patterns
            ("/irb-kakfa-only/cloudera", "Cloudera"),
            ("/irb-kakfa-only/cloudera-api", "Cloudera API"),
            ("/cloudera", "Cloudera Root"),
            ("/cloudera-api", "Cloudera API Root"),
            
            # DataHub patterns
            ("/irb-kakfa-only/datahub", "DataHub"),
            ("/irb-kakfa-only/datahub-api", "DataHub API"),
            ("/datahub", "DataHub Root"),
            ("/datahub-api", "DataHub API Root"),
            
            # Additional patterns
            ("/irb-kakfa-only/services", "Services"),
            ("/irb-kakfa-only/endpoints", "Endpoints"),
            ("/irb-kakfa-only/apis", "APIs"),
            ("/services", "Services Root"),
            ("/endpoints", "Endpoints Root"),
            ("/apis", "APIs Root")
        ]
        
        for path, description in service_patterns:
            full_url = urljoin(self.base_url, path)
            status = self._test_endpoint(full_url, description)
            all_services[path] = status
            
            # Print interesting results immediately
            if status['available'] and status['status_code'] in [200, 401, 403]:
                print(f"✅ {description}: {status['status_code']} ({status['content_type']})")
                if status['response_preview']:
                    print(f"   Preview: {status['response_preview'][:100]}...")
        
        self.discovered_services = all_services
        return all_services
    
    def _test_endpoint(self, url: str, description: str) -> Dict[str, Any]:
        """Test a specific endpoint with detailed analysis."""
        try:
            response = self.session.get(url, timeout=10)
            
            # Analyze response
            content_type = response.headers.get('content-type', '').lower()
            is_json = 'json' in content_type
            is_html = 'html' in content_type
            is_text = 'text' in content_type
            is_xml = 'xml' in content_type
            
            # Check for specific service indicators
            response_text = response.text.lower() if response.text else ''
            is_kafka_related = any(keyword in response_text for keyword in ['kafka', 'broker', 'topic', 'partition'])
            is_connect_related = any(keyword in response_text for keyword in ['connect', 'connector', 'plugin'])
            is_knox_related = any(keyword in response_text for keyword in ['knox', 'gateway', 'token', 'auth'])
            is_admin_related = any(keyword in response_text for keyword in ['admin', 'management', 'api', 'service'])
            is_cdp_related = any(keyword in response_text for keyword in ['cdp', 'cloudera', 'data platform'])
            
            # Determine if this is a useful endpoint
            is_useful = (
                response.status_code in [200, 401, 403] and
                (is_json or is_kafka_related or is_connect_related or is_knox_related or is_admin_related or is_cdp_related)
            )
            
            return {
                'url': url,
                'description': description,
                'status_code': response.status_code,
                'available': is_useful,
                'content_type': content_type,
                'is_json': is_json,
                'is_html': is_html,
                'is_text': is_text,
                'is_xml': is_xml,
                'is_kafka_related': is_kafka_related,
                'is_connect_related': is_connect_related,
                'is_knox_related': is_knox_related,
                'is_admin_related': is_admin_related,
                'is_cdp_related': is_cdp_related,
                'response_size': len(response.text),
                'response_preview': response.text[:300] if response.text else '',
                'headers': dict(response.headers),
                'cookies': dict(response.cookies) if response.cookies else {}
            }
        except Exception as e:
            return {
                'url': url,
                'description': description,
                'status_code': 'error',
                'available': False,
                'error': str(e),
                'content_type': '',
                'is_json': False,
                'is_html': False,
                'is_text': False,
                'is_xml': False,
                'is_kafka_related': False,
                'is_connect_related': False,
                'is_knox_related': False,
                'is_admin_related': False,
                'is_cdp_related': False,
                'response_size': 0,
                'response_preview': '',
                'headers': {},
                'cookies': {}
            }
    
    def analyze_discovered_services(self) -> Dict[str, Any]:
        """Analyze discovered services and categorize them."""
        print("\n📊 Analyzing Discovered Services...")
        print("=" * 50)
        
        analysis = {
            'total_tested': len(self.discovered_services),
            'available_services': 0,
            'kafka_services': [],
            'connect_services': [],
            'knox_services': [],
            'admin_services': [],
            'cdp_services': [],
            'other_services': [],
            'error_services': []
        }
        
        for path, service_info in self.discovered_services.items():
            if service_info['available']:
                analysis['available_services'] += 1
                
                # Categorize services
                if service_info.get('is_kafka_related') or 'kafka' in path.lower():
                    analysis['kafka_services'].append((path, service_info))
                elif service_info.get('is_connect_related') or 'connect' in path.lower():
                    analysis['connect_services'].append((path, service_info))
                elif service_info.get('is_knox_related') or 'knox' in path.lower() or 'gateway' in path.lower():
                    analysis['knox_services'].append((path, service_info))
                elif service_info.get('is_admin_related') or 'admin' in path.lower() or 'api' in path.lower():
                    analysis['admin_services'].append((path, service_info))
                elif service_info.get('is_cdp_related') or 'cdp' in path.lower():
                    analysis['cdp_services'].append((path, service_info))
                else:
                    analysis['other_services'].append((path, service_info))
            else:
                if service_info.get('error'):
                    analysis['error_services'].append((path, service_info))
        
        return analysis
    
    def generate_optimal_configuration(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimal configuration based on analysis."""
        print("\n⚙️ Generating Optimal Configuration...")
        print("=" * 50)
        
        config = {
            'base_url': self.base_url,
            'username': self.username,
            'password': '***',  # Hide password
            'recommended_endpoints': {},
            'configuration_files': {}
        }
        
        # Select best endpoints for each service type
        def select_best_endpoint(services: List[tuple], service_type: str) -> Optional[str]:
            if not services:
                return None
            
            # Sort by status code (200 > 401 > 403 > others)
            def sort_key(item):
                status = item[1]['status_code']
                if isinstance(status, int):
                    return (0 if status == 200 else 1 if status == 401 else 2 if status == 403 else 3, -item[1]['response_size'])
                return (4, 0)
            
            services.sort(key=sort_key)
            return services[0][1]['url']
        
        # Select best endpoints
        config['recommended_endpoints']['kafka_rest'] = select_best_endpoint(analysis['kafka_services'], 'kafka_rest')
        config['recommended_endpoints']['kafka_connect'] = select_best_endpoint(analysis['connect_services'], 'kafka_connect')
        config['recommended_endpoints']['knox_gateway'] = select_best_endpoint(analysis['knox_services'], 'knox_gateway')
        config['recommended_endpoints']['admin_api'] = select_best_endpoint(analysis['admin_services'], 'admin_api')
        config['recommended_endpoints']['cdp_api'] = select_best_endpoint(analysis['cdp_services'], 'cdp_api')
        
        # Generate configuration files
        config['configuration_files']['kafka_config_cdp_rest.yaml'] = {
            'kafka': {
                'bootstrap_servers': [f"{self.base_url.split('://')[1]}"],
                'security_protocol': 'SASL_SSL',
                'sasl_mechanism': 'PLAIN',
                'sasl_username': self.username,
                'sasl_password': self.password,
                'verify_ssl': False,
                'cluster_id': 'irb-kakfa-only'
            },
            'cdp_rest': {
                'base_url': self.base_url,
                'username': self.username,
                'password': self.password,
                'cluster_id': 'irb-kakfa-only',
                'endpoints': {
                    'kafka_rest': config['recommended_endpoints']['kafka_rest'] or '',
                    'kafka_connect': config['recommended_endpoints']['kafka_connect'] or '',
                    'kafka_topics': config['recommended_endpoints']['kafka_rest'] or '',
                    'smm_api': config['recommended_endpoints']['admin_api'] or '',
                    'cdp_api': config['recommended_endpoints']['cdp_api'] or ''
                }
            },
            'knox': {
                'gateway': config['recommended_endpoints']['knox_gateway'] or '',
                'username': self.username,
                'password': self.password,
                'verify_ssl': False
            },
            'cdp': {
                'url': self.base_url,
                'username': self.username,
                'password': self.password,
                'cluster_id': 'irb-kakfa-only'
            }
        }
        
        return config
    
    def print_comprehensive_report(self, analysis: Dict[str, Any]):
        """Print comprehensive discovery report."""
        print("\n" + "=" * 80)
        print("📊 COMPREHENSIVE CDP SERVICE DISCOVERY REPORT")
        print("=" * 80)
        
        # Summary
        print(f"Total Services Tested: {analysis['total_tested']}")
        print(f"Available Services: {analysis['available_services']}")
        print(f"Success Rate: {(analysis['available_services']/analysis['total_tested']*100):.1f}%")
        
        # Service categories
        print(f"\n📋 Service Categories:")
        print(f"  Kafka Services: {len(analysis['kafka_services'])}")
        print(f"  Connect Services: {len(analysis['connect_services'])}")
        print(f"  Knox Services: {len(analysis['knox_services'])}")
        print(f"  Admin Services: {len(analysis['admin_services'])}")
        print(f"  CDP Services: {len(analysis['cdp_services'])}")
        print(f"  Other Services: {len(analysis['other_services'])}")
        print(f"  Error Services: {len(analysis['error_services'])}")
        
        # Detailed results by category
        for category, services in [
            ("Kafka Services", analysis['kafka_services']),
            ("Connect Services", analysis['connect_services']),
            ("Knox Services", analysis['knox_services']),
            ("Admin Services", analysis['admin_services']),
            ("CDP Services", analysis['cdp_services']),
            ("Other Services", analysis['other_services'])
        ]:
            if services:
                print(f"\n✅ {category}:")
                for path, service_info in services:
                    status = service_info['status_code']
                    content_type = service_info['content_type']
                    print(f"  {path}: {status} ({content_type})")
                    if service_info['response_preview']:
                        print(f"    Preview: {service_info['response_preview'][:100]}...")
        
        # Error services
        if analysis['error_services']:
            print(f"\n❌ Error Services:")
            for path, service_info in analysis['error_services']:
                error = service_info.get('error', f"Status {service_info['status_code']}")
                print(f"  {path}: {error}")

def main():
    """Main function to run comprehensive CDP discovery."""
    # Configuration
    base_url = "https://irb-kakfa-only-master0.cgsi-dem.prep-j1tk.a3.cloudera.site:443"
    username = "ibrooks"
    password = "Admin12345#"
    
    print("🚀 Comprehensive CDP Service Discovery")
    print("=" * 60)
    print(f"Base URL: {base_url}")
    print(f"Username: {username}")
    print("=" * 60)
    
    # Initialize discovery
    discovery = ComprehensiveCDPDiscovery(base_url, username, password)
    
    # Discover all services
    discovered = discovery.discover_all_services()
    
    # Analyze discovered services
    analysis = discovery.analyze_discovered_services()
    
    # Generate optimal configuration
    config = discovery.generate_optimal_configuration(analysis)
    
    # Print comprehensive report
    discovery.print_comprehensive_report(analysis)
    
    # Save results
    results_file = "comprehensive_cdp_discovery_results.json"
    with open(results_file, 'w') as f:
        json.dump({
            'discovered_services': discovered,
            'analysis': analysis,
            'configuration': config
        }, f, indent=2)
    
    print(f"\n💾 Complete results saved to: {results_file}")
    
    # Print recommended configuration
    print(f"\n⚙️ Recommended Configuration:")
    print(json.dumps(config['configuration_files']['kafka_config_cdp_rest.yaml'], indent=2))

if __name__ == "__main__":
    main()
