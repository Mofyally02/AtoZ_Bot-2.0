-- AtoZ Bot Dashboard Database Schema
-- PostgreSQL Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Bot Sessions Table
CREATE TABLE bot_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_name VARCHAR(255) NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_time TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL DEFAULT 'running', -- running, stopped, error
    login_status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, success, failed
    total_checks INTEGER DEFAULT 0,
    total_accepted INTEGER DEFAULT 0,
    total_rejected INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Job Records Table (Scraped from AtoZ)
CREATE TABLE job_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES bot_sessions(id) ON DELETE CASCADE,
    job_ref VARCHAR(100) NOT NULL,
    language VARCHAR(100) NOT NULL,
    appointment_date DATE NOT NULL,
    appointment_time TIME NOT NULL,
    duration VARCHAR(50) NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE NOT NULL,
    status VARCHAR(50) NOT NULL, -- matched, accepted, rejected
    job_type VARCHAR(100), -- Telephone interpreting, Face-to-Face, etc.
    rejection_reason TEXT,
    scraped_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Analytics Table (4-hour periods)
CREATE TABLE analytics_periods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    total_jobs_processed INTEGER DEFAULT 0,
    jobs_accepted INTEGER DEFAULT 0,
    jobs_rejected INTEGER DEFAULT 0,
    acceptance_rate DECIMAL(5,2) DEFAULT 0.00,
    most_common_language VARCHAR(100),
    peak_hour INTEGER,
    bot_uptime_seconds INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bot Configuration Table
CREATE TABLE bot_configurations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_name VARCHAR(255) NOT NULL UNIQUE,
    check_interval_seconds DECIMAL(5,2) DEFAULT 0.5,
    results_report_interval_seconds INTEGER DEFAULT 5,
    rejected_report_interval_seconds INTEGER DEFAULT 43200,
    quick_check_interval_seconds INTEGER DEFAULT 10,
    enable_quick_check BOOLEAN DEFAULT false,
    enable_results_reporting BOOLEAN DEFAULT true,
    enable_rejected_reporting BOOLEAN DEFAULT true,
    max_accept_per_run INTEGER DEFAULT 5,
    job_type_filter VARCHAR(100) DEFAULT 'Telephone interpreting',
    exclude_types TEXT[], -- Array of excluded job types
    is_active BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System Logs Table
CREATE TABLE system_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID REFERENCES bot_sessions(id) ON DELETE CASCADE,
    log_level VARCHAR(20) NOT NULL, -- INFO, WARNING, ERROR, DEBUG
    message TEXT NOT NULL,
    component VARCHAR(100), -- bot, api, frontend, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_job_records_session_id ON job_records(session_id);
CREATE INDEX idx_job_records_scraped_at ON job_records(scraped_at);
CREATE INDEX idx_job_records_status ON job_records(status);
CREATE INDEX idx_job_records_language ON job_records(language);
CREATE INDEX idx_analytics_periods_start ON analytics_periods(period_start);
CREATE INDEX idx_analytics_periods_end ON analytics_periods(period_end);
CREATE INDEX idx_bot_sessions_start_time ON bot_sessions(start_time);
CREATE INDEX idx_bot_sessions_status ON bot_sessions(status);
CREATE INDEX idx_system_logs_session_id ON system_logs(session_id);
CREATE INDEX idx_system_logs_created_at ON system_logs(created_at);

-- Function to automatically clean up old data (7 days)
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    -- Delete old analytics periods (keep only 7 days)
    DELETE FROM analytics_periods 
    WHERE period_start < NOW() - INTERVAL '7 days';
    
    -- Delete old system logs (keep only 7 days)
    DELETE FROM system_logs 
    WHERE created_at < NOW() - INTERVAL '7 days';
    
    -- Delete old job records (keep only rejected and failed with reasons)
    DELETE FROM job_records 
    WHERE created_at < NOW() - INTERVAL '7 days'
    AND status NOT IN ('rejected', 'failed');
    
    -- Update bot sessions end_time for old running sessions
    UPDATE bot_sessions 
    SET end_time = NOW(), status = 'stopped'
    WHERE status = 'running' 
    AND start_time < NOW() - INTERVAL '7 days';
END;
$$ LANGUAGE plpgsql;

-- Function to create 4-hour analytics periods
CREATE OR REPLACE FUNCTION create_analytics_period()
RETURNS void AS $$
DECLARE
    period_start TIMESTAMP WITH TIME ZONE;
    period_end TIMESTAMP WITH TIME ZONE;
    total_processed INTEGER;
    total_accepted INTEGER;
    total_rejected INTEGER;
    acceptance_rate DECIMAL(5,2);
    most_common_lang VARCHAR(100);
    peak_hour_val INTEGER;
BEGIN
    -- Calculate period start (last 4 hours)
    period_start := date_trunc('hour', NOW()) - INTERVAL '4 hours';
    period_end := period_start + INTERVAL '4 hours';
    
    -- Check if period already exists
    IF EXISTS (SELECT 1 FROM analytics_periods WHERE period_start = $1) THEN
        RETURN;
    END IF;
    
    -- Calculate metrics for the period
    SELECT 
        COUNT(*),
        COUNT(CASE WHEN status = 'accepted' THEN 1 END),
        COUNT(CASE WHEN status = 'rejected' THEN 1 END)
    INTO total_processed, total_accepted, total_rejected
    FROM job_records 
    WHERE scraped_at >= period_start AND scraped_at < period_end;
    
    -- Calculate acceptance rate
    IF total_processed > 0 THEN
        acceptance_rate := (total_accepted::DECIMAL / total_processed) * 100;
    ELSE
        acceptance_rate := 0;
    END IF;
    
    -- Find most common language
    SELECT language INTO most_common_lang
    FROM job_records 
    WHERE scraped_at >= period_start AND scraped_at < period_end
    GROUP BY language 
    ORDER BY COUNT(*) DESC 
    LIMIT 1;
    
    -- Find peak hour
    SELECT EXTRACT(hour FROM appointment_time)::INTEGER INTO peak_hour_val
    FROM job_records 
    WHERE scraped_at >= period_start AND scraped_at < period_end
    GROUP BY EXTRACT(hour FROM appointment_time)
    ORDER BY COUNT(*) DESC 
    LIMIT 1;
    
    -- Insert analytics period
    INSERT INTO analytics_periods (
        period_start, period_end, total_jobs_processed, 
        jobs_accepted, jobs_rejected, acceptance_rate,
        most_common_language, peak_hour
    ) VALUES (
        period_start, period_end, total_processed,
        total_accepted, total_rejected, acceptance_rate,
        most_common_lang, peak_hour_val
    );
END;
$$ LANGUAGE plpgsql;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
CREATE TRIGGER update_bot_sessions_updated_at 
    BEFORE UPDATE ON bot_sessions 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bot_configurations_updated_at 
    BEFORE UPDATE ON bot_configurations 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default configuration
INSERT INTO bot_configurations (
    config_name, is_active
) VALUES (
    'default', true
);

-- Create a view for dashboard metrics
CREATE VIEW dashboard_metrics AS
SELECT 
    bs.id as session_id,
    bs.session_name,
    bs.start_time,
    bs.end_time,
    bs.status,
    bs.login_status,
    bs.total_checks,
    bs.total_accepted,
    bs.total_rejected,
    CASE 
        WHEN bs.total_checks > 0 THEN (bs.total_accepted::DECIMAL / bs.total_checks) * 100
        ELSE 0 
    END as success_rate,
    COUNT(jr.id) as total_jobs_scraped,
    COUNT(CASE WHEN jr.status = 'accepted' THEN 1 END) as jobs_accepted_count,
    COUNT(CASE WHEN jr.status = 'rejected' THEN 1 END) as jobs_rejected_count,
    bs.created_at
FROM bot_sessions bs
LEFT JOIN job_records jr ON bs.id = jr.session_id
GROUP BY bs.id, bs.session_name, bs.start_time, bs.end_time, 
         bs.status, bs.login_status, bs.total_checks, 
         bs.total_accepted, bs.total_rejected, bs.created_at;
