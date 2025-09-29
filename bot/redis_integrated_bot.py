#!/usr/bin/env python3
"""
Redis-integrated AtoZ Bot with real-time state management
"""
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

from app.services.redis_bot_state import redis_bot_state, BotTaskType
from app.database.connection import get_db
from app.models.bot_models import BotSession, SystemLog

# Import existing bot components
from config import BOT_CONFIG
from login_handler import LoginHandler
from filter_handler import FilterHandler
from data_processor import DataProcessor

class RedisIntegratedBot:
    """AtoZ Bot with Redis state management"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.db = next(get_db())
        self.login_handler = LoginHandler()
        self.filter_handler = FilterHandler()
        self.data_processor = DataProcessor()
        self.running = True
        
        # Bot state
        self.current_status = "starting"
        self.login_status = "attempting"
        self.total_checks = 0
        self.total_accepted = 0
        self.total_rejected = 0
        
        print(f"✅ AtoZ config loaded.")
        print(f"[{datetime.now(timezone.utc).isoformat()}] Starting Redis-integrated AtoZ bot for session {session_id}")
    
    async def start(self):
        """Start the bot with Redis integration"""
        try:
            # Update initial state
            await self.update_state("starting", "attempting")
            
            # Initialize browser
            print("[AtoZBot] Initializing browser...")
            await self.login_handler.initialize_browser()
            
            # Perform login
            print("[AtoZBot] Attempting to login to AtoZ portal...")
            login_success = await self.perform_login()
            
            if login_success:
                await self.update_state("running", "success")
                print("[AtoZBot] ✅ Login successful! Starting job monitoring...")
                
                # Start main bot loop
                await self.main_loop()
            else:
                await self.update_state("error", "failed")
                print("[AtoZBot] ❌ Login failed!")
                
        except Exception as e:
            print(f"[AtoZBot] ❌ Bot error: {e}")
            await self.update_state("error", "failed")
            await self.log_event("bot_error", {"error": str(e)})
        finally:
            await self.cleanup()
    
    async def perform_login(self) -> bool:
        """Perform login with Redis task management"""
        try:
            # Add login task to queue
            task_id = redis_bot_state.add_task(BotTaskType.LOGIN, {
                "session_id": self.session_id,
                "username": BOT_CONFIG.get("username", "hussain02747@gmail.com")
            }, priority=10)
            
            print(f"[AtoZBot] Attempting to login with username: {BOT_CONFIG.get('username', 'hussain02747@gmail.com')}")
            
            # Perform actual login
            success = await self.login_handler.login()
            
            if success:
                await self.complete_task(task_id, {"status": "success"})
                await self.log_event("login_success", {"username": BOT_CONFIG.get("username")})
                return True
            else:
                await self.fail_task(task_id, "Login failed")
                await self.log_event("login_failed", {"username": BOT_CONFIG.get("username")})
                return False
                
        except Exception as e:
            print(f"[AtoZBot] Login error: {e}")
            await self.log_event("login_error", {"error": str(e)})
            return False
    
    async def main_loop(self):
        """Main bot monitoring loop"""
        iteration = 0
        
        while self.running:
            try:
                iteration += 1
                print(f"[AtoZBot] Bot iteration {iteration} - Checking for jobs...")
                
                # Add job check task
                task_id = redis_bot_state.add_task(BotTaskType.JOB_CHECK, {
                    "session_id": self.session_id,
                    "iteration": iteration,
                    "check_type": "scheduled"
                }, priority=5)
                
                # Perform job check
                jobs_found = await self.check_for_jobs()
                
                if jobs_found:
                    await self.complete_task(task_id, {"jobs_found": True, "count": len(jobs_found)})
                    await self.process_jobs(jobs_found)
                else:
                    await self.complete_task(task_id, {"jobs_found": False})
                
                print(f"[AtoZBot] Iteration {iteration} complete: {self.total_accepted} accepted, {self.total_rejected} rejected")
                
                # Update metrics
                await self.update_metrics()
                
                # Wait before next check
                wait_time = BOT_CONFIG.get("check_interval", 5)
                print(f"[AtoZBot] Waiting {wait_time}s before next check...")
                await asyncio.sleep(wait_time)
                
            except Exception as e:
                print(f"[AtoZBot] Error in main loop: {e}")
                await self.log_event("main_loop_error", {"error": str(e), "iteration": iteration})
                await asyncio.sleep(5)  # Wait before retrying
    
    async def check_for_jobs(self) -> list:
        """Check for available jobs"""
        try:
            print("[AtoZBot] Navigating to job board...")
            
            # Add navigation task
            nav_task_id = redis_bot_state.add_task(BotTaskType.NAVIGATION, {
                "session_id": self.session_id,
                "destination": "job_board"
            }, priority=7)
            
            # Navigate to job board
            await self.filter_handler.navigate_to_job_board()
            await self.complete_task(nav_task_id, {"status": "success"})
            
            # Check for jobs
            jobs = await self.filter_handler.get_available_jobs()
            
            if jobs:
                print(f"[AtoZBot] Found {len(jobs)} available jobs")
                await self.log_event("jobs_found", {"count": len(jobs), "jobs": jobs})
            else:
                print("[AtoZBot] No jobs available")
            
            return jobs
            
        except Exception as e:
            print(f"[AtoZBot] Error checking jobs: {e}")
            await self.log_event("job_check_error", {"error": str(e)})
            return []
    
    async def process_jobs(self, jobs: list):
        """Process found jobs"""
        for job in jobs:
            try:
                print(f"[AtoZBot] Processing job: {job.get('title', 'Unknown')}")
                
                # Add job processing task
                task_id = redis_bot_state.add_task(BotTaskType.JOB_ACCEPT, {
                    "session_id": self.session_id,
                    "job_id": job.get("id"),
                    "job_title": job.get("title")
                }, priority=8)
                
                # Process job
                result = await self.data_processor.process_job(job)
                
                if result.get("accepted"):
                    self.total_accepted += 1
                    await self.complete_task(task_id, {"status": "accepted", "job_id": job.get("id")})
                    await self.log_event("job_accepted", {"job_id": job.get("id"), "job_title": job.get("title")})
                else:
                    self.total_rejected += 1
                    await self.complete_task(task_id, {"status": "rejected", "job_id": job.get("id"), "reason": result.get("reason")})
                    await self.log_event("job_rejected", {"job_id": job.get("id"), "reason": result.get("reason")})
                
                # Update state
                await self.update_state("running", "success")
                
            except Exception as e:
                print(f"[AtoZBot] Error processing job: {e}")
                await self.log_event("job_processing_error", {"error": str(e), "job": job})
    
    async def update_state(self, status: str, login_status: str = None):
        """Update bot state in Redis and database"""
        try:
            self.current_status = status
            if login_status:
                self.login_status = login_status
            
            # Update Redis
            updates = {
                "status": status,
                "total_checks": self.total_checks,
                "total_accepted": self.total_accepted,
                "total_rejected": self.total_rejected
            }
            
            if login_status:
                updates["login_status"] = login_status
            
            redis_bot_state.update_session(self.session_id, updates)
            
            # Update database
            session = self.db.query(BotSession).filter(BotSession.id == self.session_id).first()
            if session:
                session.status = status
                session.total_checks = self.total_checks
                session.total_accepted = self.total_accepted
                session.total_rejected = self.total_rejected
                if login_status:
                    session.login_status = login_status
                self.db.commit()
            
            print(f"[{datetime.now(timezone.utc).isoformat()}] Database updated: {status}, login: {self.login_status}, checks: {self.total_checks}, accepted: {self.total_accepted}, rejected: {self.total_rejected}")
            
        except Exception as e:
            print(f"Error updating state: {e}")
    
    async def update_metrics(self):
        """Update bot metrics in Redis"""
        try:
            metrics = {
                "total_checks": self.total_checks,
                "total_accepted": self.total_accepted,
                "total_rejected": self.total_rejected,
                "login_status": self.login_status,
                "status": self.current_status,
                "uptime": time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }
            
            redis_bot_state.update_metrics(self.session_id, metrics)
            
        except Exception as e:
            print(f"Error updating metrics: {e}")
    
    async def log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to Redis"""
        try:
            redis_bot_state.log_event(self.session_id, event_type, data)
        except Exception as e:
            print(f"Error logging event: {e}")
    
    async def complete_task(self, task_id: str, result: Dict[str, Any]):
        """Complete a task in Redis"""
        try:
            redis_bot_state.complete_task(task_id, result)
        except Exception as e:
            print(f"Error completing task: {e}")
    
    async def fail_task(self, task_id: str, error: str):
        """Fail a task in Redis"""
        try:
            redis_bot_state.fail_task(task_id, error)
        except Exception as e:
            print(f"Error failing task: {e}")
    
    async def cleanup(self):
        """Cleanup bot resources"""
        try:
            print("[AtoZBot] Cleaning up...")
            
            # Update final state
            await self.update_state("stopped", self.login_status)
            
            # Log final event
            await self.log_event("bot_stopped", {
                "final_checks": self.total_checks,
                "final_accepted": self.total_accepted,
                "final_rejected": self.total_rejected
            })
            
            # Close browser
            if hasattr(self.login_handler, 'close_browser'):
                await self.login_handler.close_browser()
            
            print("[AtoZBot] Cleanup complete")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")

async def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python redis_integrated_bot.py <session_id>")
        sys.exit(1)
    
    session_id = sys.argv[1]
    bot = RedisIntegratedBot(session_id)
    bot.start_time = time.time()
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        print("\n[AtoZBot] Bot stopped by user")
        bot.running = False
    except Exception as e:
        print(f"[AtoZBot] Fatal error: {e}")
    finally:
        await bot.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
