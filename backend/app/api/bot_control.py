"""
Bot control API endpoints
"""
import asyncio
import json
import os
import signal
import subprocess
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

import psutil
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database.connection import get_db
from app.models.bot_models import (BotConfiguration, BotSession,
                                           JobRecord, SystemLog)
from app.schemas.bot_schemas import (AnalyticsResponse,
                                             BotControlRequest,
                                             BotSessionCreate,
                                             BotSessionResponse,
                                             BotStatusResponse,
                                             JobRecordResponse,
                                             DashboardMetrics,
                                             BotConfigurationResponse)
from app.services.bot_service import BotService

router = APIRouter(prefix="/api/bot", tags=["bot-control"])

# Custom JSON encoder to handle UUIDs and datetimes
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Global bot process tracking
bot_process = None
bot_thread = None
bot_running = False
bot_service = BotService()

# Initialize bot_running to False to ensure clean state
bot_running = False
bot_thread = None

# Bot state management
class BotState:
    def __init__(self):
        self.running = False
        self.thread = None
        self.process = None
        self.lock = threading.Lock()
    
    def is_running(self):
        with self.lock:
            print(f"[DEBUG] is_running check: self.running={self.running}, self.thread={self.thread}")
            if self.thread:
                print(f"[DEBUG] Thread alive: {self.thread.is_alive()}")
            
            # Check if we have a thread and it's actually alive
            if self.thread and self.thread.is_alive():
                print(f"[DEBUG] Bot is running (thread alive)")
                return True
            # If thread is dead, reset the state
            if self.thread and not self.thread.is_alive():
                print(f"[DEBUG] Thread is dead, resetting state")
                self.running = False
                self.thread = None
            
            print(f"[DEBUG] Bot is not running")
            return False
    
    def start(self):
        with self.lock:
            # Check if we already have a running thread
            if self.thread and self.thread.is_alive():
                return False  # Already running
            
            # Start new thread
            self.running = True
            self.thread = threading.Thread(target=bot_loop, daemon=True)
            self.thread.start()
            return True
    
    def stop(self):
        with self.lock:
            # Check if we have a running thread
            if self.thread and self.thread.is_alive():
                self.running = False
                self.thread.join(timeout=5)
                self.thread = None
                return True
            
            # Reset state even if no thread
            self.running = False
            self.thread = None
            return True
    
    def reset(self):
        with self.lock:
            self.running = False
            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=2)
            self.thread = None
            self.process = None

# Global bot state
bot_state = BotState()

# Reset bot state on startup
bot_state.reset()

@router.post("/force-reset", response_model=dict)
async def force_reset_bot():
    """Force reset bot state completely"""
    print(f"\n🔄 FORCE RESET REQUEST:")
    
    # Kill any existing bot processes
    import subprocess
    try:
        subprocess.run(['pkill', '-f', 'real_atoz_bot'], check=False)
        print("   🔪 Killed any existing bot processes")
    except:
        pass
    
    # Force reset bot state
    bot_state.reset()
    print(f"   🔄 Reset bot state")
    
    # Reset database sessions
    try:
        from app.database.connection import get_db
        db = next(get_db())
        if db:
            db.execute(text("""
                UPDATE bot_sessions 
                SET status = 'stopped', updated_at = :updated_at
                WHERE status = 'running' OR status = 'starting'
            """), {
                'updated_at': datetime.now(timezone.utc).isoformat()
            })
            db.commit()
            print(f"   🗄️ Reset database sessions")
    except Exception as e:
        print(f"   ⚠️ Could not reset database sessions: {e}")
    
    print(f"   ✅ Force reset complete")
    return {"status": "Force reset complete", "running": bot_state.is_running()}

def bot_loop():
    """Bot loop function that runs the real AtoZ bot script"""
    global bot_running
    print(f"[{datetime.now()}] 🤖 REAL ATOZ BOT STARTED!")
    print(f"[{datetime.now()}] 🔍 bot_running flag: {bot_running}")
    print(f"[{datetime.now()}] 🧵 Thread is executing bot_loop function!")
    
    try:
        # Import and run the real AtoZ bot
        import subprocess
        import os
        
        # Get the path to the real AtoZ bot script
        bot_script_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "bot", "real_atoz_bot.py")
        bot_script_path = os.path.abspath(bot_script_path)
        
        print(f"[{datetime.now()}] 🚀 Running real AtoZ bot: {bot_script_path}")
        
        # Run the real AtoZ bot script
        process = subprocess.Popen(
            [sys.executable, bot_script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=os.path.dirname(bot_script_path)
        )
        
        # Monitor the process while bot state is running
        while bot_state.is_running() and process.poll() is None:
            time.sleep(0.1)
        
        # If bot state is not running, terminate the process
        if not bot_state.is_running() and process.poll() is None:
            print(f"[{datetime.now()}] 🛑 Stopping real AtoZ bot...")
            
            # Create stop signal file for the bot to detect
            stop_file_path = os.path.join(os.path.dirname(__file__), "..", "..", "bot_stop_signal.txt")
            try:
                with open(stop_file_path, 'w') as f:
                    f.write("stop")
                print(f"[{datetime.now()}] 📝 Created stop signal file")
            except Exception as e:
                print(f"[{datetime.now()}] ⚠️ Could not create stop signal file: {e}")
            
            # Give the bot a moment to detect the stop signal
            time.sleep(1)
            
            # Force terminate if still running
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            
            # Clean up stop signal file
            try:
                if os.path.exists(stop_file_path):
                    os.remove(stop_file_path)
            except:
                pass
        
        print(f"[{datetime.now()}] ✅ Real AtoZ bot finished")
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error in bot_loop: {e}")
        import traceback
        traceback.print_exc()

@router.post("/realtime-update")
async def realtime_update(update_data: dict):
    """Handle real-time updates from the bot"""
    try:
        print(f"[{datetime.now()}] 📡 Real-time update received: {update_data.get('type', 'unknown')}")
        
        # Handle different types of updates
        update_type = update_data.get('type', '')
        data = update_data.get('data', {})
        
        if update_type == "database_update":
            # Update database with bot status
            session_id = data.get('session_id')
            status = data.get('status', 'running')
            total_checks = data.get('total_checks', 0)
            total_accepted = data.get('total_accepted', 0)
            total_rejected = data.get('total_rejected', 0)
            login_status = data.get('login_status', 'unknown')
            
            if session_id:
                try:
                    from app.database.connection import get_db
                    from sqlalchemy import text
                    
                    db = next(get_db())
                    if db:
                        # Update or create session
                        db.execute(text("""
                            INSERT OR REPLACE INTO bot_sessions 
                            (id, session_name, status, login_status, total_checks, total_accepted, total_rejected, created_at, updated_at)
                            VALUES (:id, :session_name, :status, :login_status, :checks, :accepted, :rejected, :created_at, :updated_at)
                        """), {
                            'id': session_id,
                            'session_name': f"real-atoz-session-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                            'status': status,
                            'login_status': login_status,
                            'checks': total_checks,
                            'accepted': total_accepted,
                            'rejected': total_rejected,
                            'created_at': datetime.now(timezone.utc).isoformat(),
                            'updated_at': datetime.now(timezone.utc).isoformat()
                        })
                        db.commit()
                        print(f"[{datetime.now()}] 💾 Database updated: {total_checks} checks, {total_accepted} accepted, {total_rejected} rejected")
                except Exception as e:
                    print(f"[{datetime.now()}] ❌ Database update error: {e}")
        
        return {"status": "update_received", "type": update_type}
        
    except Exception as e:
        print(f"[{datetime.now()}] ❌ Error handling real-time update: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/toggle", response_model=dict)
async def toggle_bot():
    """Toggle bot on/off using proper state management"""
    print(f"\n🤖 BOT TOGGLE REQUEST:")
    print(f"   Current bot state: {bot_state.is_running()}")
    
    if not bot_state.is_running():
        # Start bot
        print(f"   🟢 STARTING BOT...")
        if bot_state.start():
            print(f"   ✅ Bot started successfully")
            response = {"status": "Bot started", "running": True}
        else:
            print(f"   ❌ Failed to start bot")
            response = {"status": "Failed to start bot", "running": False}
    else:
        # Stop bot
        print(f"   🔴 STOPPING BOT...")
        if bot_state.stop():
            print(f"   ✅ Bot stopped successfully")
            
            # Reset database sessions
            try:
                from app.database.connection import get_db
                db = next(get_db())
                if db:
                    db.execute(text("""
                        UPDATE bot_sessions 
                        SET status = 'stopped', updated_at = :updated_at
                        WHERE status = 'running'
                    """), {
                        'updated_at': datetime.now(timezone.utc).isoformat()
                    })
                    db.commit()
                    print(f"   🔧 Reset database sessions to stopped")
            except Exception as e:
                print(f"   ⚠️ Could not reset database sessions: {e}")
            
            response = {"status": "Bot stopped", "running": False}
        else:
            print(f"   ❌ Failed to stop bot")
            response = {"status": "Failed to stop bot", "running": True}
    
    # Correct response logic
    if bot_state.is_running():
        response = {"status": "Bot started", "running": True}
    else:
        response = {"status": "Bot stopped", "running": False}
    
    print(f"   📤 RESPONSE: {response}")
    print(f"   {'='*40}")
    return response

@router.post("/start", response_model=BotSessionResponse)
async def start_bot(
    request: BotControlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start the AtoZ bot with connection validation"""
    global bot_process
    
    # Check if bot is already running
    if bot_process and bot_process.poll() is None:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    session = None  # Initialize session variable
    try:
        # First, check all connections before starting bot
        from app.services.connection_monitor import connection_monitor
        connection_status = await connection_monitor.check_all_services()
        
        # Check if critical services are healthy
        critical_services = ['database', 'external_api', 'websocket']
        unhealthy_services = []
        
        if connection_status:
            for service in critical_services:
                if service in connection_status and connection_status[service].status != 'healthy':
                    unhealthy_services.append(service)
        else:
            # If connection status is None, assume all services are unhealthy
            unhealthy_services = critical_services
        
        if unhealthy_services:
            raise HTTPException(
                status_code=503, 
                detail=f"Cannot start bot: Critical services are not healthy: {', '.join(unhealthy_services)}"
            )
        
        # Create new bot session
        session = BotSession(
            session_name=request.session_name or f"Session_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            status="starting"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Send real-time update about connection check
        await send_realtime_update("connection_check", {
            "status": "success",
            "message": "All connections verified successfully",
            "session_id": str(session.id)
        })
        
        # Start bot process
        bot_path = os.path.join(os.path.dirname(__file__), "../../../bot")
        if not os.path.exists(bot_path):
            raise HTTPException(status_code=500, detail="Bot directory not found")
        
        # Use the backend's Python environment
        python_executable = os.path.join(os.path.dirname(__file__), "../../../venv/bin/python")
        if not os.path.exists(python_executable):
            python_executable = "python"  # Fallback to system python
        
        # Check if smart_bot.py exists (preferred for testing)
        bot_script = os.path.join(bot_path, "smart_bot.py")
        if not os.path.exists(bot_script):
            # Fallback to integrated_bot.py
            bot_script = os.path.join(bot_path, "integrated_bot.py")
            if not os.path.exists(bot_script):
                # Fallback to realistic_test_bot.py
                bot_script = os.path.join(bot_path, "realistic_test_bot.py")
                if not os.path.exists(bot_script):
                    # Fallback to test_bot.py
                    bot_script = os.path.join(bot_path, "test_bot.py")
                    if not os.path.exists(bot_script):
                        raise HTTPException(status_code=500, detail="Bot script not found")
        
        # Send real-time update about bot process starting
        await send_realtime_update("bot_starting", {
            "status": "starting",
            "message": "Starting bot process...",
            "session_id": str(session.id)
        })
        
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
            await send_realtime_update("bot_error", {
                "status": "error",
                "message": f"Failed to start bot process: {str(e)}",
                "session_id": str(session.id)
            })
            raise HTTPException(status_code=500, detail=f"Failed to start bot process: {str(e)}")
        
        # Update session status
        session.status = "running"
        session.login_status = "attempting"
        db.commit()
        
        # Send real-time update about bot process started
        await send_realtime_update("bot_started", {
            "status": "running",
            "message": "Bot process started successfully",
            "session_id": str(session.id)
        })
        
        # Add system log
        log_entry = SystemLog(
            session_id=session.id,
            log_level="INFO",
            message="Bot started successfully",
            component="api"
        )
        db.add(log_entry)
        db.commit()
        
        # Start background monitoring
        background_tasks.add_task(monitor_bot_process, session.id, db)
        
        # Return immediately after starting the process
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
        if session:
            session.status = "error"
            db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")

@router.post("/realtime-update")
async def receive_realtime_update(update_data: dict, db: Session = Depends(get_db)):
    """Receive real-time updates from bot processes"""
    try:
        update_type = update_data.get("type")
        data = update_data.get("data", {})
        
        # Handle database updates from smart bot
        if update_type == "database_update" and "session_id" in data:
            session_id = data["session_id"]
            session = db.query(BotSession).filter(BotSession.id == session_id).first()
            if session:
                session.status = data.get("status", session.status)
                session.login_status = data.get("login_status", session.login_status)
                session.total_checks = data.get("total_checks", session.total_checks)
                session.total_accepted = data.get("total_accepted", session.total_accepted)
                session.total_rejected = data.get("total_rejected", session.total_rejected)
                session.updated_at = datetime.now(timezone.utc)
                db.commit()
        
        # Broadcast the update to all connected WebSocket clients
        await send_realtime_update(update_type, data)
        return {"status": "success", "message": "Update broadcasted"}
    except Exception as e:
        print(f"Error handling real-time update: {e}")
        return {"status": "error", "message": str(e)}

@router.post("/stop", response_model=dict)
async def stop_bot(db: Session = Depends(get_db)):
    """Stop the AtoZ bot immediately"""
    global bot_process
    
    # Get current running session first
    current_session = db.query(BotSession).filter(
        BotSession.status == "running"
    ).first()
    
    if not current_session:
        raise HTTPException(status_code=400, detail="No active bot session found")
    
    # Immediately update session status to stopped
    current_session.status = "stopped"
    current_session.end_time = datetime.now(timezone.utc)
    db.commit()
    
    # Send real-time update about bot stopping
    await send_realtime_update("bot_stopping", {
        "status": "stopping",
        "message": "Bot is being stopped...",
        "session_id": str(current_session.id)
    })
    
    # Terminate ALL bot processes immediately
    terminated_processes = []
    
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if any(keyword in cmdline.lower() for keyword in ['smart_bot', 'integrated_bot', 'test_bot', 'atoz_bot']):
                    if proc.is_running():
                        try:
                            # First try graceful termination
                            proc.terminate()
                            terminated_processes.append(f"Terminated {proc.pid}")
                            
                            # Wait a moment for graceful shutdown
                            try:
                                proc.wait(timeout=2)
                            except psutil.TimeoutExpired:
                                # Force kill if it doesn't stop gracefully
                                proc.kill()
                                terminated_processes.append(f"Force killed {proc.pid}")
                                
                        except Exception as e:
                            try:
                                # Force kill as last resort
                                proc.kill()
                                terminated_processes.append(f"Force killed {proc.pid} (after error: {e})")
                            except Exception as kill_error:
                                terminated_processes.append(f"Failed to kill {proc.pid}: {kill_error}")
                                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        print(f"Error checking bot processes: {e}")
    
    # Also terminate global bot_process if it exists
    if bot_process:
        try:
            if os.name == 'nt':  # Windows
                bot_process.terminate()
            else:  # Unix-like
                try:
                    os.killpg(os.getpgid(bot_process.pid), signal.SIGTERM)
                    # Wait for graceful shutdown
                    try:
                        bot_process.wait(timeout=2)
                    except subprocess.TimeoutExpired:
                        # Force kill if it doesn't stop gracefully
                        os.killpg(os.getpgid(bot_process.pid), signal.SIGKILL)
                except Exception as e:
                    print(f"Error terminating global bot process: {e}")
        except Exception as e:
            print(f"Error with global bot process: {e}")
        finally:
            bot_process = None
    
    # Add system log
    log_entry = SystemLog(
        session_id=current_session.id,
        log_level="INFO",
        message=f"Bot stopped by user. Terminated processes: {', '.join(terminated_processes)}",
        component="api"
    )
    db.add(log_entry)
    db.commit()
    
    # Send final real-time update
    await send_realtime_update("bot_stopped", {
        "status": "stopped",
        "message": "Bot has been stopped successfully",
        "session_id": str(current_session.id),
        "terminated_processes": terminated_processes
    })
    
    return {
        "message": "Bot stopped successfully", 
        "status": "stopped",
        "terminated_processes": terminated_processes
    }

@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status(db: Session = Depends(get_db)):
    """Get current bot status using proper state management"""
    print(f"\n📊 STATUS REQUEST:")
    print(f"   Bot state: {bot_state.is_running()}")
    
    is_running = bot_state.is_running()
    
    # If bot is not running, return basic status immediately
    if not is_running:
        return BotStatusResponse(
            is_running=False,
            session_id=None,
            session_name="No active session",
            start_time=None,
            status="stopped",
            login_status="not_started",
            total_checks=0,
            total_accepted=0,
            total_rejected=0
        )
    
    # Get current session only if bot is running
    current_session = db.query(BotSession).filter(
        BotSession.status == "running"
    ).first()
    
    if current_session:
        return BotStatusResponse(
            is_running=is_running,
            session_id=str(current_session.id),
            session_name=current_session.session_name,
            start_time=current_session.start_time,
            status=current_session.status,
            login_status=current_session.login_status,
            total_checks=current_session.total_checks,
            total_accepted=current_session.total_accepted,
            total_rejected=current_session.total_rejected
        )
    
    # If no running session, return basic status
    return BotStatusResponse(
        is_running=is_running,
        session_id=None,
        session_name="Starting...",
        start_time=None,
        status="starting",
        login_status="attempting",
        total_checks=0,
        total_accepted=0,
        total_rejected=0
    )

@router.get("/sessions", response_model=List[BotSessionResponse])
async def get_bot_sessions(
    limit: int = 10,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get bot session history"""
    sessions = db.query(BotSession).order_by(
        BotSession.created_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [BotSessionResponse.from_orm(session) for session in sessions]

@router.get("/jobs", response_model=List[JobRecordResponse])
async def get_job_records(
    session_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get job records"""
    query = db.query(JobRecord)
    
    if session_id:
        query = query.filter(JobRecord.session_id == session_id)
    if status:
        query = query.filter(JobRecord.status == status)
    
    jobs = query.order_by(
        JobRecord.scraped_at.desc()
    ).offset(offset).limit(limit).all()
    
    return [JobRecordResponse.from_orm(job) for job in jobs]

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get analytics data for the specified time period"""
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=hours)
    
    # Get job records in time period
    jobs = db.query(JobRecord).filter(
        JobRecord.scraped_at >= start_time,
        JobRecord.scraped_at <= end_time
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
    
    return AnalyticsResponse(
        period_hours=hours,
        total_jobs_processed=total_jobs,
        jobs_accepted=accepted_jobs,
        jobs_rejected=rejected_jobs,
        acceptance_rate=round(acceptance_rate, 2),
        most_common_language=most_common_language,
        peak_hour=peak_hour,
        language_distribution=language_counts,
        hourly_distribution=hourly_counts
    )

@router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(db: Session = Depends(get_db)):
    """Get dashboard metrics for the frontend"""
    metrics = bot_service.get_dashboard_metrics(db)
    return DashboardMetrics(**metrics)

@router.get("/configuration", response_model=BotConfigurationResponse)
async def get_bot_configuration(db: Session = Depends(get_db)):
    """Get bot configuration"""
    config = db.query(BotConfiguration).filter(BotConfiguration.is_active == True).first()
    if not config:
        # Return default configuration if none exists
        default_config = BotConfiguration(
            config_name="default",
            check_interval_seconds=0.5,
            results_report_interval_seconds=5,
            rejected_report_interval_seconds=43200,
            quick_check_interval_seconds=10,
            enable_quick_check=False,
            enable_results_reporting=True,
            enable_rejected_reporting=True,
            max_accept_per_run=5,
            job_type_filter="Telephone interpreting",
            is_active=True
        )
        db.add(default_config)
        db.commit()
        db.refresh(default_config)
        config = default_config
    
    return BotConfigurationResponse.from_orm(config)

@router.put("/configuration", response_model=BotConfigurationResponse)
async def update_bot_configuration(
    config_data: BotConfigurationResponse,
    db: Session = Depends(get_db)
):
    """Update bot configuration"""
    config = db.query(BotConfiguration).filter(BotConfiguration.is_active == True).first()
    
    if not config:
        config = BotConfiguration(
            config_name=config_data.config_name,
            is_active=True
        )
        db.add(config)
    
    # Update configuration fields
    for field, value in config_data.dict(exclude={'id', 'created_at', 'updated_at'}).items():
        setattr(config, field, value)
    
    db.commit()
    db.refresh(config)
    return BotConfigurationResponse.from_orm(config)

async def monitor_bot_process(session_id: str, db: Session):
    """Background task to monitor bot process"""
    global bot_process
    
    while bot_process and bot_process.poll() is None:
        try:
            # Update session with current metrics
            session = db.query(BotSession).filter(BotSession.id == session_id).first()
            if session:
                # Update login status if not already set
                if session.login_status == "attempting":
                    session.login_status = "success"
                
                db.commit()
                
                # Send status update
                await send_realtime_update("status_change", {
                    "session_id": str(session_id),
                    "bot_status": {
                        "is_running": True,
                        "session_id": str(session.id),
                        "session_name": session.session_name,
                        "status": session.status,
                        "login_status": session.login_status,
                        "total_checks": session.total_checks or 0,
                        "total_accepted": session.total_accepted or 0,
                        "total_rejected": session.total_rejected or 0
                    }
                })
            
            await asyncio.sleep(10)  # Check every 10 seconds
            
        except Exception as e:
            # Log error
            log_entry = SystemLog(
                session_id=session_id,
                log_level="ERROR",
                message=f"Bot monitoring error: {str(e)}",
                component="monitor"
            )
            db.add(log_entry)
            db.commit()
            print(f"Bot monitoring error: {e}")
            break
    
    # Bot process ended
    session = db.query(BotSession).filter(BotSession.id == session_id).first()
    if session and session.status == "running":
        session.status = "stopped"
        session.end_time = datetime.now(timezone.utc)
        db.commit()
        
        # Send final status update
        await send_realtime_update("status_change", {
            "session_id": str(session_id),
            "bot_status": {
                "is_running": False,
                "session_id": str(session.id),
                "session_name": session.session_name,
                "status": session.status,
                "login_status": session.login_status,
                "total_checks": session.total_checks or 0,
                "total_accepted": session.total_accepted or 0,
                "total_rejected": session.total_rejected or 0
            }
        })

async def send_realtime_update(update_type: str, data: dict):
    """Send real-time update to all connected WebSocket clients"""
    try:
        from simple_main import manager
        update_data = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        await manager.broadcast(json.dumps(update_data, cls=CustomJSONEncoder))
    except Exception as e:
        print(f"Error sending real-time update: {e}")
