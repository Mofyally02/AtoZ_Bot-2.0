# AtoZ Bot System - Connection Guide

This guide explains how to connect and integrate all components of the AtoZ Bot system: Database, API, WebSocket, and Bot.

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │     Bot         │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (Playwright)   │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │    Database     │
                       │  (PostgreSQL)   │
                       │   Port: 5432    │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │     Redis       │
                       │   Port: 6379    │
                       └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)

```bash
# Start all components automatically
./start_system.sh
```

This script will:
- Start PostgreSQL and Redis using Docker
- Start the FastAPI backend server
- Start the React frontend development server
- Monitor all components and provide status updates

### Option 2: Manual Startup

```bash
# 1. Start database and Redis
docker-compose up -d database redis

# 2. Start backend server
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 3. Start frontend server (in new terminal)
cd frontend
npm run dev -- --host 0.0.0.0 --port 3000

# 4. Start bot (in new terminal)
cd bot
python integrated_bot.py <session_id>
```

### Option 3: Python Integration Script

```bash
# Start all components using Python
python connect_system.py
```

## 🔧 Component Details

### 1. Database (PostgreSQL)

**Connection Details:**
- Host: localhost
- Port: 5432
- Database: atoz_bot_db
- Username: atoz_user
- Password: atoz_password

**Schema:**
- `bot_sessions` - Bot session tracking
- `job_records` - Job processing history
- `analytics_periods` - Performance analytics
- `bot_configurations` - Bot settings
- `system_logs` - System event logs

**Verification:**
```bash
# Test database connection
python verify_connections.py
```

### 2. Backend API (FastAPI)

**Endpoints:**
- Health Check: `GET /health`
- Detailed Health: `GET /health/detailed`
- Bot Status: `GET /api/bot/status`
- Bot Toggle: `POST /api/bot/toggle`
- Dashboard Metrics: `GET /api/bot/dashboard/metrics`
- Bot Configuration: `GET /api/bot/configuration`
- WebSocket: `WS /ws`

**Features:**
- Real-time bot control
- WebSocket communication
- Database integration
- Redis caching
- Connection monitoring

### 3. Frontend (React)

**Access:** http://localhost:3000

**Features:**
- Real-time dashboard
- Bot control interface
- System status monitoring
- Configuration management
- WebSocket integration

### 4. Bot (Playwright)

**Scripts:**
- `integrated_bot.py` - Full-featured bot with API integration
- `real_atoz_bot.py` - Real AtoZ portal bot
- `atoz_bot.py` - Core bot functionality

**Features:**
- Automated login to AtoZ portal
- Job detection and filtering
- Real-time status updates
- Database integration
- Error handling and recovery

### 5. Redis Cache

**Purpose:**
- Bot state management
- Session caching
- Real-time metrics
- Task queue management

## 🔗 Connection Verification

### Automated Testing

```bash
# Run comprehensive integration tests
python test_integration.py

# Verify all connections
python verify_connections.py
```

### Manual Testing

```bash
# Test database
psql -h localhost -p 5432 -U atoz_user -d atoz_bot_db -c "SELECT 1;"

# Test Redis
redis-cli -h localhost -p 6379 ping

# Test backend API
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Test WebSocket
wscat -c ws://localhost:8000/ws
```

## 📊 System Monitoring

### Health Checks

```bash
# Overall system health
curl http://localhost:8000/health

# Detailed service status
curl http://localhost:8000/health/detailed

# Bot status
curl http://localhost:8000/api/bot/status
```

### Logs

```bash
# Backend logs
tail -f logs/backend.log

# Frontend logs
tail -f logs/frontend.log

# Docker logs
docker-compose logs -f
```

## 🤖 Bot Management

### Starting the Bot

```bash
# Via API
curl -X POST http://localhost:8000/api/bot/toggle

# Via Python script
python connect_system.py

# Direct execution
cd bot
python integrated_bot.py session-$(date +%Y%m%d_%H%M%S)
```

### Bot Configuration

```bash
# Get current configuration
curl http://localhost:8000/api/bot/configuration

# Update configuration
curl -X PUT http://localhost:8000/api/bot/configuration \
  -H "Content-Type: application/json" \
  -d '{
    "check_interval_seconds": 0.5,
    "max_accept_per_run": 5,
    "job_type_filter": "Telephone interpreting"
  }'
```

## 🔄 Real-time Communication

### WebSocket Events

The system uses WebSocket for real-time communication between components:

**Event Types:**
- `connection_established` - WebSocket connection confirmed
- `status_update` - Bot status changes
- `job_processed` - Job acceptance/rejection
- `cycle_complete` - Bot cycle completion
- `error` - Error notifications
- `configuration_updated` - Config changes

**Example WebSocket Client:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data.type, data.data);
};
```

## 🛠️ Troubleshooting

### Common Issues

1. **Database Connection Failed**
   ```bash
   # Check if PostgreSQL is running
   docker-compose ps database
   
   # Check database logs
   docker-compose logs database
   ```

2. **Redis Connection Failed**
   ```bash
   # Check if Redis is running
   docker-compose ps redis
   
   # Check Redis logs
   docker-compose logs redis
   ```

3. **Backend API Not Responding**
   ```bash
   # Check if backend process is running
   ps aux | grep uvicorn
   
   # Check backend logs
   tail -f logs/backend.log
   ```

4. **Frontend Not Loading**
   ```bash
   # Check if frontend process is running
   ps aux | grep "npm run dev"
   
   # Check frontend logs
   tail -f logs/frontend.log
   ```

5. **Bot Not Starting**
   ```bash
   # Check bot logs
   python integrated_bot.py session-test 2>&1 | tee bot.log
   
   # Check dependencies
   pip list | grep playwright
   ```

### Port Conflicts

If you encounter port conflicts, update the configuration:

**Backend (main.py):**
```python
uvicorn.run("main:app", host="0.0.0.0", port=8001)  # Change port
```

**Frontend (package.json):**
```json
{
  "scripts": {
    "dev": "vite --port 3001"  // Change port
  }
}
```

**Docker (docker-compose.yml):**
```yaml
ports:
  - "5433:5432"  # Change host port
  - "6380:6379"  # Change host port
```

## 📈 Performance Monitoring

### Metrics Available

- Bot uptime and status
- Job processing rates
- Success/failure rates
- System resource usage
- Database performance
- WebSocket connection count

### Dashboard Access

- **Frontend Dashboard:** http://localhost:3000
- **API Documentation:** http://localhost:8000/docs
- **Health Monitor:** http://localhost:8000/health/detailed

## 🔐 Security Considerations

1. **Database Credentials:** Update default credentials in production
2. **API Endpoints:** Implement authentication for production use
3. **CORS Settings:** Configure appropriate CORS policies
4. **Environment Variables:** Use environment variables for sensitive data
5. **SSL/TLS:** Enable HTTPS for production deployment

## 📝 Configuration Files

- `docker-compose.yml` - Docker services configuration
- `backend/app/main.py` - FastAPI application setup
- `backend/app/database/connection.py` - Database connection settings
- `bot/config.py` - Bot configuration
- `frontend/vite.config.ts` - Frontend build configuration

## 🚀 Production Deployment

For production deployment:

1. **Environment Setup:**
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:5432/db"
   export REDIS_URL="redis://host:6379"
   export ENVIRONMENT="production"
   ```

2. **Security:**
   - Update all default passwords
   - Enable SSL/TLS
   - Configure firewall rules
   - Set up monitoring and alerting

3. **Scaling:**
   - Use connection pooling for database
   - Implement Redis clustering
   - Set up load balancing for API
   - Use CDN for frontend assets

## 📞 Support

For issues and questions:

1. Check the logs first
2. Run verification scripts
3. Review this connection guide
4. Check component-specific documentation
5. Test individual components separately

---

**Happy Botting! 🤖**
