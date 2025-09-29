#!/usr/bin/env python3
"""
Real-time request/response monitor for AtoZ Bot API
"""
import requests
import time
import json
from datetime import datetime

def monitor_api():
    """Monitor API requests and responses"""
    base_url = "http://localhost:8000"
    
    print("🔍 AtoZ Bot API Monitor Started")
    print("=" * 50)
    
    while True:
        try:
            # Test health endpoint
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Testing API...")
            
            # Health check
            health_response = requests.get(f"{base_url}/health", timeout=5)
            print(f"   Health: {health_response.status_code} - {health_response.json()}")
            
            # Status check
            status_response = requests.get(f"{base_url}/api/bot/status", timeout=5)
            status_data = status_response.json()
            print(f"   Bot Status: {status_data['is_running']} - {status_data['status']}")
            
            # Detailed health
            detailed_response = requests.get(f"{base_url}/health/detailed", timeout=5)
            detailed_data = detailed_response.json()
            print(f"   Overall Status: {detailed_data['overall_status']}")
            print(f"   Services: {[f'{k}:{v['status']}' for k, v in detailed_data['services'].items()]}")
            
            time.sleep(5)  # Check every 5 seconds
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection error: {e}")
            time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped")
            break

if __name__ == "__main__":
    monitor_api()
