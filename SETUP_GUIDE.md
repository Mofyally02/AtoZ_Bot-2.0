# AtoZ Bot Dashboard - Complete Setup & Testing Guide

This guide will walk you through setting up and testing both the frontend and backend of your AtoZ Bot Dashboard.

## 📋 Prerequisites Check

Before starting, ensure you have the following installed:

### Required Software
- [ ] **Docker Desktop** (Latest version)
- [ ] **Docker Compose** (Usually included with Docker Desktop)
- [ ] **Node.js 18+** (For frontend development)
- [ ] **Python 3.11+** (For backend development)
- [ ] **Git** (For version control)

### Optional Software
- [ ] **Postman** (For API testing)
- [ ] **VS Code** (Recommended IDE)

## 🚀 Step-by-Step Setup

### Step 1: Verify Prerequisites

Let's check if you have the required software installed:

```powershell
# Check Docker
docker --version
docker-compose --version

# Check Node.js
node --version
npm --version

# Check Python
python --version
pip --version
```

### Step 2: Clone and Navigate to Project

```powershell
# Navigate to your project directory
cd "C:\Users\USER\Desktop\Al-Tech\Bot\AtoZ-Bot"

# Verify you're in the right directory
ls
```

### Step 3: Environment Configuration

#### 3.1 Create Environment File
```powershell
# Copy the template
Copy-Item env.template .env

# Open .env file to edit
notepad .env
```

#### 3.2 Update Environment Variables
Edit the `.env` file with your actual values:

```env
# Database Configuration
POSTGRES_DB=atoz_bot_db
POSTGRES_USER=atoz_user
POSTGRES_PASSWORD=your_secure_password_here
DATABASE_URL=postgresql://atoz_user:your_secure_password_here@localhost:5432/atoz_bot_db

# Redis Configuration
REDIS_URL=redis://localhost:6379

# AtoZ Bot Credentials (REQUIRED - Update these!)
ATOZ_BASE_URL=https://portal.atozinterpreting.com
ATOZ_USERNAME=your_email@example.com
ATOZ_PASSWORD=your_actual_password
ATOZ_INTERPRETER_JOBS_PATH=/interpreter-jobs

# Bot Configuration
REFRESH_INTERVAL_SEC=0.5
MAX_ACCEPT_PER_RUN=5
HEADLESS=true

# Features
ENABLE_QUICK_CHECK=false
ENABLE_RESULTS_REPORTING=true
ENABLE_REJECTED_REPORTING=true

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
ENVIRONMENT=development

# Frontend Configuration
VITE_API_URL=http://localhost:8000
NODE_ENV=development
```

### Step 4: Generate SSL Certificates (Optional but Recommended)

```powershell
# Navigate to SSL directory
cd ssl

# Generate development certificates
.\generate-dev-certs.ps1

# Return to project root
cd ..
```

### Step 5: Start All Services

#### Option A: Automated Setup (Recommended)
```powershell
# Run the automated setup script
.\setup-dev.ps1
```

#### Option B: Manual Setup
```powershell
# Create necessary directories
New-Item -ItemType Directory -Path "logs/nginx" -Force
New-Item -ItemType Directory -Path "logs/bot" -Force
New-Item -ItemType Directory -Path "data/postgres" -Force
New-Item -ItemType Directory -Path "data/redis" -Force

# Start all services
docker-compose up -d --build

# Check service status
docker-compose ps
```

### Step 6: Verify Services are Running

```powershell
# Check if all containers are running
docker-compose ps

# Check logs
docker-compose logs -f

# Check individual service health
# Database
docker-compose exec database pg_isready -U atoz_user -d atoz_bot_db

# Redis
docker-compose exec redis redis-cli ping

# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000
```

## 🧪 Testing Guide

### Test 1: Backend API Testing

#### 1.1 Health Check
```powershell
# Test backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","timestamp":"2024-01-15T10:30:00.000000","version":"1.0.0"}
```

#### 1.2 API Documentation
- Open browser: `http://localhost:8000/docs`
- You should see the FastAPI interactive documentation

#### 1.3 Test Bot Endpoints
```powershell
# Get bot status
curl http://localhost:8000/api/bot/status

# Get bot sessions
curl http://localhost:8000/api/bot/sessions

# Get dashboard metrics
curl http://localhost:8000/api/dashboard/metrics
```

### Test 2: Frontend Testing

#### 2.1 Access Frontend
- Open browser: `http://localhost:3000`
- You should see the AtoZ Bot Dashboard

#### 2.2 Test Frontend Features
1. **Dashboard Page**
   - [ ] Verify dashboard loads
   - [ ] Check if metrics are displayed
   - [ ] Test real-time updates

2. **Bot Control Panel**
   - [ ] Test "Start Bot" button
   - [ ] Test "Stop Bot" button
   - [ ] Check status indicators

3. **Analytics Page**
   - [ ] Navigate to Analytics
   - [ ] Check if charts load
   - [ ] Test date range filters

4. **Jobs Page**
   - [ ] Navigate to Jobs
   - [ ] Test job filtering
   - [ ] Test search functionality

5. **Settings Page**
   - [ ] Navigate to Settings
   - [ ] Test configuration changes
   - [ ] Test save functionality

### Test 3: Bot Integration Testing

#### 3.1 Test Bot Configuration
```powershell
# Navigate to bot directory
cd bot

# Test bot configuration
python -c "import config; print('Bot config loaded successfully')"

# Test bot login (dry run)
python -c "
from login_handler import LoginHandler
from config import USER_CREDENTIALS
lh = LoginHandler()
print('Login handler initialized successfully')
"
```

#### 3.2 Test Bot Execution
```powershell
# Test bot run (short test)
python test_quick_check.py

# Test continuous operation (5 minutes)
python test_continuous_operation.py

# Test results reporting
python test_results_reporting.py
```

#### 3.3 Test Bot with Dashboard
1. Start the bot from the frontend
2. Monitor real-time updates
3. Check if jobs are being processed
4. Verify analytics are updating

### Test 4: Database Testing

#### 4.1 Connect to Database
```powershell
# Connect to PostgreSQL
docker-compose exec database psql -U atoz_user -d atoz_bot_db

# List tables
\dt

# Check bot_sessions table
SELECT * FROM bot_sessions;

# Check job_records table
SELECT * FROM job_records LIMIT 5;

# Exit database
\q
```

#### 4.2 Test Database Operations
```powershell
# Test database connection from backend
curl http://localhost:8000/api/dashboard/metrics

# Expected: Should return database metrics
```

### Test 5: WebSocket Testing

#### 5.1 Test Real-time Updates
1. Open browser: `http://localhost:3000`
2. Open browser developer tools (F12)
3. Go to Console tab
4. Look for WebSocket connection messages
5. Start/stop bot and watch for real-time updates

#### 5.2 Test WebSocket Endpoint
```powershell
# Test WebSocket connection (using curl)
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==" http://localhost:8000/ws
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### Issue 1: Services Won't Start
```powershell
# Check Docker status
docker --version
docker-compose --version

# Check if ports are available
netstat -an | findstr :3000
netstat -an | findstr :8000
netstat -an | findstr :5432

# Restart Docker Desktop if needed
```

#### Issue 2: Database Connection Failed
```powershell
# Check database logs
docker-compose logs database

# Restart database
docker-compose restart database

# Check database health
docker-compose exec database pg_isready -U atoz_user -d atoz_bot_db
```

#### Issue 3: Frontend Won't Load
```powershell
# Check frontend logs
docker-compose logs frontend

# Check if frontend is building
docker-compose exec frontend npm run build

# Restart frontend
docker-compose restart frontend
```

#### Issue 4: Backend API Errors
```powershell
# Check backend logs
docker-compose logs backend

# Check if backend is healthy
curl http://localhost:8000/health

# Restart backend
docker-compose restart backend
```

#### Issue 5: Bot Login Issues
```powershell
# Check bot logs
docker-compose logs bot

# Test bot configuration
cd bot
python -c "import config; print(config.USER_CREDENTIALS)"

# Test login manually
python login_handler.py
```

## 📊 Performance Testing

### Load Testing
```powershell
# Test API response times
Measure-Command { curl http://localhost:8000/health }

# Test multiple concurrent requests
for ($i=1; $i -le 10; $i++) {
    Start-Job -ScriptBlock { curl http://localhost:8000/health }
}
```

### Memory Usage
```powershell
# Check container resource usage
docker stats

# Check specific container
docker stats atoz-backend
docker stats atoz-frontend
docker stats atoz-database
```

## 🎯 Success Criteria

Your setup is successful when:

- [ ] All Docker containers are running (`docker-compose ps`)
- [ ] Backend API responds at `http://localhost:8000/health`
- [ ] Frontend loads at `http://localhost:3000`
- [ ] Database is accessible and contains tables
- [ ] Bot can authenticate with AtoZ portal
- [ ] Real-time updates work in the frontend
- [ ] All test scripts run without errors

## 🚀 Next Steps

Once everything is working:

1. **Customize Configuration**: Update bot settings in the frontend
2. **Set Up Monitoring**: Configure logging and alerts
3. **Deploy to Production**: Use `docker-compose.prod.yml`
4. **Set Up Backups**: Configure database backups
5. **Add Notifications**: Set up email/webhook notifications

## 📞 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure all ports are available
4. Check Docker Desktop is running
5. Review this troubleshooting guide

---

**Happy Testing! 🎉**

