#!/usr/bin/env python3
"""
Integrated AtoZ Bot that performs real login and job checking
"""
import sys
import time
import signal
import os
import json
import random
import requests
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import psycopg

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

# Import AtoZ bot components
from config import ATOZ_BASE_URL, ATOZ_USERNAME, ATOZ_PASSWORD, BOT_CONFIG
from login_handler import initialize_browser, perform_login
from filter_handler import navigate_to_job_board, get_matched_rows
from data_processor import (
    extract_jobs,
    is_all_params_set,
    is_telephone_job,
    accept_from_board,
    get_interpreter_details_text,
    reject_on_detail,
)

def signal_handler(sig, frame):
    print(f"[{datetime.now(timezone.utc).isoformat()}] Bot received stop signal, shutting down...")
    sys.exit(0)

def send_realtime_update(update_type, data):
    """Send real-time update to the backend"""
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
        if response.status_code != 200:
            print(f"Failed to send real-time update: {response.status_code}")
    except Exception as e:
        print(f"Error sending real-time update: {e}")

def update_database(session_id, status, checks=0, accepted=0, rejected=0, login_status="not_started"):
    """Update the database with bot status"""
    try:
        # Connect to the database
        engine = create_engine("postgresql+psycopg://atoz_user:atoz_password@localhost:5432/atoz_bot_db")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            # First, try to find the session by session_name if session_id is not a UUID
            if not session_id.startswith('test-session-'):
                # If it's a UUID, use it directly
                session_uuid = session_id
            else:
                # If it's a test session, find by session_name
                result = db.execute(text("SELECT id FROM bot_sessions WHERE session_name = :session_name"), {
                    'session_name': session_id
                }).fetchone()
                if result:
                    session_uuid = str(result[0])
                else:
                    # Create a new session if it doesn't exist
                    import uuid
                    session_uuid = str(uuid.uuid4())
                    db.execute(text("""
                        INSERT INTO bot_sessions (id, session_name, status, login_status, total_checks, total_accepted, total_rejected, created_at, updated_at)
                        VALUES (:id, :session_name, :status, :login_status, :checks, :accepted, :rejected, :created_at, :updated_at)
                    """), {
                        'id': session_uuid,
                        'session_name': session_id,
                        'status': status,
                        'login_status': login_status,
                        'checks': checks,
                        'accepted': accepted,
                        'rejected': rejected,
                        'created_at': datetime.now(timezone.utc).isoformat(),
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    })
                    db.commit()
                    print(f"[{datetime.now(timezone.utc).isoformat()}] Created new session: {session_id}")
            
            # Update the session status
            db.execute(text("""
                UPDATE bot_sessions 
                SET status = :status, 
                    login_status = :login_status,
                    total_checks = :checks, 
                    total_accepted = :accepted, 
                    total_rejected = :rejected,
                    updated_at = :updated_at
                WHERE id = :session_id
            """), {
                'status': status,
                'login_status': login_status,
                'checks': checks,
                'accepted': accepted,
                'rejected': rejected,
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'session_id': session_uuid
            })
            db.commit()
            print(f"[{datetime.now(timezone.utc).isoformat()}] Database updated: {status}, login: {login_status}, checks: {checks}, accepted: {accepted}, rejected: {rejected}")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Database update error: {e}")

def log(message: str) -> None:
    print(f"[AtoZBot] {message}")

def try_login(page) -> bool:
    """Attempt to login to AtoZ portal"""
    if not (ATOZ_USERNAME and ATOZ_PASSWORD):
        log("No credentials provided")
        return False
    
    try:
        log(f"Attempting to login with username: {ATOZ_USERNAME}")
        perform_login(page, ATOZ_BASE_URL, {"username": ATOZ_USERNAME, "password": ATOZ_PASSWORD})
        log("✅ Logged in successfully!")
        return True
    except Exception as e:
        log(f"❌ Login failed: {e}")
        return False

def check_jobs_on_page(page, session_id) -> tuple[int, int]:
    """Check for jobs on the current page and process them"""
    accepted = 0
    rejected = 0
    
    try:
        log("Navigating to job board...")
        navigate_to_job_board(page, ATOZ_BASE_URL)
        
        log("Looking for available jobs...")
        matched_rows = get_matched_rows(page)
        
        if not matched_rows:
            log("No jobs available at this time")
            return accepted, rejected
        
        log(f"Found {len(matched_rows)} job(s) to evaluate")
        
        for i, row in enumerate(matched_rows):
            try:
                log(f"Evaluating job {i+1}/{len(matched_rows)}")
                
                # Extract job details
                job_data = extract_jobs([row])[0] if extract_jobs([row]) else None
                
                if not job_data:
                    log(f"Could not extract job data for row {i+1}")
                    continue
                
                # Check if it's a telephone job
                if not is_telephone_job(job_data):
                    log(f"Job {i+1}: Not a telephone job, skipping")
                    rejected += 1
                    continue
                
                # Check if all required parameters are set
                if not is_all_params_set(job_data):
                    log(f"Job {i+1}: Missing required parameters, skipping")
                    rejected += 1
                    continue
                
                # Get detailed job information
                details_text = get_interpreter_details_text(page, row)
                
                # Make decision based on job details
                if should_accept_job(job_data, details_text):
                    log(f"Job {i+1}: ✅ ACCEPTING - {job_data.get('language', 'Unknown')} job")
                    
                    # Send real-time update for job acceptance
                    send_realtime_update("job_accepted", {
                        "session_id": session_id,
                        "job_number": i+1,
                        "language": job_data.get('language', 'Unknown'),
                        "job_type": job_data.get('job_type', 'Unknown'),
                        "duration": job_data.get('duration', 'Unknown'),
                        "message": f"Accepted {job_data.get('language', 'Unknown')} telephone interpreting job"
                    })
                    
                    try:
                        accept_from_board(page, row)
                        accepted += 1
                        log(f"Successfully accepted job {i+1}")
                    except Exception as e:
                        log(f"Failed to accept job {i+1}: {e}")
                        rejected += 1
                else:
                    # Determine rejection reason
                    job_type = job_data.get('job_type', '').lower()
                    status = job_data.get('status', '').lower()
                    language = job_data.get('language', 'Unknown')
                    
                    if 'telephone' not in job_type and 'phone' not in job_type:
                        reason = "Not a telephone interpreting job"
                    elif status != 'open':
                        reason = f"Job status is {status} (not open)"
                    elif not language or len(language) < 2:
                        reason = "Invalid or missing language"
                    else:
                        reason = "Does not meet quality requirements"
                    
                    log(f"Job {i+1}: ❌ REJECTING - {language} job ({reason})")
                    
                    # Send real-time update for job rejection
                    send_realtime_update("job_rejected", {
                        "session_id": session_id,
                        "job_number": i+1,
                        "language": language,
                        "job_type": job_data.get('job_type', 'Unknown'),
                        "reason": reason,
                        "message": f"Rejected {language} job: {reason}"
                    })
                    
                    try:
                        reject_on_detail(page, row)
                        rejected += 1
                        log(f"Successfully rejected job {i+1}")
                    except Exception as e:
                        log(f"Failed to reject job {i+1}: {e}")
                        rejected += 1
                
                # Update database after each job
                update_database(session_id, "running", accepted + rejected, accepted, rejected, "success")
                
                # Human-like pause between jobs
                time.sleep(random.uniform(1, 3))
                
            except Exception as e:
                log(f"Error processing job {i+1}: {e}")
                rejected += 1
                continue
        
        return accepted, rejected
        
    except Exception as e:
        log(f"Error checking jobs: {e}")
        return accepted, rejected

def should_accept_job(job_data: dict, details_text: str) -> bool:
    """Determine if a job should be accepted based on comprehensive criteria"""
    try:
        # Extract job parameters
        language = job_data.get('language', '').lower().strip()
        duration = job_data.get('duration', '').strip()
        status = job_data.get('status', '').lower().strip()
        job_type = job_data.get('job_type', '').lower().strip()
        ref = job_data.get('ref', '').strip()
        submitted = job_data.get('submitted', '').strip()
        appt_date = job_data.get('appt_date', '').strip()
        appt_time = job_data.get('appt_time', '').strip()
        
        log(f"Evaluating job: {language} | {job_type} | {duration} | {status}")
        
        # 1. Check if it's a telephone interpreting job (REQUIRED)
        if 'telephone' not in job_type and 'phone' not in job_type:
            log(f"❌ Rejecting: Not a telephone job (type: {job_type})")
            return False
        
        # 2. Check if status is open (REQUIRED)
        if status != 'open':
            log(f"❌ Rejecting: Job not open (status: {status})")
            return False
        
        # 3. Check if all required fields are present (REQUIRED)
        required_fields = ['language', 'duration', 'ref', 'submitted', 'appt_date', 'appt_time']
        missing_fields = []
        for field in required_fields:
            if not job_data.get(field, '').strip():
                missing_fields.append(field)
        
        if missing_fields:
            log(f"❌ Rejecting: Missing required fields: {missing_fields}")
            return False
        
        # 4. Check language is valid (REQUIRED)
        if not language or len(language) < 2:
            log(f"❌ Rejecting: Invalid language ({language})")
            return False
        
        # 5. Check duration is reasonable (REQUIRED)
        try:
            # Extract numeric duration (e.g., "2 hours" -> 2)
            duration_num = float(''.join(filter(str.isdigit, duration)))
            if duration_num < 0.5 or duration_num > 8:  # 30 minutes to 8 hours
                log(f"❌ Rejecting: Duration out of range ({duration})")
                return False
        except (ValueError, TypeError):
            log(f"❌ Rejecting: Invalid duration format ({duration})")
            return False
        
        # 6. Check for excluded job types in details
        excluded_keywords = ['face-to-face', 'face to face', 'in-person', 'onsite', 'physical', 'office']
        if any(keyword in details_text.lower() for keyword in excluded_keywords):
            log(f"❌ Rejecting: Contains excluded keywords in details")
            return False
        
        # 7. Check appointment date is not in the past
        try:
            from datetime import datetime
            appt_datetime = datetime.strptime(f"{appt_date} {appt_time}", "%Y-%m-%d %H:%M")
            if appt_datetime < datetime.now():
                log(f"❌ Rejecting: Appointment in the past ({appt_date} {appt_time})")
                return False
        except (ValueError, TypeError):
            log(f"⚠️ Warning: Could not parse appointment time ({appt_date} {appt_time})")
            # Don't reject for this, just log warning
        
        # 8. Additional quality checks
        if len(language) > 50:  # Language name too long
            log(f"❌ Rejecting: Language name too long ({len(language)} chars)")
            return False
        
        # All criteria passed
        log(f"✅ Accepting: {language} telephone job for {duration}")
        return True
        
    except Exception as e:
        log(f"Error evaluating job criteria: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python integrated_bot.py <session_id>")
        sys.exit(1)
    
    session_id = sys.argv[1]
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting integrated AtoZ bot for session {session_id}")
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize counters
    total_checks = 0
    total_accepted = 0
    total_rejected = 0
    login_successful = False
    
    try:
        # Update status to starting
        update_database(session_id, "starting", total_checks, total_accepted, total_rejected, "attempting")
        
        # Send real-time update about login attempt
        send_realtime_update("login_attempt", {
            "session_id": session_id,
            "message": "Attempting to log in..."
        })
        
        # Initialize browser
        log("Initializing browser...")
        playwright, browser, context, page = initialize_browser(headless=BOT_CONFIG.get("headless", True))
        
        try:
            # Attempt login
            log("Attempting to login to AtoZ portal...")
            if try_login(page):
                login_successful = True
                update_database(session_id, "running", total_checks, total_accepted, total_rejected, "success")
                log("✅ Login successful! Starting job monitoring...")
                
                # Send real-time update about successful login
                send_realtime_update("login_success", {
                    "session_id": session_id,
                    "message": "Successfully logged in! Bot is now running..."
                })
            else:
                log("❌ Login failed! Bot cannot continue without authentication")
                update_database(session_id, "error", total_checks, total_accepted, total_rejected, "failed")
                
                # Send real-time update about failed login
                send_realtime_update("login_failed", {
                    "session_id": session_id,
                    "message": "Login failed. Please check credentials."
                })
                return
            
            # Main bot loop - only start counting after successful login
            iteration = 0
            log("✅ Login successful! Starting job monitoring with 0.5-second checks...")
            
            while True:
                try:
                    iteration += 1
                    log(f"Bot iteration {iteration} - Checking for jobs...")
                    
                    # Send real-time update about job checking
                    send_realtime_update("checking_jobs", {
                        "session_id": session_id,
                        "iteration": iteration,
                        "message": f"Checking for jobs (iteration {iteration})..."
                    })
                    
                    # Check for jobs
                    accepted, rejected = check_jobs_on_page(page, session_id)
                    total_checks += 1
                    total_accepted += accepted
                    total_rejected += rejected
                    
                    log(f"Iteration {iteration} complete: {accepted} accepted, {rejected} rejected")
                    
                    # Send real-time update about job processing results
                    send_realtime_update("job_processing_complete", {
                        "session_id": session_id,
                        "iteration": iteration,
                        "accepted": accepted,
                        "rejected": rejected,
                        "total_checks": total_checks,
                        "total_accepted": total_accepted,
                        "total_rejected": total_rejected,
                        "message": f"Processed {accepted + rejected} jobs: {accepted} accepted, {rejected} rejected"
                    })
                    
                    # Update database with current status
                    update_database(session_id, "running", total_checks, total_accepted, total_rejected, "success")
                    
                    # Wait before next check (faster checks)
                    wait_time = BOT_CONFIG.get("check_interval", 0.5)
                    log(f"Waiting {wait_time}s before next check...")
                    time.sleep(wait_time)
                    
                except KeyboardInterrupt:
                    log("Bot stopped by user (KeyboardInterrupt)")
                    break
                except Exception as e:
                    log(f"Error in bot iteration {iteration}: {e}")
                    # Continue running instead of breaking
                    time.sleep(5)  # Wait a bit before retrying
                
        finally:
            # Clean up browser resources
            try:
                page.close()
                context.close()
                browser.close()
                playwright.stop()
                log("Browser resources cleaned up")
            except Exception as e:
                log(f"Error cleaning up browser: {e}")
            
    except KeyboardInterrupt:
        log("Bot stopped by user")
    except Exception as e:
        log(f"Bot error: {e}")
        update_database(session_id, "error", total_checks, total_accepted, total_rejected, "failed" if not login_successful else "success")
    finally:
        # Update final status
        final_status = "stopped" if login_successful else "error"
        update_database(session_id, final_status, total_checks, total_accepted, total_rejected, "success" if login_successful else "failed")
        log(f"Bot shutdown complete - Final stats: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")

if __name__ == "__main__":
    main()
