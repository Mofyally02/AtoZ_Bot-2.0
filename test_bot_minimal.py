#!/usr/bin/env python3
"""
Minimal bot test to isolate issues
"""
import sys
import os
sys.path.append('bot')

from config import ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH, USER_CREDENTIALS
from login_handler import initialize_browser, perform_login
from filter_handler import navigate_to_job_board
from data_processor import extract_jobs
from urllib.parse import urljoin
import time

def test_minimal_bot():
    """Test minimal bot functionality"""
    print("🤖 Starting minimal bot test...")
    
    # Initialize browser
    print("🌐 Initializing browser...")
    p, browser, context, page = initialize_browser(headless=True)
    
    try:
        # Navigate to jobs page
        jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
        print(f"📄 Navigating to: {jobs_url}")
        page.goto(jobs_url, wait_until='networkidle')
        
        # Login
        print("🔐 Logging in...")
        perform_login(page, ATOZ_BASE_URL, USER_CREDENTIALS)
        print("✅ Login successful")
        
        # Navigate to job board
        print("📋 Navigating to job board...")
        navigate_to_job_board(page, ATOZ_BASE_URL)
        
        # Extract jobs
        print("🔍 Extracting jobs...")
        jobs = extract_jobs(page)
        print(f"📊 Found {len(jobs)} jobs")
        
        if jobs:
            for i, job in enumerate(jobs[:3]):
                print(f"   Job {i+1}: {job.get('ref', 'N/A')} - {job.get('language', 'N/A')} - {job.get('status', 'N/A')}")
        
        # Simulate job checking loop
        print("🔄 Starting job checking loop...")
        for cycle in range(3):
            print(f"   Cycle {cycle + 1}: Checking jobs...")
            jobs = extract_jobs(page)
            print(f"   Found {len(jobs)} jobs in cycle {cycle + 1}")
            time.sleep(1)  # Wait 1 second between cycles
        
        print("✅ Minimal bot test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in minimal bot test: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print("🧹 Cleaning up...")
        try:
            context.close()
            browser.close()
            p.stop()
        except:
            pass

if __name__ == "__main__":
    success = test_minimal_bot()
    if success:
        print("\n✅ Minimal bot test passed!")
    else:
        print("\n❌ Minimal bot test failed!")

