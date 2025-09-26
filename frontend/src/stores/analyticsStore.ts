import { create } from 'zustand';
import { apiService } from '../services/api';
import { AnalyticsData, DashboardMetrics, JobRecord } from '../types';

interface AnalyticsStore {
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

export const useAnalyticsStore = create<AnalyticsStore>((set, get) => ({
  // Initial state
  analytics: null,
  jobRecords: [],
  dashboardMetrics: null,
  
  // Actions
  setAnalytics: (analytics) => set({ analytics }),
  
  setJobRecords: (records) => set({ jobRecords: records }),
  
  setDashboardMetrics: (metrics) => set({ dashboardMetrics: metrics }),
  
  fetchAnalytics: async (hours = 24) => {
    try {
      const analytics = await apiService.getAnalytics(hours);
      set({ analytics });
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  },
  
  fetchJobRecords: async (sessionId?: string, status?: string) => {
    try {
      const records = await apiService.getJobRecords({ sessionId, status });
      set({ jobRecords: records });
    } catch (error) {
      console.error('Failed to fetch job records:', error);
    }
  },
  
  fetchDashboardMetrics: async () => {
    try {
      const metrics = await apiService.getDashboardMetrics();
      set({ dashboardMetrics: metrics });
    } catch (error) {
      console.error('Failed to fetch dashboard metrics:', error);
    }
  },
}));
