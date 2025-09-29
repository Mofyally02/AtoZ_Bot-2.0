#!/usr/bin/env python3
"""
Realistic test bot that simulates AtoZ translation work
"""
import sys
import time
import signal
import os
import random
import json
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

def signal_handler(sig, frame):
    print(f"[{datetime.now(timezone.utc).isoformat()}] Bot received stop signal, shutting down...")
    sys.exit(0)

def update_database(session_id, status, checks=0, accepted=0, rejected=0):
    """Update the database with bot status"""
    try:
        # Connect to the database
        engine = create_engine("postgresql://atoz_user:atoz_password@localhost:5432/atoz_bot_db")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as db:
            # Update the session status
            db.execute(text("""
                UPDATE bot_sessions 
                SET status = :status, 
                    total_checks = :checks, 
                    total_accepted = :accepted, 
                    total_rejected = :rejected,
                    updated_at = :updated_at
                WHERE id = :session_id
            """), {
                'status': status,
                'checks': checks,
                'accepted': accepted,
                'rejected': rejected,
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'session_id': session_id
            })
            db.commit()
            print(f"[{datetime.now(timezone.utc).isoformat()}] Database updated: {status}, checks: {checks}, accepted: {accepted}, rejected: {rejected}")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Database update error: {e}")

def simulate_translation_work():
    """Simulate actual translation work"""
    # Simulate different types of jobs
    job_types = [
        {"type": "Medical", "difficulty": "High", "duration": 3},
        {"type": "Legal", "difficulty": "Medium", "duration": 2},
        {"type": "Business", "difficulty": "Low", "duration": 1},
        {"type": "Technical", "difficulty": "High", "duration": 4},
        {"type": "General", "difficulty": "Low", "duration": 1}
    ]
    
    job = random.choice(job_types)
    
    # Simulate job evaluation
    print(f"[{datetime.now(timezone.utc).isoformat()}] Evaluating {job['type']} job (difficulty: {job['difficulty']})")
    
    # Simulate acceptance/rejection based on difficulty and random factors
    if job['difficulty'] == 'Low' or (job['difficulty'] == 'Medium' and random.random() > 0.3):
        return "accepted", job
    else:
        return "rejected", job

def main():
    if len(sys.argv) < 2:
        print("Usage: python realistic_test_bot.py <session_id>")
        sys.exit(1)
    
    session_id = sys.argv[1]
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting realistic test bot for session {session_id}")
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    # Initialize counters
    total_checks = 0
    total_accepted = 0
    total_rejected = 0
    
    try:
        # Update status to running
        update_database(session_id, "running", total_checks, total_accepted, total_rejected)
        
        iteration = 0
        while True:
            iteration += 1
            print(f"[{datetime.now(timezone.utc).isoformat()}] Bot iteration {iteration} - Checking for jobs...")
            
            # Simulate checking for jobs (random chance of finding jobs)
            if random.random() > 0.3:  # 70% chance of finding jobs
                # Simulate finding 1-3 jobs
                num_jobs = random.randint(1, 3)
                print(f"[{datetime.now(timezone.utc).isoformat()}] Found {num_jobs} job(s) to evaluate")
                
                for job_num in range(num_jobs):
                    total_checks += 1
                    result, job_info = simulate_translation_work()
                    
                    if result == "accepted":
                        total_accepted += 1
                        print(f"[{datetime.now(timezone.utc).isoformat()}] ✅ ACCEPTED: {job_info['type']} job")
                    else:
                        total_rejected += 1
                        print(f"[{datetime.now(timezone.utc).isoformat()}] ❌ REJECTED: {job_info['type']} job")
                    
                    # Update database after each job
                    update_database(session_id, "running", total_checks, total_accepted, total_rejected)
                    
                    # Simulate processing time
                    time.sleep(random.uniform(1, 3))
            else:
                print(f"[{datetime.now(timezone.utc).isoformat()}] No jobs available at this time")
            
            # Update database with current status
            update_database(session_id, "running", total_checks, total_accepted, total_rejected)
            
            # Wait before next check (2-5 seconds)
            wait_time = random.uniform(2, 5)
            print(f"[{datetime.now(timezone.utc).isoformat()}] Waiting {wait_time:.1f}s before next check...")
            time.sleep(wait_time)
            
    except KeyboardInterrupt:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Bot stopped by user")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Bot error: {e}")
    finally:
        # Update status to stopped
        update_database(session_id, "stopped", total_checks, total_accepted, total_rejected)
        print(f"[{datetime.now(timezone.utc).isoformat()}] Bot shutdown complete - Final stats: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")

if __name__ == "__main__":
    main()

