"""
Bot service for managing bot operations and data processing
"""
import os
import signal
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import psutil
from sqlalchemy.orm import Session

from ..database.connection import get_redis
from ..models.bot_models import (AnalyticsPeriod, BotSession,
                                    JobRecord, SystemLog)


class BotService:
    """Service for managing bot operations"""
    
    def __init__(self):
        try:
            self.redis_client = get_redis()
        except Exception as e:
            print(f"Redis not available, running without Redis: {e}")
            self.redis_client = None
        self.bot_process = None
    
    def start_bot(self, session_id: str, config: Dict[str, Any]) -> bool:
        """Start the bot process"""
        try:
            # Set bot configuration in Redis (if available)
            if self.redis_client:
                self.redis_client.hset(f"bot_config:{session_id}", mapping=config)
            
            # Start bot process
            bot_script_path = os.path.join(
                os.path.dirname(__file__), 
                "../../../persistent_bot.py"
            )
            
            self.bot_process = subprocess.Popen(
                [sys.executable, bot_script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )
            
            # Store process info in Redis (if available)
            if self.redis_client:
                self.redis_client.hset(
                    f"bot_process:{session_id}",
                    mapping={
                        "pid": str(self.bot_process.pid),
                        "start_time": datetime.now(timezone.utc).isoformat(),
                        "status": "running"
                    }
                )
            
            return True
            
        except Exception as e:
            print(f"Error starting bot: {e}")
            return False
    
    def stop_bot(self, session_id: str) -> bool:
        """Stop the bot process"""
        try:
            # Get process info from Redis (if available)
            if self.redis_client:
                process_info = self.redis_client.hgetall(f"bot_process:{session_id}")
                
                if process_info and "pid" in process_info:
                    pid = int(process_info["pid"])
                    
                    # Terminate process
                    if os.name == 'nt':  # Windows
                        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)])
                    else:  # Unix-like
                        os.killpg(os.getpgid(pid), signal.SIGTERM)
                
                # Clean up Redis data
                self.redis_client.delete(f"bot_process:{session_id}")
                self.redis_client.delete(f"bot_config:{session_id}")
            
            return True
            
        except Exception as e:
            print(f"Error stopping bot: {e}")
            return False
    
    def is_bot_running(self, session_id: str) -> bool:
        """Check if bot is running"""
        if not self.redis_client:
            return False
            
        process_info = self.redis_client.hgetall(f"bot_process:{session_id}")
        
        if not process_info or "pid" not in process_info:
            return False
        
        try:
            pid = int(process_info["pid"])
            return psutil.pid_exists(pid)
        except:
            return False
    
    def get_bot_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get current bot metrics from Redis"""
        if not self.redis_client:
            return {}
            
        metrics = self.redis_client.hgetall(f"bot_metrics:{session_id}")
        
        # Convert string values to appropriate types
        result = {}
        for key, value in metrics.items():
            if key in ["total_checks", "total_accepted", "total_rejected"]:
                result[key] = int(value)
            elif key in ["acceptance_rate", "success_rate"]:
                result[key] = float(value)
            else:
                result[key] = value
        
        return result
    
    def update_bot_metrics(self, session_id: str, metrics: Dict[str, Any]):
        """Update bot metrics in Redis"""
        if self.redis_client:
            self.redis_client.hset(f"bot_metrics:{session_id}", mapping=metrics)
    
    def log_bot_activity(self, session_id: str, level: str, message: str, component: str = "bot"):
        """Log bot activity to Redis and database"""
        log_entry = {
            "session_id": session_id,
            "level": level,
            "message": message,
            "component": component,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Store in Redis for real-time access (if available)
        if self.redis_client:
            self.redis_client.lpush(f"bot_logs:{session_id}", str(log_entry))
            self.redis_client.ltrim(f"bot_logs:{session_id}", 0, 999)  # Keep last 1000 logs
    
    def get_recent_logs(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent bot logs"""
        if not self.redis_client:
            return []
            
        logs = self.redis_client.lrange(f"bot_logs:{session_id}", 0, limit - 1)
        return [eval(log) for log in logs]  # Convert string back to dict
    
    def create_analytics_period(self, db: Session, start_time: datetime, end_time: datetime) -> AnalyticsPeriod:
        """Create analytics period with calculated metrics"""
        
        # Get job records for the period
        jobs = db.query(JobRecord).filter(
            JobRecord.scraped_at >= start_time,
            JobRecord.scraped_at < end_time
        ).all()
        
        # Calculate metrics
        total_jobs = len(jobs)
        accepted_jobs = len([j for j in jobs if j.status == "accepted"])
        rejected_jobs = len([j for j in jobs if j.status == "rejected"])
        
        acceptance_rate = (accepted_jobs / total_jobs * 100) if total_jobs > 0 else 0
        
        # Language distribution
        language_counts = {}
        for job in jobs:
            language_counts[job.language] = language_counts.get(job.language, 0) + 1
        
        most_common_language = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else None
        
        # Hourly distribution
        hourly_counts = {}
        for job in jobs:
            hour = job.appointment_time.hour
            hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
        
        peak_hour = max(hourly_counts.items(), key=lambda x: x[1])[0] if hourly_counts else None
        
        # Create analytics period
        analytics = AnalyticsPeriod(
            period_start=start_time,
            period_end=end_time,
            total_jobs_processed=total_jobs,
            jobs_accepted=accepted_jobs,
            jobs_rejected=rejected_jobs,
            acceptance_rate=acceptance_rate,
            most_common_language=most_common_language,
            peak_hour=peak_hour
        )
        
        db.add(analytics)
        db.commit()
        db.refresh(analytics)
        
        return analytics
    
    def cleanup_old_data(self, db: Session, days: int = 7):
        """Clean up old data based on retention policy"""
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Delete old analytics periods
        db.query(AnalyticsPeriod).filter(
            AnalyticsPeriod.period_start < cutoff_date
        ).delete()
        
        # Delete old system logs
        db.query(SystemLog).filter(
            SystemLog.created_at < cutoff_date
        ).delete()
        
        # Delete old job records (keep only rejected and failed)
        db.query(JobRecord).filter(
            JobRecord.created_at < cutoff_date,
            ~JobRecord.status.in_(['rejected', 'failed'])
        ).delete()
        
        # Update old running sessions
        db.query(BotSession).filter(
            BotSession.status == "running",
            BotSession.start_time < cutoff_date
        ).update({
            "status": "stopped",
            "end_time": datetime.now(timezone.utc)
        })
        
        db.commit()
    
    def get_dashboard_metrics(self, db: Session) -> Dict[str, Any]:
        """Get dashboard metrics for the frontend"""
        today = datetime.now(timezone.utc).date()
        today_start = datetime.combine(today, datetime.min.time())
        
        # Active sessions
        active_sessions = db.query(BotSession).filter(
            BotSession.status == "running"
        ).count()
        
        # Today's jobs
        today_jobs = db.query(JobRecord).filter(
            JobRecord.scraped_at >= today_start
        ).all()
        
        total_jobs_today = len(today_jobs)
        accepted_today = len([j for j in today_jobs if j.status == "accepted"])
        acceptance_rate_today = (accepted_today / total_jobs_today * 100) if total_jobs_today > 0 else 0
        
        # Most active language today
        language_counts = {}
        for job in today_jobs:
            language_counts[job.language] = language_counts.get(job.language, 0) + 1
        
        most_active_language = max(language_counts.items(), key=lambda x: x[1])[0] if language_counts else None
        
        # Bot uptime (from active sessions)
        active_session = db.query(BotSession).filter(
            BotSession.status == "running"
        ).first()
        
        bot_uptime_hours = 0
        if active_session:
            now = datetime.now(timezone.utc)
            start_time = active_session.start_time
            # Ensure both datetimes are timezone-aware
            if start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            uptime = now - start_time
            bot_uptime_hours = uptime.total_seconds() / 3600
        
        # Last activity
        last_job = db.query(JobRecord).order_by(
            JobRecord.scraped_at.desc()
        ).first()
        
        last_activity = last_job.scraped_at if last_job else None
        
        return {
            "active_sessions": active_sessions,
            "total_jobs_today": total_jobs_today,
            "acceptance_rate_today": round(acceptance_rate_today, 2),
            "most_active_language": most_active_language,
            "bot_uptime_hours": round(bot_uptime_hours, 2),
            "last_activity": last_activity
        }
