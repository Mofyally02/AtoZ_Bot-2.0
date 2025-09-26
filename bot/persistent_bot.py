import time
from urllib.parse import urljoin

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from config import (ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH, ATOZ_PASSWORD,
                    ATOZ_USERNAME, BOT_CONFIG, MAX_ACCEPT_PER_RUN)
from data_processor import (accept_from_board, extract_jobs,
                            get_interpreter_details_text, is_all_params_set,
                            is_telephone_job, quick_job_check_cycle,
                            reject_on_detail)
from filter_handler import navigate_to_job_board
from login_handler import perform_login
from results_tracker import (add_accepted_job, add_rejected_job,
                             check_and_report, check_and_report_rejected,
                             increment_check_cycle, initialize_tracker,
                             print_accepted_job_report, set_login_status,
                             update_activity)


def log(message: str) -> None:
    print(f"[AtoZBot] {message}")


def persistent_bot_cycle(page, jobs_url: str) -> int:
    """Single cycle of job checking without login (assumes already logged in)"""
    try:
        # Navigate to job board (refresh)
        page.goto(jobs_url, wait_until="networkidle")
        
        # Extract and process jobs
        jobs = extract_jobs(page)
        
        accepted = 0
        for job in jobs:
            if accepted >= MAX_ACCEPT_PER_RUN:
                break
            
            # Only consider matched
            if "matched" not in (job.get("status", "").lower()):
                continue
                
            # Required fields present
            required = BOT_CONFIG.get("accept_preconditions", {}).get("required_fields", [])
            if required and not is_all_params_set(job, required):
                continue

            # Check job type on detail page
            pre = BOT_CONFIG.get("accept_preconditions", {})
            job_type = pre.get("job_type", "")
            exclude_types = pre.get("exclude_types", [])
            
            if not job.get("view_url"):
                continue
                
            if not is_telephone_job(page, job["view_url"], job_type, exclude_types):
                # If face to face, reject
                details_text = get_interpreter_details_text(page, job["view_url"]).lower()
                if any(ex in details_text for ex in [t.lower() for t in exclude_types]):
                    if reject_on_detail(page):
                        # Track rejected job
                        add_rejected_job(job, "Face-to-face job (not telephone translation)")
                        log(f"❌ REJECTED: Job {job['ref']} - Face-to-face job (not telephone translation)")
                    # Go back to board for next job
                    navigate_to_job_board(page, ATOZ_BASE_URL)
                continue

            # Accept from board
            navigate_to_job_board(page, ATOZ_BASE_URL)
            if not accept_from_board(page, job["ref"]):
                continue

            try:
                if page.is_visible("#24HourModal"):
                    page.click("#24HourModal #continueButton")
            except Exception:
                pass

            try:
                if page.is_visible("#cancelModal"):
                    page.fill("#cancelModal textarea[name='message']", "Accepting job via automation")
                    page.click("#cancelModal .modal-footer .btn.btn--primary")
            except Exception:
                pass

            page.wait_for_load_state("networkidle")
            accepted += 1
            
            # Track the accepted job
            add_accepted_job(job)
            log(f"🎉 ACCEPTED: Job {job['ref']} - {job.get('language', 'N/A')} - {job.get('appt_date', 'N/A')} {job.get('appt_time', 'N/A')} (Telephone Translation)")

    except Exception as e:
        log(f"Cycle error: {e}")
        
    return accepted


def run_persistent_bot():
    """Run bot with persistent login session"""
    jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
    
    # Initialize results tracker
    results_interval = BOT_CONFIG.get("results_report_interval", 5)
    rejected_interval = BOT_CONFIG.get("rejected_report_interval", 0.5)
    enable_results_reporting = BOT_CONFIG.get("enable_results_reporting", True)
    enable_rejected_reporting = BOT_CONFIG.get("enable_rejected_reporting", True)
    tracker = initialize_tracker(results_interval, rejected_interval)
    
    with sync_playwright() as p:
        headless = BOT_CONFIG.get("headless", True)
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        # Login once at startup
        log("Logging in...")
        set_login_status("Attempting login...", False)
        page.goto(jobs_url, wait_until="networkidle")
        
        try:
            perform_login(page, ATOZ_BASE_URL, {"username": ATOZ_USERNAME, "password": ATOZ_PASSWORD})
            set_login_status("Login successful", True)
            log("Login complete. Starting job monitoring...")
        except Exception as e:
            set_login_status(f"Login failed: {str(e)}", False)
            log(f"Login failed: {e}")
            raise
        
        # Initialize quick check timing
        last_quick_check = time.time()
        quick_check_interval = BOT_CONFIG.get("quick_check_interval", 10)
        enable_quick_check = BOT_CONFIG.get("enable_quick_check", False)
        selected_category = BOT_CONFIG.get("accept_preconditions", {}).get("job_type", "")
        
        if enable_quick_check:
            log(f"Quick check enabled: checking every {quick_check_interval}s for category '{selected_category}'")
            
        if enable_results_reporting:
            log(f"Results reporting enabled: reporting every {results_interval}s")
            
        if enable_rejected_reporting:
            if rejected_interval >= 3600:  # If 1 hour or more
                hours = rejected_interval / 3600
                log(f"Rejected jobs reporting enabled: reporting every {hours:.1f} hours")
            else:
                log(f"Rejected jobs reporting enabled: reporting every {rejected_interval}s")
        
        log("🚀 Bot is now running continuously. Press Ctrl+C to stop.")
        log("📋 Bot will check for jobs every 0.5 seconds and report every 5 seconds.")
        
        # Continuous job checking without re-login
        while BOT_CONFIG.get("bot_running", False):
            current_time = time.time()
            
            # Increment check cycle counter (every 0.5s)
            increment_check_cycle()
            
            # Perform quick check if enabled and enough time has passed
            if enable_quick_check and (current_time - last_quick_check) >= quick_check_interval:
                try:
                    matches = quick_job_check_cycle(page, jobs_url, selected_category)
                    if matches > 0:
                        log(f"Quick check found {matches} jobs matching category '{selected_category}'")
                    last_quick_check = current_time
                except Exception as e:
                    log(f"Quick check error: {e}")
            
            # Regular bot cycle
            accepted = persistent_bot_cycle(page, jobs_url)
            if accepted > 0:
                log(f"📊 Cycle completed. Jobs accepted: {accepted}")
                update_activity()  # Update activity when jobs are processed
            else:
                # Log every 10 cycles (5 seconds) when no jobs are found
                if tracker.check_cycles % 10 == 0:
                    log(f"🔍 Checking for jobs... (Cycle {tracker.check_cycles})")
            
            # Check and report results if enabled
            if enable_results_reporting:
                check_and_report()
                
            # Check and report rejected jobs if enabled
            if enable_rejected_reporting:
                check_and_report_rejected()
            
            time.sleep(float(BOT_CONFIG.get("check_interval", 0.5)))
        
        # Final results report
        if enable_results_reporting:
            log("Final results summary:")
            tracker.print_detailed_stats()
            
            # Show dedicated accepted job report
            log("Accepted Job Report:")
            print_accepted_job_report()
        
        log("Bot stopped.")
        context.close()
        browser.close()


if __name__ == "__main__":
    BOT_CONFIG["bot_running"] = True
    run_persistent_bot()
