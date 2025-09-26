# PowerShell script to generate development SSL certificates
# This script creates self-signed certificates for local development

Write-Host "🔐 Generating development SSL certificates..." -ForegroundColor Green

# Check if OpenSSL is available
try {
    $opensslVersion = openssl version
    Write-Host "✅ OpenSSL found: $opensslVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ OpenSSL not found. Please install OpenSSL or use WSL." -ForegroundColor Red
    Write-Host "You can install OpenSSL via:" -ForegroundColor Yellow
    Write-Host "  - Chocolatey: choco install openssl" -ForegroundColor Yellow
    Write-Host "  - WSL: sudo apt-get install openssl" -ForegroundColor Yellow
    exit 1
}

# Create private key
Write-Host "Generating private key..." -ForegroundColor Blue
openssl genrsa -out key.pem 2048

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to generate private key" -ForegroundColor Red
    exit 1
}

# Generate certificate
Write-Host "Generating certificate..." -ForegroundColor Blue
openssl req -new -x509 -key key.pem -out cert.pem -days 365 `
    -subj "/C=US/ST=Development/L=Local/O=AtoZ-Bot/CN=localhost" `
    -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:0.0.0.0"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to generate certificate" -ForegroundColor Red
    exit 1
}

Write-Host "✅ SSL certificates generated successfully!" -ForegroundColor Green
Write-Host "📁 Files created:" -ForegroundColor Cyan
Write-Host "   - ssl/key.pem (private key)" -ForegroundColor White
Write-Host "   - ssl/cert.pem (certificate)" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  These are self-signed certificates for development only." -ForegroundColor Yellow
Write-Host "   For production, use certificates from a trusted CA." -ForegroundColor Yellow

