#!/usr/bin/env python3
"""
Test script for real AtoZ bot functionality
"""
import requests
import time
import json

def test_real_atoz_bot():
    """Test the real AtoZ bot functionality"""
    print("🌐 Real AtoZ Bot Test")
    print("=" * 50)
    
    # Test 1: Check initial status
    print("\n1. Checking initial status...")
    try:
        response = requests.get("http://localhost:8000/api/bot/status")
        status = response.json()
        print(f"   Status: {json.dumps(status, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test 2: Start bot (this should trigger real AtoZ login)
    print("\n2. Starting real AtoZ bot...")
    try:
        response = requests.post("http://localhost:8000/api/bot/toggle")
        result = response.json()
        print(f"   Response: {result}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test 3: Monitor for 30 seconds to see real login and job checking
    print("\n3. Monitoring real AtoZ bot for 30 seconds...")
    print("   This should show real login attempts and job checking...")
    
    for i in range(30):
        time.sleep(1)
        try:
            response = requests.get("http://localhost:8000/api/bot/status")
            status = response.json()
            print(f"   [{i+1:2d}s] Running={status.get('is_running')}, "
                  f"Login={status.get('login_status')}, "
                  f"Checks={status.get('total_checks')}, "
                  f"Accepted={status.get('total_accepted')}, "
                  f"Rejected={status.get('total_rejected')}")
        except Exception as e:
            print(f"   [{i+1:2d}s] Error: {e}")
    
    # Test 4: Stop bot
    print("\n4. Stopping bot...")
    try:
        response = requests.post("http://localhost:8000/api/bot/toggle")
        result = response.json()
        print(f"   Response: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Final status
    print("\n5. Final status...")
    try:
        response = requests.get("http://localhost:8000/api/bot/status")
        status = response.json()
        print(f"   Status: {json.dumps(status, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_real_atoz_bot()
    print("\n✅ Real AtoZ bot test completed!")
