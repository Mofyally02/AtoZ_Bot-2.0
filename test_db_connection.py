#!/usr/bin/env python3
"""
Test database connection from within Docker container
"""
import os
import sys
import time
import socket

def test_hostname_resolution():
    """Test if we can resolve the database hostname"""
    print("🔍 Testing hostname resolution...")
    
    hostnames = ["database", "redis", "localhost"]
    
    for hostname in hostnames:
        try:
            ip = socket.gethostbyname(hostname)
            print(f"✅ {hostname} resolves to {ip}")
        except socket.gaierror as e:
            print(f"❌ {hostname} cannot be resolved: {e}")

def test_port_connectivity():
    """Test if we can connect to database and redis ports"""
    print("\n🔍 Testing port connectivity...")
    
    services = [
        ("database", "database", 5432),
        ("redis", "redis", 6379),
        ("localhost-db", "localhost", 5432),
        ("localhost-redis", "localhost", 6379)
    ]
    
    for name, host, port in services:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {name} ({host}:{port}) - Port is open")
            else:
                print(f"❌ {name} ({host}:{port}) - Port is closed")
        except Exception as e:
            print(f"❌ {name} ({host}:{port}) - Error: {e}")

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    env_vars = [
        "DATABASE_URL",
        "REDIS_URL", 
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        print(f"{var}: {value}")

def test_network_info():
    """Test network information"""
    print("\n🔍 Testing network information...")
    
    try:
        # Get hostname
        hostname = socket.gethostname()
        print(f"Container hostname: {hostname}")
        
        # Get IP address
        import subprocess
        result = subprocess.run(['hostname', '-i'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Container IP: {result.stdout.strip()}")
        
        # Check if we're in Docker
        if os.path.exists('/.dockerenv'):
            print("✅ Running inside Docker container")
        else:
            print("⚠️  Not running inside Docker container")
            
    except Exception as e:
        print(f"❌ Error getting network info: {e}")

def main():
    """Main test function"""
    print("🔍 Database Connection Test")
    print("=" * 40)
    
    test_environment()
    test_network_info()
    test_hostname_resolution()
    test_port_connectivity()
    
    print("\n📊 Summary:")
    print("If hostname resolution fails, the issue is with Docker networking")
    print("If port connectivity fails, the services aren't running")
    print("If environment variables are missing, check docker-compose.yml")

if __name__ == "__main__":
    main()