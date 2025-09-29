/**
 * Connection monitoring and management service
 */
import { apiService } from './api';
import { wsService } from './websocket';

export interface ServiceStatus {
  status: 'healthy' | 'unhealthy' | 'unknown' | 'connecting' | 'disconnected';
  lastCheck?: string;
  retryCount: number;
}

export interface ConnectionStatus {
  overallStatus: 'healthy' | 'degraded' | 'partial' | 'unknown';
  services: {
    database: ServiceStatus;
    redis: ServiceStatus;
    bot_process: ServiceStatus;
    external_api: ServiceStatus;
    websocket: ServiceStatus;
  };
  monitoringActive: boolean;
  checkInterval: number;
}

export type ConnectionCallback = (status: ConnectionStatus) => void;

class ConnectionService {
  private status: ConnectionStatus | null = null;
  private callbacks: ConnectionCallback[] = [];
  private checkInterval: number = 5000; // 5 seconds
  private intervalId: number | null = null;
  private isMonitoring = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // 1 second

  constructor() {
    this.startMonitoring();
    // Load initial status immediately
    this.checkConnections();
    // Also force a detailed status check
    this.getDetailedStatus().then(status => {
      if (status) {
        this.updateStatus(status);
      }
    });
  }

  /**
   * Add a callback to be notified of connection status changes
   */
  addCallback(callback: ConnectionCallback): () => void {
    this.callbacks.push(callback);
    
    // Immediately call the callback with current status if available
    if (this.status) {
      try {
        callback(this.status);
      } catch (error) {
        console.error('Error in initial connection callback:', error);
      }
    }
    
    // Return unsubscribe function
    return () => {
      const index = this.callbacks.indexOf(callback);
      if (index > -1) {
        this.callbacks.splice(index, 1);
      }
    };
  }

  /**
   * Get current connection status
   */
  getStatus(): ConnectionStatus | null {
    return this.status;
  }

  /**
   * Start monitoring connections
   */
  startMonitoring(): void {
    if (this.isMonitoring) return;
    
    this.isMonitoring = true;
    this.checkConnections();
    
    // Set up periodic checking
    this.intervalId = setInterval(() => {
      this.checkConnections();
    }, this.checkInterval);
  }

  /**
   * Stop monitoring connections
   */
  stopMonitoring(): void {
    this.isMonitoring = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  /**
   * Check all connections
   */
  async checkConnections(): Promise<void> {
    try {
      console.log('Checking connections...');
      await apiService.healthCheck();
      const detailedResponse = await this.getDetailedStatus();
      
      if (detailedResponse) {
        console.log('Detailed status received:', detailedResponse.overallStatus);
        this.updateStatus(detailedResponse);
        this.reconnectAttempts = 0; // Reset on successful check
      }
    } catch (error) {
      console.error('Connection check failed:', error);
      this.handleConnectionError();
    }
  }

  /**
   * Get detailed connection status
   */
  async getDetailedStatus(): Promise<ConnectionStatus | null> {
    try {
      const response = await fetch('http://localhost:8000/health/detailed');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      console.log('Received detailed status from backend:', data.overall_status);
      return data;
    } catch (error) {
      console.error('Failed to get detailed status:', error);
      return null;
    }
  }

  /**
   * Check a specific service
   */
  async checkService(serviceName: string): Promise<ServiceStatus | null> {
    try {
      const response = await fetch(`http://localhost:8000/health/service/${serviceName}`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      return {
        status: data.status,
        lastCheck: data.timestamp,
        retryCount: 0
      };
    } catch (error) {
      console.error(`Failed to check service ${serviceName}:`, error);
      return null;
    }
  }

  /**
   * Force check all services
   */
  async forceCheckAll(): Promise<void> {
    try {
      console.log('Force checking all services...');
      const response = await fetch('http://localhost:8000/health/force-check', { method: 'POST' });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const data = await response.json();
      if (data.status) {
        console.log('Force check returned status:', data.status.overall_status);
        this.updateStatus(data.status);
      }
    } catch (error) {
      console.error('Failed to force check all services:', error);
    }
  }

  /**
   * Force update status (for testing)
   */
  forceUpdateStatus(): void {
    if (this.status) {
      console.log('Force updating status...');
      this.notifyCallbacks(this.status);
    }
  }

  /**
   * Update connection status and notify callbacks
   */
  private updateStatus(newStatus: ConnectionStatus): void {
    const oldStatus = this.status;
    this.status = newStatus;
    
    // Always notify callbacks for the first status or when status changes
    if (!oldStatus || this.hasStatusChanged(oldStatus, newStatus)) {
      console.log('Connection status updated:', newStatus.overallStatus);
      this.notifyCallbacks(newStatus);
    } else {
      console.log('Status unchanged, not notifying callbacks');
    }
  }

  /**
   * Check if status has changed significantly
   */
  private hasStatusChanged(oldStatus: ConnectionStatus, newStatus: ConnectionStatus): boolean {
    if (oldStatus.overallStatus !== newStatus.overallStatus) return true;
    
    for (const [serviceName, service] of Object.entries(newStatus.services)) {
      const oldService = oldStatus.services[serviceName as keyof typeof oldStatus.services];
      if (oldService && oldService.status !== service.status) {
        return true;
      }
    }
    
    return false;
  }

  /**
   * Notify all callbacks of status change
   */
  private notifyCallbacks(status: ConnectionStatus): void {
    console.log(`Notifying ${this.callbacks.length} callbacks with status:`, status.overallStatus);
    this.callbacks.forEach(callback => {
      try {
        callback(status);
      } catch (error) {
        console.error('Error in connection callback:', error);
      }
    });
  }

  /**
   * Handle connection errors and attempt reconnection
   */
  private handleConnectionError(): void {
    this.reconnectAttempts++;
    
    if (this.reconnectAttempts <= this.maxReconnectAttempts) {
      console.log(`Connection error, retrying in ${this.reconnectDelay}ms (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.checkConnections();
      }, this.reconnectDelay);
    } else {
      console.error('Max reconnection attempts reached');
      this.updateStatus({
        overallStatus: 'unknown',
        services: {
          database: { status: 'disconnected', retryCount: this.reconnectAttempts },
          redis: { status: 'disconnected', retryCount: this.reconnectAttempts },
          bot_process: { status: 'disconnected', retryCount: this.reconnectAttempts },
          external_api: { status: 'disconnected', retryCount: this.reconnectAttempts },
          websocket: { status: 'disconnected', retryCount: this.reconnectAttempts }
        },
        monitoringActive: false,
        checkInterval: this.checkInterval
      });
    }
  }

  /**
   * Reconnect WebSocket if needed
   */
  async reconnectWebSocket(): Promise<void> {
    try {
      if (!wsService.isConnected()) {
        await wsService.connect();
        console.log('WebSocket reconnected');
      }
    } catch (error) {
      console.error('Failed to reconnect WebSocket:', error);
    }
  }

  /**
   * Get connection health summary
   */
  getHealthSummary(): {
    isHealthy: boolean;
    unhealthyServices: string[];
    overallStatus: string;
  } {
    if (!this.status) {
      return {
        isHealthy: false,
        unhealthyServices: ['unknown'],
        overallStatus: 'unknown'
      };
    }

    const unhealthyServices: string[] = [];
    
    for (const [serviceName, service] of Object.entries(this.status.services)) {
      if (service.status !== 'healthy') {
        unhealthyServices.push(serviceName);
      }
    }

    return {
      isHealthy: this.status.overallStatus === 'healthy',
      unhealthyServices,
      overallStatus: this.status.overallStatus
    };
  }

  /**
   * Cleanup resources
   */
  destroy(): void {
    this.stopMonitoring();
    this.callbacks = [];
  }
}

// Export singleton instance
export const connectionService = new ConnectionService();
export default connectionService;
