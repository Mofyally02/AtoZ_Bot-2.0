import time
from urllib.parse import urljoin

import schedule

from config import ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH, BOT_CONFIG
from data_processor import quick_job_check_cycle
from results_tracker import (check_and_report, check_and_report_rejected,
                             initialize_tracker, set_login_status,
                             update_activity)
from run_once import run_once


def run_bot_cycle():
    if not BOT_CONFIG.get("bot_running", False):
        # Respect trigger flag; skip work until UI starts the bot
        return
    try:
        accepted = run_once()
        print(f"Processed cycle in background. Accepted: {accepted}")
    except Exception as e:
        print(f"Cycle error: {e}")


def run_quick_check_cycle():
    """Run a quick check cycle for job category matching"""
    if not BOT_CONFIG.get("bot_running", False):
        return
    
    if not BOT_CONFIG.get("enable_quick_check", False):
        return
        
    try:
        # This would need a page object from the main bot context
        # For now, we'll just log that quick check is enabled
        selected_category = BOT_CONFIG.get("accept_preconditions", {}).get("job_type", "")
        print(f"Quick check enabled for category: {selected_category}")
    except Exception as e:
        print(f"Quick check cycle error: {e}")


def main():
    interval = int(BOT_CONFIG.get("check_interval", 300))
    quick_interval = int(BOT_CONFIG.get("quick_check_interval", 10))
    results_interval = int(BOT_CONFIG.get("results_report_interval", 5))
    rejected_interval = float(BOT_CONFIG.get("rejected_report_interval", 0.5))
    enable_quick_check = BOT_CONFIG.get("enable_quick_check", False)
    enable_results_reporting = BOT_CONFIG.get("enable_results_reporting", True)
    enable_rejected_reporting = BOT_CONFIG.get("enable_rejected_reporting", True)
    
    # Initialize results tracker
    if enable_results_reporting or enable_rejected_reporting:
        initialize_tracker(results_interval, rejected_interval)
    
    schedule.every(interval).seconds.do(run_bot_cycle)
    
    if enable_quick_check:
        schedule.every(quick_interval).seconds.do(run_quick_check_cycle)
        print(f"Scheduler started. Main interval: {interval}s, Quick check: {quick_interval}s")
    else:
        print(f"Scheduler started. Interval: {interval}s")
    
    if enable_results_reporting:
        schedule.every(results_interval).seconds.do(check_and_report)
        print(f"Results reporting enabled: every {results_interval}s")
        
    if enable_rejected_reporting:
        schedule.every(rejected_interval).seconds.do(check_and_report_rejected)
        if rejected_interval >= 3600:  # If 1 hour or more
            hours = rejected_interval / 3600
            print(f"Rejected jobs reporting enabled: every {hours:.1f} hours")
        else:
            print(f"Rejected jobs reporting enabled: every {rejected_interval}s")
    
    run_bot_cycle()
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()


