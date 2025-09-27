import { create } from 'zustand';
import { apiService } from '../services/api';
import { wsService } from '../services/websocket';
import { BotSession, BotStatus, Theme, RealtimeUpdate } from '../types';

interface BotStore {
  // State
  botStatus: BotStatus | null;
  currentSession: BotSession | null;
  isConnected: boolean;
  isWebSocketConnected: boolean;
  theme: Theme;
  error: string | null;
  isLoading: boolean;
  
  // Actions
  setBotStatus: (status: BotStatus) => void;
  setCurrentSession: (session: BotSession | null) => void;
  setConnected: (connected: boolean) => void;
  setWebSocketConnected: (connected: boolean) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  toggleTheme: () => void;
  startBot: (sessionName?: string) => Promise<void>;
  stopBot: () => Promise<void>;
  refreshStatus: () => Promise<void>;
  connectWebSocket: () => Promise<void>;
  disconnectWebSocket: () => void;
  handleRealtimeUpdate: (update: RealtimeUpdate) => void;
}

export const useBotStore = create<BotStore>((set, get) => ({
  // Initial state
  botStatus: null,
  currentSession: null,
  isConnected: false,
  isWebSocketConnected: false,
  theme: (localStorage.getItem('theme') as Theme) || 'light',
  error: null,
  isLoading: false,
  
  // Actions
  setBotStatus: (status) => set({ botStatus: status }),
  
  setCurrentSession: (session) => set({ currentSession: session }),
  
  setConnected: (connected) => set({ isConnected: connected }),
  
  setWebSocketConnected: (connected) => set({ isWebSocketConnected: connected }),
  
  setError: (error) => set({ error }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  toggleTheme: () => {
    const newTheme = get().theme === 'light' ? 'dark' : 'light';
    set({ theme: newTheme });
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  },
  
  startBot: async (sessionName?: string) => {
    const { setLoading, setError, refreshStatus } = get();
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiService.startBot({ session_name: sessionName });
      set({ currentSession: response });
      
      // Refresh status to get updated bot information
      await refreshStatus();
      
      // Connect to WebSocket for real-time updates
      await get().connectWebSocket();
      
    } catch (error: any) {
      console.error('Failed to start bot:', error);
      setError(error.message || 'Failed to start bot');
      throw error;
    } finally {
      setLoading(false);
    }
  },
  
  stopBot: async () => {
    const { setLoading, setError, refreshStatus, disconnectWebSocket } = get();
    
    try {
      setLoading(true);
      setError(null);
      
      await apiService.stopBot();
      set({ currentSession: null });
      
      // Disconnect WebSocket
      disconnectWebSocket();
      
      // Refresh status to get updated bot information
      await refreshStatus();
      
    } catch (error: any) {
      console.error('Failed to stop bot:', error);
      setError(error.message || 'Failed to stop bot');
      throw error;
    } finally {
      setLoading(false);
    }
  },
  
  refreshStatus: async () => {
    const { setError, setConnected } = get();
    
    try {
      const status = await apiService.getBotStatus();
      set({ botStatus: status });
      setConnected(true);
      setError(null); // Clear any previous errors
    } catch (error: any) {
      console.error('Failed to refresh bot status:', error);
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to refresh bot status';
      setError(errorMessage);
      setConnected(false);
    }
  },
  
  connectWebSocket: async () => {
    const { setWebSocketConnected, setError } = get();
    
    try {
      await wsService.connect();
      setWebSocketConnected(true);
      setError(null);
      
      // Subscribe to real-time updates
      wsService.subscribe('status_update', (data) => {
        get().handleRealtimeUpdate({ type: 'status_update', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('status_change', (data) => {
        get().handleRealtimeUpdate({ type: 'status_change', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('metric_update', (data) => {
        get().handleRealtimeUpdate({ type: 'metric_update', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('job_accepted', (data) => {
        get().handleRealtimeUpdate({ type: 'job_accepted', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('job_rejected', (data) => {
        get().handleRealtimeUpdate({ type: 'job_rejected', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('analytics_update', (data) => {
        get().handleRealtimeUpdate({ type: 'analytics_update', data, timestamp: new Date().toISOString() });
      });
      
    } catch (error: any) {
      console.error('Failed to connect WebSocket:', error);
      setError('Real-time updates unavailable - using periodic refresh');
      setWebSocketConnected(false);
    }
  },
  
  disconnectWebSocket: () => {
    wsService.disconnect();
    set({ isWebSocketConnected: false });
  },
  
  handleRealtimeUpdate: (update: RealtimeUpdate) => {
    const { botStatus, setBotStatus } = get();
    
    switch (update.type) {
      case 'status_update':
        if (update.data.bot_status) {
          setBotStatus(update.data.bot_status);
        }
        break;
        
      case 'status_change':
        if (update.data.bot_status) {
          setBotStatus(update.data.bot_status);
        }
        break;
        
      case 'metric_update':
        if (update.data.bot_status) {
          setBotStatus(update.data.bot_status);
        }
        break;
        
      case 'job_accepted':
      case 'job_rejected':
        if (botStatus && update.data.counts) {
          setBotStatus({
            ...botStatus,
            total_checks: update.data.counts.total_checks || botStatus.total_checks,
            total_accepted: update.data.counts.total_accepted || botStatus.total_accepted,
            total_rejected: update.data.counts.total_rejected || botStatus.total_rejected,
          });
        }
        break;
        
      default:
        console.log('Unhandled real-time update:', update);
    }
  },
}));
