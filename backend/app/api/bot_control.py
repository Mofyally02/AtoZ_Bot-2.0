"""
Bot control API endpoints
"""
import asyncio
import os
import signal
import subprocess
from datetime import datetime, timedelta
from typing import List, Optional

import psutil
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.models.bot_models import (BotConfiguration, BotSession,
                                           JobRecord, SystemLog)
from backend.app.schemas.bot_schemas import (AnalyticsResponse,
                                             BotControlRequest,
                                             BotSessionCreate,
                                             BotSessionResponse,
                                             BotStatusResponse,
                                             JobRecordResponse)
from backend.app.services.bot_service import BotService

router = APIRouter(prefix="/api/bot", tags=["bot-control"])

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
            ["python", "persistent_bot.py"],
            cwd=os.path.join(os.path.dirname(__file__), "../../.."),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid if os.name != 'nt' else None
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
        
        return BotSessionResponse.from_orm(session)
        
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
    
    is_running = bot_process and bot_process.poll() is None
    
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

async def monitor_bot_process(session_id: str, db: Session):
    """Background task to monitor bot process"""
    global bot_process
    
    while bot_process and bot_process.poll() is None:
        try:
            # Update session with current metrics
            session = db.query(BotSession).filter(BotSession.id == session_id).first()
            if session:
                # Read bot output and update metrics
                # This would integrate with the existing results_tracker
                pass
            
            await asyncio.sleep(5)  # Check every 5 seconds
            
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
            break
    
    # Bot process ended
    session = db.query(BotSession).filter(BotSession.id == session_id).first()
    if session and session.status == "running":
        session.status = "stopped"
        session.end_time = datetime.utcnow()
        db.commit()
