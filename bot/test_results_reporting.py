#!/usr/bin/env python3
"""
Test script for the 5-second results reporting functionality.
This script demonstrates how the results tracking and reporting works.
"""

import os
import random
import sys
import time
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BOT_CONFIG
from results_tracker import (add_accepted_job, check_and_report,
                             initialize_tracker, print_detailed_stats)


def simulate_job_acceptance():
    """Simulate accepting jobs for testing purposes."""
    languages = ["Spanish", "French", "German", "Italian", "Portuguese", "Arabic", "Chinese", "Japanese"]
    
    # Simulate accepting a job
    job = {
        "ref": f"TEST-{random.randint(10000, 99999)}",
        "language": random.choice(languages),
        "appt_date": datetime.now().strftime("%Y-%m-%d"),
        "appt_time": f"{random.randint(8, 20):02d}:{random.choice(['00', '15', '30', '45'])}",
        "duration": f"{random.choice([30, 45, 60, 90])} minutes",
        "submitted": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "status": "matched"
    }
    
    add_accepted_job(job)
    print(f"✅ Simulated accepting job: {job['ref']} - {job['language']} - {job['appt_date']} {job['appt_time']}")


def test_results_reporting():
    """Test the results reporting functionality."""
    print("=== Testing 5-Second Results Reporting ===")
    
    # Initialize tracker with 5-second interval
    results_interval = BOT_CONFIG.get("results_report_interval", 5)
    tracker = initialize_tracker(results_interval)
    
    print(f"Results reporting interval: {results_interval} seconds")
    print(f"Enable results reporting: {BOT_CONFIG.get('enable_results_reporting', True)}")
    print()
    
    print("Starting simulation for 30 seconds...")
    print("Jobs will be accepted randomly, and results will be reported every 5 seconds")
    print("Press Ctrl+C to stop early")
    print()
    
    start_time = time.time()
    last_job_time = 0
    
    try:
        while time.time() - start_time < 30:  # Run for 30 seconds
            current_time = time.time()
            
            # Simulate accepting a job every 2-8 seconds
            if current_time - last_job_time >= random.uniform(2, 8):
                simulate_job_acceptance()
                last_job_time = current_time
            
            # Check and report results
            check_and_report()
            
            time.sleep(0.5)  # Small delay to prevent excessive CPU usage
            
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    
    print("\n" + "="*60)
    print("FINAL RESULTS SUMMARY")
    print("="*60)
    print_detailed_stats()


def test_manual_job_adding():
    """Test manually adding jobs and checking reporting."""
    print("=== Manual Job Addition Test ===")
    
    # Initialize tracker
    tracker = initialize_tracker(3)  # 3-second interval for faster testing
    
    print("Adding jobs manually...")
    
    # Add some test jobs
    test_jobs = [
        {
            "ref": "TEST-12345",
            "language": "Spanish",
            "appt_date": "2024-01-15",
            "appt_time": "14:30",
            "duration": "60 minutes",
            "submitted": "2024-01-15 10:00",
            "status": "matched"
        },
        {
            "ref": "TEST-12346",
            "language": "French",
            "appt_date": "2024-01-15",
            "appt_time": "16:00",
            "duration": "45 minutes",
            "submitted": "2024-01-15 11:30",
            "status": "matched"
        },
        {
            "ref": "TEST-12347",
            "language": "German",
            "appt_date": "2024-01-16",
            "appt_time": "09:15",
            "duration": "90 minutes",
            "submitted": "2024-01-15 12:00",
            "status": "matched"
        }
    ]
    
    for job in test_jobs:
        add_accepted_job(job)
        print(f"Added job: {job['ref']} - {job['language']}")
        time.sleep(1)  # Wait 1 second between additions
    
    print("\nWaiting for results report...")
    time.sleep(4)  # Wait for the 3-second interval to trigger
    
    print("\nFinal detailed stats:")
    print_detailed_stats()


def show_config():
    """Show current configuration."""
    print("=== Current Results Reporting Configuration ===")
    print(f"Results report interval: {BOT_CONFIG.get('results_report_interval', 5)} seconds")
    print(f"Enable results reporting: {BOT_CONFIG.get('enable_results_reporting', True)}")
    print(f"Main check interval: {BOT_CONFIG.get('check_interval', 0.5)} seconds")
    print(f"Quick check interval: {BOT_CONFIG.get('quick_check_interval', 10)} seconds")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "config":
            show_config()
        elif sys.argv[1] == "manual":
            test_manual_job_adding()
        else:
            print("Usage: python test_results_reporting.py [config|manual]")
            print("  config  - Show current configuration")
            print("  manual  - Test manual job addition")
            print("  (no arg) - Run simulation test")
    else:
        test_results_reporting()
