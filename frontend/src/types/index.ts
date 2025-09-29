/**
 * TypeScript types for AtoZ Bot Dashboard
 */

export interface BotSession {
  id: string;
  session_name: string;
  start_time: string;
  end_time?: string;
  status: 'running' | 'stopped' | 'error' | 'starting';
  login_status: 'pending' | 'success' | 'failed' | 'not_started';
  total_checks: number;
  total_accepted: number;
  total_rejected: number;
  created_at: string;
  updated_at?: string;
}

export interface JobRecord {
  id: string;
  session_id: string;
  job_ref: string;
  language: string;
  appointment_date: string;
  appointment_time: string;
  duration: string;
  submitted_at: string;
  status: 'matched' | 'accepted' | 'rejected' | 'failed';
  job_type?: string;
  rejection_reason?: string;
  scraped_at: string;
  created_at: string;
}

export interface AnalyticsData {
  period_hours: number;
  total_jobs_processed: number;
  jobs_accepted: number;
  jobs_rejected: number;
  acceptance_rate: number;
  most_common_language?: string;
  peak_hour?: number;
  language_distribution: Record<string, number>;
  hourly_distribution: Record<number, number>;
}

export interface BotStatus {
  is_running: boolean;
  session_id?: string | null;
  session_name?: string | null;
  start_time?: string | null;
  status: 'running' | 'stopped' | 'error' | 'starting';
  login_status: string;
  total_checks: number;
  total_accepted: number;
  total_rejected: number;
}

export interface DashboardMetrics {
  active_sessions: number;
  total_jobs_today: number;
  acceptance_rate_today: number;
  most_active_language?: string;
  bot_uptime_hours: number;
  last_activity?: string;
}

export interface BotConfiguration {
  id: string;
  config_name: string;
  check_interval_seconds: number;
  results_report_interval_seconds: number;
  rejected_report_interval_seconds: number;
  quick_check_interval_seconds: number;
  enable_quick_check: boolean;
  enable_results_reporting: boolean;
  enable_rejected_reporting: boolean;
  max_accept_per_run: number;
  job_type_filter: string;
  exclude_types?: string[];
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface SystemLog {
  id: string;
  session_id: string;
  log_level: 'INFO' | 'WARNING' | 'ERROR' | 'DEBUG';
  message: string;
  component?: string;
  created_at: string;
}

export interface WebSocketMessage {
  type: string;
  data: Record<string, any>;
  timestamp: string;
}

export interface RealtimeUpdate {
  type: 'job_accepted' | 'job_rejected' | 'status_change' | 'status_update' | 'metric_update' | 'analytics_update' | 'connection_check' | 'bot_starting' | 'bot_started' | 'bot_error' | 'login_attempt' | 'login_success' | 'login_failed' | 'starting' | 'login_attempting' | 'login_failed' | 'running' | 'cycle_complete' | 'database_update' | 'stopped' | 'error' | 'bot_stopping' | 'bot_stopped' | 'checking_jobs' | 'job_processing_complete';
  data: Record<string, any>;
  timestamp: string;
}

// UI Component Props
export interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  className?: string;
}

export interface CardProps {
  children: React.ReactNode;
  className?: string;
  variant?: 'default' | 'glass' | 'outline';
}

export interface MetricCardProps {
  title: string;
  value: string | number;
  change?: number;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon?: React.ReactNode;
  className?: string;
}

// API Response Types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

// Chart Data Types
export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

export interface LanguageDistribution {
  language: string;
  count: number;
  percentage: number;
}

export interface HourlyDistribution {
  hour: number;
  count: number;
  percentage: number;
}

// Theme Types
export type Theme = 'light' | 'dark';

export interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

// Store Types
export interface BotStore {
  // State
  botStatus: BotStatus | null;
  currentSession: BotSession | null;
  isConnected: boolean;
  theme: Theme;
  
  // Actions
  setBotStatus: (status: BotStatus) => void;
  setCurrentSession: (session: BotSession | null) => void;
  setConnected: (connected: boolean) => void;
  toggleTheme: () => void;
  startBot: (sessionName?: string) => Promise<void>;
  stopBot: () => Promise<void>;
  refreshStatus: () => Promise<void>;
}

export interface AnalyticsStore {
  // State
  analytics: AnalyticsData | null;
  jobRecords: JobRecord[];
  dashboardMetrics: DashboardMetrics | null;
  
  // Actions
  setAnalytics: (analytics: AnalyticsData) => void;
  setJobRecords: (records: JobRecord[]) => void;
  setDashboardMetrics: (metrics: DashboardMetrics) => void;
  fetchAnalytics: (hours?: number) => Promise<void>;
  fetchJobRecords: (sessionId?: string, status?: string) => Promise<void>;
  fetchDashboardMetrics: () => Promise<void>;
}
