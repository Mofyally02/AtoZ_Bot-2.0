"""
Bot control API endpoints
"""
import asyncio
import json
import os
import signal
import subprocess
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

import psutil
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

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
bot_service = BotService()

@router.post("/start", response_model=BotSessionResponse)
async def start_bot(
    request: BotControlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Start the AtoZ bot"""
    global bot_process
    
    # Check if bot is already running
    if bot_process and bot_process.poll() is None:
        raise HTTPException(status_code=400, detail="Bot is already running")
    
    try:
        # Create new bot session
        session = BotSession(
            session_name=request.session_name or f"Session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            status="starting"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
        # Start bot process
        bot_process = subprocess.Popen(
            ["python", "smart_bot.py", str(session.id)],
            cwd=os.path.join(os.path.dirname(__file__), "../../../bot"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != 'nt' else None,
            start_new_session=True
        )
        
        # Update session status
        session.status = "running"
        session.login_status = "attempting"
        db.commit()
        
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

@router.post("/stop", response_model=dict)
async def stop_bot(db: Session = Depends(get_db)):
    """Stop the AtoZ bot"""
    global bot_process
    
    if not bot_process or bot_process.poll() is not None:
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    try:
        # Get current running session
        current_session = db.query(BotSession).filter(
            BotSession.status == "running"
        ).first()
        
        if current_session:
            # Update session
            current_session.status = "stopped"
            current_session.end_time = datetime.utcnow()
            db.commit()
            
            # Add system log
            log_entry = SystemLog(
                session_id=current_session.id,
                log_level="INFO",
                message="Bot stopped by user",
                component="api"
            )
            db.add(log_entry)
            db.commit()
        
        # Terminate bot process
        if os.name == 'nt':  # Windows
            bot_process.terminate()
        else:  # Unix-like
            os.killpg(os.getpgid(bot_process.pid), signal.SIGTERM)
        
        bot_process = None
        
        return {"message": "Bot stopped successfully", "status": "stopped"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop bot: {str(e)}")

@router.get("/status", response_model=BotStatusResponse)
async def get_bot_status(db: Session = Depends(get_db)):
    """Get current bot status"""
    global bot_process
    
    # Check if bot process is running
    is_running = False
    if bot_process:
        try:
            # Check if process is still running
            poll_result = bot_process.poll()
            is_running = poll_result is None
        except:
            is_running = False
    
    # Get current session
    current_session = db.query(BotSession).filter(
        BotSession.status == "running"
    ).first()
    
    if current_session:
        return BotStatusResponse(
            is_running=is_running,
            session_id=str(current_session.id),
            session_name=current_session.session_name,
            start_time=current_session.start_time,
            login_status=current_session.login_status,
            total_checks=current_session.total_checks,
            total_accepted=current_session.total_accepted,
            total_rejected=current_session.total_rejected
        )
    
    return BotStatusResponse(
        is_running=is_running,
        session_id=None,
        session_name=None,
        start_time=None,
        login_status="not_started",
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
    end_time = datetime.utcnow()
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
        session.end_time = datetime.utcnow()
        db.commit()
        
        # Send final status update
        await send_realtime_update("status_change", {
            "session_id": str(session_id),
            "bot_status": {
                "is_running": False,
                "session_id": str(session.id),
                "session_name": session.session_name,
                "login_status": session.login_status,
                "total_checks": session.total_checks or 0,
                "total_accepted": session.total_accepted or 0,
                "total_rejected": session.total_rejected or 0
            }
        })

async def send_realtime_update(update_type: str, data: dict):
    """Send real-time update to all connected WebSocket clients"""
    try:
        from main import manager
        update_data = {
            "type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        await manager.broadcast(json.dumps(update_data, cls=CustomJSONEncoder))
    except Exception as e:
        print(f"Error sending real-time update: {e}")
