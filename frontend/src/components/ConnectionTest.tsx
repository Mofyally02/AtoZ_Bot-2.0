import { CheckCircle, XCircle, Wifi, WifiOff, RefreshCw, AlertTriangle } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { connectionService, ConnectionStatus } from '../services/connectionService';
import Button from './ui/Button';
import Card from './ui/Card';

const ConnectionTest: React.FC = () => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Subscribe to connection status updates
    const unsubscribe = connectionService.addCallback((status) => {
      console.log('Connection status received in component:', status.overallStatus);
      setConnectionStatus(status);
      setLastUpdate(new Date());
      setIsLoading(false);
    });

    // Get initial status
    const initialStatus = connectionService.getStatus();
    if (initialStatus) {
      console.log('Initial status found:', initialStatus.overallStatus);
      setConnectionStatus(initialStatus);
      setIsLoading(false);
    } else {
      console.log('No initial status, forcing check...');
      // Force an immediate check if no initial status
      connectionService.checkConnections();
    }

    // Always force a fresh check when component mounts
    setTimeout(() => {
      connectionService.checkConnections();
    }, 100);

    return () => {
      unsubscribe();
    };
  }, []);

  const testConnections = async () => {
    setIsTesting(true);
    try {
      await connectionService.forceCheckAll();
      toast.success('All connections checked');
    } catch (error) {
      console.error('Connection test failed:', error);
      toast.error('Connection test failed');
    } finally {
      setIsTesting(false);
    }
  };

  const getServiceStatus = (serviceName: keyof ConnectionStatus['services']): boolean => {
    if (!connectionStatus) return false;
    
    // Special handling for Redis - show as healthy when not required
    if (serviceName === 'redis') {
      const status = connectionStatus.services[serviceName]?.status;
      return status === 'healthy' || status === 'disconnected' || !status;
    }
    
    return connectionStatus.services[serviceName]?.status === 'healthy';
  };

  const getServiceStatusText = (serviceName: keyof ConnectionStatus['services']): string => {
    if (!connectionStatus) return 'Unknown';
    
    // Special handling for Redis - show as "Not Required" when not available
    if (serviceName === 'redis') {
      const status = connectionStatus.services[serviceName]?.status;
      if (status === 'disconnected' || !status) {
        return 'Not Required';
      }
    }
    
    return connectionStatus.services[serviceName]?.status || 'Unknown';
  };

  const getOverallStatusColor = (): string => {
    if (isLoading || !connectionStatus) return 'text-blue-500';
    
    switch (connectionStatus.overallStatus) {
      case 'healthy':
        return 'text-green-500';
      case 'degraded':
        return 'text-yellow-500';
      case 'partial':
        return 'text-orange-500';
      default:
        return 'text-blue-500';
    }
  };

  const getOverallStatusText = (): string => {
    if (isLoading || !connectionStatus) return 'CHECKING...';
    
    switch (connectionStatus.overallStatus) {
      case 'healthy':
        return 'HEALTHY';
      case 'degraded':
        return 'DEGRADED';
      case 'partial':
        return 'PARTIAL';
      default:
        return 'CHECKING...';
    }
  };

  const getOverallStatusIcon = () => {
    if (isLoading || !connectionStatus) return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
    
    switch (connectionStatus.overallStatus) {
      case 'healthy':
        return <Wifi className="w-5 h-5 text-green-500" />;
      case 'degraded':
        return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
      case 'partial':
        return <Wifi className="w-5 h-5 text-orange-500" />;
      default:
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
    }
  };

  const getServiceIcon = (isHealthy: boolean, status: string) => {
    if (isHealthy) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    
    // Special case for Redis "Not Required" status
    if (status === 'Not Required') {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    }
    
    switch (status) {
      case 'connecting':
        return <RefreshCw className="w-4 h-4 text-blue-500 animate-spin" />;
      case 'disconnected':
        return <WifiOff className="w-4 h-4 text-red-500" />;
      case 'unhealthy':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <AlertTriangle className="w-4 h-4 text-yellow-500" />;
    }
  };

  const getServiceColor = (isHealthy: boolean, status: string): string => {
    if (isHealthy) return 'text-green-500';
    
    // Special case for Redis "Not Required" status
    if (status === 'Not Required') {
      return 'text-green-500';
    }
    
    switch (status) {
      case 'connecting':
        return 'text-blue-500';
      case 'disconnected':
        return 'text-red-500';
      case 'unhealthy':
        return 'text-red-500';
      default:
        return 'text-yellow-500';
    }
  };

  const services = [
    { key: 'database' as const, name: 'Database', description: 'PostgreSQL database connection', critical: true },
    { key: 'redis' as const, name: 'Redis', description: 'Redis cache connection (not required)', critical: false },
    { key: 'external_api' as const, name: 'API', description: 'Backend API connection', critical: true },
    { key: 'websocket' as const, name: 'WebSocket', description: 'Real-time communication', critical: true },
    { key: 'bot_process' as const, name: 'Bot Process', description: 'AtoZ Bot process status', critical: true },
  ];

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          {getOverallStatusIcon()}
          <div>
            <h3 className="text-lg font-semibold">Connection Status</h3>
            <p className={`text-sm font-medium ${getOverallStatusColor()}`}>
              {getOverallStatusText()}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
        <Button
          onClick={testConnections}
          disabled={isTesting}
            variant="secondary"
            size="sm"
            className="flex items-center space-x-2"
          >
            <RefreshCw className={`w-4 h-4 ${isTesting ? 'animate-spin' : ''}`} />
            <span>{isTesting ? 'Testing...' : 'Test All'}</span>
          </Button>
          <Button
            onClick={() => connectionService.forceUpdateStatus()}
            variant="secondary"
          size="sm"
        >
            Force Update
        </Button>
        </div>
      </div>

      <div className="space-y-4">
        {services.map((service) => {
          const isHealthy = getServiceStatus(service.key);
          const statusText = getServiceStatusText(service.key);
          
          return (
            <div
              key={service.key}
              className={`flex items-center justify-between p-3 rounded-lg ${
                service.critical 
                  ? 'bg-gray-50 dark:bg-gray-800' 
                  : 'bg-blue-50 dark:bg-blue-900/20'
              }`}
            >
          <div className="flex items-center space-x-3">
                {getServiceIcon(isHealthy, statusText)}
                <div>
                  <p className="font-medium flex items-center space-x-2">
                    <span>{service.name}</span>
                    {!service.critical && (
                      <span className="text-xs bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200 px-2 py-1 rounded">
                        {service.key === 'redis' ? 'Not Required' : 'Optional'}
                      </span>
                    )}
                  </p>
                  <p className="text-sm text-gray-500">{service.description}</p>
          </div>
        </div>
              <div className="flex items-center space-x-2">
                <span className={`text-sm font-medium ${getServiceColor(isHealthy, statusText)}`}>
                  {statusText.toUpperCase()}
                </span>
                {connectionStatus?.services?.[service.key]?.retryCount && connectionStatus.services[service.key].retryCount > 0 && (
                  <span className="text-xs text-gray-500">
                    (Retry: {connectionStatus.services[service.key].retryCount})
                  </span>
                )}
              </div>
          </div>
          );
        })}
        </div>

      {lastUpdate && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <p className="text-xs text-gray-500">
            Last updated: {lastUpdate.toLocaleTimeString()}
          </p>
          {connectionStatus?.monitoringActive && (
            <p className="text-xs text-gray-500">
              Auto-checking every {connectionStatus.checkInterval / 1000}s
            </p>
          )}
        </div>
      )}

      {connectionStatus && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="flex items-center space-x-2">
            <Wifi className="w-4 h-4 text-blue-500" />
            <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
              Real-time Monitoring Active
            </span>
          </div>
          <p className="text-xs text-blue-600 dark:text-blue-400 mt-1">
            Connection status is automatically monitored and will update in real-time.
            Failed connections will be automatically retried.
          </p>
        </div>
      )}
    </Card>
  );
};

export default ConnectionTest;