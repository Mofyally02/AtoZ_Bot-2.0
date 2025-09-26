#!/usr/bin/env python3
"""
Script to show the detailed Accepted Job Report.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from results_tracker import get_tracker, print_accepted_job_report


def show_accepted_jobs():
    """Show the detailed accepted job report."""
    print("=== Accepted Job Report ===")
    
    try:
        tracker = get_tracker()
        
        if tracker.total_accepted == 0:
            print("❌ No jobs have been accepted yet.")
            print("Make sure the bot has been running and has accepted some jobs.")
            return
            
        print_accepted_job_report()
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the bot has been initialized first.")

if __name__ == "__main__":
    show_accepted_jobs()
