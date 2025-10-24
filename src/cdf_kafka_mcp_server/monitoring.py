"""
Monitoring and Health Check Module

This module provides comprehensive monitoring and health check capabilities
for the CDF Kafka MCP Server, including Knox Gateway, CDP Cloud, and Kafka services.
"""

import time
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheck:
    """Health check result."""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    response_time_ms: Optional[float] = None
    details: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result['status'] = self.status.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


@dataclass
class ServiceHealth:
    """Service health information."""
    service_name: str
    overall_status: HealthStatus
    checks: List[HealthCheck]
    last_updated: datetime
    uptime_seconds: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'service_name': self.service_name,
            'overall_status': self.overall_status.value,
            'checks': [check.to_dict() for check in self.checks],
            'last_updated': self.last_updated.isoformat(),
            'uptime_seconds': self.uptime_seconds
        }


class HealthMonitor:
    """
    Health monitoring system for CDF Kafka MCP Server.
    
    Provides comprehensive health checks for:
    - Kafka cluster connectivity
    - Knox Gateway services
    - CDP Cloud services
    - MCP server operations
    """
    
    def __init__(self, kafka_client=None, knox_gateway_client=None, cdp_client=None):
        """
        Initialize health monitor.
        
        Args:
            kafka_client: Kafka client instance
            knox_gateway_client: Knox Gateway client instance
            cdp_client: CDP client instance
        """
        self.kafka_client = kafka_client
        self.knox_gateway_client = knox_gateway_client
        self.cdp_client = cdp_client
        self.start_time = datetime.now()
        self.health_history: List[ServiceHealth] = []
        
    def get_uptime(self) -> float:
        """Get server uptime in seconds."""
        return (datetime.now() - self.start_time).total_seconds()
    
    def check_kafka_health(self) -> HealthCheck:
        """Check Kafka cluster health."""
        start_time = time.time()
        
        try:
            if not self.kafka_client:
                return HealthCheck(
                    name="kafka_connectivity",
                    status=HealthStatus.UNHEALTHY,
                    message="Kafka client not available",
                    timestamp=datetime.now()
                )
            
            # Test basic connectivity
            topics = self.kafka_client.list_topics()
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="kafka_connectivity",
                status=HealthStatus.HEALTHY,
                message=f"Successfully connected to Kafka cluster, found {len(topics)} topics",
                timestamp=datetime.now(),
                response_time_ms=response_time,
                details={"topic_count": len(topics), "topics": topics[:10]}  # Limit topics for brevity
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="kafka_connectivity",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to connect to Kafka: {e}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    def check_knox_health(self) -> HealthCheck:
        """Check Knox Gateway health."""
        start_time = time.time()
        
        try:
            if not self.knox_gateway_client:
                return HealthCheck(
                    name="knox_gateway",
                    status=HealthStatus.UNKNOWN,
                    message="Knox Gateway client not available",
                    timestamp=datetime.now()
                )
            
            # Test Knox Gateway connectivity
            gateway_info = self.knox_gateway_client.get_gateway_info()
            response_time = (time.time() - start_time) * 1000
            
            if gateway_info:
                return HealthCheck(
                    name="knox_gateway",
                    status=HealthStatus.HEALTHY,
                    message="Knox Gateway is accessible",
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    details=gateway_info
                )
            else:
                return HealthCheck(
                    name="knox_gateway",
                    status=HealthStatus.DEGRADED,
                    message="Knox Gateway is accessible but returned no info",
                    timestamp=datetime.now(),
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="knox_gateway",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to connect to Knox Gateway: {e}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    def check_cdp_health(self) -> HealthCheck:
        """Check CDP Cloud health."""
        start_time = time.time()
        
        try:
            if not self.cdp_client:
                return HealthCheck(
                    name="cdp_cloud",
                    status=HealthStatus.UNKNOWN,
                    message="CDP client not available",
                    timestamp=datetime.now()
                )
            
            # Test CDP Cloud connectivity
            connected = self.cdp_client.test_connection()
            response_time = (time.time() - start_time) * 1000
            
            if connected:
                apis = self.cdp_client.get_available_apis()
                return HealthCheck(
                    name="cdp_cloud",
                    status=HealthStatus.HEALTHY,
                    message="CDP Cloud is accessible",
                    timestamp=datetime.now(),
                    response_time_ms=response_time,
                    details={"apis": apis}
                )
            else:
                return HealthCheck(
                    name="cdp_cloud",
                    status=HealthStatus.UNHEALTHY,
                    message="CDP Cloud is not accessible",
                    timestamp=datetime.now(),
                    response_time_ms=response_time
                )
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="cdp_cloud",
                status=HealthStatus.UNHEALTHY,
                message=f"Failed to connect to CDP Cloud: {e}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    def check_mcp_server_health(self) -> HealthCheck:
        """Check MCP server health."""
        start_time = time.time()
        
        try:
            # Basic server health checks
            uptime = self.get_uptime()
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="mcp_server",
                status=HealthStatus.HEALTHY,
                message=f"MCP server is running (uptime: {uptime:.1f}s)",
                timestamp=datetime.now(),
                response_time_ms=response_time,
                details={"uptime_seconds": uptime}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="mcp_server",
                status=HealthStatus.UNHEALTHY,
                message=f"MCP server health check failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    def check_topic_operations(self) -> HealthCheck:
        """Check topic operations health."""
        start_time = time.time()
        
        try:
            if not self.kafka_client:
                return HealthCheck(
                    name="topic_operations",
                    status=HealthStatus.UNHEALTHY,
                    message="Kafka client not available for topic operations",
                    timestamp=datetime.now()
                )
            
            # Test topic listing
            topics = self.kafka_client.list_topics()
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="topic_operations",
                status=HealthStatus.HEALTHY,
                message=f"Topic operations working, found {len(topics)} topics",
                timestamp=datetime.now(),
                response_time_ms=response_time,
                details={"topic_count": len(topics)}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="topic_operations",
                status=HealthStatus.UNHEALTHY,
                message=f"Topic operations failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    def check_connect_operations(self) -> HealthCheck:
        """Check Kafka Connect operations health."""
        start_time = time.time()
        
        try:
            if not self.kafka_client:
                return HealthCheck(
                    name="connect_operations",
                    status=HealthStatus.UNHEALTHY,
                    message="Kafka client not available for Connect operations",
                    timestamp=datetime.now()
                )
            
            # Test connector listing
            connectors = self.kafka_client.list_connectors()
            response_time = (time.time() - start_time) * 1000
            
            return HealthCheck(
                name="connect_operations",
                status=HealthStatus.HEALTHY,
                message=f"Connect operations working, found {len(connectors)} connectors",
                timestamp=datetime.now(),
                response_time_ms=response_time,
                details={"connector_count": len(connectors), "connectors": connectors}
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return HealthCheck(
                name="connect_operations",
                status=HealthStatus.UNHEALTHY,
                message=f"Connect operations failed: {e}",
                timestamp=datetime.now(),
                response_time_ms=response_time
            )
    
    def run_all_health_checks(self) -> ServiceHealth:
        """Run all health checks and return overall status."""
        checks = [
            self.check_mcp_server_health(),
            self.check_kafka_health(),
            self.check_knox_health(),
            self.check_cdp_health(),
            self.check_topic_operations(),
            self.check_connect_operations()
        ]
        
        # Determine overall status
        statuses = [check.status for check in checks]
        if all(status == HealthStatus.HEALTHY for status in statuses):
            overall_status = HealthStatus.HEALTHY
        elif any(status == HealthStatus.UNHEALTHY for status in statuses):
            overall_status = HealthStatus.UNHEALTHY
        elif any(status == HealthStatus.DEGRADED for status in statuses):
            overall_status = HealthStatus.DEGRADED
        else:
            overall_status = HealthStatus.UNKNOWN
        
        service_health = ServiceHealth(
            service_name="cdf-kafka-mcp-server",
            overall_status=overall_status,
            checks=checks,
            last_updated=datetime.now(),
            uptime_seconds=self.get_uptime()
        )
        
        # Store in history
        self.health_history.append(service_health)
        
        # Keep only last 100 health checks
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        return service_health
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a summary of health status."""
        if not self.health_history:
            return {"message": "No health checks performed yet"}
        
        latest = self.health_history[-1]
        
        # Count statuses
        status_counts = {}
        for check in latest.checks:
            status = check.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "overall_status": latest.overall_status.value,
            "uptime_seconds": latest.uptime_seconds,
            "last_updated": latest.last_updated.isoformat(),
            "status_counts": status_counts,
            "total_checks": len(latest.checks),
            "healthy_checks": status_counts.get("healthy", 0),
            "degraded_checks": status_counts.get("degraded", 0),
            "unhealthy_checks": status_counts.get("unhealthy", 0),
            "unknown_checks": status_counts.get("unknown", 0)
        }
    
    def get_health_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get health check history."""
        return [health.to_dict() for health in self.health_history[-limit:]]
    
    def get_service_metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        if not self.health_history:
            return {"message": "No metrics available"}
        
        # Calculate average response times
        response_times = {}
        for health in self.health_history:
            for check in health.checks:
                if check.response_time_ms is not None:
                    if check.name not in response_times:
                        response_times[check.name] = []
                    response_times[check.name].append(check.response_time_ms)
        
        # Calculate averages
        avg_response_times = {}
        for check_name, times in response_times.items():
            avg_response_times[check_name] = {
                "average_ms": sum(times) / len(times),
                "min_ms": min(times),
                "max_ms": max(times),
                "count": len(times)
            }
        
        return {
            "uptime_seconds": self.get_uptime(),
            "total_health_checks": len(self.health_history),
            "average_response_times": avg_response_times,
            "current_status": self.health_history[-1].overall_status.value if self.health_history else "unknown"
        }


class MetricsCollector:
    """
    Metrics collection system for monitoring server performance.
    """
    
    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = {
            "requests_total": 0,
            "requests_successful": 0,
            "requests_failed": 0,
            "tool_calls": {},
            "response_times": [],
            "errors": []
        }
        self.start_time = datetime.now()
    
    def record_request(self, success: bool, tool_name: str, response_time_ms: float):
        """Record a request."""
        self.metrics["requests_total"] += 1
        if success:
            self.metrics["requests_successful"] += 1
        else:
            self.metrics["requests_failed"] += 1
        
        # Record tool usage
        if tool_name not in self.metrics["tool_calls"]:
            self.metrics["tool_calls"][tool_name] = 0
        self.metrics["tool_calls"][tool_name] += 1
        
        # Record response time
        self.metrics["response_times"].append(response_time_ms)
        
        # Keep only last 1000 response times
        if len(self.metrics["response_times"]) > 1000:
            self.metrics["response_times"] = self.metrics["response_times"][-1000:]
    
    def record_error(self, error: str, tool_name: str):
        """Record an error."""
        self.metrics["errors"].append({
            "error": error,
            "tool": tool_name,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 100 errors
        if len(self.metrics["errors"]) > 100:
            self.metrics["errors"] = self.metrics["errors"][-100:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        # Calculate success rate
        success_rate = 0
        if self.metrics["requests_total"] > 0:
            success_rate = (self.metrics["requests_successful"] / self.metrics["requests_total"]) * 100
        
        # Calculate average response time
        avg_response_time = 0
        if self.metrics["response_times"]:
            avg_response_time = sum(self.metrics["response_times"]) / len(self.metrics["response_times"])
        
        return {
            "uptime_seconds": uptime,
            "requests_total": self.metrics["requests_total"],
            "requests_successful": self.metrics["requests_successful"],
            "requests_failed": self.metrics["requests_failed"],
            "success_rate_percent": round(success_rate, 2),
            "average_response_time_ms": round(avg_response_time, 2),
            "tool_usage": self.metrics["tool_calls"],
            "recent_errors": self.metrics["errors"][-10:],  # Last 10 errors
            "total_errors": len(self.metrics["errors"])
        }
