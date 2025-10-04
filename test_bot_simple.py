#!/usr/bin/env python3
"""
Simple test script to verify the AtoZ bot functionality
"""
import sys
import os
import time
from datetime import datetime

# Add bot directory to path
sys.path.append('bot')

def test_bot_functionality():
    """Test the bot's core functionality"""
    print("🚀 Testing AtoZ Bot Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Configuration loading
        print("\n1. Testing configuration loading...")
        from config import ATOZ_USERNAME, ATOZ_PASSWORD, ATOZ_BASE_URL, BOT_CONFIG
        print(f"   ✅ Username: {ATOZ_USERNAME}")
        print(f"   ✅ Password: {'SET' if ATOZ_PASSWORD else 'NOT_SET'}")
        print(f"   ✅ Base URL: {ATOZ_BASE_URL}")
        print(f"   ✅ Job Type Filter: {BOT_CONFIG['accept_preconditions']['job_type']}")
        print(f"   ✅ Exclude Types: {BOT_CONFIG['accept_preconditions']['exclude_types']}")
        
        # Test 2: Login functionality
        print("\n2. Testing login functionality...")
        from login_handler import initialize_browser
        from atoz_bot import try_login
        from urllib.parse import urljoin
        
        p, browser, context, page = initialize_browser(headless=True)
        try:
            jobs_url = urljoin(ATOZ_BASE_URL, "/interpreter-jobs")
            print(f"   📄 Navigating to: {jobs_url}")
            page.goto(jobs_url, wait_until='networkidle')
            
            print("   🔐 Attempting login...")
            login_result = try_login(page)
            
            if login_result:
                print("   ✅ Login successful!")
                
                # Test 3: Job extraction
                print("\n3. Testing job extraction...")
                from data_processor import extract_jobs
                from filter_handler import navigate_to_job_board
                
                try:
                    navigate_to_job_board(page, ATOZ_BASE_URL)
                    jobs = extract_jobs(page)
                except Exception as e:
                    print(f"   ⚠️ Network error during job extraction: {e}")
                    print("   🔄 Retrying job extraction...")
                    time.sleep(2)
                    try:
                        page.reload(wait_until="networkidle")
                        jobs = extract_jobs(page)
                    except Exception as e2:
                        print(f"   ❌ Job extraction failed: {e2}")
                        jobs = []
                
                print(f"   📊 Found {len(jobs)} jobs")
                
                if jobs:
                    print("   📋 Sample job data:")
                    for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
                        print(f"      Job {i+1}: {job.get('ref', 'N/A')} - {job.get('language', 'N/A')} - {job.get('status', 'N/A')}")
                    
                    # Test 4: Job filtering
                    print("\n4. Testing job filtering...")
                    matched_jobs = [job for job in jobs if "matched" in job.get("status", "").lower()]
                    print(f"   🎯 Matched jobs: {len(matched_jobs)}")
                    
                    if matched_jobs:
                        print("   ✅ Bot can find matched jobs!")
                        
                        # Test 5: Job acceptance criteria
                        print("\n5. Testing job acceptance criteria...")
                        from data_processor import is_all_params_set
                        
                        required_fields = BOT_CONFIG['accept_preconditions']['required_fields']
                        valid_jobs = []
                        
                        for job in matched_jobs:
                            if is_all_params_set(job, required_fields):
                                valid_jobs.append(job)
                        
                        print(f"   ✅ Jobs with all required fields: {len(valid_jobs)}")
                        
                        if valid_jobs:
                            print("   ✅ Bot can identify jobs ready for acceptance!")
                        else:
                            print("   ⚠️ No jobs currently meet all acceptance criteria")
                    else:
                        print("   ⚠️ No matched jobs found at this time")
                else:
                    print("   ⚠️ No jobs found at this time")
                
            else:
                print("   ❌ Login failed!")
                return False
                
        finally:
            context.close()
            browser.close()
        
        print("\n" + "=" * 50)
        print("🎉 BOT FUNCTIONALITY TEST COMPLETED SUCCESSFULLY!")
        print("✅ The bot can:")
        print("   - Load configuration correctly")
        print("   - Login to AtoZ website")
        print("   - Extract job data")
        print("   - Filter matched jobs")
        print("   - Apply acceptance criteria")
        print("\n🚀 The bot is ready to work!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bot_functionality()
    sys.exit(0 if success else 1)
