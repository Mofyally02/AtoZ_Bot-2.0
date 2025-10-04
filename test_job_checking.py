#!/usr/bin/env python3
"""
Test job checking functionality
"""
import sys
import os
sys.path.append('bot')

from config import ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH
from login_handler import initialize_browser
from atoz_bot import try_login, update_database_stats, send_status_update
from filter_handler import navigate_to_job_board
from data_processor import extract_jobs
from urllib.parse import urljoin
import time

def test_job_checking_cycle():
    """Test a single job checking cycle"""
    print("🔍 Testing job checking cycle...")
    
    # Initialize browser
    p, browser, context, page = initialize_browser(headless=True)
    session_id = "test-cycle-123"
    
    try:
        # Navigate to jobs page
        jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
        print(f"📄 Navigating to: {jobs_url}")
        page.goto(jobs_url, wait_until='networkidle')
        
        # Login
        print("🔐 Logging in...")
        login_result = try_login(page)
        if not login_result:
            print("❌ Login failed")
            return False
        
        print("✅ Login successful")
        
        # Update database
        update_database_stats(session_id, 0, 0, 0, "running")
        send_status_update(session_id, "running", {"message": "Bot is now running and checking for jobs"})
        
        # Start job checking loop (just one cycle for testing)
        cycle = 1
        total_checks = 0
        total_accepted = 0
        total_rejected = 0
        
        print(f"🔄 Starting job check cycle #{cycle}")
        send_status_update(session_id, "checking_jobs", {"cycle": cycle, "step": "navigating"})
        
        # Navigate to job board
        print("📋 Navigating to job board...")
        navigate_to_job_board(page, ATOZ_BASE_URL)
        send_status_update(session_id, "checking_jobs", {"cycle": cycle, "step": "loading_jobs"})
        
        # Extract jobs
        print("🔍 Extracting jobs...")
        jobs = extract_jobs(page)
        total_checks += 1
        
        print(f"📊 Found {len(jobs)} jobs")
        
        if not jobs:
            print("No jobs available at this time")
            send_status_update(session_id, "no_jobs", {"cycle": cycle})
        else:
            print(f"Found {len(jobs)} available jobs")
            send_status_update(session_id, "processing_jobs", {"cycle": cycle, "jobs_found": len(jobs)})
            
            # Show job details
            for i, job in enumerate(jobs[:3]):  # Show first 3 jobs
                print(f"   Job {i+1}: {job.get('ref', 'N/A')} - {job.get('language', 'N/A')} - {job.get('status', 'N/A')}")
        
        # Update database with current stats
        print(f"📊 Updating database: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")
        update_database_stats(session_id, total_checks, total_accepted, total_rejected, "running")
        
        # Send cycle complete update
        send_status_update(session_id, "cycle_complete", {
            "cycle": cycle,
            "stats": {
                "total_checks": total_checks,
                "total_accepted": total_accepted,
                "total_rejected": total_rejected,
                "total_skipped": 0
            }
        })
        
        print("✅ Job checking cycle completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in job checking cycle: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        context.close()
        browser.close()

if __name__ == "__main__":
    success = test_job_checking_cycle()
    if success:
        print("\n✅ Job checking test passed!")
    else:
        print("\n❌ Job checking test failed!")

