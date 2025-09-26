# AtoZ Bot Dashboard 🚀

A modern, comprehensive dashboard for the AtoZ translation bot with real-time analytics, job management, and beautiful UI.

## ✨ Features

### 🎯 Core Functionality
- **Real-time Bot Control**: Start/stop bot with one click
- **Live Analytics**: Real-time metrics and performance tracking
- **Job Management**: View, filter, and manage all job records
- **Modern UI**: iPhone-inspired design with light/dark mode
- **Database Integration**: PostgreSQL with automatic data cleanup
- **WebSocket Support**: Real-time updates and notifications

### 📊 Analytics & Reporting
- **4-Hour Analytics**: Automated reporting every 4 hours
- **7-Day Retention**: Automatic cleanup of old data
- **Visual Charts**: Interactive dashboards with Chart.js
- **Performance Metrics**: Acceptance rates, language distribution, peak hours
- **Export Options**: CSV/JSON data export capabilities

### 🔧 Technical Features
- **TypeScript Frontend**: React 18 with modern tooling
- **FastAPI Backend**: High-performance Python API
- **PostgreSQL Database**: Robust data storage with indexing
- **Redis Caching**: Fast data access and session management
- **Docker Support**: Easy deployment and scaling
- **WebSocket Integration**: Real-time communication

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └──────────────►│     Redis       │◄─────────────┘
                        │   (Caching)     │
                        │   Port: 6379    │
                        └─────────────────┘
```

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd atoz-bot-dashboard

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Manual Setup

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### Database Setup
```bash
# Install PostgreSQL
# Create database
createdb atoz_bot_db

# Run schema
psql atoz_bot_db < database/schema.sql
```

## 📱 Usage

### 1. Access the Dashboard
- Open your browser to `http://localhost:3000`
- The dashboard will automatically connect to the backend

### 2. Start the Bot
- Click "Start Bot" in the control panel
- Enter a session name (optional)
- Monitor real-time status and metrics

### 3. View Analytics
- Navigate to the Analytics page
- View charts and performance metrics
- Export data as needed

### 4. Manage Jobs
- Go to the Jobs page
- Filter by status (accepted/rejected)
- Search by job reference or language
- View detailed job information

### 5. Configure Settings
- Access the Settings page
- Adjust bot parameters
- Toggle features on/off
- Save your preferences

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://atoz_user:atoz_password@localhost:5432/atoz_bot_db
REDIS_URL=redis://localhost:6379

# Bot Configuration
CHECK_INTERVAL_SEC=0.5
RESULTS_REPORT_INTERVAL_SEC=5
REJECTED_REPORT_INTERVAL_SEC=43200
QUICK_CHECK_INTERVAL_SEC=10

# Features
ENABLE_QUICK_CHECK=false
ENABLE_RESULTS_REPORTING=true
ENABLE_REJECTED_REPORTING=true

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Bot Integration

To integrate with your existing bot:

```bash
# Run the integrated bot
python bot_integration.py

# Or use the original bot (standalone)
python persistent_bot.py
```

## 📊 Database Schema

### Key Tables
- **bot_sessions**: Bot session tracking
- **job_records**: All job data (scraped from AtoZ)
- **analytics_periods**: 4-hour analytics data
- **system_logs**: Application logs
- **bot_configurations**: Bot settings

### Data Retention
- **Analytics**: 7 days (automatic cleanup)
- **Job Records**: 7 days (rejected/failed kept longer)
- **System Logs**: 7 days
- **Sessions**: Permanent (with end times)

## 🎨 UI/UX Features

### Design System
- **iPhone-inspired**: Clean, modern interface
- **Light/Dark Mode**: Automatic theme switching
- **Responsive**: Mobile-first design
- **Animations**: Smooth transitions with Framer Motion
- **Accessibility**: WCAG compliant

### Color Palette
- **Primary**: Blue (#0ea5e9)
- **Success**: Green (#22c55e)
- **Warning**: Orange (#f59e0b)
- **Error**: Red (#ef4444)
- **Neutral**: Gray scale

## 🔌 API Endpoints

### Bot Control
- `POST /api/bot/start` - Start bot
- `POST /api/bot/stop` - Stop bot
- `GET /api/bot/status` - Get bot status
- `GET /api/bot/sessions` - Get session history

### Data
- `GET /api/bot/jobs` - Get job records
- `GET /api/bot/analytics` - Get analytics data
- `GET /api/dashboard/metrics` - Get dashboard metrics

### WebSocket
- `WS /ws` - Real-time updates

## 🛠️ Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend Development
```bash
cd backend
python main.py       # Start dev server
python -m pytest    # Run tests
```

### Database Migrations
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## 📈 Performance

### Optimization Features
- **Database Indexing**: Optimized queries
- **Redis Caching**: Fast data access
- **Lazy Loading**: Efficient data loading
- **Code Splitting**: Smaller bundle sizes
- **Image Optimization**: Compressed assets

### Monitoring
- **Health Checks**: Service monitoring
- **Metrics Collection**: Performance tracking
- **Error Logging**: Comprehensive logging
- **Real-time Updates**: Live status monitoring

## 🔒 Security

### Security Features
- **CORS Protection**: Configured for production
- **Input Validation**: Data sanitization
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content Security Policy
- **Rate Limiting**: API protection

## 🚀 Deployment

### Production Deployment
```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Environment Setup
1. Set up PostgreSQL database
2. Configure Redis instance
3. Set environment variables
4. Deploy with Docker or manually
5. Set up reverse proxy (Nginx)

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Frontend Guide](docs/FRONTEND.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Database Schema](database/schema.sql)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

## 🔄 Changelog

### v1.0.0
- Initial release
- Complete dashboard implementation
- Database integration
- Real-time analytics
- Modern UI/UX

---

**Built with ❤️ for the AtoZ translation bot community**
