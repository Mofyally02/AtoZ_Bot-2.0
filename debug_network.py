#!/usr/bin/env python3
"""
Network debugging script for AtoZ Bot
"""
import os
import sys
import socket
import time
from datetime import datetime

def check_port(host, port, timeout=5):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except Exception as e:
        print(f"Error checking {host}:{port} - {e}")
        return False

def check_dns_resolution(hostname):
    """Check if hostname resolves"""
    try:
        ip = socket.gethostbyname(hostname)
        return True, ip
    except Exception as e:
        return False, str(e)

def main():
    print("🔍 AtoZ Bot Network Debugging")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check environment
    print("📋 Environment Variables:")
    print(f"  DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"  REDIS_URL: {os.getenv('REDIS_URL', 'Not set')}")
    print(f"  PYTHONPATH: {os.getenv('PYTHONPATH', 'Not set')}")
    print()
    
    # Check local ports
    print("🌐 Local Port Check:")
    ports_to_check = [
        ("Backend API", "localhost", 8000),
        ("Frontend", "localhost", 3000),
        ("Database", "localhost", 5432),
        ("Redis", "localhost", 6379),
    ]
    
    for service, host, port in ports_to_check:
        if check_port(host, port):
            print(f"✅ {service}: {host}:{port} - Open")
        else:
            print(f"❌ {service}: {host}:{port} - Closed/Filtered")
    
    print()
    
    # Check Docker service resolution
    print("🐳 Docker Service Resolution:")
    docker_services = ["redis", "database", "app"]
    
    for service in docker_services:
        resolved, result = check_dns_resolution(service)
        if resolved:
            print(f"✅ {service}: {result}")
        else:
            print(f"❌ {service}: {result}")
    
    print()
    
    # Check file permissions
    print("📁 File Permissions:")
    important_files = [
        "backend/app/main.py",
        "backend/app/database/connection.py",
        "frontend/Dockerfile",
        "Dockerfile",
        "docker-compose.yml"
    ]
    
    for file_path in important_files:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            print(f"✅ {file_path} - Readable")
        else:
            print(f"❌ {file_path} - Missing")
    
    print()
    
    # Recommendations
    print("💡 Recommendations:")
    print("1. Ensure all services are running: docker-compose up -d")
    print("2. Check logs: docker-compose logs -f")
    print("3. Verify network: docker network ls")
    print("4. Test connectivity: docker exec -it <container> ping <service>")
    print("5. Check firewall settings if using external access")

if __name__ == "__main__":
    main()
