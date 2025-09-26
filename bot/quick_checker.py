"""
Quick job checker module for 10-second interval job monitoring.
This module provides functionality to check for jobs matching specific categories
every 10 seconds without the overhead of full job processing.
"""

import time
from typing import Optional
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright

from config import (ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH, ATOZ_PASSWORD,
                    ATOZ_USERNAME, BOT_CONFIG)
from data_processor import quick_job_check_cycle
from login_handler import perform_login


def log(message: str) -> None:
    """Log message with timestamp."""
    print(f"[QuickChecker] {message}")


def run_quick_checker(selected_category: str = None, duration_minutes: int = None):
    """
    Run the quick job checker for a specified duration or indefinitely.
    
    Args:
        selected_category: The job category to filter by (e.g., "Telephone interpreting")
        duration_minutes: How long to run in minutes (None for indefinite)
    """
    jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
    quick_interval = BOT_CONFIG.get("quick_check_interval", 10)
    
    log(f"Starting quick checker with {quick_interval}s interval")
    log(f"Filtering for category: {selected_category or 'All matched jobs'}")
    
    if duration_minutes:
        log(f"Will run for {duration_minutes} minutes")
    
    start_time = time.time()
    total_checks = 0
    total_matches = 0
    
    with sync_playwright() as p:
        headless = BOT_CONFIG.get("headless", True)
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        # Login once at startup
        log("Logging in...")
        page.goto(jobs_url, wait_until="networkidle")
        perform_login(page, ATOZ_BASE_URL, {"username": ATOZ_USERNAME, "password": ATOZ_PASSWORD})
        log("Login complete. Starting quick job monitoring...")
        
        # Quick checking loop
        while True:
            try:
                # Check if we should stop based on duration
                if duration_minutes:
                    elapsed_minutes = (time.time() - start_time) / 60
                    if elapsed_minutes >= duration_minutes:
                        log(f"Duration limit reached ({duration_minutes} minutes). Stopping.")
                        break
                
                # Perform quick check
                matches = quick_job_check_cycle(page, jobs_url, selected_category)
                total_checks += 1
                total_matches += matches
                
                if matches > 0:
                    log(f"Check #{total_checks}: Found {matches} matching jobs")
                else:
                    log(f"Check #{total_checks}: No matching jobs found")
                
                # Wait for next check
                time.sleep(quick_interval)
                
            except KeyboardInterrupt:
                log("Stopped by user")
                break
            except Exception as e:
                log(f"Error in quick check cycle: {e}")
                time.sleep(quick_interval)  # Wait before retrying
        
        log(f"Quick checker stopped. Total checks: {total_checks}, Total matches: {total_matches}")
        context.close()
        browser.close()


def run_quick_checker_with_bot(selected_category: str = None):
    """
    Run quick checker alongside the main bot.
    This function can be called from the main bot loop to add 10-second checking.
    """
    if not BOT_CONFIG.get("enable_quick_check", False):
        return
    
    quick_interval = BOT_CONFIG.get("quick_check_interval", 10)
    jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
    
    # This would be called from within the main bot's page context
    # The page object should be passed from the calling function
    pass


if __name__ == "__main__":
    # Example usage
    import sys
    
    category = None
    duration = None
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        category = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            duration = int(sys.argv[2])
        except ValueError:
            print("Invalid duration. Using indefinite run.")
    
    run_quick_checker(selected_category=category, duration_minutes=duration)
