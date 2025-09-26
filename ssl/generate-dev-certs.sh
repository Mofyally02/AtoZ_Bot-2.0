#!/bin/bash

# Generate development SSL certificates
# This script creates self-signed certificates for local development

echo "🔐 Generating development SSL certificates..."

# Create private key
echo "Generating private key..."
openssl genrsa -out key.pem 2048

# Generate certificate
echo "Generating certificate..."
openssl req -new -x509 -key key.pem -out cert.pem -days 365 \
    -subj "/C=US/ST=Development/L=Local/O=AtoZ-Bot/CN=localhost" \
    -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:0.0.0.0"

echo "✅ SSL certificates generated successfully!"
echo "📁 Files created:"
echo "   - ssl/key.pem (private key)"
echo "   - ssl/cert.pem (certificate)"
echo ""
echo "⚠️  These are self-signed certificates for development only."
echo "   For production, use certificates from a trusted CA."

