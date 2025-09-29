#!/usr/bin/env python3
"""
Test the enhanced bot functionality
"""
import requests
import time
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def test_enhanced_bot():
    """Test the enhanced bot functionality"""
    print("🤖 Enhanced Bot Test")
    print("=" * 50)
    
    # 1. Check initial status
    print("1. Checking initial status...")
    response = requests.get(f"{API_BASE_URL}/api/bot/status")
    status = response.json()
    print(f"   Initial: Running={status.get('is_running')}, Checks={status.get('total_checks')}")
    
    # 2. Start bot
    print("\n2. Starting bot...")
    response = requests.post(f"{API_BASE_URL}/api/bot/toggle")
    result = response.json()
    print(f"   Response: {result}")
    
    # 3. Monitor bot for 30 seconds
    print("\n3. Monitoring bot for 30 seconds...")
    for i in range(15):  # 15 checks over 30 seconds
        time.sleep(2)
        response = requests.get(f"{API_BASE_URL}/api/bot/status")
        status = response.json()
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"   [{timestamp}] Running={status.get('is_running')}, "
              f"Login={status.get('login_status')}, "
              f"Checks={status.get('total_checks')}, "
              f"Accepted={status.get('total_accepted')}, "
              f"Rejected={status.get('total_rejected')}")
    
    # 4. Stop bot
    print("\n4. Stopping bot...")
    response = requests.post(f"{API_BASE_URL}/api/bot/toggle")
    result = response.json()
    print(f"   Response: {result}")
    
    # 5. Check final status
    print("\n5. Checking final status...")
    response = requests.get(f"{API_BASE_URL}/api/bot/status")
    status = response.json()
    print(f"   Final: Running={status.get('is_running')}, Checks={status.get('total_checks')}")
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_enhanced_bot()
