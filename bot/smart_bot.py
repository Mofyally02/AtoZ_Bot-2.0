#!/usr/bin/env python3
"""
Smart AtoZ Bot for testing purposes
This simulates the complete bot workflow: login → job checking → tracking
"""

import time
import sys
import json
import random
import requests
from datetime import datetime
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
SESSION_ID = None

def log(message: str) -> None:
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [SmartBot] {message}")

def send_status_update(status: str, data: Dict[str, Any] = None) -> None:
    """Send status update to backend API"""
    try:
        if SESSION_ID:
            update_data = {
                "session_id": SESSION_ID,
                "status": status,
                "data": data or {}
            }
            # This would normally send to a WebSocket or API endpoint
            log(f"Status update: {status} - {data}")
    except Exception as e:
        log(f"Failed to send status update: {e}")

def simulate_login_process():
    """Simulate the login process with detailed steps"""
    log("🔐 Starting login process...")
    send_status_update("login_attempting", {"step": "connecting"})
    
    # Step 1: Connect to AtoZ portal
    time.sleep(2)
    log("📡 Connecting to AtoZ portal...")
    send_status_update("login_attempting", {"step": "connecting", "progress": 25})
    
    # Step 2: Enter credentials
    time.sleep(1.5)
    log("🔑 Entering credentials...")
    send_status_update("login_attempting", {"step": "credentials", "progress": 50})
    
    # Step 3: Submit login form
    time.sleep(2)
    log("📤 Submitting login form...")
    send_status_update("login_attempting", {"step": "submitting", "progress": 75})
    
    # Step 4: Verify login success
    time.sleep(1.5)
    log("✅ Login successful!")
    send_status_update("login_successful", {"step": "completed", "progress": 100})
    
    return True

def simulate_job_check_cycle(cycle_number: int) -> Dict[str, int]:
    """Simulate a single job checking cycle"""
    log(f"🔍 Starting job check cycle #{cycle_number}")
    send_status_update("checking_jobs", {"cycle": cycle_number, "step": "navigating"})
    
    # Simulate navigating to job board
    time.sleep(random.uniform(1, 2))
    log("📋 Navigating to job board...")
    send_status_update("checking_jobs", {"cycle": cycle_number, "step": "loading_jobs"})
    
    # Simulate loading jobs
    time.sleep(random.uniform(0.5, 1.5))
    
    # Simulate finding jobs (random number)
    jobs_found = random.randint(0, 5)
    log(f"📊 Found {jobs_found} available jobs")
    
    accepted = 0
    rejected = 0
    skipped = 0
    
    if jobs_found > 0:
        send_status_update("processing_jobs", {"cycle": cycle_number, "jobs_found": jobs_found})
        
        for i in range(jobs_found):
            time.sleep(random.uniform(0.5, 1.2))
            
            # Simulate job evaluation
            job_type = random.choice(["interpreting", "translation", "documentation"])
            language = random.choice(["Spanish", "French", "German", "Chinese", "Arabic"])
            
            # Simulate decision making (70% accept, 20% reject, 10% skip)
            decision = random.choices(
                ["accepted", "rejected", "skipped"], 
                weights=[70, 20, 10]
            )[0]
            
            if decision == "accepted":
                accepted += 1
                log(f"✅ Job {i+1} ({job_type} - {language}): ACCEPTED")
            elif decision == "rejected":
                rejected += 1
                reason = random.choice(["schedule conflict", "language not preferred", "rate too low"])
                log(f"❌ Job {i+1} ({job_type} - {language}): REJECTED - {reason}")
            else:
                skipped += 1
                log(f"⏭️ Job {i+1} ({job_type} - {language}): SKIPPED")
            
            # Send real-time update
            send_status_update("job_processed", {
                "cycle": cycle_number,
                "job_number": i + 1,
                "total_jobs": jobs_found,
                "accepted": accepted,
                "rejected": rejected,
                "skipped": skipped
            })
    else:
        log("📭 No jobs available at this time")
        send_status_update("no_jobs", {"cycle": cycle_number})
    
    log(f"🏁 Cycle #{cycle_number} completed: {accepted} accepted, {rejected} rejected, {skipped} skipped")
    
    return {
        "total_checks": 1,
        "accepted": accepted,
        "rejected": rejected,
        "skipped": skipped
    }

def simulate_bot_workflow():
    """Simulate the complete bot workflow"""
    global SESSION_ID
    
    log("🚀 Starting Smart AtoZ Bot...")
    send_status_update("starting", {"message": "Bot initialization complete"})
    
    # Step 1: Login Process
    if not simulate_login_process():
        log("❌ Login failed, stopping bot")
        send_status_update("login_failed", {"error": "Authentication failed"})
        return
    
    # Step 2: Job Checking Cycles
    log("🔄 Starting job checking cycles...")
    send_status_update("running", {"message": "Bot is now running and checking for jobs"})
    
    total_stats = {
        "total_checks": 0,
        "total_accepted": 0,
        "total_rejected": 0,
        "total_skipped": 0
    }
    
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            cycle_stats = simulate_job_check_cycle(cycle_count)
            
            # Update totals
            total_stats["total_checks"] += cycle_stats["total_checks"]
            total_stats["total_accepted"] += cycle_stats["accepted"]
            total_stats["total_rejected"] += cycle_stats["rejected"]
            total_stats["total_skipped"] += cycle_stats["skipped"]
            
            # Send summary update
            send_status_update("cycle_complete", {
                "cycle": cycle_count,
                "stats": total_stats
            })
            
            # Wait before next cycle (5-15 seconds)
            wait_time = random.uniform(5, 15)
            log(f"⏳ Waiting {wait_time:.1f}s before next cycle...")
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            log("🛑 Bot stopped by user")
            send_status_update("stopped", {"reason": "User interruption"})
            break
        except Exception as e:
            log(f"❌ Bot error: {e}")
            send_status_update("error", {"error": str(e)})
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    try:
        # Get session ID from command line if provided
        if len(sys.argv) > 1:
            SESSION_ID = sys.argv[1]
            log(f"Using session ID: {SESSION_ID}")
        
        simulate_bot_workflow()
    except KeyboardInterrupt:
        log("Bot stopped by user")
    except Exception as e:
        log(f"Bot error: {e}")
        sys.exit(1)
