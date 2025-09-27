import { CheckCircle, XCircle, Wifi, WifiOff } from 'lucide-react';
import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { apiService } from '../services/api';
import { wsService } from '../services/websocket';
import Button from './ui/Button';
import Card from './ui/Card';

interface ConnectionStatus {
  api: boolean;
  websocket: boolean;
  database: boolean;
}

const ConnectionTest: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatus>({
    api: false,
    websocket: false,
    database: false,
  });
  const [isTesting, setIsTesting] = useState(false);

  const testConnections = async () => {
    setIsTesting(true);
    const newStatus: ConnectionStatus = {
      api: false,
      websocket: false,
      database: false,
    };

    // Test API connection
    try {
      const healthResponse = await apiService.healthCheck();
      newStatus.api = healthResponse.status === 'healthy';
      if (newStatus.api) {
        toast.success('API connection successful');
      }
    } catch (error) {
      console.error('API connection failed:', error);
      toast.error('API connection failed');
    }

    // Test WebSocket connection
    try {
      await wsService.connect();
      newStatus.websocket = wsService.isConnected();
      if (newStatus.websocket) {
        toast.success('WebSocket connection successful');
        wsService.disconnect(); // Disconnect after test
      }
    } catch (error) {
      console.error('WebSocket connection failed:', error);
      toast.error('WebSocket connection failed');
    }

    // Test Database connection (via dashboard metrics)
    try {
      const metrics = await apiService.getDashboardMetrics();
      newStatus.database = metrics !== null;
      if (newStatus.database) {
        toast.success('Database connection successful');
      }
    } catch (error) {
      console.error('Database connection failed:', error);
      toast.error('Database connection failed');
    }

    setStatus(newStatus);
    setIsTesting(false);
  };

  useEffect(() => {
    testConnections();
  }, []);

  const getStatusIcon = (isConnected: boolean) => {
    return isConnected ? (
      <CheckCircle className="w-5 h-5 text-success-600" />
    ) : (
      <XCircle className="w-5 h-5 text-error-600" />
    );
  };

  const getStatusColor = (isConnected: boolean) => {
    return isConnected
      ? 'bg-success-50 border-success-200 dark:bg-success-900/20 dark:border-success-800'
      : 'bg-error-50 border-error-200 dark:bg-error-900/20 dark:border-error-800';
  };

  const allConnected = status.api && status.websocket && status.database;

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-secondary-900 dark:text-white">
          Connection Status
        </h3>
        <Button
          onClick={testConnections}
          loading={isTesting}
          disabled={isTesting}
          size="sm"
        >
          Test Connections
        </Button>
      </div>

      <div className="space-y-3">
        {/* API Connection */}
        <div className={`flex items-center justify-between p-3 rounded-lg border ${getStatusColor(status.api)}`}>
          <div className="flex items-center space-x-3">
            {status.api ? (
              <Wifi className="w-4 h-4 text-success-600" />
            ) : (
              <WifiOff className="w-4 h-4 text-error-600" />
            )}
            <span className="text-sm font-medium text-secondary-900 dark:text-white">
              API Server
            </span>
          </div>
          {getStatusIcon(status.api)}
        </div>

        {/* WebSocket Connection */}
        <div className={`flex items-center justify-between p-3 rounded-lg border ${getStatusColor(status.websocket)}`}>
          <div className="flex items-center space-x-3">
            {status.websocket ? (
              <Wifi className="w-4 h-4 text-success-600" />
            ) : (
              <WifiOff className="w-4 h-4 text-error-600" />
            )}
            <span className="text-sm font-medium text-secondary-900 dark:text-white">
              WebSocket (Real-time)
            </span>
          </div>
          {getStatusIcon(status.websocket)}
        </div>

        {/* Database Connection */}
        <div className={`flex items-center justify-between p-3 rounded-lg border ${getStatusColor(status.database)}`}>
          <div className="flex items-center space-x-3">
            {status.database ? (
              <Wifi className="w-4 h-4 text-success-600" />
            ) : (
              <WifiOff className="w-4 h-4 text-error-600" />
            )}
            <span className="text-sm font-medium text-secondary-900 dark:text-white">
              Database
            </span>
          </div>
          {getStatusIcon(status.database)}
        </div>
      </div>

      {/* Overall Status */}
      <div className="mt-4 p-3 rounded-lg bg-secondary-50 dark:bg-secondary-800">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-secondary-900 dark:text-white">
            Overall Status:
          </span>
          <div className="flex items-center space-x-2">
            {getStatusIcon(allConnected)}
            <span className={`text-sm font-medium ${
              allConnected ? 'text-success-600' : 'text-error-600'
            }`}>
              {allConnected ? 'All Connected' : 'Issues Detected'}
            </span>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default ConnectionTest;
