import os
import sys
import time
import requests
from urllib.parse import urljoin

from config import (ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH, ATOZ_PASSWORD,
                    ATOZ_USERNAME, BOT_CONFIG, MAX_ACCEPT_PER_RUN)
from dynamic_config import get_bot_config, get_check_interval, get_max_accept_per_run, get_job_type_filter, refresh_config
from login_handler import initialize_browser, perform_login
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from filter_handler import navigate_to_job_board, get_matched_rows
from data_processor import (
    extract_jobs,
    is_all_params_set,
    is_telephone_job,
    accept_from_board,
    get_interpreter_details_text,
    reject_on_detail,
)


def log(message: str) -> None:
    print(f"[AtoZBot] {message}")


def send_status_update(session_id: str, update_type: str, data: dict) -> None:
    """Send status update to the API"""
    try:
        api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        response = requests.post(
            f"{api_url}/api/bot/realtime-update",
            json={
                "session_id": session_id,
                "update_type": update_type,
                "data": data
            },
            timeout=5
        )
        if response.status_code == 200:
            log(f"Status update sent: {update_type}")
        else:
            log(f"Failed to send status update: {response.status_code}")
    except Exception as e:
        log(f"Error sending status update: {e}")


def update_database_stats(session_id: str, total_checks: int, total_accepted: int, total_rejected: int, status: str = "running") -> None:
    """Update database with bot statistics"""
    try:
        api_url = os.getenv("API_BASE_URL", "http://localhost:8000")
        log(f"🔄 Sending database update: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")
        
        response = requests.post(
            f"{api_url}/api/bot/realtime-update",
            json={
                "session_id": session_id,
                "update_type": "database_update",
                "data": {
                    "session_id": session_id,
                    "status": status,
                    "total_checks": total_checks,
                    "total_accepted": total_accepted,
                    "total_rejected": total_rejected,
                    "login_status": "success" if status == "running" else "failed"
                }
            },
            timeout=5
        )
        
        log(f"📡 Database update response: {response.status_code} - {response.text}")
        
        if response.status_code == 200:
            log(f"✅ Database updated: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")
        else:
            log(f"❌ Failed to update database: {response.status_code} - {response.text}")
    except Exception as e:
        log(f"Error updating database: {e}")


def try_login(page) -> bool:
    """Attempt to login and return success status"""
    if not (ATOZ_USERNAME and ATOZ_PASSWORD):
        log("❌ No credentials provided")
        return False
    
    try:
        log(f"🔐 Attempting login with username: {ATOZ_USERNAME}")
        perform_login(page, ATOZ_BASE_URL, {"username": ATOZ_USERNAME, "password": ATOZ_PASSWORD})
        
        # Verify login success by checking for user elements or dashboard
        try:
            # Wait for either user header or dashboard elements
            page.wait_for_selector(".header__name, .dashboard, .user-menu, [data-testid='user-menu']", timeout=10000)
            log("✅ Successfully logged in!")
            return True
        except PlaywrightTimeoutError:
            # Check if we're on a dashboard/jobs page
            current_url = page.url
            if "dashboard" in current_url.lower() or "jobs" in current_url.lower() or "interpreter" in current_url.lower():
                log("✅ Login appears successful (redirected to dashboard)")
                return True
            else:
                log("❌ Login verification failed - not on expected page")
                return False
                
    except Exception as e:
        log(f"❌ Login failed: {e}")
        return False


def accept_jobs_on_page(page) -> int:
    accepted = 0
    try:
        page.wait_for_selector("section.content__table table tbody", timeout=10000)

        if page.query_selector("text=There are no interpreter jobs"):
            log("No jobs available.")
            return 0

        rows = page.query_selector_all("tbody tr.table__row")

        for row in rows:
            if accepted >= MAX_ACCEPT_PER_RUN:
                break

            try:
                # Gate 1: remote only (avoid face to face). Heuristic: text contains 'remote' and not 'face to face'
                row_text = (row.inner_text() or "").lower()
                if ("remote" not in row_text) or ("face to face" in row_text):
                    continue

                # Gate 2: all key fields present and status is matched
                cells = row.query_selector_all("td.table__data")
                if len(cells) < 8:
                    continue
                ref_val = cells[0].inner_text().strip() if cells[0] else ""
                submitted_val = cells[1].inner_text().strip() if cells[1] else ""
                appt_date_val = cells[2].inner_text().strip() if cells[2] else ""
                appt_time_val = cells[3].inner_text().strip() if cells[3] else ""
                duration_val = cells[4].inner_text().strip() if cells[4] else ""
                language_val = cells[5].inner_text().strip() if cells[5] else ""
                status_text = cells[6].inner_text().strip().lower() if cells[6] else ""

                required_present = all([
                    ref_val,
                    submitted_val,
                    appt_date_val,
                    appt_time_val,
                    duration_val,
                    language_val,
                ])
                if not required_present:
                    continue
                if "matched" not in status_text:
                    continue

                # Find Accept button only within this row
                accept_btn = row.query_selector(".btn.btn--primary.table__btn, button:has-text('Accept'), a:has-text('Accept')")
                if not accept_btn:
                    continue

                accept_btn.click()

                # Handle possible 24-hour modal
                try:
                    if page.is_visible("#24HourModal"):
                        page.click("#24HourModal #continueButton")
                except Exception:
                    pass

                # If a confirmation/cancel modal appears, submit a generic message
                try:
                    if page.is_visible("#cancelModal"):
                        page.fill("#cancelModal textarea[name='message']", "Accepting job via automation")
                        page.click("#cancelModal .modal-footer .btn.btn--primary")
                except Exception:
                    pass

                page.wait_for_load_state("networkidle")
                accepted += 1
                log(f"Accepted job {ref_val}.")
            except Exception:
                continue

    except PlaywrightTimeoutError:
        log("Jobs table not found or timed out.")

    return accepted


def run_bot_with_session(session_id: str) -> None:
    """Run the bot continuously with session management"""
    log(f"Starting AtoZ Bot with session ID: {session_id}")
    
    # Send initial status update
    send_status_update(session_id, "starting", {"message": "Bot initialization complete"})
    update_database_stats(session_id, 0, 0, 0, "starting")
    
    jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
    total_checks = 0
    total_accepted = 0
    total_rejected = 0
    
    try:
        with sync_playwright() as p:
            headless = BOT_CONFIG.get("headless", True)
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--disable-renderer-backgrounding'
                ]
            )
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            page = context.new_page()
            
            # Login once at start with retry logic
            send_status_update(session_id, "login_attempting", {"step": "connecting"})
            
            login_successful = False
            max_login_retries = 3
            
            for login_attempt in range(max_login_retries):
                try:
                    log(f"Login attempt {login_attempt + 1}/{max_login_retries}")
                    page.goto(jobs_url, wait_until="networkidle")
                    
                    # Check if we got a Chrome error page
                    current_url = page.url
                    if "chrome-error://" in current_url or "error" in current_url.lower():
                        log(f"Chrome error page detected: {current_url}")
                        if login_attempt < max_login_retries - 1:
                            log("Retrying login in 3 seconds...")
                            time.sleep(3)
                            continue
                    
                    login_successful = try_login(page)
                    if login_successful:
                        break
                    else:
                        if login_attempt < max_login_retries - 1:
                            log("Login failed, retrying in 3 seconds...")
                            time.sleep(3)
                            continue
                            
                except Exception as login_error:
                    log(f"Login attempt {login_attempt + 1} failed: {login_error}")
                    if login_attempt < max_login_retries - 1:
                        log("Retrying login in 3 seconds...")
                        time.sleep(3)
                        continue
            
            if not login_successful:
                log("❌ Failed to login after all attempts. Bot cannot continue.")
                update_database_stats(session_id, total_checks, total_accepted, total_rejected, "error")
                send_status_update(session_id, "login_failed", {"message": "Login failed after multiple attempts. Please check credentials."})
                return
            
            send_status_update(session_id, "login_successful", {"step": "completed"})
            
            # Update database with login success
            update_database_stats(session_id, total_checks, total_accepted, total_rejected, "running")
            send_status_update(session_id, "running", {"message": "Bot is now running and checking for jobs"})
            
            # Continuous job checking loop - runs infinitely
            cycle = 0
            consecutive_errors = 0
            max_consecutive_errors = 10  # Allow up to 10 consecutive errors before giving up
            total_cycles = 0
            
            log("🔄 Starting infinite job checking loop...")
            log("🔄 Bot will run continuously until manually stopped...")
            
            while True:
                try:
                    cycle += 1
                    consecutive_errors = 0  # Reset error counter on successful cycle start
                    log(f"Starting job check cycle #{cycle}")
                    send_status_update(session_id, "checking_jobs", {"cycle": cycle, "step": "navigating"})
                    
                    # Navigate to job board
                    navigate_to_job_board(page, ATOZ_BASE_URL)
                    send_status_update(session_id, "checking_jobs", {"cycle": cycle, "step": "loading_jobs"})
                    
                    # Extract jobs
                    jobs = extract_jobs(page)
                    total_checks += 1
                    
                    if not jobs:
                        log("No jobs available at this time")
                        send_status_update(session_id, "no_jobs", {"cycle": cycle})
                    else:
                        log(f"Found {len(jobs)} available jobs")
                        send_status_update(session_id, "processing_jobs", {"cycle": cycle, "jobs_found": len(jobs)})
                        
                        accepted_this_cycle = 0
                        rejected_this_cycle = 0
                        
                        for i, job in enumerate(jobs):
                            if accepted_this_cycle >= MAX_ACCEPT_PER_RUN:
                                break
                                
                            # Only consider matched jobs
                            if "matched" not in (job.get("status", "").lower()):
                                continue
                                
                            # Required fields present
                            required = BOT_CONFIG.get("accept_preconditions", {}).get("required_fields", [])
                            if required and not is_all_params_set(job, required):
                                continue

                            # Confirm job type on detail page
                            pre = BOT_CONFIG.get("accept_preconditions", {})
                            job_type = pre.get("job_type", "")
                            exclude_types = pre.get("exclude_types", [])
                            if not job.get("view_url"):
                                continue
                                
                            if not is_telephone_job(page, job["view_url"], job_type, exclude_types):
                                # If details indicate face to face or excluded types, reject from detail view
                                details_text = get_interpreter_details_text(page, job["view_url"]).lower()
                                if any(ex in details_text for ex in [t.lower() for t in exclude_types]):
                                    if reject_on_detail(page):
                                        log(f"Rejected face to face job {job['ref']}.")
                                        rejected_this_cycle += 1
                                    # Go back to board for next job
                                    navigate_to_job_board(page, ATOZ_BASE_URL)
                                continue

                            # Back to board (in case we navigated away) and click Accept
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
                            accepted_this_cycle += 1
                            log(f"Accepted job {job['ref']}.")
                            
                            # Send job processed update
                            send_status_update(session_id, "job_processed", {
                                "cycle": cycle,
                                "job_number": i + 1,
                                "total_jobs": len(jobs),
                                "accepted": accepted_this_cycle,
                                "rejected": rejected_this_cycle,
                                "skipped": 0
                            })
                        
                        total_accepted += accepted_this_cycle
                        total_rejected += rejected_this_cycle
                        
                        log(f"Cycle #{cycle} completed: {accepted_this_cycle} accepted, {rejected_this_cycle} rejected")
                    
                    # Update database with current stats
                    update_database_stats(session_id, total_checks, total_accepted, total_rejected, "running")
                    
                    # Send cycle complete update
                    send_status_update(session_id, "cycle_complete", {
                        "cycle": cycle,
                        "stats": {
                            "total_checks": total_checks,
                            "total_accepted": total_accepted,
                            "total_rejected": total_rejected,
                            "total_skipped": 0
                        }
                    })
                    
                    # Wait before next cycle
                    # Wait before next check (using dynamic interval from database)
                    wait_time = get_check_interval()
                    total_cycles += 1
                    log(f"✅ Cycle #{cycle} completed successfully. Total cycles: {total_cycles}")
                    log(f"⏳ Waiting {wait_time}s before next cycle...")
                    time.sleep(wait_time)
                
                except Exception as cycle_error:
                    consecutive_errors += 1
                    log(f"Error in cycle #{cycle} (consecutive errors: {consecutive_errors}): {cycle_error}")
                    send_status_update(session_id, "cycle_error", {"cycle": cycle, "error": str(cycle_error), "consecutive_errors": consecutive_errors})
                    
                    # Check if we've hit the maximum consecutive errors
                    if consecutive_errors >= max_consecutive_errors:
                        log(f"❌ Maximum consecutive errors ({max_consecutive_errors}) reached. Bot will continue but log the issue.")
                        send_status_update(session_id, "max_errors_reached", {"consecutive_errors": consecutive_errors})
                        # Don't break - continue running but reset counter after a longer wait
                        time.sleep(30)
                        consecutive_errors = 0
                        continue
                    
                    # If it's a Playwright error, try to recover
                    if "EPIPE" in str(cycle_error) or "playwright" in str(cycle_error).lower():
                        log("Playwright error detected, attempting to recover...")
                        try:
                            # Try to refresh the page
                            page.reload(wait_until="networkidle")
                            log("Page refreshed successfully")
                        except Exception as refresh_error:
                            log(f"Failed to refresh page: {refresh_error}")
                            # If refresh fails, try to reinitialize browser
                            try:
                                log("Attempting to reinitialize browser...")
                                if 'context' in locals():
                                    context.close()
                                if 'browser' in locals():
                                    browser.close()
                                
                                # Reinitialize browser
                                p, browser, context, page = initialize_browser()
                                jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
                                page.goto(jobs_url, wait_until="networkidle")
                                
                                # Re-login
                                login_successful = try_login(page)
                                if not login_successful:
                                    log("❌ Failed to re-login after browser restart, will retry in next cycle")
                                    # Don't break - continue the loop to retry
                                    time.sleep(10)  # Wait longer before retrying
                                    continue
                                
                                log("✅ Browser reinitialized and re-logged in successfully")
                            except Exception as restart_error:
                                log(f"Failed to restart browser: {restart_error}, will retry in next cycle")
                                # Don't break - continue the loop to retry
                                time.sleep(15)  # Wait longer before retrying
                                continue
                    else:
                        # For other errors, just log and continue
                        log(f"Non-Playwright error, continuing...")
                    
                    # Wait a bit before retrying (longer wait for consecutive errors)
                    wait_time = min(5 + (consecutive_errors * 2), 30)  # Progressive backoff, max 30 seconds
                    log(f"Waiting {wait_time}s before retrying (progressive backoff)...")
                    time.sleep(wait_time)
                
    except KeyboardInterrupt:
        log("🛑 Bot stopped by user (KeyboardInterrupt)")
        update_database_stats(session_id, total_checks, total_accepted, total_rejected, "stopped")
        send_status_update(session_id, "bot_stopped", {"message": "Bot stopped by user"})
    except Exception as e:
        log(f"❌ Critical bot error: {e}")
        update_database_stats(session_id, total_checks, total_accepted, total_rejected, "error")
        send_status_update(session_id, "error", {"message": str(e)})
        # Even on critical errors, try to continue the loop
        log("🔄 Attempting to continue bot operation despite critical error...")
        time.sleep(10)  # Wait before continuing
    finally:
        # Only cleanup if we're actually stopping (not continuing)
        if 'context' in locals() and 'browser' in locals():
            try:
                log("🧹 Cleaning up browser resources...")
                context.close()
                browser.close()
                if 'p' in locals():
                    p.stop()
                log("✅ Browser resources cleaned up")
            except Exception as e:
                log(f"⚠️ Error cleaning up browser resources: {e}")
        
        # Update final status only if we're actually stopping
        try:
            update_database_stats(session_id, total_checks, total_accepted, total_rejected, "stopped")
            send_status_update(session_id, "bot_stopped", {"message": "Bot stopped"})
            log(f"🛑 Bot session {session_id} ended. Total: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")
        except Exception as e:
            log(f"⚠️ Error updating final status: {e}")


def run_once() -> int:
    """Legacy function for single run"""
    jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
    with sync_playwright() as p:
        headless = BOT_CONFIG.get("headless", True)
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        # Login once at start
        page.goto(jobs_url, wait_until="networkidle")
        login_successful = try_login(page)
        if not login_successful:
            log("❌ Failed to login. Cannot proceed.")
            return 0
        
        # Navigate to job board and stay logged in
        navigate_to_job_board(page, ATOZ_BASE_URL)

        # Extract full job objects and then filter/process
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

            # Confirm job type on detail page
            pre = BOT_CONFIG.get("accept_preconditions", {})
            job_type = pre.get("job_type", "")
            exclude_types = pre.get("exclude_types", [])
            if not job.get("view_url"):
                continue
            if not is_telephone_job(page, job["view_url"], job_type, exclude_types):
                # If details indicate face to face or excluded types, reject from detail view
                details_text = get_interpreter_details_text(page, job["view_url"]).lower()
                if any(ex in details_text for ex in [t.lower() for t in exclude_types]):
                    if reject_on_detail(page):
                        log(f"Rejected face to face job {job['ref']}.")
                    # Go back to board for next job
                    navigate_to_job_board(page, ATOZ_BASE_URL)
                continue

            # Back to board (in case we navigated away) and click Accept
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
            log(f"Accepted job {job['ref']}.")
        context.close()
        browser.close()
        return accepted


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run with session ID for API integration
        session_id = sys.argv[1]
        run_bot_with_session(session_id)
    else:
        # Legacy single run
        count = run_once()
        log(f"Run completed. Accepted: {count}")


