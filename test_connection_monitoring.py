#!/usr/bin/env python3
"""
Test script to demonstrate connection monitoring functionality
"""
import asyncio
import aiohttp
import json
import time
from datetime import datetime

async def test_connection_monitoring():
    """Test the connection monitoring endpoints"""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing Connection Monitoring System")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Test basic health check
        print("\n1. Basic Health Check:")
        try:
            async with session.get(f"{base_url}/health") as response:
                data = await response.json()
                print(f"   Status: {data['status']}")
                print(f"   Timestamp: {data['timestamp']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test detailed health check
        print("\n2. Detailed Health Check:")
        try:
            async with session.get(f"{base_url}/health/detailed") as response:
                data = await response.json()
                print(f"   Overall Status: {data['overall_status']}")
                print(f"   Monitoring Active: {data['monitoring_active']}")
                print(f"   Check Interval: {data['check_interval']}s")
                print("\n   Service Status:")
                for service, status in data['services'].items():
                    print(f"     {service}: {status['status']} (retry: {status['retry_count']})")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test individual service checks
        print("\n3. Individual Service Checks:")
        services = ['database', 'redis', 'bot_process', 'external_api', 'websocket']
        for service in services:
            try:
                async with session.get(f"{base_url}/health/service/{service}") as response:
                    data = await response.json()
                    print(f"   {service}: {data['status']}")
            except Exception as e:
                print(f"   {service}: Error - {e}")
        
        # Test force check
        print("\n4. Force Check All Services:")
        try:
            async with session.post(f"{base_url}/health/force-check") as response:
                data = await response.json()
                print(f"   Message: {data['message']}")
                print(f"   Timestamp: {data['timestamp']}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Monitor for changes over time
        print("\n5. Monitoring Changes Over Time:")
        print("   (Checking every 10 seconds for 30 seconds)")
        
        for i in range(3):
            await asyncio.sleep(10)
            try:
                async with session.get(f"{base_url}/health/detailed") as response:
                    data = await response.json()
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    print(f"   [{timestamp}] Overall: {data['overall_status']}")
                    
                    # Show any services that are not healthy
                    unhealthy = [k for k, v in data['services'].items() if v['status'] != 'healthy']
                    if unhealthy:
                        print(f"   [{timestamp}] Unhealthy services: {', '.join(unhealthy)}")
                    else:
                        print(f"   [{timestamp}] All services healthy")
            except Exception as e:
                print(f"   [{timestamp}] Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection_monitoring())

