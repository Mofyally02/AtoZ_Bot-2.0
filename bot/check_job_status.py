#!/usr/bin/env python3
"""
Quick script to check current job acceptance status.
"""

import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from results_tracker import (get_tracker, print_accepted_job_report,
                             print_detailed_stats)


def check_job_status():
    """Check current job acceptance status."""
    print("=== Current Job Status ===")
    
    try:
        tracker = get_tracker()
        
        print(f"✅ Jobs Accepted: {tracker.total_accepted}")
        print(f"🚫 Jobs Rejected: {tracker.total_rejected}")
        print(f"📈 Total Processed: {tracker.total_accepted + tracker.total_rejected}")
        print(f"⏱️  Session Duration: {(tracker.last_activity_time - tracker.session_start_time) / 60:.1f} minutes" if tracker.last_activity_time else "No activity yet")
        print(f"🔄 Check Cycles: {tracker.check_cycles}")
        print(f"🔐 Login Status: {tracker.login_status}")
        
        if tracker.total_accepted > 0:
            print(f"\n📋 Recent Accepted Jobs:")
            for i, job in enumerate(tracker.accepted_jobs[-5:], 1):  # Show last 5
                print(f"  {i}. Job {job.get('ref', 'N/A')}: {job.get('language', 'N/A')} - {job.get('appt_date', 'N/A')} {job.get('appt_time', 'N/A')}")
                print(f"     Accepted at: {job.get('accepted_at', 'N/A')}")
        
        if tracker.total_rejected > 0:
            print(f"\n📋 Recent Rejected Jobs:")
            for i, job in enumerate(tracker.rejected_jobs[-5:], 1):  # Show last 5
                print(f"  {i}. Job {job.get('ref', 'N/A')}: {job.get('language', 'N/A')} - {job.get('appt_date', 'N/A')} {job.get('appt_time', 'N/A')}")
                print(f"     Reason: {job.get('rejection_reason', 'Unknown')}")
        
        # Show detailed accepted job report if there are accepted jobs
        if tracker.total_accepted > 0:
            print(f"\n{'='*60}")
            print("Would you like to see the detailed Accepted Job Report? (y/n): ", end="")
            try:
                response = input().lower().strip()
                if response in ['y', 'yes']:
                    print_accepted_job_report()
            except KeyboardInterrupt:
                print("\nSkipping detailed report.")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the bot has been initialized first.")

if __name__ == "__main__":
    check_job_status()
