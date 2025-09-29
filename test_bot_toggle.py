#!/usr/bin/env python3
"""
Test script to simulate frontend bot toggle requests
"""
import requests
import time
import json
from datetime import datetime

def test_bot_toggle():
    """Test bot toggle functionality with detailed logging"""
    base_url = "http://localhost:8000"
    
    print("🤖 Bot Toggle Test Started")
    print("=" * 50)
    
    # Test 1: Check initial status
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 1. Checking initial status...")
    try:
        response = requests.get(f"{base_url}/api/bot/status", timeout=5)
        status = response.json()
        print(f"   Status: {status['is_running']} - {status['status']}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test 2: Start bot
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 2. Starting bot...")
    try:
        response = requests.post(f"{base_url}/api/bot/toggle", timeout=5)
        result = response.json()
        print(f"   Response: {result}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test 3: Check status after start
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 3. Checking status after start...")
    try:
        response = requests.get(f"{base_url}/api/bot/status", timeout=5)
        status = response.json()
        print(f"   Status: {status['is_running']} - {status['status']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Wait a bit
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 4. Waiting 3 seconds...")
    time.sleep(3)
    
    # Test 4: Stop bot
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 5. Stopping bot...")
    try:
        response = requests.post(f"{base_url}/api/bot/toggle", timeout=5)
        result = response.json()
        print(f"   Response: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Check final status
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 6. Checking final status...")
    try:
        response = requests.get(f"{base_url}/api/bot/status", timeout=5)
        status = response.json()
        print(f"   Status: {status['is_running']} - {status['status']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print(f"\n✅ Test completed!")

if __name__ == "__main__":
    test_bot_toggle()
