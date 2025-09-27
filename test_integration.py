#!/usr/bin/env python3
"""
Integration test script for AtoZ Bot Dashboard
Tests all API endpoints and WebSocket functionality
"""
import asyncio
import json
import requests
import websockets
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing API Endpoints...")
    
    # Test health check
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
    
    # Test bot status
    try:
        response = requests.get(f"{API_BASE_URL}/api/bot/status")
        print(f"✅ Bot status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Bot status failed: {e}")
    
    # Test dashboard metrics
    try:
        response = requests.get(f"{API_BASE_URL}/api/bot/dashboard/metrics")
        print(f"✅ Dashboard metrics: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Dashboard metrics failed: {e}")
    
    # Test analytics
    try:
        response = requests.get(f"{API_BASE_URL}/api/bot/analytics")
        print(f"✅ Analytics: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Analytics failed: {e}")
    
    # Test job records
    try:
        response = requests.get(f"{API_BASE_URL}/api/bot/jobs")
        print(f"✅ Job records: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"❌ Job records failed: {e}")

def test_bot_control():
    """Test bot start/stop functionality"""
    print("\n🤖 Testing Bot Control...")
    
    # Test start bot
    try:
        response = requests.post(f"{API_BASE_URL}/api/bot/start", json={
            "session_name": "Test Session"
        })
        print(f"✅ Start bot: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        if response.status_code == 200:
            # Wait a bit for bot to start
            import time
            time.sleep(2)
            
            # Test stop bot
            response = requests.post(f"{API_BASE_URL}/api/bot/stop")
            print(f"✅ Stop bot: {response.status_code}")
            print(f"   Response: {response.json()}")
        
    except Exception as e:
        print(f"❌ Bot control failed: {e}")

async def test_websocket():
    """Test WebSocket connection and real-time updates"""
    print("\n🔌 Testing WebSocket Connection...")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket connected successfully")
            
            # Listen for messages for 10 seconds
            timeout = 10
            start_time = datetime.now()
            
            while (datetime.now() - start_time).seconds < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    print(f"📨 Received: {data['type']}")
                    print(f"   Data: {json.dumps(data['data'], indent=2)}")
                except asyncio.TimeoutError:
                    print("⏰ No message received in 1 second")
                    break
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            print("✅ WebSocket test completed")
            
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")

async def test_full_integration():
    """Test complete integration flow"""
    print("\n🚀 Testing Full Integration Flow...")
    
    try:
        # Start bot
        print("1. Starting bot...")
        response = requests.post(f"{API_BASE_URL}/api/bot/start", json={
            "session_name": "Integration Test"
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to start bot: {response.text}")
            return
        
        print("✅ Bot started successfully")
        
        # Connect to WebSocket
        print("2. Connecting to WebSocket...")
        async with websockets.connect(WS_URL) as websocket:
            print("✅ WebSocket connected")
            
            # Monitor for 15 seconds
            print("3. Monitoring real-time updates...")
            timeout = 15
            start_time = datetime.now()
            message_count = 0
            
            while (datetime.now() - start_time).seconds < timeout:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(message)
                    message_count += 1
                    
                    if data['type'] == 'status_update':
                        bot_status = data['data'].get('bot_status', {})
                        print(f"📊 Bot Status: Running={bot_status.get('is_running')}, "
                              f"Checks={bot_status.get('total_checks')}, "
                              f"Accepted={bot_status.get('total_accepted')}, "
                              f"Rejected={bot_status.get('total_rejected')}")
                    
                    elif data['type'] in ['job_accepted', 'job_rejected']:
                        counts = data['data'].get('counts', {})
                        print(f"🎯 Job {data['type']}: Checks={counts.get('total_checks')}, "
                              f"Accepted={counts.get('total_accepted')}, "
                              f"Rejected={counts.get('total_rejected')}")
                    
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            print(f"✅ Received {message_count} real-time updates")
        
        # Stop bot
        print("4. Stopping bot...")
        response = requests.post(f"{API_BASE_URL}/api/bot/stop")
        if response.status_code == 200:
            print("✅ Bot stopped successfully")
        else:
            print(f"❌ Failed to stop bot: {response.text}")
        
        print("🎉 Full integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")

def main():
    """Main test function"""
    print("🧪 AtoZ Bot Dashboard Integration Test")
    print("=" * 50)
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test bot control
    test_bot_control()
    
    # Test WebSocket
    asyncio.run(test_websocket())
    
    # Test full integration
    asyncio.run(test_full_integration())
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()

