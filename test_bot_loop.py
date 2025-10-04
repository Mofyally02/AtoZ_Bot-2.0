#!/usr/bin/env python3
"""
Test bot job checking loop specifically
"""
import sys
import os
sys.path.append('bot')

from config import ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH, USER_CREDENTIALS
from login_handler import initialize_browser, perform_login
from filter_handler import navigate_to_job_board
from data_processor import extract_jobs
from atoz_bot import update_database_stats, send_status_update
from urllib.parse import urljoin
import time

def test_bot_loop():
    """Test the bot job checking loop specifically"""
    print("🤖 Testing bot job checking loop...")
    
    session_id = "test-loop-123"
    
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
        
        # Initialize counters
        total_checks = 0
        total_accepted = 0
        total_rejected = 0
        
        # Send initial status
        send_status_update(session_id, "running", {"message": "Bot is now running and checking for jobs"})
        
        # Test job checking loop (3 cycles)
        for cycle in range(3):
            print(f"\n🔄 Starting job check cycle #{cycle + 1}")
            send_status_update(session_id, "checking_jobs", {"cycle": cycle + 1, "step": "navigating"})
            
            # Navigate to job board
            print("📋 Navigating to job board...")
            navigate_to_job_board(page, ATOZ_BASE_URL)
            send_status_update(session_id, "checking_jobs", {"cycle": cycle + 1, "step": "loading_jobs"})
            
            # Extract jobs
            print("🔍 Extracting jobs...")
            jobs = extract_jobs(page)
            total_checks += 1
            
            print(f"📊 Found {len(jobs)} jobs in cycle {cycle + 1}")
            
            if not jobs:
                print("No jobs available at this time")
                send_status_update(session_id, "no_jobs", {"cycle": cycle + 1})
            else:
                print(f"Found {len(jobs)} available jobs")
                send_status_update(session_id, "processing_jobs", {"cycle": cycle + 1, "jobs_found": len(jobs)})
                
                # Show job details
                for i, job in enumerate(jobs[:2]):  # Show first 2 jobs
                    print(f"   Job {i+1}: {job.get('ref', 'N/A')} - {job.get('language', 'N/A')} - {job.get('status', 'N/A')}")
            
            # Update database with current stats
            print(f"💾 Updating database: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")
            update_database_stats(session_id, total_checks, total_accepted, total_rejected, "running")
            
            # Send cycle complete update
            send_status_update(session_id, "cycle_complete", {
                "cycle": cycle + 1,
                "stats": {
                    "total_checks": total_checks,
                    "total_accepted": total_accepted,
                    "total_rejected": total_rejected,
                    "total_skipped": 0
                }
            })
            
            print(f"✅ Cycle #{cycle + 1} completed: {total_checks} total checks")
            
            # Wait before next cycle
            wait_time = 2  # 2 seconds for testing
            print(f"⏰ Waiting {wait_time}s before next cycle...")
            time.sleep(wait_time)
        
        print(f"\n🎉 Bot loop test completed successfully!")
        print(f"📊 Final stats: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")
        return True
        
    except Exception as e:
        print(f"❌ Error in bot loop test: {e}")
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
    success = test_bot_loop()
    if success:
        print("\n✅ Bot loop test passed!")
    else:
        print("\n❌ Bot loop test failed!")

