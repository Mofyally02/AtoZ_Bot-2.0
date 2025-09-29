#!/usr/bin/env python3
"""
Monitor bot real-time updates and job processing
"""
import requests
import time
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"

def monitor_bot_status():
    """Monitor bot status and job processing"""
    print("🤖 Bot Status Monitor")
    print("=" * 50)
    
    while True:
        try:
            # Get bot status
            response = requests.get(f"{API_BASE_URL}/api/bot/status")
            if response.status_code == 200:
                status = response.json()
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"[{timestamp}] Bot Status:")
                print(f"  Running: {status.get('is_running', False)}")
                print(f"  Status: {status.get('status', 'unknown')}")
                print(f"  Login: {status.get('login_status', 'unknown')}")
                print(f"  Checks: {status.get('total_checks', 0)}")
                print(f"  Accepted: {status.get('total_accepted', 0)}")
                print(f"  Rejected: {status.get('total_rejected', 0)}")
                print("-" * 30)
                
                # If bot is not running, break
                if not status.get('is_running', False):
                    print("Bot stopped, ending monitor...")
                    break
            else:
                print(f"Error getting bot status: {response.status_code}")
                
        except Exception as e:
            print(f"Error: {e}")
            
        time.sleep(2)  # Check every 2 seconds

if __name__ == "__main__":
    monitor_bot_status()
