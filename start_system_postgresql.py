#!/usr/bin/env python3
"""
AtoZ Bot System - PostgreSQL Startup Script
Starts system with PostgreSQL database using Docker
"""

import os
import sys
import time
import subprocess
import signal
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Optional psycopg2 import
try:
    import psycopg2
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

class AtoZBotSystemPostgreSQL:
    """PostgreSQL system orchestrator"""
    
    def __init__(self):
        self.components = {
            'database': {'running': False, 'process': None},
            'redis': {'running': False, 'process': None},
            'backend': {'running': False, 'process': None, 'port': 8000},
            'frontend': {'running': False, 'process': None, 'port': 3000},
            'bot': {'running': False, 'process': None, 'port': None}
        }
        self.running = False
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_docker_available(self) -> bool:
        """Check if Docker is available and accessible"""
        self.log("Checking Docker availability...")
        
        try:
            # Test Docker without sudo
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("✅ Docker is available")
                return True
            else:
                self.log("❌ Docker command failed", "ERROR")
                return False
        except FileNotFoundError:
            self.log("❌ Docker not found. Please install Docker.", "ERROR")
            return False
        except PermissionError:
            self.log("❌ Docker permission denied. Adding user to docker group...", "WARNING")
            return self.setup_docker_permissions()
    
    def setup_docker_permissions(self) -> bool:
        """Setup Docker permissions for current user"""
        try:
            # Add user to docker group
            username = os.getenv('USER', 'user')
            self.log(f"Adding user {username} to docker group...")
            
            # This requires sudo, so we'll provide instructions
            self.log("⚠️ Please run the following commands to fix Docker permissions:", "WARNING")
            self.log("sudo usermod -aG docker $USER", "WARNING")
            self.log("newgrp docker", "WARNING")
            self.log("Then restart this script.", "WARNING")
            
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to setup Docker permissions: {e}", "ERROR")
            return False
    
    def start_postgresql(self) -> bool:
        """Start PostgreSQL using Docker"""
        self.log("Starting PostgreSQL database...")
        
        try:
            # Start PostgreSQL service using docker-compose
            cmd = ['docker-compose', 'up', '-d', 'database']
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(__file__),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.log(f"❌ Failed to start PostgreSQL: {stderr}", "ERROR")
                return False
            
            self.components['database']['process'] = process
            
            # Wait for PostgreSQL to be ready
            self.log("Waiting for PostgreSQL to be ready...")
            max_wait = 60  # Increased timeout
            wait_time = 0
            
            while wait_time < max_wait:
                if self.check_postgresql_connection():
                    self.components['database']['running'] = True
                    self.log("✅ PostgreSQL started successfully")
                    return True
                time.sleep(3)
                wait_time += 3
                self.log(f"⏳ Waiting for PostgreSQL... ({wait_time}/{max_wait}s)")
            
            self.log("❌ PostgreSQL failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start PostgreSQL: {e}", "ERROR")
            return False
    
    def start_redis(self) -> bool:
        """Start Redis using Docker"""
        self.log("Starting Redis cache...")
        
        try:
            # Start Redis service using docker-compose
            cmd = ['docker-compose', 'up', '-d', 'redis']
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(__file__),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                self.log(f"❌ Failed to start Redis: {stderr}", "ERROR")
                return False
            
            self.components['redis']['process'] = process
            
            # Wait for Redis to be ready
            self.log("Waiting for Redis to be ready...")
            max_wait = 30
            wait_time = 0
            
            while wait_time < max_wait:
                if self.check_redis_connection():
                    self.components['redis']['running'] = True
                    self.log("✅ Redis started successfully")
                    return True
                time.sleep(2)
                wait_time += 2
                self.log(f"⏳ Waiting for Redis... ({wait_time}/{max_wait}s)")
            
            self.log("❌ Redis failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start Redis: {e}", "ERROR")
            return False
    
    def check_postgresql_connection(self) -> bool:
        """Check if PostgreSQL is accessible"""
        if not PSYCOPG2_AVAILABLE:
            # Fallback: check if port is open
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', 5432))
                sock.close()
                return result == 0
            except Exception:
                return False
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="atoz_bot_db",
                user="atoz_user",
                password="atoz_password"
            )
            conn.close()
            return True
        except Exception:
            return False
    
    def check_redis_connection(self) -> bool:
        """Check if Redis is accessible"""
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            return True
        except Exception:
            return False
    
    def start_backend(self) -> bool:
        """Start FastAPI backend server"""
        self.log("Starting FastAPI backend server...")
        
        try:
            # Set environment variables for PostgreSQL
            env = os.environ.copy()
            env.update({
                'DATABASE_URL': 'postgresql://atoz_user:atoz_password@localhost:5432/atoz_bot_db',
                'REDIS_URL': 'redis://localhost:6379',
                'PYTHONPATH': os.path.join(os.path.dirname(__file__), 'backend')
            })
            
            backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
            if not os.path.exists(backend_dir):
                self.log("Backend directory not found", "ERROR")
                return False
            
            # Use virtual environment if available
            venv_python = os.path.join(backend_dir, 'venv', 'bin', 'python')
            if not os.path.exists(venv_python):
                venv_python = 'python'  # Fallback to system python
            
            # Start backend server
            cmd = [venv_python, '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload']
            process = subprocess.Popen(
                cmd,
                cwd=backend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            self.components['backend']['process'] = process
            
            # Wait for backend to be ready
            self.log("Waiting for backend server to be ready...")
            max_wait = 30
            wait_time = 0
            
            while wait_time < max_wait:
                if self.check_backend_connection():
                    self.components['backend']['running'] = True
                    self.log("✅ Backend server started successfully")
                    return True
                time.sleep(2)
                wait_time += 2
                self.log(f"⏳ Waiting for backend... ({wait_time}/{max_wait}s)")
            
            self.log("❌ Backend server failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start backend: {e}", "ERROR")
            return False
    
    def start_frontend(self) -> bool:
        """Start React frontend development server"""
        self.log("Starting React frontend server...")
        
        try:
            frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
            if not os.path.exists(frontend_dir):
                self.log("Frontend directory not found", "ERROR")
                return False
            
            # Check if node_modules exists
            node_modules = os.path.join(frontend_dir, 'node_modules')
            if not os.path.exists(node_modules):
                self.log("Installing frontend dependencies...")
                install_cmd = ['npm', 'install']
                install_process = subprocess.run(
                    install_cmd,
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True
                )
                if install_process.returncode != 0:
                    self.log(f"Failed to install dependencies: {install_process.stderr}", "ERROR")
                    return False
            
            # Start frontend development server
            cmd = ['npm', 'run', 'dev', '--', '--host', '0.0.0.0', '--port', '3000']
            process = subprocess.Popen(
                cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.components['frontend']['process'] = process
            
            # Wait for frontend to be ready
            self.log("Waiting for frontend server to be ready...")
            max_wait = 30
            wait_time = 0
            
            while wait_time < max_wait:
                if self.check_frontend_connection():
                    self.components['frontend']['running'] = True
                    self.log("✅ Frontend server started successfully")
                    return True
                time.sleep(2)
                wait_time += 2
                self.log(f"⏳ Waiting for frontend... ({wait_time}/{max_wait}s)")
            
            self.log("❌ Frontend server failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start frontend: {e}", "ERROR")
            return False
    
    def start_bot(self) -> bool:
        """Start the AtoZ bot"""
        self.log("Starting AtoZ bot...")
        
        try:
            bot_dir = os.path.join(os.path.dirname(__file__), 'bot')
            if not os.path.exists(bot_dir):
                self.log("Bot directory not found", "ERROR")
                return False
            
            # Use virtual environment if available
            venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
            if not os.path.exists(venv_python):
                venv_python = 'python'  # Fallback to system python
            
            # Set environment variables for bot
            env = os.environ.copy()
            env.update({
                'DATABASE_URL': 'postgresql://atoz_user:atoz_password@localhost:5432/atoz_bot_db',
                'REDIS_URL': 'redis://localhost:6379',
                'API_BASE_URL': 'http://localhost:8000'
            })
            
            # Start bot with session ID
            session_id = f"postgresql-session-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cmd = [venv_python, 'integrated_bot.py', session_id]
            process = subprocess.Popen(
                cmd,
                cwd=bot_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            
            self.components['bot']['process'] = process
            self.components['bot']['session_id'] = session_id
            self.components['bot']['running'] = True
            
            self.log(f"✅ AtoZ bot started successfully with session ID: {session_id}")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start bot: {e}", "ERROR")
            return False
    
    def check_backend_connection(self) -> bool:
        """Check if backend API is accessible"""
        try:
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_frontend_connection(self) -> bool:
        """Check if frontend is accessible"""
        try:
            import requests
            response = requests.get("http://localhost:3000", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def start_all(self) -> bool:
        """Start all system components"""
        self.log("🚀 Starting AtoZ Bot System (PostgreSQL Mode)...")
        self.log("=" * 50)
        
        # Check Docker availability first
        if not self.check_docker_available():
            self.log("❌ Docker is not available. Cannot start PostgreSQL and Redis.", "ERROR")
            self.log("Please install Docker and ensure your user has permission to access it.", "ERROR")
            return False
        
        # Start components in order
        components_to_start = [
            ('database', self.start_postgresql),
            ('redis', self.start_redis),
            ('backend', self.start_backend),
            ('frontend', self.start_frontend),
            ('bot', self.start_bot)
        ]
        
        for name, start_func in components_to_start:
            self.log(f"Starting {name}...")
            if not start_func():
                self.log(f"❌ Failed to start {name}. Stopping system.", "ERROR")
                self.stop_all()
                return False
            time.sleep(2)  # Brief pause between components
        
        self.running = True
        self.log("✅ All components started successfully!")
        self.log("=" * 50)
        
        # Display system status
        self.display_status()
        
        return True
    
    def stop_component(self, name: str):
        """Stop a specific component"""
        component = self.components[name]
        
        if component['process']:
            try:
                self.log(f"Stopping {name}...")
                component['process'].terminate()
                
                # Wait for graceful shutdown
                try:
                    component['process'].wait(timeout=10)
                except subprocess.TimeoutExpired:
                    self.log(f"Force killing {name}...", "WARNING")
                    component['process'].kill()
                
                component['process'] = None
                component['running'] = False
                self.log(f"✅ {name} stopped")
                
            except Exception as e:
                self.log(f"❌ Error stopping {name}: {e}", "ERROR")
    
    def stop_all(self):
        """Stop all system components"""
        self.log("🛑 Stopping AtoZ Bot System...")
        self.running = False
        
        # Stop components in reverse order
        components_to_stop = ['bot', 'frontend', 'backend', 'redis', 'database']
        
        for name in components_to_stop:
            self.stop_component(name)
        
        # Stop Docker services
        try:
            self.log("Stopping Docker services...")
            subprocess.run(['docker-compose', 'down'], cwd=os.path.dirname(__file__))
            self.log("✅ Docker services stopped")
        except Exception as e:
            self.log(f"⚠️ Error stopping Docker services: {e}", "WARNING")
        
        self.log("✅ All components stopped")
    
    def display_status(self):
        """Display current system status"""
        self.log("📊 System Status:")
        self.log("-" * 30)
        
        for name, component_status in self.components.items():
            running_icon = "🟢" if component_status['running'] else "🔴"
            self.log(f"{running_icon} {name.upper()}: {'Running' if component_status['running'] else 'Stopped'}")
        
        self.log("-" * 30)
        self.log("🌐 Access URLs:")
        self.log("Frontend: http://localhost:3000")
        self.log("Backend API: http://localhost:8000")
        self.log("API Docs: http://localhost:8000/docs")
        self.log("Health Check: http://localhost:8000/health")
        self.log("WebSocket: ws://localhost:8000/ws")
        self.log("Database: PostgreSQL (localhost:5432)")
        self.log("Redis: localhost:6379")
    
    def monitor_system(self):
        """Monitor system and display periodic status updates"""
        self.log("🔍 Starting system monitoring...")
        
        try:
            while self.running:
                time.sleep(30)  # Check every 30 seconds
                
                if self.running:
                    self.log("📊 Periodic Status Check:")
                    
                    # Check database
                    if not self.check_postgresql_connection():
                        self.log("⚠️ PostgreSQL is not responding", "WARNING")
                    else:
                        self.log("✅ PostgreSQL is healthy")
                    
                    # Check Redis
                    if not self.check_redis_connection():
                        self.log("⚠️ Redis is not responding", "WARNING")
                    else:
                        self.log("✅ Redis is healthy")
                    
                    # Check backend
                    if not self.check_backend_connection():
                        self.log("⚠️ Backend API is not responding", "WARNING")
                    else:
                        self.log("✅ Backend API is healthy")
                    
                    # Check frontend
                    if not self.check_frontend_connection():
                        self.log("⚠️ Frontend is not responding", "WARNING")
                    else:
                        self.log("✅ Frontend is healthy")
                        
        except KeyboardInterrupt:
            self.log("Monitoring stopped by user")

def main():
    """Main function"""
    system = AtoZBotSystemPostgreSQL()
    
    def signal_handler(sig, frame):
        print("\n🛑 Received interrupt signal. Shutting down...")
        system.stop_all()
        sys.exit(0)
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start all components
        if system.start_all():
            # Start monitoring in a separate thread
            monitor_thread = threading.Thread(target=system.monitor_system, daemon=True)
            monitor_thread.start()
            
            # Keep main thread alive
            try:
                while system.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        
    except Exception as e:
        system.log(f"❌ System error: {e}", "ERROR")
    finally:
        system.stop_all()

if __name__ == "__main__":
    main()
