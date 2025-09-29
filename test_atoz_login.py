#!/usr/bin/env python3
"""
Test script to verify AtoZ login functionality
"""
import sys
import os
import time
import requests
from datetime import datetime

# Add the bot directory to the path
sys.path.append('/home/mofy/Desktop/Al-Tech Solutions/AtoZ_Bot-2.0/bot')

def test_atoz_login():
    """Test the AtoZ login functionality"""
    print("🔐 Testing AtoZ Login Functionality")
    print("=" * 50)
    
    try:
        # Import the bot components
        from config import ATOZ_BASE_URL, ATOZ_USERNAME, ATOZ_PASSWORD
        from login_handler import initialize_browser, perform_login
        
        print(f"🌐 AtoZ URL: {ATOZ_BASE_URL}")
        print(f"👤 Username: {ATOZ_USERNAME}")
        print(f"🔑 Password: {'*' * len(ATOZ_PASSWORD)}")
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Initializing browser...")
        playwright, browser, context, page = initialize_browser(headless=False)  # Set to False to see the browser
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Attempting login...")
        credentials = {"username": ATOZ_USERNAME, "password": ATOZ_PASSWORD}
        
        try:
            perform_login(page, ATOZ_BASE_URL, credentials)
            print(f"✅ LOGIN SUCCESSFUL!")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Login completed successfully")
            
            # Wait a bit to see the logged-in page
            time.sleep(3)
            
            # Check if we're on the dashboard
            current_url = page.url
            print(f"📍 Current URL: {current_url}")
            
            if "dashboard" in current_url.lower() or "portal" in current_url.lower():
                print("✅ Successfully navigated to AtoZ portal!")
            else:
                print("⚠️ Not on expected dashboard page")
                
        except Exception as e:
            print(f"❌ LOGIN FAILED!")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Login failed: {e}")
        
        # Close browser
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Closing browser...")
        browser.close()
        playwright.stop()
        
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_atoz_login()
