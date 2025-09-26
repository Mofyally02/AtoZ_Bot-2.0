# AtoZ Bot Dashboard - Deployment Guide

This guide covers deploying the AtoZ Bot Dashboard to various platforms.

## Quick Fix for "No FastAPI entrypoint found" Error

The error occurs because deployment platforms expect the FastAPI app to be in the root directory. We've fixed this by:

1. **Created `main.py` in root directory** - This imports and runs the FastAPI app from the backend
2. **Created `requirements.txt` in root directory** - Contains all necessary dependencies
3. **Created `Procfile`** - For Heroku and similar platforms

## Deployment Options

### 1. Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### 2. Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run individual services
docker-compose up database redis backend frontend
```

### 3. Platform-Specific Deployment

#### Railway
1. Connect your GitHub repository
2. Railway will automatically detect the `main.py` file
3. Set environment variables:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `PORT` (Railway sets this automatically)

#### Heroku
1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Set environment variables: `heroku config:set DATABASE_URL=...`
4. Deploy: `git push heroku main`

#### Render
1. Connect GitHub repository
2. Select "Web Service"
3. Build command: `pip install -r requirements.txt`
4. Start command: `python main.py`
5. Set environment variables in dashboard

#### DigitalOcean App Platform
1. Connect GitHub repository
2. Select "Web Service"
3. Build command: `pip install -r requirements.txt`
4. Run command: `python main.py`
5. Set environment variables

### 4. VPS/Server Deployment

```bash
# Clone repository
git clone <your-repo-url>
cd AtoZ-Bot

# Install dependencies
pip install -r requirements.txt

# Set up database (PostgreSQL)
# Set up Redis
# Set environment variables

# Run with process manager (PM2, systemd, etc.)
python main.py
```

## Environment Variables

Required environment variables:

```bash
DATABASE_URL=postgresql://user:password@host:port/database
REDIS_URL=redis://host:port
PORT=8000
PYTHONPATH=/path/to/project
```

## Database Setup

1. **PostgreSQL**: Create database and user
2. **Redis**: Install and start Redis server
3. **Run migrations**: The app will create tables automatically

## Frontend Build

For production, build the frontend:

```bash
cd frontend
npm install
npm run build
```

The built files will be served by the FastAPI backend.

## Troubleshooting

### Common Issues

1. **"No FastAPI entrypoint found"**
   - ✅ Fixed: Root `main.py` file now imports from backend

2. **Import errors**
   - Check `PYTHONPATH` is set correctly
   - Ensure all dependencies are installed

3. **Database connection issues**
   - Verify `DATABASE_URL` is correct
   - Ensure database is running and accessible

4. **Frontend not loading**
   - Build the frontend: `npm run build`
   - Check if `frontend/dist` directory exists

### Health Check

Visit `/health` endpoint to verify the application is running:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00.000000",
  "version": "1.0.0"
}
```

## Production Considerations

1. **Security**: Use environment variables for sensitive data
2. **HTTPS**: Set up SSL certificates
3. **Monitoring**: Add logging and monitoring
4. **Scaling**: Use load balancers for multiple instances
5. **Backup**: Regular database backups

## Support

If you encounter issues:

1. Check the logs: `docker-compose logs backend`
2. Verify environment variables
3. Test database connectivity
4. Check the health endpoint

For more help, refer to the main README.md or create an issue in the repository.


