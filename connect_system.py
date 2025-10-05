#!/usr/bin/env python3
"""
AtoZ Bot System Integration Script
Connects Database, API, WebSocket, and Bot components
"""

import os
import sys
import time
import subprocess
import signal
import threading
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import requests
import psutil

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

class AtoZBotSystem:
    """Main system orchestrator for connecting all components"""
    
    def __init__(self):
        self.components = {
            'database': {'running': False, 'process': None, 'port': 5432},
            'redis': {'running': False, 'process': None, 'port': 6379},
            'backend': {'running': False, 'process': None, 'port': 8000},
            'frontend': {'running': False, 'process': None, 'port': 3000},
            'bot': {'running': False, 'process': None, 'port': None}
        }
        self.running = False
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def start_database(self) -> bool:
        """Start PostgreSQL database using Docker"""
        self.log("Starting PostgreSQL database...")
        
        try:
            # Check if docker-compose is available
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                self.log("Docker not found. Please install Docker first.", "ERROR")
                return False
            
            # Start database service using docker-compose
            cmd = ['docker-compose', 'up', '-d', 'database']
            process = subprocess.Popen(
                cmd,
                cwd=os.path.dirname(__file__),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.components['database']['process'] = process
            
            # Wait for database to be ready
            self.log("Waiting for database to be ready...")
            max_wait = 30
            wait_time = 0
            
            while wait_time < max_wait:
                if self.check_database_connection():
                    self.components['database']['running'] = True
                    self.log("✅ Database started successfully")
                    return True
                time.sleep(2)
                wait_time += 2
            
            self.log("❌ Database failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start database: {e}", "ERROR")
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
            
            self.components['redis']['process'] = process
            
            # Wait for Redis to be ready
            self.log("Waiting for Redis to be ready...")
            max_wait = 20
            wait_time = 0
            
            while wait_time < max_wait:
                if self.check_redis_connection():
                    self.components['redis']['running'] = True
                    self.log("✅ Redis started successfully")
                    return True
                time.sleep(1)
                wait_time += 1
            
            self.log("❌ Redis failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start Redis: {e}", "ERROR")
            return False
    
    def start_backend(self) -> bool:
        """Start FastAPI backend server"""
        self.log("Starting FastAPI backend server...")
        
        try:
            # Check if backend directory exists
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
                text=True
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
            
            self.log("❌ Backend server failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start backend: {e}", "ERROR")
            return False
    
    def start_frontend(self) -> bool:
        """Start React frontend development server"""
        self.log("Starting React frontend server...")
        
        try:
            # Check if frontend directory exists
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
            
            self.log("❌ Frontend server failed to start within timeout", "ERROR")
            return False
            
        except Exception as e:
            self.log(f"❌ Failed to start frontend: {e}", "ERROR")
            return False
    
    def start_bot(self) -> bool:
        """Start the AtoZ bot"""
        self.log("Starting AtoZ bot...")
        
        try:
            # Check if bot directory exists
            bot_dir = os.path.join(os.path.dirname(__file__), 'bot')
            if not os.path.exists(bot_dir):
                self.log("Bot directory not found", "ERROR")
                return False
            
            # Use virtual environment if available
            venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
            if not os.path.exists(venv_python):
                venv_python = 'python'  # Fallback to system python
            
            # Start bot with session ID
            session_id = f"system-session-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            cmd = [venv_python, 'integrated_bot.py', session_id]
            process = subprocess.Popen(
                cmd,
                cwd=bot_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.components['bot']['process'] = process
            self.components['bot']['session_id'] = session_id
            self.components['bot']['running'] = True
            
            self.log(f"✅ AtoZ bot started successfully with session ID: {session_id}")
            return True
            
        except Exception as e:
            self.log(f"❌ Failed to start bot: {e}", "ERROR")
            return False
    
    def check_database_connection(self) -> bool:
        """Check if PostgreSQL database is accessible"""
        try:
            import psycopg2
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
    
    def check_backend_connection(self) -> bool:
        """Check if backend API is accessible"""
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_frontend_connection(self) -> bool:
        """Check if frontend is accessible"""
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def check_websocket_connection(self) -> bool:
        """Check if WebSocket is accessible"""
        try:
            response = requests.get("http://localhost:8000/ws", timeout=5)
            return True  # WebSocket endpoint exists
        except Exception:
            return False
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        status = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'components': {},
            'overall_status': 'unknown'
        }
        
        # Check each component
        for name, component in self.components.items():
            component_status = {
                'running': component['running'],
                'process_alive': False,
                'connection_ok': False
            }
            
            # Check if process is alive
            if component['process']:
                try:
                    component_status['process_alive'] = component['process'].poll() is None
                except:
                    component_status['process_alive'] = False
            
            # Check connection
            if name == 'database':
                component_status['connection_ok'] = self.check_database_connection()
            elif name == 'redis':
                component_status['connection_ok'] = self.check_redis_connection()
            elif name == 'backend':
                component_status['connection_ok'] = self.check_backend_connection()
            elif name == 'frontend':
                component_status['connection_ok'] = self.check_frontend_connection()
            elif name == 'bot':
                component_status['connection_ok'] = component_status['process_alive']
            
            status['components'][name] = component_status
        
        # Determine overall status
        critical_components = ['database', 'backend']
        all_critical_ok = all(
            status['components'][comp]['connection_ok'] 
            for comp in critical_components
        )
        
        if all_critical_ok:
            status['overall_status'] = 'healthy'
        else:
            status['overall_status'] = 'degraded'
        
        return status
    
    def start_all(self) -> bool:
        """Start all system components"""
        self.log("🚀 Starting AtoZ Bot System...")
        self.log("=" * 50)
        
        # Start components in order
        components_to_start = [
            ('database', self.start_database),
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
        
        self.log("✅ All components stopped")
    
    def display_status(self):
        """Display current system status"""
        status = self.get_system_status()
        
        self.log("📊 System Status:")
        self.log(f"Overall Status: {status['overall_status'].upper()}")
        self.log("-" * 30)
        
        for name, component_status in status['components'].items():
            status_icon = "✅" if component_status['connection_ok'] else "❌"
            running_icon = "🟢" if component_status['running'] else "🔴"
            
            self.log(f"{status_icon} {name.upper()}: {running_icon} "
                    f"Running={component_status['running']}, "
                    f"Connected={component_status['connection_ok']}")
        
        self.log("-" * 30)
        self.log("🌐 Access URLs:")
        self.log("Frontend: http://localhost:3000")
        self.log("Backend API: http://localhost:8000")
        self.log("API Docs: http://localhost:8000/docs")
        self.log("Health Check: http://localhost:8000/health")
        self.log("WebSocket: ws://localhost:8000/ws")
    
    def monitor_system(self):
        """Monitor system and display periodic status updates"""
        self.log("🔍 Starting system monitoring...")
        
        try:
            while self.running:
                time.sleep(30)  # Check every 30 seconds
                
                if self.running:
                    self.log("📊 Periodic Status Check:")
                    status = self.get_system_status()
                    
                    # Check if any critical components are down
                    critical_down = []
                    for name in ['database', 'backend']:
                        if not status['components'][name]['connection_ok']:
                            critical_down.append(name)
                    
                    if critical_down:
                        self.log(f"⚠️ Critical components down: {', '.join(critical_down)}", "WARNING")
                    else:
                        self.log("✅ All critical components healthy")
                        
        except KeyboardInterrupt:
            self.log("Monitoring stopped by user")

def main():
    """Main function"""
    system = AtoZBotSystem()
    
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
