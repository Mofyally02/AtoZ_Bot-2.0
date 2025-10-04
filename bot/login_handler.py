import random
import time
from typing import Tuple

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


def _human_pause(min_s: float = 0.2, max_s: float = 0.6) -> None:
    time.sleep(random.uniform(min_s, max_s))


def initialize_browser(headless: bool = True):
    """
    Start Playwright chromium with a realistic UA/locale and return (playwright, browser, context, page).
    Caller MUST close: page -> context -> browser, and finally stop playwright.
    """
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=headless)
    context = browser.new_context(
        locale="en-GB",
        timezone_id="Europe/London",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 768},
    )
    page = context.new_page()
    return p, browser, context, page


def perform_login(page, base_url: str, credentials: dict) -> None:
    """
    Navigate to the login page and authenticate using provided credentials.
    Waits for the header user element as a success criterion.
    """
    login_url = f"{base_url.rstrip('/')}/login"
    
    # Retry logic for network errors
    max_retries = 3
    for attempt in range(max_retries):
        try:
            page.goto(login_url, wait_until="load")
            break  # Success, continue with login
        except Exception as e:
            if "ERR_NETWORK_CHANGED" in str(e) and attempt < max_retries - 1:
                print(f"⚠️ Network error during login navigation (attempt {attempt + 1}), retrying in 2 seconds...")
                time.sleep(2)
                continue
            else:
                raise  # Re-raise if not a network error or retries exhausted
    
    _human_pause()

    # Fill email
    page.wait_for_selector("input[name='email']", timeout=10000)
    page.click("input[name='email']")
    _human_pause()
    page.fill("input[name='email']", credentials.get("username", ""))
    _human_pause()

    # Fill password
    page.click("input[name='password']")
    _human_pause()
    page.fill("input[name='password']", credentials.get("password", ""))
    _human_pause()

    # Submit
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    try:
        # Wait for login success indicators
        page.wait_for_selector(".header__name, .dashboard, .user-menu, [data-testid='user-menu'], .header__user", timeout=10000)
    except PlaywrightTimeoutError:
        # Fallback: check if we're on a dashboard/jobs page
        current_url = page.url
        if "dashboard" in current_url.lower() or "jobs" in current_url.lower() or "interpreter" in current_url.lower():
            print("Login successful - redirected to dashboard/jobs page")
        else:
            print(f"Login verification failed - current URL: {current_url}")
            raise
    _human_pause(0.8, 1.4)


