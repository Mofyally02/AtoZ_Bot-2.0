import { create } from 'zustand';
import { apiService } from '../services/api';
import { BotSession, BotStatus, Theme } from '../types';

interface BotStore {
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

export const useBotStore = create<BotStore>((set, get) => ({
  // Initial state
  botStatus: null,
  currentSession: null,
  isConnected: false,
  theme: (localStorage.getItem('theme') as Theme) || 'light',
  
  // Actions
  setBotStatus: (status) => set({ botStatus: status }),
  
  setCurrentSession: (session) => set({ currentSession: session }),
  
  setConnected: (connected) => set({ isConnected: connected }),
  
  toggleTheme: () => {
    const newTheme = get().theme === 'light' ? 'dark' : 'light';
    set({ theme: newTheme });
    localStorage.setItem('theme', newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  },
  
  startBot: async (sessionName?: string) => {
    try {
      const response = await apiService.startBot({ session_name: sessionName });
      set({ currentSession: response });
      await get().refreshStatus();
    } catch (error) {
      console.error('Failed to start bot:', error);
      throw error;
    }
  },
  
  stopBot: async () => {
    try {
      await apiService.stopBot();
      set({ currentSession: null });
      await get().refreshStatus();
    } catch (error) {
      console.error('Failed to stop bot:', error);
      throw error;
    }
  },
  
  refreshStatus: async () => {
    try {
      const status = await apiService.getBotStatus();
      set({ botStatus: status });
    } catch (error) {
      console.error('Failed to refresh bot status:', error);
      set({ isConnected: false });
    }
  },
}));
