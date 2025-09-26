from typing import List

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def navigate_to_job_board(page, base_url: str) -> None:
    page.goto(f"{base_url.rstrip('/')}/interpreter-jobs", wait_until="networkidle")


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


