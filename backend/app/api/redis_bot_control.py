"""
Redis-based bot control API endpoints
"""
import os
import subprocess
import asyncio
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.bot_models import BotSession, SystemLog
from app.schemas.bot_schemas import BotControlRequest, BotSessionResponse, BotStatusResponse
from app.services.redis_bot_state import redis_bot_state, BotState, BotTaskType
from app.services.connection_monitor import connection_monitor

router = APIRouter(prefix="/api/bot", tags=["bot-redis"])

# Global bot process tracking (fallback)
bot_process = None

@router.post("/start", response_model=BotSessionResponse)
async def start_bot_redis(
    request: BotControlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start the AtoZ bot using Redis state management"""
    global bot_process
    
    try:
        # Check if bot is already running using Redis
        if redis_bot_state.is_bot_running():
            raise HTTPException(status_code=400, detail="Bot is already running")
        
        # Create new bot session in database
        session = BotSession(
            session_name=request.session_name or f"Session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            status="starting"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Create session in Redis
        redis_bot_state.create_session(session)
        
        # Set bot state to starting
        redis_bot_state.set_bot_state(BotState.STARTING, str(session.id))
        
        # Start bot process
        bot_path = os.path.join(os.path.dirname(__file__), "../../../bot")
        if not os.path.exists(bot_path):
            raise HTTPException(status_code=500, detail="Bot directory not found")
        
        # Use the backend's Python environment
        python_executable = os.path.join(os.path.dirname(__file__), "../../../venv/bin/python")
        if not os.path.exists(python_executable):
            python_executable = "python"  # Fallback to system python
        
        # Check if integrated_bot.py exists (preferred)
        bot_script = os.path.join(bot_path, "integrated_bot.py")
        if not os.path.exists(bot_script):
            # Fallback to realistic_test_bot.py
            bot_script = os.path.join(bot_path, "realistic_test_bot.py")
            if not os.path.exists(bot_script):
                # Fallback to test_bot.py
                bot_script = os.path.join(bot_path, "test_bot.py")
                if not os.path.exists(bot_script):
                    raise HTTPException(status_code=500, detail="Bot script not found")
        
        try:
            bot_process = subprocess.Popen(
                [python_executable, os.path.basename(bot_script), str(session.id)],
                cwd=bot_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid if os.name != 'nt' else None,
                env=os.environ.copy()
            )
        except Exception as e:
            redis_bot_state.set_bot_state(BotState.ERROR, str(session.id))
            raise HTTPException(status_code=500, detail=f"Failed to start bot process: {str(e)}")
        
        # Update session status in both Redis and database
        session.status = "running"
        session.login_status = "attempting"
        db.commit()
        
        redis_bot_state.update_session(str(session.id), {
            "status": "running",
            "login_status": "attempting"
        })
        
        # Set bot state to running
        redis_bot_state.set_bot_state(BotState.RUNNING, str(session.id))
        
        # Add system log
        log_entry = SystemLog(
            session_id=session.id,
            log_level="INFO",
            message="Bot started successfully",
            component="api"
        )
        db.add(log_entry)
        db.commit()
        
        # Log event in Redis
        redis_bot_state.log_event(str(session.id), "bot_started", {
            "session_name": session.session_name,
            "process_id": bot_process.pid if bot_process else None
        })
        
        # Start background monitoring
        background_tasks.add_task(monitor_bot_process_redis, session.id, db)
        
        # Add initial tasks to queue
        redis_bot_state.add_task(BotTaskType.LOGIN, {
            "session_id": str(session.id),
            "username": "hussain02747@gmail.com"
        }, priority=10)
        
        redis_bot_state.add_task(BotTaskType.JOB_CHECK, {
            "session_id": str(session.id),
            "check_type": "initial"
        }, priority=5)
        
        return BotSessionResponse(
            id=str(session.id),
            session_name=session.session_name,
            start_time=session.start_time,
            end_time=session.end_time,
            status=session.status,
            login_status=session.login_status,
            total_checks=session.total_checks or 0,
            total_accepted=session.total_accepted or 0,
            total_rejected=session.total_rejected or 0,
            created_at=session.created_at,
            updated_at=session.updated_at
        )
        
    except Exception as e:
        if 'session' in locals():
            redis_bot_state.set_bot_state(BotState.ERROR, str(session.id))
            session.status = "error"
            db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")

@router.post("/stop", response_model=dict)
async def stop_bot_redis(db: Session = Depends(get_db)):
    """Stop the AtoZ bot using Redis state management"""
    global bot_process
    
    try:
        # Get current bot state
        bot_state = redis_bot_state.get_bot_state()
        current_session_id = bot_state.get("session_id")
        
        if not current_session_id:
            return {"message": "No active bot session to stop"}
        
        # Set bot state to stopping
        redis_bot_state.set_bot_state(BotState.STOPPING, current_session_id)
        
        # Kill bot process if running
        if bot_process and bot_process.poll() is None:
            try:
                bot_process.terminate()
                bot_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                bot_process.kill()
            except Exception as e:
                print(f"Error stopping bot process: {e}")
        
        # Update session in database
        session = db.query(BotSession).filter(BotSession.id == current_session_id).first()
        if session:
            session.status = "stopped"
            session.end_time = datetime.now(timezone.utc)
            db.commit()
        
        # End session in Redis
        redis_bot_state.end_session(current_session_id)
        redis_bot_state.set_bot_state(BotState.STOPPED)
        
        # Log event
        redis_bot_state.log_event(current_session_id, "bot_stopped", {
            "reason": "manual_stop"
        })
        
        bot_process = None
        
        return {"message": "Bot stopped successfully"}
        
    except Exception as e:
        print(f"Error stopping bot: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")

@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status_redis(db: Session = Depends(get_db)):
    """Get current bot status using Redis state management"""
    try:
        # Get bot state from Redis
        bot_state = redis_bot_state.get_bot_state()
        current_session_id = bot_state.get("session_id")
        
        is_running = bot_state.get("state") in ["starting", "running"]
        
        if current_session_id:
            # Get session data from Redis
            session_data = redis_bot_state.get_session(current_session_id)
            
            if session_data:
                return BotStatusResponse(
                    is_running=is_running,
                    session_id=session_data["id"],
                    session_name=session_data["session_name"],
                    start_time=session_data["start_time"],
                    status=session_data["status"],
                    login_status=session_data["login_status"],
                    total_checks=session_data["total_checks"],
                    total_accepted=session_data["total_accepted"],
                    total_rejected=session_data["total_rejected"]
                )
        
        return BotStatusResponse(
            is_running=is_running,
            session_id=current_session_id,
            session_name=None,
            start_time=None,
            status=bot_state.get("state", "stopped"),
            login_status="not_started",
            total_checks=0,
            total_accepted=0,
            total_rejected=0
        )
        
    except Exception as e:
        print(f"Error getting bot status: {e}")
        return BotStatusResponse(
            is_running=False,
            session_id=None,
            session_name=None,
            start_time=None,
            status="error",
            login_status="not_started",
            total_checks=0,
            total_accepted=0,
            total_rejected=0
        )

@router.get("/sessions")
async def get_sessions_redis(status: Optional[str] = None, db: Session = Depends(get_db)):
    """Get bot sessions using Redis state management"""
    try:
        if status == "running":
            # Get active sessions from Redis
            sessions = redis_bot_state.get_active_sessions()
            return sessions
        else:
            # Get all sessions from database
            query = db.query(BotSession)
            if status:
                query = query.filter(BotSession.status == status)
            
            sessions = query.order_by(BotSession.created_at.desc()).all()
            
            return [
                {
                    "id": str(session.id),
                    "session_name": session.session_name,
                    "start_time": session.start_time,
                    "end_time": session.end_time,
                    "status": session.status,
                    "login_status": session.login_status,
                    "total_checks": session.total_checks or 0,
                    "total_accepted": session.total_accepted or 0,
                    "total_rejected": session.total_rejected or 0,
                    "created_at": session.created_at,
                    "updated_at": session.updated_at
                }
                for session in sessions
            ]
            
    except Exception as e:
        print(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get sessions: {str(e)}")

@router.get("/tasks")
async def get_tasks_redis():
    """Get bot task queue status"""
    try:
        system_status = redis_bot_state.get_system_status()
        
        return {
            "pending_tasks": system_status["pending_tasks"],
            "processing_tasks": system_status["processing_tasks"],
            "bot_state": system_status["bot_state"],
            "active_sessions": system_status["active_sessions"]
        }
        
    except Exception as e:
        print(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get tasks: {str(e)}")

@router.get("/events/{session_id}")
async def get_session_events_redis(session_id: str, limit: int = 50):
    """Get events for a specific session"""
    try:
        events = redis_bot_state.get_recent_events(session_id, limit)
        return {"events": events}
        
    except Exception as e:
        print(f"Error getting events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get events: {str(e)}")

@router.get("/metrics/{session_id}")
async def get_session_metrics_redis(session_id: str):
    """Get metrics for a specific session"""
    try:
        metrics = redis_bot_state.get_metrics(session_id)
        return {"metrics": metrics}
        
    except Exception as e:
        print(f"Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@router.post("/tasks/add")
async def add_task_redis(
    task_type: str,
    data: dict,
    priority: int = 0
):
    """Add a task to the bot queue"""
    try:
        task_type_enum = BotTaskType(task_type)
        task_id = redis_bot_state.add_task(task_type_enum, data, priority)
        
        if task_id:
            return {"message": "Task added successfully", "task_id": task_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to add task")
            
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid task type: {task_type}")
    except Exception as e:
        print(f"Error adding task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to add task: {str(e)}")

@router.get("/system-status")
async def get_system_status_redis():
    """Get overall system status"""
    try:
        status = redis_bot_state.get_system_status()
        return status
        
    except Exception as e:
        print(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

async def monitor_bot_process_redis(session_id: str, db: Session):
    """Background task to monitor bot process using Redis"""
    global bot_process
    
    while bot_process and bot_process.poll() is None:
        try:
            # Update session with current metrics from Redis
            session_data = redis_bot_state.get_session(session_id)
            if session_data:
                # Update database session
                session = db.query(BotSession).filter(BotSession.id == session_id).first()
                if session:
                    session.total_checks = session_data.get("total_checks", 0)
                    session.total_accepted = session_data.get("total_accepted", 0)
                    session.total_rejected = session_data.get("total_rejected", 0)
                    session.login_status = session_data.get("login_status", "attempting")
                    db.commit()
                
                # Log metrics
                redis_bot_state.update_metrics(session_id, {
                    "total_checks": session_data.get("total_checks", 0),
                    "total_accepted": session_data.get("total_accepted", 0),
                    "total_rejected": session_data.get("total_rejected", 0),
                    "login_status": session_data.get("login_status", "attempting")
                })
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            print(f"Bot monitoring error: {e}")
            redis_bot_state.log_event(session_id, "monitoring_error", {
                "error": str(e)
            })
            break
    
    # Bot process ended
    redis_bot_state.set_bot_state(BotState.STOPPED)
    redis_bot_state.end_session(session_id)
    
    # Update database
    session = db.query(BotSession).filter(BotSession.id == session_id).first()
    if session and session.status == "running":
        session.status = "stopped"
        session.end_time = datetime.now(timezone.utc)
        db.commit()
    
    redis_bot_state.log_event(session_id, "bot_ended", {
        "reason": "process_ended"
    })
