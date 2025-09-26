from urllib.parse import urljoin

from config import (ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH, ATOZ_PASSWORD,
                    ATOZ_USERNAME, BOT_CONFIG, MAX_ACCEPT_PER_RUN)
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


def try_login(page) -> None:
    if not (ATOZ_USERNAME and ATOZ_PASSWORD):
        return
    try:
        perform_login(page, ATOZ_BASE_URL, {"username": ATOZ_USERNAME, "password": ATOZ_PASSWORD})
        log("Logged in.")
    except Exception:
        pass


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


def run_once() -> int:
    jobs_url = urljoin(ATOZ_BASE_URL, ATOZ_INTERPRETER_JOBS_PATH)
    with sync_playwright() as p:
        headless = BOT_CONFIG.get("headless", True)
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()
        
        # Login once at start
        page.goto(jobs_url, wait_until="networkidle")
        try_login(page)
        
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
    count = run_once()
    log(f"Run completed. Accepted: {count}")


