#!/usr/bin/env python3
"""
Real AtoZ Bot - Performs actual login and job checking on AtoZ portal
"""
import time
import sys
import os
import json
import requests
from datetime import datetime, timezone
from playwright.sync_api import sync_playwright

# AtoZ Portal Credentials
ATOZ_URL = "https://portal.atozinterpreting.com/login"
USERNAME = "hussain02747@gmail.com"
PASSWORD = "Ngoma2003#"

def log(message: str) -> None:
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [RealAtoZBot] {message}")

def send_status_update(update_type: str, data: dict) -> None:
    """Send status update to backend API"""
    try:
        update_data = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        response = requests.post(
            "http://localhost:8000/api/bot/realtime-update",
            json=update_data,
            timeout=5
        )
        if response.status_code == 200:
            log(f"Status update sent: {update_type}")
        else:
            log(f"Failed to send status update: HTTP {response.status_code}")
    except Exception as e:
        log(f"Failed to send status update: {e}")

def update_database(session_id: str, status: str, total_checks: int, total_accepted: int, total_rejected: int, login_status: str):
    """Update database with current bot status"""
    try:
        # Send as real-time update to backend
        send_status_update("database_update", {
            "session_id": session_id,
            "status": status,
            "total_checks": total_checks,
            "total_accepted": total_accepted,
            "total_rejected": total_rejected,
            "login_status": login_status
        })
    except Exception as e:
        log(f"Failed to update database: {e}")

def perform_atoz_login(page, username: str, password: str) -> bool:
    """Perform actual login to AtoZ portal"""
    try:
        log("🔐 Attempting login to AtoZ portal...")
        
        # Navigate to login page
        page.goto(ATOZ_URL, wait_until='networkidle')
        log("📄 Navigated to login page")
        
        # Wait for login form to load
        page.wait_for_selector('input[type="email"], input[name="email"], input[id="email"]', timeout=10000)
        log("📝 Login form loaded")
        
        # Fill in credentials
        email_input = page.query_selector('input[type="email"], input[name="email"], input[id="email"]')
        if email_input:
            email_input.fill(username)
            log("✅ Email entered")
        
        password_input = page.query_selector('input[type="password"], input[name="password"], input[id="password"]')
        if password_input:
            password_input.fill(password)
            log("✅ Password entered")
        
        # Find and click login button
        login_button = page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Login"), button:has-text("Sign In")')
        if login_button:
            login_button.click()
            log("✅ Login button clicked")
        
        # Wait for login to complete - try multiple approaches
        try:
            # Wait for any change in the page (login redirect)
            page.wait_for_load_state('networkidle', timeout=10000)
        except:
            pass
        
        # Check if login was successful
        current_url = page.url
        page_content = page.content()
        
        # More flexible login success detection
        success_indicators = [
            'dashboard' in current_url.lower(),
            'portal' in current_url.lower(),
            'welcome' in page_content.lower(),
            'logout' in page_content.lower(),
            'profile' in page_content.lower(),
            'account' in page_content.lower(),
            'interpreter' in page_content.lower(),
            'jobs' in page_content.lower()
        ]
        
        if any(success_indicators):
            log(f"✅ LOGIN SUCCESSFUL! Redirected to: {current_url}")
            log(f"📄 Page content preview: {page_content[:300]}...")
            return True
        else:
            log(f"❌ LOGIN FAILED! Current URL: {current_url}")
            log(f"📄 Page content preview: {page_content[:300]}...")
            return False
            
    except Exception as e:
        log(f"❌ Login error: {e}")
        return False

def check_jobs_on_page(page) -> tuple[int, int]:
    """Check for jobs on current page and return (accepted, rejected)"""
    try:
        # Look for job listings
        job_elements = page.query_selector_all('.job, .job-listing, .job-item, [class*="job"], [id*="job"]')
        
        if not job_elements:
            log("📭 No job elements found on current page")
            return 0, 0
        
        log(f"📋 Found {len(job_elements)} job elements on page")
        
        accepted = 0
        rejected = 0
        
        for i, job_element in enumerate(job_elements[:5]):  # Check first 5 jobs
            try:
                job_text = job_element.inner_text().lower()
                
                # Check if it's a telephone interpreting job
                if 'telephone' in job_text or 'phone' in job_text:
                    # Check if it's open/available
                    if 'open' in job_text or 'available' in job_text:
                        accepted += 1
                        log(f"✅ ACCEPTED: Job {i+1} - Telephone interpreting job")
                        
                        # Try to click accept/apply button
                        try:
                            accept_button = job_element.query_selector('button:has-text("Accept"), button:has-text("Apply"), .accept, .apply')
                            if accept_button:
                                accept_button.click()
                                log(f"🎯 Clicked accept for job {i+1}")
                        except Exception as e:
                            log(f"⚠️ Could not click accept for job {i+1}: {e}")
                    else:
                        rejected += 1
                        log(f"❌ REJECTED: Job {i+1} - Telephone job but not open")
                else:
                    rejected += 1
                    log(f"❌ REJECTED: Job {i+1} - Not a telephone job")
                    
            except Exception as e:
                log(f"⚠️ Error processing job {i+1}: {e}")
                rejected += 1
        
        return accepted, rejected
        
    except Exception as e:
        log(f"❌ Error checking jobs: {e}")
        return 0, 0

def main():
    """Main bot function"""
    log("🚀 Starting Real AtoZ Bot...")
    
    # Send startup update
    send_status_update("bot_starting", {
        "message": "Starting Real AtoZ Bot with actual login..."
    })
    
    # Create session ID
    session_id = f"real-atoz-session-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Update database with starting status
    update_database(session_id, "starting", 0, 0, 0, "attempting")
    
    browser = None
    page = None
    login_successful = False
    check_count = 0
    total_accepted = 0
    total_rejected = 0
    
    try:
        # Initialize Playwright
        log("🌐 Starting browser automation...")
        playwright = sync_playwright().start()
        
        # Launch browser
        browser = playwright.chromium.launch(
            headless=True,  # Set to False for debugging
            args=['--no-sandbox', '--disable-dev-shm-usage']
        )
        
        # Create new page
        page = browser.new_page()
        
        # Set user agent
        page.set_extra_http_headers({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
        # Perform login
        login_successful = perform_atoz_login(page, USERNAME, PASSWORD)
        
        if not login_successful:
            log("❌ Cannot proceed without successful login")
            send_status_update("login_failed", {
                "session_id": session_id,
                "message": "Login failed. Please check credentials."
            })
            update_database(session_id, "error", 0, 0, 0, "failed")
            return
        
        # Update database with successful login
        update_database(session_id, "running", 0, 0, 0, "success")
        send_status_update("login_success", {
            "session_id": session_id,
            "message": "Successfully logged in! Bot is now running..."
        })
        
        # Main job checking loop
        check_count = 0
        total_accepted = 0
        total_rejected = 0
        
        log("🔄 Starting real job checking loop...")
        
        # Check for stop signal file
        stop_file_path = os.path.join(os.path.dirname(__file__), "..", "backend", "bot_stop_signal.txt")
        
        while True:  # Run indefinitely until stopped
            # Check for stop signal
            if os.path.exists(stop_file_path):
                log("🛑 Stop signal detected. Stopping bot...")
                try:
                    os.remove(stop_file_path)  # Remove the stop signal file
                except:
                    pass
                break
            try:
                check_count += 1
                log(f"🔍 Bot check #{check_count} - Checking for jobs on AtoZ platform...")
                
                # Send checking jobs update
                send_status_update("checking_jobs", {
                    "session_id": session_id,
                    "iteration": check_count,
                    "message": f"Checking for jobs (iteration {check_count})..."
                })
                
                # Check for jobs
                accepted, rejected = check_jobs_on_page(page)
                total_accepted += accepted
                total_rejected += rejected
                
                log(f"Iteration {check_count} complete: {accepted} accepted, {rejected} rejected")
                
                # Send job processing complete update
                send_status_update("job_processing_complete", {
                    "session_id": session_id,
                    "iteration": check_count,
                    "accepted": accepted,
                    "rejected": rejected,
                    "total_checks": check_count,
                    "total_accepted": total_accepted,
                    "total_rejected": total_rejected,
                    "message": f"Processed {accepted + rejected} jobs: {accepted} accepted, {rejected} rejected"
                })
                
                # Update database with current status
                update_database(session_id, "running", check_count, total_accepted, total_rejected, "success")
                
                # Wait before next check (0.5 seconds as requested)
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                log("🛑 Bot stopped by user (KeyboardInterrupt)")
                break
            except Exception as e:
                log(f"❌ Error in bot iteration {check_count}: {e}")
                time.sleep(1)  # Wait a bit before retrying
                
    except ImportError:
        log("❌ Playwright not installed. Installing...")
        import subprocess
        subprocess.run(['pip', 'install', 'playwright'], check=True)
        subprocess.run(['playwright', 'install', 'chromium'], check=True)
        log("✅ Playwright installed. Please restart the bot.")
        return
    except Exception as e:
        log(f"❌ Browser automation error: {e}")
        send_status_update("bot_error", {
            "session_id": session_id,
            "error": str(e)
        })
    finally:
        # Clean up browser resources
        try:
            if page:
                page.close()
            if browser:
                browser.close()
            log("🧹 Browser resources cleaned up")
        except Exception as e:
            log(f"⚠️ Error cleaning up browser resources: {e}")
        
        # Update final status
        update_database(session_id, "stopped", check_count, total_accepted, total_rejected, "success")
        send_status_update("bot_stopped", {
            "session_id": session_id,
            "message": "Bot stopped"
        })
        
        log(f"🛑 Bot session {session_id} finished after {check_count} checks")

if __name__ == "__main__":
    main()
