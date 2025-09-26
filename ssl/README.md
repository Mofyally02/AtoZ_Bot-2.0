# SSL Certificates Directory

This directory contains SSL certificates for HTTPS configuration.

## Development Setup

For development, you can generate self-signed certificates:

```bash
# Generate private key
openssl genrsa -out key.pem 2048

# Generate certificate
openssl req -new -x509 -key key.pem -out cert.pem -days 365 -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

## Production Setup

For production, replace these files with your actual SSL certificates:

- `cert.pem` - Your SSL certificate
- `key.pem` - Your private key

## Security Note

⚠️ **Never commit real SSL certificates to version control!**

Add this directory to your `.gitignore`:
```
ssl/*.pem
ssl/*.crt
ssl/*.key
```

## File Structure

```
ssl/
├── README.md          # This file
├── cert.pem          # SSL certificate (replace with real cert)
└── key.pem           # Private key (replace with real key)
```

## Docker Usage

The nginx container will automatically use these certificates when configured with the docker-compose.yml file.

