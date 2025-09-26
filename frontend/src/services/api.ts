import axios from 'axios';
import { AnalyticsData, BotSession, BotStatus, DashboardMetrics, JobRecord } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const apiService = {
  // Bot Control
  async startBot(data: { session_name?: string }): Promise<BotSession> {
    const response = await apiClient.post('/api/bot/start', data);
    return response.data;
  },

  async stopBot(): Promise<{ message: string; status: string }> {
    const response = await apiClient.post('/api/bot/stop');
    return response.data;
  },

  async getBotStatus(): Promise<BotStatus> {
    const response = await apiClient.get('/api/bot/status');
    return response.data;
  },

  async getBotSessions(limit = 10, offset = 0): Promise<BotSession[]> {
    const response = await apiClient.get('/api/bot/sessions', {
      params: { limit, offset }
    });
    return response.data;
  },

  // Job Records
  async getJobRecords(params?: {
    session_id?: string;
    status?: string;
    limit?: number;
    offset?: number;
  }): Promise<JobRecord[]> {
    const response = await apiClient.get('/api/bot/jobs', { params });
    return response.data;
  },

  // Analytics
  async getAnalytics(hours = 24): Promise<AnalyticsData> {
    const response = await apiClient.get('/api/bot/analytics', {
      params: { hours }
    });
    return response.data;
  },

  // Dashboard Metrics
  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await apiClient.get('/api/dashboard/metrics');
    return response.data;
  },

  // Health Check
  async healthCheck(): Promise<{ status: string; timestamp: string; version: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  },
};

export default apiService;
