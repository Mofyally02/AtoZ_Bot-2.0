# PostgreSQL Setup Guide for AtoZ Bot System

## 🎯 PostgreSQL-Only Configuration

Your AtoZ Bot system is now configured to use **PostgreSQL only** as the database. SQLite has been completely removed.

## 🚀 Quick Start

### Option 1: Automated PostgreSQL Startup (Recommended)
```bash
python start_system_postgresql.pyr
```

### Option 2: Shell Script Startup
```bash
./start_system.sh
```

### Option 3: Python Integration Script
```bash
python connect_system.py
```

## 🔧 Docker Permissions Fix

If you encounter Docker permission issues, run:
```bash
./fix_docker_permissions.sh
```

Or manually:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

## 🗄️ Database Configuration

### PostgreSQL Connection Details
- **Host:** localhost
- **Port:** 5432
- **Database:** atoz_bot_db
- **Username:** atoz_user
- **Password:** atoz_password

### Environment Variables
```bash
export DATABASE_URL="postgresql://atoz_user:atoz_password@localhost:5432/atoz_bot_db"
export REDIS_URL="redis://localhost:6379"
```

## 📊 Database Schema

The system uses the following PostgreSQL tables:

- `bot_sessions` - Bot session tracking
- `job_records` - Job processing history
- `analytics_periods` - Performance analytics
- `bot_configurations` - Bot settings
- `system_logs` - System event logs

## 🐳 Docker Services

The system uses Docker Compose to run:

1. **PostgreSQL Database**
   - Image: postgres:15-alpine
   - Port: 5432 (mapped to 5433 on host)
   - Persistent data volume

2. **Redis Cache**
   - Image: redis:7-alpine
   - Port: 6379 (mapped to 6380 on host)
   - Persistent data volume

## 🔍 Troubleshooting

### Database Connection Issues

1. **Check Docker services:**
   ```bash
   docker-compose ps
   ```

2. **Check PostgreSQL logs:**
   ```bash
   docker-compose logs database
   ```

3. **Test PostgreSQL connection:**
   ```bash
   psql -h localhost -p 5432 -U atoz_user -d atoz_bot_db -c "SELECT 1;"
   ```

### Docker Permission Issues

1. **Fix permissions:**
   ```bash
   ./fix_docker_permissions.sh
   ```

2. **Or manually:**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Restart Docker service:**
   ```bash
   sudo systemctl restart docker
   ```

### Port Conflicts

If ports 5432 or 6379 are already in use:

1. **Check what's using the ports:**
   ```bash
   sudo netstat -tlnp | grep :5432
   sudo netstat -tlnp | grep :6379
   ```

2. **Stop conflicting services or change ports in docker-compose.yml**

## 🧪 Testing

### Run Integration Tests
```bash
python test_integration.py
```

### Verify Connections
```bash
python verify_connections.py
```

### Manual Database Test
```bash
# Connect to PostgreSQL
psql -h localhost -p 5432 -U atoz_user -d atoz_bot_db

# Run some test queries
SELECT * FROM bot_sessions LIMIT 5;
SELECT * FROM bot_configurations;
```

## 📈 Monitoring

### Database Health Check
```bash
curl http://localhost:8000/health/detailed
```

### Direct Database Access
```bash
# Connect to PostgreSQL container
docker-compose exec database psql -U atoz_user -d atoz_bot_db

# Connect to Redis container
docker-compose exec redis redis-cli
```

## 🔄 Backup and Restore

### Backup Database
```bash
docker-compose exec database pg_dump -U atoz_user atoz_bot_db > backup.sql
```

### Restore Database
```bash
docker-compose exec -T database psql -U atoz_user atoz_bot_db < backup.sql
```

## 🌐 Access URLs

- **Frontend Dashboard:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **WebSocket:** ws://localhost:8000/ws
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

## 📝 Configuration Files

- `docker-compose.yml` - PostgreSQL and Redis services
- `backend/app/database/connection.py` - Database connection settings
- `database/schema.sql` - PostgreSQL schema
- `start_system_postgresql.py` - PostgreSQL startup script

## 🎉 System Ready!

Your AtoZ Bot system is now configured for PostgreSQL with:

- ✅ **PostgreSQL Database** (no SQLite)
- ✅ **Redis Cache** for performance
- ✅ **FastAPI Backend** with database integration
- ✅ **React Frontend** with real-time updates
- ✅ **Bot Integration** with PostgreSQL persistence
- ✅ **WebSocket Communication** for live updates
- ✅ **Health Monitoring** for all services
- ✅ **Docker Services** for easy deployment

Start your system with:
```bash
python start_system_postgresql.py
```
