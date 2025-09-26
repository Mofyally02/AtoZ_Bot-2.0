#!/usr/bin/env python3
"""
Test script for continuous bot operation with real-time reporting.
This script demonstrates the bot's continuous operation with 0.5-second intervals,
unified reporting, and proper job validation (telephone vs face-to-face).
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


def simulate_continuous_operation():
    """Simulate continuous bot operation with realistic job processing."""
    print("=== Continuous Bot Operation Simulation ===")
    print("This simulation demonstrates:")
    print("1. Continuous operation with 0.5-second intervals")
    print("2. Unified reporting showing accepted and rejected jobs together")
    print("3. Proper job validation (telephone vs face-to-face)")
    print("4. Real-time highlighting of job acceptance")
    print()
    
    # Initialize tracker with 12-hour rejected reporting
    results_interval = BOT_CONFIG.get("results_report_interval", 5)
    rejected_interval = BOT_CONFIG.get("rejected_report_interval", 43200)
    tracker = initialize_tracker(results_interval, rejected_interval)
    
    print(f"Configuration:")
    print(f"  Check interval: 0.5 seconds")
    print(f"  Results reporting: every {results_interval}s")
    print(f"  Rejected reporting: every {rejected_interval/3600:.1f} hours")
    print()
    
    # Simulate login
    print("🔐 Simulating login process...")
    set_login_status("Attempting login...", False)
    time.sleep(1)
    set_login_status("Login successful", True)
    print("✅ Login successful! Bot is now monitoring for jobs...")
    print()
    
    print("🚀 Starting continuous operation for 30 seconds...")
    print("The bot will:")
    print("- Check for jobs every 0.5 seconds")
    print("- Accept telephone translation jobs")
    print("- Reject face-to-face jobs")
    print("- Report results every 5 seconds")
    print("- Report rejected jobs every 12 hours")
    print("Press Ctrl+C to stop early")
    print()
    
    start_time = time.time()
    cycle_count = 0
    
    try:
        while time.time() - start_time < 30:  # Run for 30 seconds
            cycle_count += 1
            
            # Simulate job processing every 2-5 seconds
            if random.random() < 0.3:  # 30% chance of finding a job each cycle
                simulate_job_processing()
                update_activity()
            
            # Increment check cycle (every 0.5s)
            increment_check_cycle()
            
            # Report rejected jobs (every 0.5s)
            check_and_report_rejected()
            
            # Report results (every 5s)
            check_and_report()
            
            # Log status every 10 cycles (5 seconds)
            if cycle_count % 10 == 0:
                elapsed = time.time() - start_time
                print(f"🔍 Bot Status: Running for {elapsed:.1f}s, Checked {cycle_count} times")
            
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


def test_unified_reporting():
    """Test the unified reporting functionality."""
    print("=== Unified Reporting Test ===")
    
    # Initialize tracker
    tracker = initialize_tracker(2, 43200)  # 2s for results, 12h for rejected
    
    print("Testing unified reporting with mixed job types...")
    
    # Simulate login
    set_login_status("Login successful", True)
    
    # Add some accepted jobs
    accepted_jobs = [
        {
            "ref": "TEL-001",
            "language": "Spanish",
            "appt_date": "2024-01-15",
            "appt_time": "14:30",
            "duration": "60 minutes",
            "submitted": "2024-01-15 10:00",
            "status": "matched"
        },
        {
            "ref": "TEL-002",
            "language": "French",
            "appt_date": "2024-01-15",
            "appt_time": "16:00",
            "duration": "45 minutes",
            "submitted": "2024-01-15 11:30",
            "status": "matched"
        }
    ]
    
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
        }
    ]
    
    print("Adding accepted jobs (telephone translations)...")
    for job in accepted_jobs:
        add_accepted_job(job)
        print(f"✅ Added: {job['ref']} - {job['language']}")
        time.sleep(0.5)
    
    print("\nAdding rejected jobs (face-to-face/video)...")
    for i, job in enumerate(rejected_jobs, 1):
        reason = "Face-to-face job" if "F2F" in job['ref'] else "Video interpreting (not telephone)"
        add_rejected_job(job, reason)
        print(f"❌ Added: {job['ref']} - {job['language']} ({reason})")
        time.sleep(0.5)
    
    print("\nGenerating unified report...")
    time.sleep(1)  # Wait for report to trigger
    check_and_report()
    
    print("\nFinal detailed statistics:")
    print_detailed_stats()


def test_continuous_monitoring():
    """Test continuous monitoring with realistic intervals."""
    print("=== Continuous Monitoring Test ===")
    
    # Initialize tracker
    tracker = initialize_tracker(3, 43200)  # 3s for results, 12h for rejected
    
    print("Testing continuous monitoring with 0.5-second intervals...")
    print("This will show how the bot continuously checks and reports...")
    
    # Simulate login
    set_login_status("Login successful", True)
    
    start_time = time.time()
    cycle_count = 0
    
    try:
        while time.time() - start_time < 15:  # Run for 15 seconds
            cycle_count += 1
            
            # Simulate occasional job processing
            if random.random() < 0.2:  # 20% chance each cycle
                simulate_job_processing()
                update_activity()
            
            # Increment check cycle
            increment_check_cycle()
            
            # Report rejected jobs
            check_and_report_rejected()
            
            # Report results
            check_and_report()
            
            time.sleep(0.5)  # 0.5-second interval
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    
    print(f"\nCompleted {cycle_count} check cycles in 15 seconds")
    print("Final results:")
    print_detailed_stats()


def show_config():
    """Show current configuration."""
    print("=== Continuous Operation Configuration ===")
    print(f"Check interval: {BOT_CONFIG.get('check_interval', 0.5)} seconds")
    print(f"Results report interval: {BOT_CONFIG.get('results_report_interval', 5)} seconds")
    rejected_interval = BOT_CONFIG.get('rejected_report_interval', 43200)
    if rejected_interval >= 3600:
        print(f"Rejected report interval: {rejected_interval/3600:.1f} hours")
    else:
        print(f"Rejected report interval: {rejected_interval} seconds")
    print(f"Enable results reporting: {BOT_CONFIG.get('enable_results_reporting', True)}")
    print(f"Enable rejected reporting: {BOT_CONFIG.get('enable_rejected_reporting', True)}")
    print(f"Quick check interval: {BOT_CONFIG.get('quick_check_interval', 10)} seconds")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "config":
            show_config()
        elif sys.argv[1] == "unified":
            test_unified_reporting()
        elif sys.argv[1] == "monitoring":
            test_continuous_monitoring()
        else:
            print("Usage: python test_continuous_operation.py [config|unified|monitoring]")
            print("  config     - Show current configuration")
            print("  unified    - Test unified reporting")
            print("  monitoring - Test continuous monitoring")
            print("  (no arg)   - Run full continuous operation simulation")
    else:
        simulate_continuous_operation()
