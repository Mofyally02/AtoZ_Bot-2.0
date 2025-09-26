#!/usr/bin/env python3
"""
Enhanced test script for the comprehensive reporting functionality.
This script demonstrates login status tracking, job acceptance/rejection reporting,
and session period tracking with 0.5-second intervals.
"""

import os
import random
import sys
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BOT_CONFIG
from results_tracker import (add_accepted_job, add_rejected_job,
                             check_and_report, check_and_report_rejected,
                             increment_check_cycle, initialize_tracker,
                             print_detailed_stats, set_login_status,
                             update_activity)


def simulate_login_process():
    """Simulate the login process with status tracking."""
    print("🔐 Simulating login process...")
    
    # Simulate login attempt
    set_login_status("Attempting login...", False)
    time.sleep(1)
    
    # Simulate successful login (90% success rate)
    if random.random() < 0.9:
        set_login_status("Login successful", True)
        print("✅ Login successful!")
        return True
    else:
        set_login_status("Login failed: Invalid credentials", False)
        print("❌ Login failed!")
        return False


def simulate_job_processing():
    """Simulate job processing with both accepted and rejected jobs."""
    languages = ["Spanish", "French", "German", "Italian", "Portuguese", "Arabic", "Chinese", "Japanese"]
    rejection_reasons = [
        "Face-to-face job",
        "Missing required fields", 
        "Wrong job type",
        "Language not supported",
        "Time conflict",
        "Location not available",
        "Duplicate job",
        "System error"
    ]
    
    # Simulate processing a job (accepted or rejected)
    job = {
        "ref": f"JOB-{random.randint(10000, 99999)}",
        "language": random.choice(languages),
        "appt_date": datetime.now().strftime("%Y-%m-%d"),
        "appt_time": f"{random.randint(8, 20):02d}:{random.choice(['00', '15', '30', '45'])}",
        "duration": f"{random.choice([30, 45, 60, 90])} minutes",
        "submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "matched"
    }
    
    # 60% chance of rejection, 40% chance of acceptance
    if random.random() < 0.6:
        reason = random.choice(rejection_reasons)
        add_rejected_job(job, reason)
        print(f"❌ Rejected: {job['ref']} - {job['language']} - {job['appt_date']} {job['appt_time']} (Reason: {reason})")
    else:
        add_accepted_job(job)
        print(f"✅ Accepted: {job['ref']} - {job['language']} - {job['appt_date']} {job['appt_time']}")
    
    # Update activity
    update_activity()


def test_enhanced_reporting():
    """Test the enhanced reporting functionality with login status and job tracking."""
    print("=== Enhanced Reporting Test ===")
    print("This test demonstrates:")
    print("1. Login status tracking")
    print("2. Jobs accepted/rejected reporting")
    print("3. Session period tracking with 0.5s intervals")
    print("4. Comprehensive statistics")
    print()
    
    # Initialize tracker with enhanced intervals
    results_interval = BOT_CONFIG.get("results_report_interval", 5)
    rejected_interval = BOT_CONFIG.get("rejected_report_interval", 0.5)
    tracker = initialize_tracker(results_interval, rejected_interval)
    
    print(f"Configuration:")
    print(f"  Results reporting: every {results_interval}s")
    print(f"  Rejected reporting: every {rejected_interval}s")
    print(f"  Check cycles: every 0.5s")
    print()
    
    # Simulate login
    login_success = simulate_login_process()
    if not login_success:
        print("❌ Login failed, cannot proceed with job processing")
        return
    
    print("\nStarting job processing simulation for 20 seconds...")
    print("Reports will show:")
    print("- Login status and timing")
    print("- Jobs accepted/rejected counts")
    print("- Session periods with check cycles")
    print("- Activity tracking")
    print("Press Ctrl+C to stop early")
    print()
    
    start_time = time.time()
    last_job_time = 0
    
    try:
        while time.time() - start_time < 20:  # Run for 20 seconds
            current_time = time.time()
            
            # Simulate processing a job every 2-4 seconds
            if current_time - last_job_time >= random.uniform(2, 4):
                simulate_job_processing()
                last_job_time = current_time
            
            # Increment check cycle (simulating 0.5s intervals)
            increment_check_cycle()
            
            # Check and report rejected jobs (every 0.5s)
            check_and_report_rejected()
            
            # Check and report accepted jobs (every 5s)
            check_and_report()
            
            time.sleep(0.1)  # Small delay to prevent excessive CPU usage
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    
    print("\n" + "="*80)
    print("FINAL COMPREHENSIVE RESULTS")
    print("="*80)
    print_detailed_stats()


def test_login_scenarios():
    """Test different login scenarios."""
    print("=== Login Scenarios Test ===")
    
    # Initialize tracker
    tracker = initialize_tracker(2, 0.5)
    
    print("Testing different login scenarios...")
    
    # Scenario 1: Successful login
    print("\n1. Testing successful login...")
    set_login_status("Attempting login...", False)
    time.sleep(0.5)
    set_login_status("Login successful", True)
    time.sleep(1)
    
    # Add some jobs
    for i in range(3):
        job = {
            "ref": f"SUCCESS-{i+1:03d}",
            "language": "Spanish",
            "appt_date": "2024-01-15",
            "appt_time": f"{10+i}:00",
            "duration": "60 minutes",
            "submitted": "2024-01-15 09:00",
            "status": "matched"
        }
        add_accepted_job(job)
        increment_check_cycle()
        time.sleep(0.5)
    
    check_and_report()
    
    # Scenario 2: Failed login
    print("\n2. Testing failed login...")
    set_login_status("Login failed: Network timeout", False)
    time.sleep(1)
    
    check_and_report()
    
    # Scenario 3: Re-login attempt
    print("\n3. Testing re-login attempt...")
    set_login_status("Attempting re-login...", False)
    time.sleep(0.5)
    set_login_status("Re-login successful", True)
    time.sleep(1)
    
    # Add more jobs
    for i in range(2):
        job = {
            "ref": f"RETRY-{i+1:03d}",
            "language": "French",
            "appt_date": "2024-01-15",
            "appt_time": f"{14+i}:30",
            "duration": "45 minutes",
            "submitted": "2024-01-15 10:00",
            "status": "matched"
        }
        add_accepted_job(job)
        increment_check_cycle()
        time.sleep(0.5)
    
    check_and_report()
    
    print("\nFinal results:")
    print_detailed_stats()


def test_activity_tracking():
    """Test activity tracking functionality."""
    print("=== Activity Tracking Test ===")
    
    # Initialize tracker
    tracker = initialize_tracker(1, 0.5)
    
    print("Testing activity tracking...")
    print("This will show how activity timestamps are updated")
    print()
    
    # Simulate login
    set_login_status("Login successful", True)
    
    start_time = time.time()
    
    try:
        while time.time() - start_time < 10:  # Run for 10 seconds
            # Simulate activity every 2 seconds
            if int(time.time() - start_time) % 2 == 0:
                update_activity()
                print(f"🔄 Activity updated at {time.time() - start_time:.1f}s")
            
            # Add some jobs occasionally
            if random.random() < 0.3:
                job = {
                    "ref": f"ACT-{random.randint(100, 999)}",
                    "language": "German",
                    "appt_date": "2024-01-15",
                    "appt_time": "15:00",
                    "duration": "60 minutes",
                    "submitted": "2024-01-15 12:00",
                    "status": "matched"
                }
                if random.random() < 0.5:
                    add_accepted_job(job)
                else:
                    add_rejected_job(job, "Test rejection")
            
            increment_check_cycle()
            check_and_report()
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    
    print("\nFinal activity results:")
    print_detailed_stats()


def show_config():
    """Show current configuration."""
    print("=== Enhanced Reporting Configuration ===")
    print(f"Results report interval: {BOT_CONFIG.get('results_report_interval', 5)} seconds")
    print(f"Rejected report interval: {BOT_CONFIG.get('rejected_report_interval', 0.5)} seconds")
    print(f"Enable results reporting: {BOT_CONFIG.get('enable_results_reporting', True)}")
    print(f"Enable rejected reporting: {BOT_CONFIG.get('enable_rejected_reporting', True)}")
    print(f"Main check interval: {BOT_CONFIG.get('check_interval', 0.5)} seconds")
    print(f"Quick check interval: {BOT_CONFIG.get('quick_check_interval', 10)} seconds")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "config":
            show_config()
        elif sys.argv[1] == "login":
            test_login_scenarios()
        elif sys.argv[1] == "activity":
            test_activity_tracking()
        else:
            print("Usage: python test_enhanced_reporting.py [config|login|activity]")
            print("  config   - Show current configuration")
            print("  login    - Test login scenarios")
            print("  activity - Test activity tracking")
            print("  (no arg) - Run full enhanced reporting test")
    else:
        test_enhanced_reporting()
