# Connection Monitoring System

## Overview

A comprehensive connection monitoring and management system that ensures all parameter connections (API, WebSocket, Database, Redis, Bot Process) maintain constant status and can automatically reconnect when needed.

## Features

### 🔍 **Real-time Monitoring**
- Continuous monitoring of all system components
- Configurable check intervals (default: 30 seconds)
- Automatic status updates and notifications
- Real-time connection health tracking

### 🔄 **Automatic Reconnection**
- Intelligent retry logic with exponential backoff
- Configurable retry attempts (default: 3)
- Automatic service recovery detection
- Graceful degradation handling

### 📊 **Comprehensive Status Tracking**
- Individual service status monitoring
- Overall system health assessment
- Retry count tracking
- Last check timestamp recording

### 🎯 **Service Coverage**
- **Database**: PostgreSQL connection health
- **Redis**: Cache service availability
- **Bot Process**: AtoZ Bot process status
- **External API**: Backend API connectivity
- **WebSocket**: Real-time communication status

## Backend Implementation

### Connection Monitor Service
- **File**: `backend/app/services/connection_monitor.py`
- **Features**:
  - Async connection checking
  - Callback system for status changes
  - Retry logic with configurable limits
  - Service-specific health checks

### API Endpoints
- `GET /health` - Basic health check
- `GET /health/detailed` - Comprehensive status overview
- `GET /health/service/{service_name}` - Individual service check
- `POST /health/force-check` - Force immediate check of all services

### Status Types
- `healthy` - Service is working normally
- `unhealthy` - Service is experiencing issues
- `disconnected` - Service is not available
- `connecting` - Service is attempting to connect
- `unknown` - Service status cannot be determined

## Frontend Implementation

### Connection Service
- **File**: `frontend/src/services/connectionService.ts`
- **Features**:
  - Real-time status updates
  - Automatic reconnection attempts
  - Callback system for UI updates
  - Health summary generation

### Connection Test Component
- **File**: `frontend/src/components/ConnectionTest.tsx`
- **Features**:
  - Visual status indicators
  - Real-time status updates
  - Manual testing capabilities
  - Service-specific information display

## Usage Examples

### Backend API Usage

```python
# Get detailed status
curl http://localhost:8000/health/detailed

# Check specific service
curl http://localhost:8000/health/service/database

# Force check all services
curl -X POST http://localhost:8000/health/force-check
```

### Frontend Integration

```typescript
import { connectionService } from './services/connectionService';

// Subscribe to status updates
const unsubscribe = connectionService.addCallback((status) => {
  console.log('Connection status updated:', status);
});

// Get current status
const status = connectionService.getStatus();

// Force check all connections
await connectionService.forceCheckAll();
```

## Configuration

### Backend Configuration
- **Check Interval**: 30 seconds (configurable)
- **Max Retries**: 3 attempts per service
- **Retry Delay**: 5 seconds between attempts
- **Timeout**: 5 seconds per service check

### Frontend Configuration
- **Update Interval**: 30 seconds
- **Reconnect Attempts**: 5 attempts
- **Reconnect Delay**: 5 seconds

## Monitoring Dashboard

The connection monitoring system provides a comprehensive dashboard showing:

- **Overall System Status**: Healthy, Degraded, Partial, Unknown
- **Individual Service Status**: Real-time status for each component
- **Retry Information**: Number of retry attempts for failed services
- **Last Update Time**: Timestamp of last status check
- **Monitoring Status**: Whether automatic monitoring is active

## Error Handling

### Automatic Recovery
- Failed connections are automatically retried
- Service status is continuously monitored
- Recovery is detected and reported immediately

### Graceful Degradation
- System continues to function with partial service availability
- Unhealthy services are clearly identified
- Manual intervention options are provided

## Testing

### Test Script
- **File**: `test_connection_monitoring.py`
- **Features**:
  - Comprehensive endpoint testing
  - Real-time monitoring demonstration
  - Service status validation
  - Error handling verification

### Running Tests
```bash
python test_connection_monitoring.py
```

## Benefits

1. **Proactive Monitoring**: Issues are detected before they impact users
2. **Automatic Recovery**: Failed connections are automatically restored
3. **Real-time Updates**: Status changes are immediately reflected in the UI
4. **Comprehensive Coverage**: All system components are monitored
5. **User-Friendly**: Clear visual indicators and status information
6. **Configurable**: Flexible configuration for different environments

## Future Enhancements

- Email/SMS notifications for critical failures
- Historical status tracking and analytics
- Custom health check endpoints
- Integration with external monitoring tools
- Performance metrics collection

