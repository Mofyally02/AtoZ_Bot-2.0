"""
Database models for AtoZ Bot Dashboard
"""
import uuid

from sqlalchemy import (ARRAY, DECIMAL, UUID, Boolean, Column, DateTime,
                        ForeignKey, Integer, String, Text)
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.connection import Base


class BotSession(Base):
    __tablename__ = "bot_sessions"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_name = Column(String(255), nullable=False)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(50), nullable=False, default="running")
    login_status = Column(String(50), nullable=False, default="pending")
    total_checks = Column(Integer, default=0)
    total_accepted = Column(Integer, default=0)
    total_rejected = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    job_records = relationship("JobRecord", back_populates="session", cascade="all, delete-orphan")
    system_logs = relationship("SystemLog", back_populates="session", cascade="all, delete-orphan")


class JobRecord(Base):
    __tablename__ = "job_records"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PostgresUUID(as_uuid=True), ForeignKey("bot_sessions.id", ondelete="CASCADE"))
    job_ref = Column(String(100), nullable=False)
    language = Column(String(100), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    appointment_time = Column(DateTime, nullable=False)
    duration = Column(String(50), nullable=False)
    submitted_at = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), nullable=False)  # matched, accepted, rejected
    job_type = Column(String(100), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("BotSession", back_populates="job_records")


class AnalyticsPeriod(Base):
    __tablename__ = "analytics_periods"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    period_start = Column(DateTime(timezone=True), nullable=False)
    period_end = Column(DateTime(timezone=True), nullable=False)
    total_jobs_processed = Column(Integer, default=0)
    jobs_accepted = Column(Integer, default=0)
    jobs_rejected = Column(Integer, default=0)
    acceptance_rate = Column(DECIMAL(5, 2), default=0.00)
    most_common_language = Column(String(100), nullable=True)
    peak_hour = Column(Integer, nullable=True)
    bot_uptime_seconds = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BotConfiguration(Base):
    __tablename__ = "bot_configurations"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    config_name = Column(String(255), nullable=False, unique=True)
    check_interval_seconds = Column(DECIMAL(5, 2), default=0.5)
    results_report_interval_seconds = Column(Integer, default=5)
    rejected_report_interval_seconds = Column(Integer, default=43200)
    quick_check_interval_seconds = Column(Integer, default=10)
    enable_quick_check = Column(Boolean, default=False)
    enable_results_reporting = Column(Boolean, default=True)
    enable_rejected_reporting = Column(Boolean, default=True)
    max_accept_per_run = Column(Integer, default=5)
    job_type_filter = Column(String(100), default="Telephone interpreting")
    exclude_types = Column(ARRAY(String), nullable=True)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(PostgresUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PostgresUUID(as_uuid=True), ForeignKey("bot_sessions.id", ondelete="CASCADE"))
    log_level = Column(String(20), nullable=False)  # INFO, WARNING, ERROR, DEBUG
    message = Column(Text, nullable=False)
    component = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    session = relationship("BotSession", back_populates="system_logs")
