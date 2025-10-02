"""
Connection monitoring and health check service
"""
import asyncio
import logging
import os
import time
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Callable
try:
    import aiohttp
except ImportError:
    aiohttp = None
import psutil
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import get_db, engine, get_redis

logger = logging.getLogger(__name__)

class ConnectionStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"
    CONNECTING = "connecting"
    DISCONNECTED = "disconnected"

class ServiceType(Enum):
    DATABASE = "database"
    REDIS = "redis"
    BOT_PROCESS = "bot_process"
    EXTERNAL_API = "external_api"
    WEBSOCKET = "websocket"

class ConnectionMonitor:
    def __init__(self, check_interval: int = 5):
        self.check_interval = check_interval
        self.status: Dict[ServiceType, ConnectionStatus] = {
            service: ConnectionStatus.UNKNOWN for service in ServiceType
        }
        self.last_check: Dict[ServiceType, datetime] = {}
        self.retry_counts: Dict[ServiceType, int] = {
            service: 0 for service in ServiceType
        }
        self.max_retries = 3
        self.callbacks: Dict[ServiceType, List[Callable]] = {
            service: [] for service in ServiceType
        }
        self.monitoring = False
        self.monitor_task: Optional[asyncio.Task] = None

    def add_callback(self, service: ServiceType, callback: Callable):
        """Add a callback to be called when service status changes"""
        self.callbacks[service].append(callback)

    def remove_callback(self, service: ServiceType, callback: Callable):
        """Remove a callback"""
        if callback in self.callbacks[service]:
            self.callbacks[service].remove(callback)

    async def _notify_status_change(self, service: ServiceType, old_status: ConnectionStatus, new_status: ConnectionStatus):
        """Notify all callbacks about status change"""
        for callback in self.callbacks[service]:
            try:
                await callback(service, old_status, new_status)
            except Exception as e:
                logger.error(f"Error in callback for {service}: {e}")

    async def check_database(self) -> ConnectionStatus:
        """Check database connection"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.fetchone()
            return ConnectionStatus.HEALTHY
        except SQLAlchemyError as e:
            logger.error(f"Database check failed: {e}")
            return ConnectionStatus.UNHEALTHY
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            return ConnectionStatus.UNHEALTHY

    async def check_redis(self) -> ConnectionStatus:
        """Check Redis connection"""
        try:
            redis_client = get_redis()
            if redis_client is None:
                logger.info("Redis client not available - Redis is optional")
                return ConnectionStatus.HEALTHY  # Show as healthy when not needed
            redis_client.ping()
            return ConnectionStatus.HEALTHY
        except Exception as e:
            logger.info(f"Redis not available (optional): {e}")
            return ConnectionStatus.HEALTHY  # Show as healthy when not needed

    async def check_bot_process(self) -> ConnectionStatus:
        """Check if bot process is running"""
        try:
            # First check if simple toggle bot is running
            try:
                from app.api.bot_control import bot_running
                if bot_running:
                    return ConnectionStatus.HEALTHY
            except ImportError:
                pass
            
            # Check for bot processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if any(keyword in cmdline.lower() for keyword in ['integrated_bot', 'realistic_test_bot', 'test_bot', 'atoz_bot']):
                        if proc.is_running():
                            return ConnectionStatus.HEALTHY
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return ConnectionStatus.DISCONNECTED
        except Exception as e:
            logger.error(f"Bot process check failed: {e}")
            return ConnectionStatus.UNHEALTHY

    async def check_external_api(self) -> ConnectionStatus:
        """Check external API connectivity"""
        if aiohttp is None:
            logger.warning("aiohttp not available, skipping external API check")
            return ConnectionStatus.HEALTHY
        
        try:
            async with aiohttp.ClientSession() as session:
                # Use environment variable or default to localhost for development
                health_url = os.getenv('HEALTH_CHECK_URL', 'http://localhost:8000/health')
                async with session.get(health_url, timeout=2) as response:
                    if response.status == 200:
                        return ConnectionStatus.HEALTHY
                    else:
                        return ConnectionStatus.UNHEALTHY
        except Exception as e:
            logger.error(f"External API check failed: {e}")
            return ConnectionStatus.UNHEALTHY

    async def check_websocket(self) -> ConnectionStatus:
        """Check WebSocket connectivity"""
        try:
            # This is a simplified check - in practice, you'd want to maintain
            # a list of active WebSocket connections
            return ConnectionStatus.HEALTHY  # Placeholder
        except Exception as e:
            logger.error(f"WebSocket check failed: {e}")
            return ConnectionStatus.UNHEALTHY

    async def check_service(self, service: ServiceType) -> ConnectionStatus:
        """Check a specific service"""
        check_methods = {
            ServiceType.DATABASE: self.check_database,
            ServiceType.REDIS: self.check_redis,
            ServiceType.BOT_PROCESS: self.check_bot_process,
            ServiceType.EXTERNAL_API: self.check_external_api,
            ServiceType.WEBSOCKET: self.check_websocket,
        }
        
        if service in check_methods:
            return await check_methods[service]()
        return ConnectionStatus.UNKNOWN

    async def update_service_status(self, service: ServiceType, new_status: ConnectionStatus):
        """Update service status and notify callbacks"""
        old_status = self.status[service]
        self.status[service] = new_status
        self.last_check[service] = datetime.now(timezone.utc)
        
        if old_status != new_status:
            logger.info(f"Service {service} status changed: {old_status} -> {new_status}")
            await self._notify_status_change(service, old_status, new_status)
            
            # Reset retry count on successful connection
            if new_status == ConnectionStatus.HEALTHY:
                self.retry_counts[service] = 0

    async def check_all_services(self):
        """Check all services and update their status"""
        tasks = []
        for service in ServiceType:
            task = asyncio.create_task(self._check_and_update_service(service))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Return the current status
        return self.status

    async def _check_and_update_service(self, service: ServiceType):
        """Check a single service and update its status"""
        try:
            new_status = await self.check_service(service)
            await self.update_service_status(service, new_status)
            
            # Handle retry logic for unhealthy services
            if new_status == ConnectionStatus.UNHEALTHY:
                self.retry_counts[service] += 1
                if self.retry_counts[service] <= self.max_retries:
                    logger.info(f"Service {service} unhealthy, retry {self.retry_counts[service]}/{self.max_retries}")
                    # Schedule retry
                    asyncio.create_task(self._retry_service(service))
                    
        except Exception as e:
            logger.error(f"Error checking service {service}: {e}")
            await self.update_service_status(service, ConnectionStatus.UNHEALTHY)

    async def _retry_service(self, service: ServiceType):
        """Retry connecting to a service after a delay"""
        await asyncio.sleep(1)  # Wait 1 second before retry
        new_status = await self.check_service(service)
        await self.update_service_status(service, new_status)

    async def start_monitoring(self):
        """Start the connection monitoring loop"""
        if self.monitoring:
            return
        
        self.monitoring = True
        logger.info("Starting connection monitoring...")
        
        # Initial check
        await self.check_all_services()
        
        # Start monitoring loop
        self.monitor_task = asyncio.create_task(self._monitoring_loop())

    async def stop_monitoring(self):
        """Stop the connection monitoring loop"""
        self.monitoring = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("Connection monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                await asyncio.sleep(self.check_interval)
                if self.monitoring:  # Check again in case it was stopped
                    await self.check_all_services()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying

    def get_status_summary(self) -> Dict:
        """Get a summary of all service statuses"""
        return {
            "overall_status": self._get_overall_status(),
            "services": {
                service.value: {
                    "status": status.value,
                    "last_check": self.last_check.get(service),
                    "retry_count": self.retry_counts[service]
                }
                for service, status in self.status.items()
            },
            "monitoring_active": self.monitoring,
            "check_interval": self.check_interval
        }

    def _get_overall_status(self) -> str:
        """Get overall system status"""
        if not self.status:
            return "unknown"
        
        # Get critical services (exclude Redis as it's optional)
        critical_services = [s for s in self.status.keys() if s != ServiceType.REDIS]
        critical_statuses = [self.status[s] for s in critical_services]
        
        # Check if all critical services are healthy
        if all(s == ConnectionStatus.HEALTHY for s in critical_statuses):
            return "healthy"
        elif any(s == ConnectionStatus.UNHEALTHY for s in critical_statuses):
            return "degraded"
        elif any(s == ConnectionStatus.DISCONNECTED for s in critical_statuses):
            return "partial"
        else:
            return "unknown"

    async def force_check_all(self):
        """Force check all services immediately"""
        await self.check_all_services()

# Global connection monitor instance
connection_monitor = ConnectionMonitor()
