#!/usr/bin/env python3
"""
Simple local setup test for AtoZ Bot (no external dependencies)
"""
import os
import sys
import subprocess
import socket
from datetime import datetime

def check_docker():
    """Check if Docker is running"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker is installed and running")
            return True
        else:
            print("❌ Docker is not running")
            return False
    except FileNotFoundError:
        print("❌ Docker is not installed")
        return False

def check_docker_compose():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker Compose is available")
            return True
        else:
            print("❌ Docker Compose is not available")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose is not installed")
        return False

def check_file_structure():
    """Check if all required files exist"""
    print("\n📁 File Structure Check:")
    
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        "backend/app/main.py",
        "backend/app/database/connection.py",
        "frontend/package.json",
        "frontend/Dockerfile",
        "database/schema.sql"
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - Missing!")
            all_files_exist = False
    
    return all_files_exist

def check_environment():
    """Check environment variables and configuration"""
    print("\n🔧 Environment Check:")
    
    # Check if we're in the right directory
    if os.path.exists("docker-compose.yml"):
        print("✅ In correct project directory")
    else:
        print("❌ Not in project directory")
        return False
    
    # Check Python version
    python_version = sys.version_info
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    return True

def check_docker_services():
    """Check if Docker services are running"""
    print("\n🐳 Docker Services Check:")
    
    try:
        # Check if containers are running
        result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
        if result.returncode == 0:
            output = result.stdout
            if 'atoz-bot-app' in output:
                print("✅ AtoZ Bot app container is running")
            else:
                print("⚠️  AtoZ Bot app container is not running")
            
            if 'atoz-database' in output:
                print("✅ PostgreSQL database container is running")
            else:
                print("⚠️  PostgreSQL database container is not running")
            
            if 'atoz-redis' in output:
                print("✅ Redis container is running")
            else:
                print("⚠️  Redis container is not running")
        else:
            print("❌ Could not check Docker containers")
            return False
    except Exception as e:
        print(f"❌ Error checking Docker services: {e}")
        return False
    
    return True

def check_ports():
    """Check if ports are accessible"""
    print("\n🌐 Port Check:")
    
    ports_to_check = [
        ("Backend API", "localhost", 8000),
        ("Frontend", "localhost", 3000),
        ("PostgreSQL", "localhost", 5432),
        ("Redis", "localhost", 6379),
    ]
    
    all_ports_open = True
    for service, host, port in ports_to_check:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✅ {service}: {host}:{port} - Open")
            else:
                print(f"❌ {service}: {host}:{port} - Closed")
                all_ports_open = False
        except Exception as e:
            print(f"❌ {service}: {host}:{port} - Error: {e}")
            all_ports_open = False
    
    return all_ports_open

def start_services():
    """Start Docker services"""
    print("\n🚀 Starting Docker Services:")
    
    try:
        # Start services in background
        result = subprocess.run(['docker-compose', 'up', '-d'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Docker services started successfully")
            print("⏳ Waiting for services to be ready...")
            import time
            time.sleep(15)  # Wait for services to start
            return True
        else:
            print(f"❌ Failed to start services: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error starting services: {e}")
        return False

def check_docker_compose_config():
    """Check docker-compose.yml configuration"""
    print("\n📋 Docker Compose Configuration Check:")
    
    try:
        # Check if docker-compose.yml is valid
        result = subprocess.run(['docker-compose', 'config'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ docker-compose.yml is valid")
            return True
        else:
            print(f"❌ docker-compose.yml has errors: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error checking docker-compose.yml: {e}")
        return False

def main():
    """Main test function"""
    print("🔍 AtoZ Bot Local Setup Test")
    print("=" * 50)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check prerequisites
    docker_ok = check_docker()
    compose_ok = check_docker_compose()
    env_ok = check_environment()
    files_ok = check_file_structure()
    config_ok = check_docker_compose_config()
    
    if not all([docker_ok, compose_ok, env_ok, files_ok, config_ok]):
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return 1
    
    # Start services if not running
    print("\n🚀 Starting Services...")
    if start_services():
        print("✅ Services started")
    else:
        print("❌ Failed to start services")
        return 1
    
    # Check running services
    services_ok = check_docker_services()
    ports_ok = check_ports()
    
    print("\n📊 Summary:")
    if all([services_ok, ports_ok]):
        print("🎉 Everything is running correctly!")
        print("\n🌐 Access your application:")
        print("  - Backend API: http://localhost:8000")
        print("  - Frontend: http://localhost:3000")
        print("  - Health Check: http://localhost:8000/health")
        print("\n📝 Useful commands:")
        print("  - View logs: docker-compose logs -f")
        print("  - Stop services: docker-compose down")
        print("  - Restart: docker-compose restart")
        return 0
    else:
        print("⚠️  Some issues found. Check the details above.")
        print("\n💡 Troubleshooting:")
        print("  - Check logs: docker-compose logs -f")
        print("  - Restart services: docker-compose restart")
        print("  - Stop and start: docker-compose down && docker-compose up -d")
        return 1

if __name__ == "__main__":
    sys.exit(main())
