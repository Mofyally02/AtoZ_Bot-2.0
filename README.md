# AtoZ Bot Dashboard 2.0

A modern, streamlined dashboard for managing the AtoZ translation bot with real-time analytics and monitoring.

## 🏗️ Project Structure

```
AtoZ_Bot-2.0/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── database/       # Database connection & models
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   └── services/       # Business logic
│   ├── main.py             # Main FastAPI application
│   ├── simple_main.py      # Simplified version for testing
│   └── requirements.txt    # Backend dependencies
├── frontend/               # React + TypeScript frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── stores/         # State management
│   │   └── types/          # TypeScript types
│   └── package.json        # Frontend dependencies
├── bot/                    # Bot implementation
│   ├── smart_bot.py        # Main bot logic
│   ├── persistent_bot.py   # Persistent bot runner
│   └── config.py           # Bot configuration
├── database/               # Database schema
├── docker-compose.yml      # Docker configuration for Coolify deployment
├── docker-compose.dev.yml  # Docker configuration for development
├── requirements.txt        # Main Python dependencies
├── start.py               # Simple startup script
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- PostgreSQL (optional, can run without database)

### Installation

1. **Clone and setup:**
   ```bash
   cd AtoZ_Bot-2.0
   pip install -r requirements.txt
   ```

2. **Start the backend:**
   ```bash
   python start.py
   # OR
   cd backend && python main.py
   ```

3. **Start the frontend (in another terminal):**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the dashboard:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost/atoz_bot
REDIS_URL=redis://localhost:6379
BOT_API_URL=http://localhost:8000
```

### Database Setup (Optional)
The application can run without a database in simplified mode. To enable full functionality:

1. Install PostgreSQL
2. Create database: `createdb atoz_bot`
3. Update `DATABASE_URL` in `.env`
4. Restart the backend

## 📡 API Endpoints

### Core Bot Control
- `POST /api/bot/start` - Start the bot
- `POST /api/bot/stop` - Stop the bot
- `GET /api/bot/status` - Get bot status
- `GET /api/bot/sessions` - Get session history

### Analytics & Monitoring
- `GET /api/bot/analytics` - Get analytics data
- `GET /api/bot/jobs` - Get job records
- `GET /api/bot/dashboard/metrics` - Get dashboard metrics

### WebSocket (Real-time Updates)
- `WS /ws` - Real-time bot status updates

## 🤖 Bot Integration

The bot can be integrated with the dashboard in two ways:

1. **Standalone Mode:** Run the bot independently
2. **Integrated Mode:** Bot connects to dashboard for monitoring

To run the bot:
```bash
cd bot
python smart_bot.py
```

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Key Features

- **Real-time Monitoring:** WebSocket-based live updates
- **Analytics Dashboard:** Job acceptance rates, language distribution
- **Bot Control:** Start/stop bot sessions remotely
- **Session Management:** Track bot sessions and performance
- **Responsive UI:** Modern React frontend with Tailwind CSS

## 🛠️ Development

### Backend Development
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Testing
```bash
# Test backend API
curl http://localhost:8000/health

# Test bot integration
cd bot && python test_quick_check.py
```

## 📝 Notes

- The application includes both full-featured and simplified modes
- Simplified mode works without database dependencies
- All unnecessary files have been removed for cleaner structure
- APIs are properly connected between frontend and backend
- Database models are properly defined with relationships

## 🆘 Troubleshooting

1. **Import errors:** Make sure all dependencies are installed
2. **Database connection:** Check PostgreSQL is running and credentials are correct
3. **Port conflicts:** Change ports in configuration if needed
4. **Bot not starting:** Check bot configuration and permissions

## 📞 Support

For issues or questions, check the logs in the backend console or create an issue in the repository.