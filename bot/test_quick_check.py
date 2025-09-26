#!/usr/bin/env python3
"""
Test script for the 10-second job checking functionality.
This script demonstrates how to use the new quick checking feature.
"""

import os
import sys
import time

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BOT_CONFIG
from quick_checker import run_quick_checker


def test_quick_check():
    """Test the quick check functionality"""
    print("=== Testing 10-Second Job Checking ===")
    print(f"Quick check interval: {BOT_CONFIG.get('quick_check_interval', 10)} seconds")
    print(f"Enable quick check: {BOT_CONFIG.get('enable_quick_check', False)}")
    print(f"Selected category: {BOT_CONFIG.get('accept_preconditions', {}).get('job_type', 'None')}")
    print()
    
    # Enable quick check for testing
    BOT_CONFIG["enable_quick_check"] = True
    BOT_CONFIG["bot_running"] = True
    
    print("Starting quick checker for 2 minutes...")
    print("Press Ctrl+C to stop early")
    print()
    
    try:
        # Run for 2 minutes as a test
        run_quick_checker(
            selected_category=BOT_CONFIG.get("accept_preconditions", {}).get("job_type", ""),
            duration_minutes=2
        )
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print(f"Test error: {e}")
    
    print("Test completed.")


def show_config():
    """Show current configuration"""
    print("=== Current Configuration ===")
    print(f"Main check interval: {BOT_CONFIG.get('check_interval', 0.5)} seconds")
    print(f"Quick check interval: {BOT_CONFIG.get('quick_check_interval', 10)} seconds")
    print(f"Enable quick check: {BOT_CONFIG.get('enable_quick_check', False)}")
    print(f"Selected job type: {BOT_CONFIG.get('accept_preconditions', {}).get('job_type', 'None')}")
    print(f"Exclude types: {BOT_CONFIG.get('accept_preconditions', {}).get('exclude_types', [])}")
    print()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "config":
        show_config()
    else:
        test_quick_check()
