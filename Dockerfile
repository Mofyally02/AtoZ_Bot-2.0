FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY bot/ ./bot/
COPY database/ ./database/

# PostgreSQL is handled by docker-compose service

# Set Python path
ENV PYTHONPATH=/app/backend

# Create non-root user
RUN useradd -m -u 1000 atoz && chown -R atoz:atoz /app
USER atoz

# Expose port
EXPOSE 8000

# Health check with better error handling
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/health || exit 1

# Change to backend directory and start
WORKDIR /app/backend

# Create startup script with delay
RUN echo '#!/bin/bash\n\
echo "⏳ Waiting for database to be ready..."\n\
sleep 10\n\
echo "🚀 Starting AtoZ Bot backend..."\n\
exec uvicorn app.main:app --host 0.0.0.0 --port 8000' > /app/start.sh && \
    chmod +x /app/start.sh

CMD ["/app/start.sh"]
