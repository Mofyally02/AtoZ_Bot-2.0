import { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import { SpeedInsights } from '@vercel/speed-insights/react';
import Layout from './components/layout/Layout';
import Analytics from './pages/Analytics';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Settings from './pages/Settings';
import { useBotStore } from './stores/botStore';
import './styles/globals.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const { theme, refreshStatus, connectWebSocket, disconnectWebSocket } = useBotStore();

  useEffect(() => {
    // Apply theme on mount
    document.documentElement.classList.toggle('dark', theme === 'dark');
    
    // Initialize connections with proper error handling
    const initializeConnections = async () => {
      try {
        console.log('🔄 Initializing frontend connections...');
        
        // First try to refresh status
        await refreshStatus();
        console.log('✅ API connection established');
        
        // Then connect WebSocket for real-time updates
        await connectWebSocket();
        console.log('✅ WebSocket connection established');
        
      } catch (error) {
        console.error('❌ Failed to initialize connections:', error);
        // Don't throw - let the app continue with degraded functionality
      }
    };
    
    // Initialize connections
    initializeConnections();
    
    // Set up periodic status refresh as fallback
    const interval = setInterval(async () => {
      try {
        await refreshStatus();
      } catch (error) {
        console.error('Failed to refresh status:', error);
      }
    }, 30000); // Every 30 seconds
    
    return () => {
      clearInterval(interval);
      disconnectWebSocket();
    };
  }, [theme, refreshStatus, connectWebSocket, disconnectWebSocket]);

  return (
    <QueryClientProvider client={queryClient}>
      <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="min-h-screen bg-secondary-50 dark:bg-secondary-900 transition-colors duration-200">
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/jobs" element={<Jobs />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
          
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: theme === 'dark' ? '#1e293b' : '#ffffff',
                color: theme === 'dark' ? '#f1f5f9' : '#0f172a',
                border: theme === 'dark' ? '1px solid #334155' : '1px solid #e2e8f0',
              },
            }}
          />
        </div>
        <SpeedInsights />
      </Router>
    </QueryClientProvider>
  );
}

export default App;
