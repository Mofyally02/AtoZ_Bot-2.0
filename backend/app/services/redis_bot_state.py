"""
Redis-based bot state management service
"""
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from enum import Enum

from app.database.connection import get_redis
from app.models.bot_models import BotSession

class BotState(Enum):
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class BotTaskType(Enum):
    LOGIN = "login"
    JOB_CHECK = "job_check"
    JOB_ACCEPT = "job_accept"
    JOB_REJECT = "job_reject"
    NAVIGATION = "navigation"
    SCREENSHOT = "screenshot"

class RedisBotStateManager:
    """Redis-based bot state management"""
    
    def __init__(self):
        try:
            self.redis = get_redis()
            self.redis_available = True
        except Exception as e:
            print(f"Redis not available, using fallback: {e}")
            self.redis = None
            self.redis_available = False
        
        self.bot_state_key = "bot:state"
        self.active_sessions_key = "bot:sessions:active"
        self.session_data_prefix = "bot:session:"
        self.task_queue_key = "bot:tasks:queue"
        self.task_processing_key = "bot:tasks:processing"
        self.bot_metrics_key = "bot:metrics"
        self.bot_events_key = "bot:events"
        
        # Fallback storage when Redis is not available
        self._fallback_state = {}
        self._fallback_sessions = {}
        self._fallback_tasks = []
        self._fallback_events = []
        
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session data"""
        return f"{self.session_data_prefix}{session_id}"
    
    def _get_task_key(self, task_id: str) -> str:
        """Get Redis key for task data"""
        return f"bot:task:{task_id}"
    
    def _fallback_operation(self, operation_name: str) -> bool:
        """Handle operations when Redis is not available"""
        print(f"Redis not available, {operation_name} skipped")
        return False
    
    # Bot State Management
    def set_bot_state(self, state: BotState, session_id: Optional[str] = None) -> bool:
        """Set overall bot state"""
        if not self.redis_available:
            self._fallback_state = {
                "state": state.value,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "updated_by": "system"
            }
            return True
            
        try:
            state_data = {
                "state": state.value,
                "session_id": session_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "updated_by": "system"
            }
            self.redis.hset(self.bot_state_key, mapping=state_data)
            return True
        except Exception as e:
            print(f"Error setting bot state: {e}")
            return False
    
    def get_bot_state(self) -> Dict[str, Any]:
        """Get current bot state"""
        if not self.redis_available:
            return self._fallback_state if self._fallback_state else {"state": "stopped", "session_id": None, "timestamp": None}
            
        try:
            state_data = self.redis.hgetall(self.bot_state_key)
            if not state_data:
                return {"state": "stopped", "session_id": None, "timestamp": None}
            return state_data
        except Exception as e:
            print(f"Error getting bot state: {e}")
            return {"state": "stopped", "session_id": None, "timestamp": None}
    
    def is_bot_running(self) -> bool:
        """Check if bot is currently running"""
        state = self.get_bot_state()
        return state.get("state") in ["starting", "running"]
    
    # Session Management
    def create_session(self, session: BotSession) -> bool:
        """Create a new bot session in Redis"""
        try:
            session_id = str(session.id)
            session_data = {
                "id": session_id,
                "session_name": session.session_name,
                "start_time": session.start_time.isoformat(),
                "status": session.status,
                "login_status": session.login_status,
                "total_checks": session.total_checks or 0,
                "total_accepted": session.total_accepted or 0,
                "total_rejected": session.total_rejected or 0,
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat()
            }
            
            # Store session data
            self.redis.hset(self._get_session_key(session_id), mapping=session_data)
            
            # Add to active sessions set
            self.redis.sadd(self.active_sessions_key, session_id)
            
            # Set as current active session
            self.redis.hset(self.bot_state_key, "current_session_id", session_id)
            
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def update_session(self, session_id: str, updates: Dict[str, Any]) -> bool:
        """Update session data in Redis"""
        try:
            session_key = self._get_session_key(session_id)
            
            # Add timestamp to updates
            updates["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # Update session data
            self.redis.hset(session_key, mapping=updates)
            
            return True
        except Exception as e:
            print(f"Error updating session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from Redis"""
        try:
            session_data = self.redis.hgetall(self._get_session_key(session_id))
            if not session_data:
                return None
            
            # Convert numeric fields
            if "total_checks" in session_data:
                session_data["total_checks"] = int(session_data["total_checks"])
            if "total_accepted" in session_data:
                session_data["total_accepted"] = int(session_data["total_accepted"])
            if "total_rejected" in session_data:
                session_data["total_rejected"] = int(session_data["total_rejected"])
                
            return session_data
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions"""
        try:
            session_ids = self.redis.smembers(self.active_sessions_key)
            sessions = []
            
            for session_id in session_ids:
                session_data = self.get_session(session_id)
                if session_data:
                    sessions.append(session_data)
            
            return sessions
        except Exception as e:
            print(f"Error getting active sessions: {e}")
            return []
    
    def end_session(self, session_id: str) -> bool:
        """End a session and remove from active sessions"""
        try:
            # Update session status
            self.update_session(session_id, {
                "status": "stopped",
                "end_time": datetime.now(timezone.utc).isoformat()
            })
            
            # Remove from active sessions
            self.redis.srem(self.active_sessions_key, session_id)
            
            # Clear current session if it's the active one
            current_session = self.redis.hget(self.bot_state_key, "current_session_id")
            if current_session == session_id:
                self.redis.hdel(self.bot_state_key, "current_session_id")
            
            return True
        except Exception as e:
            print(f"Error ending session: {e}")
            return False
    
    # Task Queue Management
    def add_task(self, task_type: BotTaskType, data: Dict[str, Any], priority: int = 0) -> str:
        """Add a task to the bot task queue"""
        try:
            task_id = str(uuid.uuid4())
            task_data = {
                "id": task_id,
                "type": task_type.value,
                "data": json.dumps(data),
                "priority": priority,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "status": "pending"
            }
            
            # Store task data
            self.redis.hset(self._get_task_key(task_id), mapping=task_data)
            
            # Add to priority queue (higher priority = lower score for sorted set)
            self.redis.zadd(self.task_queue_key, {task_id: -priority})
            
            return task_id
        except Exception as e:
            print(f"Error adding task: {e}")
            return ""
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next task from the queue"""
        try:
            # Get highest priority task
            result = self.redis.zpopmin(self.task_queue_key, count=1)
            if not result:
                return None
            
            task_id = result[0][0]
            task_data = self.redis.hgetall(self._get_task_key(task_id))
            
            if task_data:
                # Move to processing queue
                self.redis.zadd(self.task_processing_key, {task_id: time.time()})
                task_data["data"] = json.loads(task_data["data"])
                return task_data
            
            return None
        except Exception as e:
            print(f"Error getting next task: {e}")
            return None
    
    def complete_task(self, task_id: str, result: Dict[str, Any] = None) -> bool:
        """Mark a task as completed"""
        try:
            # Update task status
            updates = {
                "status": "completed",
                "completed_at": datetime.now(timezone.utc).isoformat()
            }
            if result:
                updates["result"] = json.dumps(result)
            
            self.redis.hset(self._get_task_key(task_id), mapping=updates)
            
            # Remove from processing queue
            self.redis.zrem(self.task_processing_key, task_id)
            
            return True
        except Exception as e:
            print(f"Error completing task: {e}")
            return False
    
    def fail_task(self, task_id: str, error: str) -> bool:
        """Mark a task as failed"""
        try:
            updates = {
                "status": "failed",
                "error": error,
                "failed_at": datetime.now(timezone.utc).isoformat()
            }
            
            self.redis.hset(self._get_task_key(task_id), mapping=updates)
            
            # Remove from processing queue
            self.redis.zrem(self.task_processing_key, task_id)
            
            return True
        except Exception as e:
            print(f"Error failing task: {e}")
            return False
    
    # Metrics and Monitoring
    def update_metrics(self, session_id: str, metrics: Dict[str, Any]) -> bool:
        """Update bot metrics"""
        try:
            metrics_key = f"{self.bot_metrics_key}:{session_id}"
            metrics["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            self.redis.hset(metrics_key, mapping=metrics)
            
            # Set expiration (keep metrics for 24 hours)
            self.redis.expire(metrics_key, 86400)
            
            return True
        except Exception as e:
            print(f"Error updating metrics: {e}")
            return False
    
    def get_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get bot metrics for a session"""
        try:
            metrics_key = f"{self.bot_metrics_key}:{session_id}"
            return self.redis.hgetall(metrics_key)
        except Exception as e:
            print(f"Error getting metrics: {e}")
            return {}
    
    def log_event(self, session_id: str, event_type: str, data: Dict[str, Any]) -> bool:
        """Log a bot event"""
        try:
            event_id = str(uuid.uuid4())
            event_data = {
                "id": event_id,
                "session_id": session_id,
                "type": event_type,
                "data": json.dumps(data),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            # Store event
            self.redis.lpush(self.bot_events_key, json.dumps(event_data))
            
            # Keep only last 1000 events
            self.redis.ltrim(self.bot_events_key, 0, 999)
            
            return True
        except Exception as e:
            print(f"Error logging event: {e}")
            return False
    
    def get_recent_events(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent events for a session"""
        try:
            events = self.redis.lrange(self.bot_events_key, 0, limit - 1)
            session_events = []
            
            for event_json in events:
                event = json.loads(event_json)
                if event.get("session_id") == session_id:
                    event["data"] = json.loads(event["data"])
                    session_events.append(event)
            
            return session_events
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    # Cleanup and Maintenance
    def cleanup_expired_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up expired sessions"""
        try:
            cutoff_time = datetime.now(timezone.utc).timestamp() - (max_age_hours * 3600)
            cleaned = 0
            
            session_ids = self.redis.smembers(self.active_sessions_key)
            for session_id in session_ids:
                session_data = self.get_session(session_id)
                if session_data:
                    created_at = datetime.fromisoformat(session_data["created_at"])
                    if created_at.timestamp() < cutoff_time:
                        self.end_session(session_id)
                        cleaned += 1
            
            return cleaned
        except Exception as e:
            print(f"Error cleaning up sessions: {e}")
            return 0
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        try:
            bot_state = self.get_bot_state()
            active_sessions = self.get_active_sessions()
            
            # Count tasks
            pending_tasks = self.redis.zcard(self.task_queue_key)
            processing_tasks = self.redis.zcard(self.task_processing_key)
            
            return {
                "bot_state": bot_state,
                "active_sessions_count": len(active_sessions),
                "active_sessions": active_sessions,
                "pending_tasks": pending_tasks,
                "processing_tasks": processing_tasks,
                "redis_connected": True
            }
        except Exception as e:
            print(f"Error getting system status: {e}")
            return {
                "bot_state": {"state": "unknown"},
                "active_sessions_count": 0,
                "active_sessions": [],
                "pending_tasks": 0,
                "processing_tasks": 0,
                "redis_connected": False,
                "error": str(e)
            }

# Global instance
redis_bot_state = RedisBotStateManager()
