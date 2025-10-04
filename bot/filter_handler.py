from typing import List

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def navigate_to_job_board(page, base_url: str) -> None:
    """Navigate to job board with retry logic for network errors"""
    import time
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            page.goto(f"{base_url.rstrip('/')}/interpreter-jobs", wait_until="networkidle")
            return  # Success, exit function
        except Exception as e:
            if "ERR_NETWORK_CHANGED" in str(e) and attempt < max_retries - 1:
                print(f"⚠️ Network error on attempt {attempt + 1}, retrying in 2 seconds...")
                time.sleep(2)
                continue
            else:
                # If it's not a network error or we've exhausted retries, re-raise
                raise


def get_matched_rows(page) -> List:
    """Return table row elements that have status 'matched'."""
    try:
        page.wait_for_selector("section.content__table table tbody", timeout=10000)
    except PlaywrightTimeoutError:
        return []

    rows = page.query_selector_all("tbody tr.table__row")
    matched_rows = []
    for row in rows:
        status_cell = row.query_selector("td.table__data.status") or row.query_selector("td.table__data .status")
        status_text = (status_cell.inner_text().strip().lower() if status_cell else "")
        if "matched" in status_text:
            matched_rows.append(row)
    return matched_rows


