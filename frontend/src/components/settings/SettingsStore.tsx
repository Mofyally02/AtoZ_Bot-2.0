import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { apiService } from '../../services/api';
import toast from 'react-hot-toast';

// Types
interface SettingsState {
  configurations: any[];
  activeConfiguration: any | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

type SettingsAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_CONFIGURATIONS'; payload: any[] }
  | { type: 'SET_ACTIVE_CONFIG'; payload: any }
  | { type: 'UPDATE_CONFIG'; payload: any }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_LAST_UPDATED'; payload: Date };

interface SettingsContextType {
  state: SettingsState;
  actions: {
    loadConfigurations: () => Promise<void>;
    loadActiveConfiguration: () => Promise<void>;
    updateConfiguration: (config: any) => Promise<void>;
    createConfiguration: (config: any) => Promise<void>;
    deleteConfiguration: (id: string) => Promise<void>;
    setActiveConfiguration: (id: string) => Promise<void>;
    refreshSettings: () => Promise<void>;
  };
}

// Initial state
const initialState: SettingsState = {
  configurations: [],
  activeConfiguration: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

// Reducer
const settingsReducer = (state: SettingsState, action: SettingsAction): SettingsState => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    case 'SET_CONFIGURATIONS':
      return { ...state, configurations: action.payload };
    case 'SET_ACTIVE_CONFIG':
      return { ...state, activeConfiguration: action.payload };
    case 'UPDATE_CONFIG':
      return {
        ...state,
        activeConfiguration: action.payload,
        configurations: state.configurations.map(config =>
          config.id === action.payload.id ? action.payload : config
        ),
        lastUpdated: new Date(),
      };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    case 'SET_LAST_UPDATED':
      return { ...state, lastUpdated: action.payload };
    default:
      return state;
  }
};

// Context
const SettingsContext = createContext<SettingsContextType | undefined>(undefined);

// Provider
export const SettingsProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(settingsReducer, initialState);

  const loadConfigurations = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      // This would be a new endpoint to get all configurations
      // For now, we'll just load the active one
      const config = await apiService.getBotConfiguration();
      dispatch({ type: 'SET_ACTIVE_CONFIG', payload: config });
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load configurations';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const loadActiveConfiguration = async () => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const config = await apiService.getBotConfiguration();
      dispatch({ type: 'SET_ACTIVE_CONFIG', payload: config });
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load configuration';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const updateConfiguration = async (config: any) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      const updatedConfig = await apiService.updateBotConfiguration(config);
      dispatch({ type: 'UPDATE_CONFIG', payload: updatedConfig });
      dispatch({ type: 'SET_ERROR', payload: null });
      
      // Signal bot to refresh its configuration
      try {
        await apiService.refreshBotConfiguration();
      } catch (refreshError) {
        console.warn('Failed to signal bot configuration refresh:', refreshError);
        // Don't fail the whole operation if refresh signal fails
      }
      
      toast.success('Configuration updated successfully');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to update configuration';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const createConfiguration = async (config: any) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      // This would be a new endpoint to create configurations
      // For now, we'll use the update endpoint
      const newConfig = await apiService.updateBotConfiguration(config);
      dispatch({ type: 'UPDATE_CONFIG', payload: newConfig });
      dispatch({ type: 'SET_ERROR', payload: null });
      toast.success('Configuration created successfully');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create configuration';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
      throw error;
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const deleteConfiguration = async (_id: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      // This would be a new endpoint to delete configurations
      // For now, we'll just show a message
      toast.error('Configuration deletion not yet implemented');
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to delete configuration';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const setActiveConfiguration = async (_id: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    try {
      // This would be a new endpoint to set active configuration
      // For now, we'll just show a message
      toast.error('Configuration switching not yet implemented');
      dispatch({ type: 'SET_ERROR', payload: null });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to set active configuration';
      dispatch({ type: 'SET_ERROR', payload: errorMessage });
      toast.error(errorMessage);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const refreshSettings = async () => {
    await loadActiveConfiguration();
  };

  const actions = {
    loadConfigurations,
    loadActiveConfiguration,
    updateConfiguration,
    createConfiguration,
    deleteConfiguration,
    setActiveConfiguration,
    refreshSettings,
  };

  // Load initial configuration
  useEffect(() => {
    loadActiveConfiguration();
  }, []);

  return (
    <SettingsContext.Provider value={{ state, actions }}>
      {children}
    </SettingsContext.Provider>
  );
};

// Hook
export const useSettings = () => {
  const context = useContext(SettingsContext);
  if (context === undefined) {
    throw new Error('useSettings must be used within a SettingsProvider');
  }
  return context;
};
