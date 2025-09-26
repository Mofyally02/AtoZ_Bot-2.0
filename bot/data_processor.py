from typing import Dict, List

from bs4 import BeautifulSoup
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def extract_jobs(page) -> List[Dict[str, str]]:
    jobs: List[Dict[str, str]] = []
    try:
        page.wait_for_selector("section.content__table table tbody", timeout=10000)
    except PlaywrightTimeoutError:
        return jobs

    rows = page.query_selector_all("tbody tr.table__row")
    for row in rows:
        # Skip empty-state rows with colspan
        colspan_cells = row.query_selector_all("td[colspan]")
        if colspan_cells:
            continue

        cells = row.query_selector_all("td.table__data")
        if len(cells) < 8:
            continue

        ref = cells[0].inner_text().strip() if cells[0] else ""
        submitted = cells[1].inner_text().strip() if cells[1] else ""
        appt_date = cells[2].inner_text().strip() if cells[2] else ""
        appt_time = cells[3].inner_text().strip() if cells[3] else ""
        duration = cells[4].inner_text().strip() if cells[4] else ""
        language = cells[5].inner_text().strip() if cells[5] else ""
        status = cells[6].inner_text().strip() if cells[6] else ""

        action_cell = cells[7]
        view_link = action_cell.query_selector("a[href*='interpreter-jobs']") if action_cell else None
        view_url = view_link.get_attribute("href") if view_link else ""

        jobs.append({
            "ref": ref,
            "submitted": submitted,
            "appt_date": appt_date,
            "appt_time": appt_time,
            "duration": duration,
            "language": language,
            "status": status,
            "view_url": view_url,
        })

    return jobs


def is_all_params_set(job: Dict[str, str], required_fields: List[str]) -> bool:
    return all(job.get(field) and str(job[field]).strip() for field in required_fields)


def _extract_interpreter_details_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    # Heuristic: find the row whose first cell contains "Interpreter details"
    for tr in soup.select("table.table.table--detail tr"):
        tds = tr.find_all("td")
        if len(tds) >= 2 and "interpreter details" in tds[0].get_text(strip=True).lower():
            return tds[1].get_text(" ", strip=True)
    # Fallback: search any element labeled as job detail with that title
    labels = soup.select(".job__detail")
    for label in labels:
        if "interpreter details" in label.get_text(strip=True).lower():
            nxt = label.find_next()
            if nxt:
                return nxt.get_text(" ", strip=True)
    return ""


def is_telephone_job(page, view_url: str, job_type: str, exclude_types: List[str]) -> bool:
    try:
        page.goto(view_url, wait_until="networkidle")
        html = page.content()
        details_text = _extract_interpreter_details_text(html).lower()
        if not details_text:
            return False
        if any(ex.lower() in details_text for ex in exclude_types):
            return False
        return job_type.lower() in details_text
    except Exception:
        return False


def accept_from_board(page, ref: str) -> bool:
    try:
        # Find accept form for the numeric ref prefix
        numeric_id = ref.split("/")[0].strip()
        form = page.query_selector(f"form[action*='/interpreter-jobs/{numeric_id}/matched']")
        if not form:
            return False
        btn = form.query_selector("button.btn.btn--primary") or form.query_selector("button[type='submit']")
        if not btn:
            return False
        btn.click()
        return True
    except Exception:
        return False


def get_interpreter_details_text(page, view_url: str) -> str:
    try:
        page.goto(view_url, wait_until="networkidle")
        html = page.content()
        return _extract_interpreter_details_text(html)
    except Exception:
        return ""


def reject_on_detail(page) -> bool:
    try:
        form = page.query_selector("form[action*='matched/reject']")
        if not form:
            # Fallback: a long reject button
            btn = page.query_selector("input.btn.btn--reject, .btn.btn--reject")
            if btn:
                btn.click()
                return True
            return False
        btn = form.query_selector("button, input[type='submit']") or form
        btn.click()
        return True
    except Exception:
        return False


def check_jobs_for_category(page, selected_category: str = None) -> List[Dict[str, str]]:
    """
    Check for jobs that match a selected category every 10 seconds.
    Returns a list of jobs that fit the category criteria.
    
    Args:
        page: Playwright page object
        selected_category: The category to filter jobs by (e.g., "Telephone interpreting")
    
    Returns:
        List of job dictionaries that match the category
    """
    try:
        # Extract all jobs from the page
        jobs = extract_jobs(page)
        
        if not selected_category:
            # If no category specified, return all matched jobs
            return [job for job in jobs if "matched" in job.get("status", "").lower()]
        
        matching_jobs = []
        
        for job in jobs:
            # Only consider matched jobs
            if "matched" not in job.get("status", "").lower():
                continue
                
            # Check if job has a view URL to examine details
            if not job.get("view_url"):
                continue
                
            # Navigate to job details to check category
            try:
                page.goto(job["view_url"], wait_until="networkidle")
                html = page.content()
                details_text = _extract_interpreter_details_text(html).lower()
                
                # Check if the selected category matches
                if selected_category.lower() in details_text:
                    matching_jobs.append(job)
                    
            except Exception as e:
                # If we can't check details, skip this job
                continue
                
        return matching_jobs
        
    except Exception as e:
        print(f"Error checking jobs for category: {e}")
        return []


def quick_job_check_cycle(page, jobs_url: str, selected_category: str = None) -> int:
    """
    Perform a quick job check cycle specifically for 10-second intervals.
    This function is optimized for faster execution.
    
    Args:
        page: Playwright page object
        jobs_url: URL to the jobs page
        selected_category: Category to filter jobs by
        
    Returns:
        Number of jobs found that match the category
    """
    try:
        # Navigate to job board (refresh)
        page.goto(jobs_url, wait_until="networkidle")
        
        # Check for jobs matching the selected category
        matching_jobs = check_jobs_for_category(page, selected_category)
        
        if matching_jobs:
            print(f"Found {len(matching_jobs)} jobs matching category '{selected_category}':")
            for job in matching_jobs:
                print(f"  - Job {job.get('ref', 'N/A')}: {job.get('language', 'N/A')} - {job.get('appt_date', 'N/A')} {job.get('appt_time', 'N/A')}")
        
        return len(matching_jobs)
        
    except Exception as e:
        print(f"Quick check cycle error: {e}")
        return 0


