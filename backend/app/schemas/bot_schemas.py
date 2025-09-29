"""
Pydantic schemas for API requests and responses
"""
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


# Request Schemas
class BotControlRequest(BaseModel):
    session_name: Optional[str] = None
    config_id: Optional[str] = None

class BotSessionCreate(BaseModel):
    session_name: str
    config_id: Optional[str] = None

class JobRecordCreate(BaseModel):
    job_ref: str
    language: str
    appointment_date: datetime
    appointment_time: datetime
    duration: str
    submitted_at: datetime
    status: str
    job_type: Optional[str] = None
    rejection_reason: Optional[str] = None

# Response Schemas
class BotSessionResponse(BaseModel):
    id: str
    session_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str
    login_status: str
    total_checks: int
    total_accepted: int
    total_rejected: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class JobRecordResponse(BaseModel):
    id: str
    session_id: str
    job_ref: str
    language: str
    appointment_date: datetime
    appointment_time: datetime
    duration: str
    submitted_at: datetime
    status: str
    job_type: Optional[str] = None
    rejection_reason: Optional[str] = None
    scraped_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class AnalyticsResponse(BaseModel):
    period_hours: int
    total_jobs_processed: int
    jobs_accepted: int
    jobs_rejected: int
    acceptance_rate: float
    most_common_language: Optional[str] = None
    peak_hour: Optional[int] = None
    language_distribution: Dict[str, int] = {}
    hourly_distribution: Dict[int, int] = {}

class BotStatusResponse(BaseModel):
    is_running: bool
    session_id: Optional[str] = None
    session_name: Optional[str] = None
    start_time: Optional[datetime] = None
    status: str
    login_status: str
    total_checks: int
    total_accepted: int
    total_rejected: int

class BotConfigurationResponse(BaseModel):
    id: str
    config_name: str
    check_interval_seconds: Decimal
    results_report_interval_seconds: int
    rejected_report_interval_seconds: int
    quick_check_interval_seconds: int
    enable_quick_check: bool
    enable_results_reporting: bool
    enable_rejected_reporting: bool
    max_accept_per_run: int
    job_type_filter: str
    exclude_types: Optional[List[str]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SystemLogResponse(BaseModel):
    id: str
    session_id: str
    log_level: str
    message: str
    component: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard specific schemas
class DashboardMetrics(BaseModel):
    active_sessions: int
    total_jobs_today: int
    acceptance_rate_today: float
    most_active_language: Optional[str] = None
    bot_uptime_hours: float
    last_activity: Optional[datetime] = None

class RealtimeUpdate(BaseModel):
    type: str  # "job_accepted", "job_rejected", "status_change", "metric_update"
    data: Dict[str, Any]
    timestamp: datetime

# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
