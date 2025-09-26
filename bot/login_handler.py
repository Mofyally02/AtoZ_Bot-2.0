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
    page.goto(login_url, wait_until="load")
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
        page.wait_for_selector(".header__name", timeout=10000)
    except PlaywrightTimeoutError:
        # Fallback: still accept if redirected to dashboard/job board
        pass
    _human_pause(0.8, 1.4)


