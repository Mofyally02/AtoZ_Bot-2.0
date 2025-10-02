import { RealtimeUpdate } from '../types';

export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 3000;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  constructor(private url: string) {}

  connect(): Promise<void> {
    return new Promise((resolve) => {
      try {
        console.log('Attempting WebSocket connection to:', this.url);
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
          console.log('✅ WebSocket connected successfully');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: RealtimeUpdate = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log(`WebSocket disconnected (code: ${event.code}, reason: ${event.reason})`);
          if (event.code === 1001) {
            console.warn('WebSocket closed with 1001 (going away) - server may not support WebSocket connections');
            // Don't attempt reconnection for 1001 errors as they indicate server doesn't support WebSocket
            return;
          }
          this.handleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket connection failed:', error);
          console.warn('WebSocket endpoint may not be available on the backend');
          // Resolve instead of reject to prevent app crashes
          resolve();
        };
      } catch (error) {
        console.error('WebSocket setup failed:', error);
        resolve(); // Resolve instead of reject to prevent app crashes
      }
    });
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`🔄 Attempting WebSocket reconnection... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect().catch((error) => {
          console.error('WebSocket reconnection failed:', error);
        });
      }, this.reconnectInterval);
    } else {
      console.warn('⚠️ Max WebSocket reconnection attempts reached - WebSocket functionality disabled');
      console.info('💡 The app will continue to work without real-time updates');
    }
  }

  private handleMessage(message: RealtimeUpdate): void {
    const listeners = this.listeners.get(message.type);
    if (listeners) {
      listeners.forEach(callback => callback(message.data));
    }
  }

  subscribe(type: string, callback: (data: any) => void): () => void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    
    this.listeners.get(type)!.add(callback);
    
    // Return unsubscribe function
    return () => {
      const listeners = this.listeners.get(type);
      if (listeners) {
        listeners.delete(callback);
        if (listeners.size === 0) {
          this.listeners.delete(type);
        }
      }
    };
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Create singleton instance
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
export const wsService = new WebSocketService(WS_URL);
