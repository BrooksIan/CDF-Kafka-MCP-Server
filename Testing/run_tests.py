#!/usr/bin/env python3
"""
Main Test Runner for CDF Kafka MCP Server Testing Suite
Runs all test suites and provides comprehensive reporting
"""

import asyncio
import json
import os
import sys
import time
from typing import Dict, List, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import test modules
from test_mcp_tools import MCPToolsTester
from test_docker_deployment import DockerDeploymentTester
from test_knox_integration import KnoxIntegrationTester

class ComprehensiveTester:
    def __init__(self):
        self.all_results = {}
        self.start_time = None
        self.end_time = None
        
    async def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Starting Comprehensive CDF Kafka MCP Server Testing")
        print("="*60)
        
        self.start_time = time.time()
        
        # Test Suite 1: MCP Tools Testing
        print("\n" + "="*60)
        print("🧪 TEST SUITE 1: MCP TOOLS TESTING")
        print("="*60)
        
        mcp_tester = MCPToolsTester()
        if await mcp_tester.setup():
            await mcp_tester.test_tool_registration()
            await mcp_tester.test_list_topics_tool()
            await mcp_tester.test_create_topic_tool()
            await mcp_tester.test_produce_message_tool()
            await mcp_tester.test_consume_messages_tool()
            await mcp_tester.test_kafka_connect_tools()
            await mcp_tester.test_knox_tools()
            await mcp_tester.cleanup()
            mcp_tester.print_summary()
            self.all_results["mcp_tools"] = mcp_tester.test_results
        
        # Test Suite 2: Docker Deployment Testing
        print("\n" + "="*60)
        print("🧪 TEST SUITE 2: DOCKER DEPLOYMENT TESTING")
        print("="*60)
        
        docker_tester = DockerDeploymentTester()
        docker_tester.test_docker_compose_services()
        docker_tester.test_kafka_connectivity()
        docker_tester.test_kafka_connect_api()
        docker_tester.test_smm_ui_accessibility()
        await docker_tester.test_mcp_server_integration()
        docker_tester.test_health_checks()
        docker_tester.print_summary()
        self.all_results["docker_deployment"] = docker_tester.test_results
        
        # Test Suite 3: Knox Integration Testing
        print("\n" + "="*60)
        print("🧪 TEST SUITE 3: KNOX INTEGRATION TESTING")
        print("="*60)
        
        knox_tester = KnoxIntegrationTester()
        if await knox_tester.setup():
            await knox_tester.test_knox_token_retrieval()
            await knox_tester.test_knox_token_validation()
            await knox_tester.test_knox_token_refresh()
            await knox_tester.test_knox_gateway_connectivity()
            await knox_tester.test_knox_authentication_flow()
            knox_tester.print_summary()
            self.all_results["knox_integration"] = knox_tester.test_results
        
        self.end_time = time.time()
    
    def print_comprehensive_summary(self):
        """Print comprehensive test results summary"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE TEST RESULTS SUMMARY")
        print("="*80)
        
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        
        for suite_name, suite_results in self.all_results.items():
            suite_total = len(suite_results)
            suite_passed = sum(1 for result in suite_results.values() if result is True)
            suite_failed = sum(1 for result in suite_results.values() if result is False)
            suite_skipped = sum(1 for result in suite_results.values() if result is None)
            
            total_tests += suite_total
            total_passed += suite_passed
            total_failed += suite_failed
            total_skipped += suite_skipped
            
            print(f"\n📋 {suite_name.upper().replace('_', ' ')}:")
            print(f"  Total: {suite_total}, Passed: {suite_passed}, Failed: {suite_failed}, Skipped: {suite_skipped}")
            print(f"  Success Rate: {(suite_passed/suite_total)*100:.1f}%")
        
        print(f"\n🎯 OVERALL SUMMARY:")
        print(f"  Total Tests: {total_tests}")
        print(f"  Passed: {total_passed}")
        print(f"  Failed: {total_failed}")
        print(f"  Skipped: {total_skipped}")
        print(f"  Overall Success Rate: {(total_passed/total_tests)*100:.1f}%")
        
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            print(f"  Total Duration: {duration:.2f} seconds")
        
        # Detailed results by suite
        print(f"\n📋 DETAILED RESULTS BY SUITE:")
        for suite_name, suite_results in self.all_results.items():
            print(f"\n  {suite_name.upper().replace('_', ' ')}:")
            for test_name, result in suite_results.items():
                if result is True:
                    status = "✅ PASS"
                elif result is False:
                    status = "❌ FAIL"
                else:
                    status = "⏭️  SKIP"
                print(f"    {test_name}: {status}")
        
        # Final assessment
        if total_failed == 0:
            print(f"\n🎉 ALL TESTS PASSED! The CDF Kafka MCP Server is fully functional.")
        elif total_failed <= total_tests * 0.2:  # Less than 20% failure rate
            print(f"\n⚠️  MOSTLY SUCCESSFUL: {total_failed} tests failed, but core functionality works.")
        else:
            print(f"\n❌ SIGNIFICANT ISSUES: {total_failed} tests failed. Review the logs above.")
    
    def save_results_to_file(self, filename: str = "test_results.json"):
        """Save test results to a JSON file"""
        try:
            results_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "duration": self.end_time - self.start_time if self.end_time and self.start_time else None,
                "results": self.all_results
            }
            
            with open(filename, 'w') as f:
                json.dump(results_data, f, indent=2)
            
            print(f"\n💾 Test results saved to {filename}")
        except Exception as e:
            print(f"\n⚠️  Failed to save results to file: {e}")

async def main():
    """Main test runner"""
    tester = ComprehensiveTester()
    
    try:
        await tester.run_all_tests()
    finally:
        tester.print_comprehensive_summary()
        tester.save_results_to_file()

if __name__ == "__main__":
    asyncio.run(main())
