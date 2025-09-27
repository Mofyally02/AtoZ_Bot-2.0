import { create } from 'zustand';
import { apiService } from '../services/api';
import { AnalyticsData, DashboardMetrics, JobRecord } from '../types';

interface AnalyticsStore {
  // State
  analytics: AnalyticsData | null;
  jobRecords: JobRecord[];
  dashboardMetrics: DashboardMetrics | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setAnalytics: (analytics: AnalyticsData) => void;
  setJobRecords: (records: JobRecord[]) => void;
  setDashboardMetrics: (metrics: DashboardMetrics) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  fetchAnalytics: (hours?: number) => Promise<void>;
  fetchJobRecords: (sessionId?: string, status?: string) => Promise<void>;
  fetchDashboardMetrics: () => Promise<void>;
  refreshAll: () => Promise<void>;
}

export const useAnalyticsStore = create<AnalyticsStore>((set, get) => ({
  // Initial state
  analytics: null,
  jobRecords: [],
  dashboardMetrics: null,
  isLoading: false,
  error: null,
  
  // Actions
  setAnalytics: (analytics) => set({ analytics }),
  
  setJobRecords: (records) => set({ jobRecords: records }),
  
  setDashboardMetrics: (metrics) => set({ dashboardMetrics: metrics }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setError: (error) => set({ error }),
  
  fetchAnalytics: async (hours = 24) => {
    const { setLoading, setError } = get();
    
    try {
      setLoading(true);
      setError(null);
      
      const analytics = await apiService.getAnalytics(hours);
      set({ analytics });
    } catch (error: any) {
      console.error('Failed to fetch analytics:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch analytics';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  },
  
  fetchJobRecords: async (sessionId?: string, status?: string) => {
    const { setLoading, setError } = get();
    
    try {
      setLoading(true);
      setError(null);
      
      const records = await apiService.getJobRecords({ session_id: sessionId, status });
      set({ jobRecords: records });
    } catch (error: any) {
      console.error('Failed to fetch job records:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch job records';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  },
  
  fetchDashboardMetrics: async () => {
    const { setLoading, setError } = get();
    
    try {
      setLoading(true);
      setError(null);
      
      const metrics = await apiService.getDashboardMetrics();
      set({ dashboardMetrics: metrics });
    } catch (error: any) {
      console.error('Failed to fetch dashboard metrics:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to fetch dashboard metrics';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  },
  
  refreshAll: async () => {
    const { fetchAnalytics, fetchJobRecords, fetchDashboardMetrics } = get();
    
    try {
      await Promise.all([
        fetchAnalytics(24),
        fetchJobRecords(),
        fetchDashboardMetrics(),
      ]);
    } catch (error) {
      console.error('Failed to refresh all data:', error);
    }
  },
}));
