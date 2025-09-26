# AtoZ Bot Dashboard Development Setup Script for PowerShell
# This script sets up the development environment on Windows

param(
    [switch]$SkipSSL,
    [switch]$Force
)

# Colors for output
$Red = "Red"
$Green = "Green"
$Yellow = "Yellow"
$Blue = "Blue"

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor $Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor $Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor $Red
}

Write-Host "🚀 Setting up AtoZ Bot Dashboard for development..." -ForegroundColor $Green

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Success "Docker found: $dockerVersion"
} catch {
    Write-Error "Docker is not installed. Please install Docker Desktop first."
    exit 1
}

# Check if Docker Compose is installed
try {
    $composeVersion = docker-compose --version
    Write-Success "Docker Compose found: $composeVersion"
} catch {
    Write-Error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
}

# Create necessary directories
Write-Status "Creating necessary directories..."
$directories = @("logs/nginx", "logs/bot", "data/postgres", "data/redis", "backups")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Success "Created directory: $dir"
    } else {
        Write-Status "Directory already exists: $dir"
    }
}

# Generate SSL certificates for development
if (!$SkipSSL) {
    Write-Status "Generating SSL certificates for development..."
    if (Test-Path "ssl/generate-dev-certs.ps1") {
        try {
            & "ssl/generate-dev-certs.ps1"
            Write-Success "SSL certificates generated successfully"
        } catch {
            Write-Warning "Failed to generate SSL certificates. Creating placeholder certificates..."
            if (!(Test-Path "ssl")) {
                New-Item -ItemType Directory -Path "ssl" -Force | Out-Null
            }
            "placeholder" | Out-File -FilePath "ssl/cert.pem" -Encoding UTF8
            "placeholder" | Out-File -FilePath "ssl/key.pem" -Encoding UTF8
            Write-Warning "Please replace placeholder certificates with real ones for production."
        }
    } else {
        Write-Warning "SSL certificate generation script not found. Creating placeholder certificates..."
        if (!(Test-Path "ssl")) {
            New-Item -ItemType Directory -Path "ssl" -Force | Out-Null
        }
        "placeholder" | Out-File -FilePath "ssl/cert.pem" -Encoding UTF8
        "placeholder" | Out-File -FilePath "ssl/key.pem" -Encoding UTF8
        Write-Warning "Please replace placeholder certificates with real ones for production."
    }
} else {
    Write-Status "Skipping SSL certificate generation"
}

# Create .env file if it doesn't exist
if (!(Test-Path ".env") -or $Force) {
    Write-Status "Creating .env file from template..."
    if (Test-Path "env.template") {
        Copy-Item "env.template" ".env"
        Write-Success ".env file created from template"
        Write-Warning "Please update .env file with your actual configuration values."
    } else {
        Write-Error "Environment template not found. Please create .env file manually."
        exit 1
    }
} else {
    Write-Status ".env file already exists, skipping creation."
}

# Build and start services
Write-Status "Building and starting services..."
try {
    docker-compose up -d --build
    Write-Success "Services started successfully"
} catch {
    Write-Error "Failed to start services. Check Docker logs for details."
    exit 1
}

# Wait for services to be ready
Write-Status "Waiting for services to be ready..."
Start-Sleep -Seconds 15

# Check if services are running
Write-Status "Checking service health..."

# Check database
try {
    $dbCheck = docker-compose exec -T database pg_isready -U atoz_user -d atoz_bot_db 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Database is ready"
    } else {
        Write-Warning "Database might not be ready yet"
    }
} catch {
    Write-Warning "Could not check database status"
}

# Check Redis
try {
    $redisCheck = docker-compose exec -T redis redis-cli ping 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Redis is ready"
    } else {
        Write-Warning "Redis might not be ready yet"
    }
} catch {
    Write-Warning "Could not check Redis status"
}

# Check backend
try {
    $backendCheck = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5 -UseBasicParsing
    if ($backendCheck.StatusCode -eq 200) {
        Write-Success "Backend is ready"
    } else {
        Write-Warning "Backend might not be ready yet"
    }
} catch {
    Write-Warning "Backend might not be ready yet"
}

# Check frontend
try {
    $frontendCheck = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    if ($frontendCheck.StatusCode -eq 200) {
        Write-Success "Frontend is ready"
    } else {
        Write-Warning "Frontend might not be ready yet"
    }
} catch {
    Write-Warning "Frontend might not be ready yet"
}

Write-Success "Setup completed!"
Write-Host ""
Write-Host "🌐 Access your application:" -ForegroundColor $Green
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor $Blue
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor $Blue
Write-Host "   API Documentation: http://localhost:8000/docs" -ForegroundColor $Blue
Write-Host ""
Write-Host "📊 Useful commands:" -ForegroundColor $Green
Write-Host "   View logs: docker-compose logs -f" -ForegroundColor $Blue
Write-Host "   Stop services: docker-compose down" -ForegroundColor $Blue
Write-Host "   Restart services: docker-compose restart" -ForegroundColor $Blue
Write-Host "   Update services: docker-compose up -d --build" -ForegroundColor $Blue
Write-Host ""
Write-Host "🔧 Development commands:" -ForegroundColor $Green
Write-Host "   Backend only: cd backend && python main.py" -ForegroundColor $Blue
Write-Host "   Frontend only: cd frontend && npm run dev" -ForegroundColor $Blue
Write-Host "   Bot only: cd bot && python persistent_bot.py" -ForegroundColor $Blue
Write-Host ""
Write-Warning "Don't forget to update your .env file with actual credentials!"

