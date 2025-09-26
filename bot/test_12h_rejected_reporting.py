#!/usr/bin/env python3
"""
Test script for 12-hour rejected job reporting functionality.
This script demonstrates how rejected jobs are reported every 12 hours.
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
                             print_accepted_job_report, print_detailed_stats,
                             set_login_status, update_activity)


def test_12h_rejected_reporting():
    """Test the 12-hour rejected job reporting functionality."""
    print("=== 12-Hour Rejected Job Reporting Test ===")
    print("This test demonstrates:")
    print("1. Rejected jobs are reported every 12 hours")
    print("2. Results are still reported every 5 seconds")
    print("3. Bot checks for jobs every 0.5 seconds")
    print()
    
    # Initialize tracker with 12-hour rejected reporting
    results_interval = BOT_CONFIG.get("results_report_interval", 5)
    rejected_interval = BOT_CONFIG.get("rejected_report_interval", 43200)  # 12 hours
    tracker = initialize_tracker(results_interval, rejected_interval)
    
    print(f"Configuration:")
    print(f"  Check interval: 0.5 seconds")
    print(f"  Results reporting: every {results_interval}s")
    print(f"  Rejected reporting: every {rejected_interval/3600:.1f} hours")
    print()
    
    # Simulate login
    print("🔐 Simulating login process...")
    set_login_status("Login successful", True)
    print("✅ Login successful! Bot is now monitoring for jobs...")
    print()
    
    print("🚀 Starting simulation for 2 minutes...")
    print("Note: Rejected jobs will only be reported after 12 hours,")
    print("but we'll simulate some rejected jobs to show the tracking.")
    print("Press Ctrl+C to stop early")
    print()
    
    start_time = time.time()
    cycle_count = 0
    
    try:
        while time.time() - start_time < 120:  # Run for 2 minutes
            cycle_count += 1
            
            # Simulate job processing every 5-10 seconds
            if random.random() < 0.2:  # 20% chance each cycle
                simulate_job_processing()
                update_activity()
            
            # Increment check cycle (every 0.5s)
            increment_check_cycle()
            
            # Report rejected jobs (every 12 hours - won't trigger in 2 minutes)
            check_and_report_rejected()
            
            # Report results (every 5s)
            check_and_report()
            
            # Log status every 20 cycles (10 seconds)
            if cycle_count % 20 == 0:
                elapsed = time.time() - start_time
                print(f"🔍 Bot Status: Running for {elapsed:.1f}s, Checked {cycle_count} times")
                print(f"   Rejected jobs will be reported in {(rejected_interval - elapsed):.0f} seconds")
            
            time.sleep(0.5)  # 0.5-second interval
            
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
    
    print(f"\n📊 Simulation completed after {cycle_count} check cycles")
    print("Final results:")
    print_detailed_stats()
    
    # Show accepted job report
    print_accepted_job_report()


def simulate_job_processing():
    """Simulate realistic job processing with proper validation."""
    languages = ["Spanish", "French", "German", "Italian", "Portuguese", "Arabic", "Chinese", "Japanese"]
    job_types = ["Telephone interpreting", "Face-to-Face", "Video interpreting", "Onsite"]
    
    # Simulate finding a job
    job = {
        "ref": f"JOB-{random.randint(10000, 99999)}",
        "language": random.choice(languages),
        "appt_date": datetime.now().strftime("%Y-%m-%d"),
        "appt_time": f"{random.randint(8, 20):02d}:{random.choice(['00', '15', '30', '45'])}",
        "duration": f"{random.choice([30, 45, 60, 90])} minutes",
        "submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "matched"
    }
    
    # Simulate job type validation
    job_type = random.choice(job_types)
    
    if job_type == "Telephone interpreting":
        # Accept telephone translation jobs
        add_accepted_job(job)
        print(f"🎉 ACCEPTED: Job {job['ref']} - {job['language']} - {job['appt_date']} {job['appt_time']} (Telephone Translation)")
    else:
        # Reject face-to-face and other types
        reason = f"{job_type} (not telephone translation)"
        add_rejected_job(job, reason)
        print(f"❌ REJECTED: Job {job['ref']} - {job['language']} - {job['appt_date']} {job['appt_time']} ({reason})")


def test_manual_rejected_report():
    """Test manually triggering a rejected job report."""
    print("=== Manual Rejected Job Report Test ===")
    
    # Initialize tracker
    tracker = initialize_tracker(5, 43200)  # 5s for results, 12h for rejected
    
    print("Adding some rejected jobs manually...")
    
    # Simulate login
    set_login_status("Login successful", True)
    
    # Add some rejected jobs
    rejected_jobs = [
        {
            "ref": "F2F-001",
            "language": "German",
            "appt_date": "2024-01-15",
            "appt_time": "09:15",
            "duration": "90 minutes",
            "submitted": "2024-01-15 12:00",
            "status": "matched"
        },
        {
            "ref": "VID-001",
            "language": "Italian",
            "appt_date": "2024-01-16",
            "appt_time": "11:00",
            "duration": "30 minutes",
            "submitted": "2024-01-15 13:00",
            "status": "matched"
        },
        {
            "ref": "ONS-001",
            "language": "Portuguese",
            "appt_date": "2024-01-16",
            "appt_time": "15:30",
            "duration": "60 minutes",
            "submitted": "2024-01-15 14:00",
            "status": "matched"
        }
    ]
    
    print("Adding rejected jobs...")
    for i, job in enumerate(rejected_jobs, 1):
        reason = f"Test rejection reason {i}"
        add_rejected_job(job, reason)
        print(f"❌ Added rejected job: {job['ref']} - {job['language']} ({reason})")
        time.sleep(0.5)
    
    print("\nManually triggering rejected job report...")
    # Manually trigger the rejected job report
    tracker.report_rejected_jobs()
    
    print("\nFinal detailed stats:")
    print_detailed_stats()


def show_config():
    """Show current configuration."""
    print("=== 12-Hour Rejected Reporting Configuration ===")
    print(f"Check interval: {BOT_CONFIG.get('check_interval', 0.5)} seconds")
    print(f"Results report interval: {BOT_CONFIG.get('results_report_interval', 5)} seconds")
    rejected_interval = BOT_CONFIG.get('rejected_report_interval', 43200)
    print(f"Rejected report interval: {rejected_interval/3600:.1f} hours")
    print(f"Enable results reporting: {BOT_CONFIG.get('enable_results_reporting', True)}")
    print(f"Enable rejected reporting: {BOT_CONFIG.get('enable_rejected_reporting', True)}")
    print(f"Quick check interval: {BOT_CONFIG.get('quick_check_interval', 10)} seconds")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "config":
            show_config()
        elif sys.argv[1] == "manual":
            test_manual_rejected_report()
        else:
            print("Usage: python test_12h_rejected_reporting.py [config|manual]")
            print("  config  - Show current configuration")
            print("  manual  - Test manual rejected job report")
            print("  (no arg) - Run 12-hour rejected reporting test")
    else:
        test_12h_rejected_reporting()
