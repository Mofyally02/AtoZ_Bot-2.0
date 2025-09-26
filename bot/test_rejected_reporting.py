#!/usr/bin/env python3
"""
Test script for the rejected job reporting functionality.
This script demonstrates how the rejected job tracking and 0.5-second reporting works.
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
                             print_detailed_stats)


def simulate_job_processing():
    """Simulate job processing with both accepted and rejected jobs."""
    languages = ["Spanish", "French", "German", "Italian", "Portuguese", "Arabic", "Chinese", "Japanese"]
    rejection_reasons = [
        "Face-to-face job",
        "Missing required fields",
        "Wrong job type",
        "Language not supported",
        "Time conflict",
        "Location not available"
    ]
    
    # Simulate processing a job (accepted or rejected)
    job = {
        "ref": f"TEST-{random.randint(10000, 99999)}",
        "language": random.choice(languages),
        "appt_date": datetime.now().strftime("%Y-%m-%d"),
        "appt_time": f"{random.randint(8, 20):02d}:{random.choice(['00', '15', '30', '45'])}",
        "duration": f"{random.choice([30, 45, 60, 90])} minutes",
        "submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "matched"
    }
    
    # 70% chance of rejection, 30% chance of acceptance
    if random.random() < 0.7:
        reason = random.choice(rejection_reasons)
        add_rejected_job(job, reason)
        print(f"❌ Simulated rejecting job: {job['ref']} - {job['language']} - {job['appt_date']} {job['appt_time']} (Reason: {reason})")
    else:
        add_accepted_job(job)
        print(f"✅ Simulated accepting job: {job['ref']} - {job['language']} - {job['appt_date']} {job['appt_time']}")


def test_rejected_reporting():
    """Test the rejected job reporting functionality."""
    print("=== Testing Rejected Job Reporting ===")
    
    # Initialize tracker with 0.5-second rejected reporting
    results_interval = BOT_CONFIG.get("results_report_interval", 5)
    rejected_interval = BOT_CONFIG.get("rejected_report_interval", 0.5)
    tracker = initialize_tracker(results_interval, rejected_interval)
    
    print(f"Results reporting interval: {results_interval} seconds")
    print(f"Rejected jobs reporting interval: {rejected_interval} seconds")
    print(f"Enable rejected reporting: {BOT_CONFIG.get('enable_rejected_reporting', True)}")
    print()
    
    print("Starting simulation for 15 seconds...")
    print("Jobs will be processed randomly, and reports will be generated:")
    print("- Rejected jobs: every 0.5 seconds")
    print("- Accepted jobs: every 5 seconds")
    print("Press Ctrl+C to stop early")
    print()
    
    start_time = time.time()
    last_job_time = 0
    
    try:
        while time.time() - start_time < 15:  # Run for 15 seconds
            current_time = time.time()
            
            # Simulate processing a job every 1-3 seconds
            if current_time - last_job_time >= random.uniform(1, 3):
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
    
    print("\n" + "="*70)
    print("FINAL RESULTS SUMMARY")
    print("="*70)
    print_detailed_stats()


def test_manual_job_processing():
    """Test manually adding accepted and rejected jobs."""
    print("=== Manual Job Processing Test ===")
    
    # Initialize tracker
    tracker = initialize_tracker(3, 0.5)  # 3s for accepted, 0.5s for rejected
    
    print("Adding jobs manually...")
    
    # Add some test accepted jobs
    accepted_jobs = [
        {
            "ref": "TEST-ACCEPT-001",
            "language": "Spanish",
            "appt_date": "2024-01-15",
            "appt_time": "14:30",
            "duration": "60 minutes",
            "submitted": "2024-01-15 10:00",
            "status": "matched"
        },
        {
            "ref": "TEST-ACCEPT-002",
            "language": "French",
            "appt_date": "2024-01-15",
            "appt_time": "16:00",
            "duration": "45 minutes",
            "submitted": "2024-01-15 11:30",
            "status": "matched"
        }
    ]
    
    # Add some test rejected jobs
    rejected_jobs = [
        {
            "ref": "TEST-REJECT-001",
            "language": "German",
            "appt_date": "2024-01-15",
            "appt_time": "09:15",
            "duration": "90 minutes",
            "submitted": "2024-01-15 12:00",
            "status": "matched"
        },
        {
            "ref": "TEST-REJECT-002",
            "language": "Italian",
            "appt_date": "2024-01-16",
            "appt_time": "11:00",
            "duration": "30 minutes",
            "submitted": "2024-01-15 13:00",
            "status": "matched"
        },
        {
            "ref": "TEST-REJECT-003",
            "language": "Portuguese",
            "appt_date": "2024-01-16",
            "appt_time": "15:30",
            "duration": "60 minutes",
            "submitted": "2024-01-15 14:00",
            "status": "matched"
        }
    ]
    
    print("Adding accepted jobs...")
    for job in accepted_jobs:
        add_accepted_job(job)
        print(f"Added accepted job: {job['ref']} - {job['language']}")
        time.sleep(0.5)
    
    print("\nAdding rejected jobs...")
    for i, job in enumerate(rejected_jobs, 1):
        reason = f"Test rejection reason {i}"
        add_rejected_job(job, reason)
        print(f"Added rejected job: {job['ref']} - {job['language']} (Reason: {reason})")
        time.sleep(0.5)
    
    print("\nWaiting for reports...")
    time.sleep(2)  # Wait for reports to trigger
    
    print("\nFinal detailed stats:")
    print_detailed_stats()


def test_check_cycles():
    """Test the check cycle tracking functionality."""
    print("=== Check Cycle Tracking Test ===")
    
    # Initialize tracker
    tracker = initialize_tracker(1, 0.5)  # 1s for accepted, 0.5s for rejected
    
    print("Simulating check cycles every 0.5 seconds for 10 seconds...")
    print("This will show how the check cycle counter increments")
    print()
    
    start_time = time.time()
    cycle_count = 0
    
    try:
        while time.time() - start_time < 10:  # Run for 10 seconds
            increment_check_cycle()
            cycle_count += 1
            
            # Report rejected jobs every 0.5s
            check_and_report_rejected()
            
            # Report accepted jobs every 1s
            check_and_report()
            
            time.sleep(0.5)  # Wait 0.5 seconds between cycles
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    
    print(f"\nCompleted {cycle_count} check cycles in 10 seconds")
    print("Final detailed stats:")
    print_detailed_stats()


def show_config():
    """Show current configuration."""
    print("=== Current Rejected Job Reporting Configuration ===")
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
        elif sys.argv[1] == "manual":
            test_manual_job_processing()
        elif sys.argv[1] == "cycles":
            test_check_cycles()
        else:
            print("Usage: python test_rejected_reporting.py [config|manual|cycles]")
            print("  config  - Show current configuration")
            print("  manual  - Test manual job processing")
            print("  cycles  - Test check cycle tracking")
            print("  (no arg) - Run simulation test")
    else:
        test_rejected_reporting()
