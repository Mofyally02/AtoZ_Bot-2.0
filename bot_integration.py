#!/usr/bin/env python3
"""
Integration script to connect existing AtoZ bot with the new dashboard
This script bridges the existing bot functionality with the new database and API
"""

import json
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict, Optional

import requests

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import BOT_CONFIG
from results_tracker import (add_accepted_job, add_rejected_job, get_tracker,
                             increment_check_cycle, set_login_status,
                             update_activity)


class BotDashboardIntegration:
    """Integrates existing bot with the new dashboard system"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.session_id: Optional[str] = None
        self.tracker = get_tracker()
        
    def start_session(self, session_name: str = None) -> str:
        """Start a new bot session and register with dashboard"""
        try:
            # Create session via API
            response = requests.post(
                f"{self.api_base_url}/api/bot/start",
                json={"session_name": session_name},
                timeout=10
            )
            
            if response.status_code == 200:
                session_data = response.json()
                self.session_id = session_data["id"]
                print(f"✅ Session started: {session_data['session_name']} (ID: {self.session_id})")
                return self.session_id
            else:
                print(f"❌ Failed to start session: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error starting session: {e}")
            return None
    
    def stop_session(self) -> bool:
        """Stop the current bot session"""
        try:
            if not self.session_id:
                print("⚠️  No active session to stop")
                return False
                
            response = requests.post(
                f"{self.api_base_url}/api/bot/stop",
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Session stopped successfully")
                self.session_id = None
                return True
            else:
                print(f"❌ Failed to stop session: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error stopping session: {e}")
            return False
    
    def sync_job_to_dashboard(self, job_data: Dict[str, Any], status: str, reason: str = None):
        """Sync job data to the dashboard database"""
        try:
            if not self.session_id:
                return
                
            # Prepare job data for API
            job_payload = {
                "job_ref": job_data.get("ref", ""),
                "language": job_data.get("language", ""),
                "appointment_date": job_data.get("appt_date", ""),
                "appointment_time": job_data.get("appt_time", ""),
                "duration": job_data.get("duration", ""),
                "submitted_at": job_data.get("submitted", ""),
                "status": status,
                "job_type": job_data.get("job_type", ""),
                "rejection_reason": reason
            }
            
            # Send to API (this would be implemented in the backend)
            # For now, we'll just log it
            print(f"📤 Syncing job to dashboard: {job_payload['job_ref']} - {status}")
            
        except Exception as e:
            print(f"❌ Error syncing job to dashboard: {e}")
    
    def sync_metrics_to_dashboard(self):
        """Sync current metrics to the dashboard"""
        try:
            if not self.session_id:
                return
                
            # Get current metrics from tracker
            metrics = {
                "total_checks": self.tracker.check_cycles,
                "total_accepted": len(self.tracker.accepted_jobs),
                "total_rejected": len(self.tracker.rejected_jobs),
                "acceptance_rate": self.tracker.get_acceptance_rate(),
                "last_activity": datetime.utcnow().isoformat()
            }
            
            # Send to API (this would be implemented in the backend)
            print(f"📊 Syncing metrics: {metrics}")
            
        except Exception as e:
            print(f"❌ Error syncing metrics: {e}")
    
    def enhanced_add_accepted_job(self, job: Dict[str, Any]):
        """Enhanced version of add_accepted_job that syncs to dashboard"""
        # Add to local tracker
        add_accepted_job(job)
        
        # Sync to dashboard
        self.sync_job_to_dashboard(job, "accepted")
        
        # Update metrics
        self.sync_metrics_to_dashboard()
    
    def enhanced_add_rejected_job(self, job: Dict[str, Any], reason: str = "Unknown"):
        """Enhanced version of add_rejected_job that syncs to dashboard"""
        # Add to local tracker
        add_rejected_job(job, reason)
        
        # Sync to dashboard
        self.sync_job_to_dashboard(job, "rejected", reason)
        
        # Update metrics
        self.sync_metrics_to_dashboard()
    
    def enhanced_set_login_status(self, status: str, success: bool = True):
        """Enhanced version of set_login_status that syncs to dashboard"""
        # Set in local tracker
        set_login_status(status, success)
        
        # Sync to dashboard
        try:
            if self.session_id:
                # This would update the session status in the database
                print(f"🔐 Syncing login status: {status} (Success: {success})")
        except Exception as e:
            print(f"❌ Error syncing login status: {e}")
    
    def enhanced_increment_check_cycle(self):
        """Enhanced version of increment_check_cycle that syncs to dashboard"""
        # Increment in local tracker
        increment_check_cycle()
        
        # Sync metrics periodically (every 10 cycles)
        if self.tracker.check_cycles % 10 == 0:
            self.sync_metrics_to_dashboard()

def create_integrated_persistent_bot():
    """Create an integrated version of the persistent bot"""
    
    # Import the existing persistent bot
    from persistent_bot import run_persistent_bot

    # Create integration instance
    integration = BotDashboardIntegration()
    
    # Start session
    session_name = f"Integrated_Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session_id = integration.start_session(session_name)
    
    if not session_id:
        print("❌ Failed to start integrated session, falling back to standalone mode")
        return run_persistent_bot()
    
    print("🚀 Starting integrated bot with dashboard connection...")
    
    try:
        # Monkey patch the tracker functions to use enhanced versions
        import results_tracker

        # Store original functions
        original_add_accepted = results_tracker.add_accepted_job
        original_add_rejected = results_tracker.add_rejected_job
        original_set_login = results_tracker.set_login_status
        original_increment = results_tracker.increment_check_cycle
        
        # Replace with enhanced versions
        results_tracker.add_accepted_job = integration.enhanced_add_accepted_job
        results_tracker.add_rejected_job = integration.enhanced_add_rejected_job
        results_tracker.set_login_status = integration.enhanced_set_login_status
        results_tracker.increment_check_cycle = integration.enhanced_increment_check_cycle
        
        # Run the persistent bot
        run_persistent_bot()
        
    except KeyboardInterrupt:
        print("\n⏹️  Bot stopped by user")
    except Exception as e:
        print(f"❌ Error in integrated bot: {e}")
    finally:
        # Restore original functions
        results_tracker.add_accepted_job = original_add_accepted
        results_tracker.add_rejected_job = original_add_rejected
        results_tracker.set_login_status = original_set_login
        results_tracker.increment_check_cycle = original_increment
        
        # Stop session
        integration.stop_session()

if __name__ == "__main__":
    print("🔗 AtoZ Bot Dashboard Integration")
    print("=" * 50)
    print("This script integrates the existing bot with the new dashboard.")
    print("Make sure the dashboard backend is running on http://localhost:8000")
    print()
    
    # Check if backend is available
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Dashboard backend is running")
        else:
            print("⚠️  Dashboard backend responded with error")
    except:
        print("❌ Dashboard backend is not available")
        print("   Please start the backend with: docker-compose up backend")
        print("   Or run: python backend/main.py")
        sys.exit(1)
    
    # Start integrated bot
    create_integrated_persistent_bot()
