#!/usr/bin/env python3
"""
Debug script to test bot functionality
"""
import requests
import time
import threading

def test_bot_directly():
    """Test bot functionality directly"""
    print("🧪 Testing bot functionality directly...")
    
    # Test 1: Check initial status
    print("\n1. Checking initial status...")
    response = requests.get("http://localhost:8000/api/bot/status")
    status = response.json()
    print(f"   Status: {status}")
    
    # Test 2: Start bot
    print("\n2. Starting bot...")
    response = requests.post("http://localhost:8000/api/bot/toggle")
    result = response.json()
    print(f"   Response: {result}")
    
    # Test 3: Monitor for 10 seconds
    print("\n3. Monitoring bot for 10 seconds...")
    for i in range(10):
        time.sleep(1)
        response = requests.get("http://localhost:8000/api/bot/status")
        status = response.json()
        print(f"   [{i+1:2d}s] Running={status.get('is_running')}, "
              f"Login={status.get('login_status')}, "
              f"Checks={status.get('total_checks')}, "
              f"Accepted={status.get('total_accepted')}, "
              f"Rejected={status.get('total_rejected')}")
    
    # Test 4: Stop bot
    print("\n4. Stopping bot...")
    response = requests.post("http://localhost:8000/api/bot/toggle")
    result = response.json()
    print(f"   Response: {result}")
    
    # Test 5: Final status
    print("\n5. Final status...")
    response = requests.get("http://localhost:8000/api/bot/status")
    status = response.json()
    print(f"   Status: {status}")

def test_threading():
    """Test threading functionality"""
    print("\n🧵 Testing threading functionality...")
    
    def test_function():
        print("   Thread function started!")
        for i in range(5):
            print(f"   Thread iteration {i+1}")
            time.sleep(1)
        print("   Thread function finished!")
    
    print("   Starting thread...")
    thread = threading.Thread(target=test_function, daemon=True)
    thread.start()
    print(f"   Thread alive: {thread.is_alive()}")
    
    print("   Waiting for thread to complete...")
    thread.join(timeout=10)
    print(f"   Thread finished: {not thread.is_alive()}")

if __name__ == "__main__":
    print("🔍 Bot Debug Test")
    print("=" * 50)
    
    # Test threading first
    test_threading()
    
    # Test bot functionality
    test_bot_directly()
    
    print("\n✅ Debug test completed!")
