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
  startupStatus: string | null;
  startupMessage: string | null;
  statusPollingInterval: number | null;
  
  // Actions
  setBotStatus: (status: BotStatus) => void;
  setCurrentSession: (session: BotSession | null) => void;
  setConnected: (connected: boolean) => void;
  setWebSocketConnected: (connected: boolean) => void;
  setError: (error: string | null) => void;
  setLoading: (loading: boolean) => void;
  setStartupStatus: (status: string | null, message?: string | null) => void;
  toggleTheme: () => void;
  startBot: (sessionName?: string) => Promise<void>;
  stopBot: () => Promise<void>;
  refreshStatus: () => Promise<void>;
  connectWebSocket: () => Promise<void>;
  disconnectWebSocket: () => void;
  handleRealtimeUpdate: (update: RealtimeUpdate) => void;
  startStatusPolling: () => void;
  stopStatusPolling: () => void;
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
  startupStatus: null,
  startupMessage: null,
  statusPollingInterval: null,
  
  // Actions
  setBotStatus: (status) => set({ botStatus: status }),
  
  setCurrentSession: (session) => set({ currentSession: session }),
  
  setConnected: (connected) => set({ isConnected: connected }),
  
  setWebSocketConnected: (connected) => set({ isWebSocketConnected: connected }),
  
  setError: (error) => set({ error }),
  
  setLoading: (loading) => set({ isLoading: loading }),
  
  setStartupStatus: (status, message) => set({ 
    startupStatus: status, 
    startupMessage: message || null 
  }),
  
  toggleTheme: () => {
    const newTheme = get().theme === 'light' ? 'dark' : 'light';
    set({ theme: newTheme });
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  },
  
  startBot: async () => {
    const { setLoading, setError, setStartupStatus, refreshStatus } = get();
    
    try {
      setLoading(true);
      setError(null);
      setStartupStatus('starting_bot', 'Starting bot...');
      
      const response = await apiService.startBot();
      
      // Backend returns the session object directly, not wrapped in success/message
      if (response.status === 'running' || response.status === 'starting') {
        setStartupStatus('bot_running', 'Bot started successfully');
        
        // Use the response directly as it matches BotSession interface
        const session = {
          id: response.id || 'unknown',
          session_name: response.session_name || 'Bot Session',
          start_time: response.start_time || new Date().toISOString(),
          status: response.status as 'running' | 'stopped' | 'error' | 'starting',
          login_status: response.login_status as 'pending' | 'success' | 'failed' | 'not_started',
          total_checks: response.total_checks || 0,
          total_accepted: response.total_accepted || 0,
          total_rejected: response.total_rejected || 0,
          created_at: response.created_at || new Date().toISOString()
        };
        
        set({ currentSession: session });
        await refreshStatus();
        
        // Start status polling for real-time updates
        get().startStatusPolling();
        
      } else {
        setError('Failed to start bot - unexpected status: ' + response.status);
        setStartupStatus('error', 'Failed to start bot - unexpected status: ' + response.status);
      }
      
    } catch (error: any) {
      console.error('Failed to start bot:', error);
      setError(error.message || 'Failed to start bot');
      setStartupStatus('error', error.message || 'Failed to start bot');
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
      
      const response = await apiService.stopBot();
      
      if (response.success && response.status === 'stopped') {
        set({ currentSession: null });
        disconnectWebSocket();
        
        // Stop status polling
        get().stopStatusPolling();
        
        await refreshStatus();
      } else {
        setError(response.message || 'Failed to stop bot');
      }
      
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
      const status = await apiService.getLiveBotStatus();
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
      
      // Subscribe to smart bot updates
      wsService.subscribe('starting', (data) => {
        get().handleRealtimeUpdate({ type: 'starting', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('login_attempting', (data) => {
        get().handleRealtimeUpdate({ type: 'login_attempting', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('running', (data) => {
        get().handleRealtimeUpdate({ type: 'running', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('cycle_complete', (data) => {
        get().handleRealtimeUpdate({ type: 'cycle_complete', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('database_update', (data) => {
        get().handleRealtimeUpdate({ type: 'database_update', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('stopped', (data) => {
        get().handleRealtimeUpdate({ type: 'stopped', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('error', (data) => {
        get().handleRealtimeUpdate({ type: 'error', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('bot_stopping', (data) => {
        get().handleRealtimeUpdate({ type: 'bot_stopping', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('bot_stopped', (data) => {
        get().handleRealtimeUpdate({ type: 'bot_stopped', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('job_accepted', (data) => {
        get().handleRealtimeUpdate({ type: 'job_accepted', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('job_rejected', (data) => {
        get().handleRealtimeUpdate({ type: 'job_rejected', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('checking_jobs', (data) => {
        get().handleRealtimeUpdate({ type: 'checking_jobs', data, timestamp: new Date().toISOString() });
      });
      
      wsService.subscribe('job_processing_complete', (data) => {
        get().handleRealtimeUpdate({ type: 'job_processing_complete', data, timestamp: new Date().toISOString() });
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
    const { botStatus, setBotStatus, setStartupStatus } = get();
    
    switch (update.type) {
      case 'connection_check':
        if (update.data.status === 'success') {
          setStartupStatus('connections_verified', update.data.message);
        } else {
          setStartupStatus('connection_error', update.data.message);
        }
        break;
        
      case 'bot_starting':
        setStartupStatus('starting_bot', update.data.message);
        break;
        
      case 'bot_started':
        setStartupStatus('bot_running', update.data.message);
        break;
        
      case 'bot_error':
        setStartupStatus('error', update.data.message);
        break;
        
      case 'login_attempt':
        setStartupStatus('logging_in', 'Attempting to log in...');
        break;
        
      case 'login_success':
        setStartupStatus('logged_in', 'Successfully logged in! Bot is now running...');
        break;
        
      case 'login_failed':
        setStartupStatus('login_error', 'Login failed. Please check credentials.');
        break;
        
      case 'starting':
        setStartupStatus('starting_bot', update.data.message || 'Bot is starting...');
        break;
        
      case 'login_attempting':
        setStartupStatus('logging_in', 'Attempting to log in...');
        break;
        
      case 'running':
        setStartupStatus('logged_in', 'Successfully logged in! Bot is now running...');
        break;
        
      case 'cycle_complete':
        if (update.data.stats) {
          setBotStatus({
            is_running: true,
            session_id: get().currentSession?.id || null,
            session_name: get().currentSession?.session_name || null,
            start_time: get().currentSession?.start_time || null,
            status: 'running',
            login_status: 'success',
            total_checks: update.data.stats.total_checks || 0,
            total_accepted: update.data.stats.total_accepted || 0,
            total_rejected: update.data.stats.total_rejected || 0
          });
        }
        break;
        
      case 'database_update':
        if (update.data.session_id) {
          setBotStatus({
            is_running: true,
            session_id: update.data.session_id,
            session_name: get().currentSession?.session_name || null,
            start_time: get().currentSession?.start_time || null,
            status: update.data.status || 'running',
            login_status: update.data.login_status || 'success',
            total_checks: update.data.total_checks || 0,
            total_accepted: update.data.total_accepted || 0,
            total_rejected: update.data.total_rejected || 0
          });
        }
        break;
        
      case 'bot_stopping':
        setStartupStatus('stopping', 'Bot is being stopped...');
        break;
        
      case 'bot_stopped':
        setStartupStatus('stopped', 'Bot has been stopped successfully');
        // Clear the bot status when stopped
        setBotStatus({
          is_running: false,
          session_id: null,
          session_name: null,
          start_time: null,
          status: 'stopped',
          login_status: 'not_started',
          total_checks: 0,
          total_accepted: 0,
          total_rejected: 0
        });
        break;
        
      case 'stopped':
        setStartupStatus('stopped', 'Bot has been stopped');
        break;
        
      case 'error':
        setStartupStatus('error', update.data.error || 'An error occurred');
        break;
        
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
        // Log individual job decisions
        if (update.type === 'job_accepted') {
          console.log(`✅ Job Accepted: ${update.data.language} - ${update.data.message}`);
        } else {
          console.log(`❌ Job Rejected: ${update.data.language} - ${update.data.reason}`);
        }
        break;
        
      case 'checking_jobs':
        setStartupStatus('checking_jobs', update.data.message);
        console.log(`🔍 ${update.data.message}`);
        break;
        
      case 'job_processing_complete':
        if (update.data.total_checks !== undefined && botStatus) {
          setBotStatus({
            ...botStatus,
            total_checks: update.data.total_checks,
            total_accepted: update.data.total_accepted || 0,
            total_rejected: update.data.total_rejected || 0,
            is_running: botStatus.is_running,
            status: botStatus.status || 'running', // Ensure status is properly typed
          });
        }
        console.log(`📊 Job Processing Complete: ${update.data.message}`);
        break;
        
      default:
        console.log('Unhandled real-time update:', update);
    }
  },

  startStatusPolling: () => {
    const { stopStatusPolling, refreshStatus } = get();
    
    // Stop any existing polling
    stopStatusPolling();
    
    // Start new polling every 5 minutes
    const interval = setInterval(async () => {
      try {
        await refreshStatus();
      } catch (error) {
        console.error('Error polling status:', error);
      }
    }, 300000); // 5 minutes = 300,000 milliseconds
    
    set({ statusPollingInterval: interval });
    console.log('🔄 Started status polling (every 5 minutes)');
  },

  stopStatusPolling: () => {
    const { statusPollingInterval } = get();
    
    if (statusPollingInterval) {
      clearInterval(statusPollingInterval);
      set({ statusPollingInterval: null });
      console.log('⏹️ Stopped status polling');
    }
  },
}));
