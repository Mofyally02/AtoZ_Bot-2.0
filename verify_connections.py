#!/usr/bin/env python3
"""
Connection Verification Script for AtoZ Bot System
Verifies all component connections and provides detailed status
"""

import os
import sys
import time
import requests
import json
import psycopg2
import redis
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

class ConnectionVerifier:
    """Verifies all system component connections"""
    
    def __init__(self):
        self.verification_results = {}
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def verify_database_connection(self) -> Dict[str, Any]:
        """Verify PostgreSQL database connection and schema"""
        self.log("🔍 Verifying database connection...")
        
        result = {
            'connected': False,
            'tables_exist': False,
            'can_read': False,
            'can_write': False,
            'error': None
        }
        
        try:
            # Test connection
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="atoz_bot_db",
                user="atoz_user",
                password="atoz_password"
            )
            result['connected'] = True
            self.log("✅ Database connection established")
            
            cursor = conn.cursor()
            
            # Test read operation
            cursor.execute("SELECT 1")
            cursor.fetchone()
            result['can_read'] = True
            self.log("✅ Database read operation successful")
            
            # Test write operation
            cursor.execute("""
                INSERT INTO bot_sessions (session_name, status, login_status)
                VALUES ('connection-test', 'testing', 'success')
                RETURNING id;
            """)
            session_id = cursor.fetchone()[0]
            result['can_write'] = True
            self.log("✅ Database write operation successful")
            
            # Clean up test data
            cursor.execute("DELETE FROM bot_sessions WHERE id = %s", (session_id,))
            conn.commit()
            
            # Check required tables
            required_tables = [
                'bot_sessions',
                'job_records', 
                'analytics_periods',
                'bot_configurations',
                'system_logs'
            ]
            
            missing_tables = []
            for table in required_tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table,))
                
                if not cursor.fetchone()[0]:
                    missing_tables.append(table)
            
            if not missing_tables:
                result['tables_exist'] = True
                self.log("✅ All required database tables exist")
            else:
                self.log(f"❌ Missing database tables: {missing_tables}", "ERROR")
                result['error'] = f"Missing tables: {missing_tables}"
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            self.log(f"❌ Database verification failed: {e}", "ERROR")
            result['error'] = str(e)
        
        return result
    
    def verify_redis_connection(self) -> Dict[str, Any]:
        """Verify Redis connection and operations"""
        self.log("🔍 Verifying Redis connection...")
        
        result = {
            'connected': False,
            'can_read': False,
            'can_write': False,
            'error': None
        }
        
        try:
            # Test connection
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            result['connected'] = True
            self.log("✅ Redis connection established")
            
            # Test write operation
            r.set("connection_test", "test_value")
            result['can_write'] = True
            self.log("✅ Redis write operation successful")
            
            # Test read operation
            value = r.get("connection_test")
            if value == "test_value":
                result['can_read'] = True
                self.log("✅ Redis read operation successful")
            else:
                self.log("❌ Redis read operation failed", "ERROR")
                result['error'] = "Read operation returned incorrect value"
            
            # Clean up test data
            r.delete("connection_test")
            
        except Exception as e:
            self.log(f"❌ Redis verification failed: {e}", "ERROR")
            result['error'] = str(e)
        
        return result
    
    def verify_backend_api(self) -> Dict[str, Any]:
        """Verify backend API endpoints"""
        self.log("🔍 Verifying backend API...")
        
        result = {
            'health_endpoint': False,
            'detailed_health': False,
            'bot_endpoints': False,
            'websocket_endpoint': False,
            'error': None
        }
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                result['health_endpoint'] = True
                health_data = response.json()
                self.log(f"✅ Health endpoint working: {health_data.get('status', 'unknown')}")
            else:
                self.log(f"❌ Health endpoint failed: {response.status_code}", "ERROR")
                result['error'] = f"Health endpoint returned {response.status_code}"
                return result
            
            # Test detailed health endpoint
            response = requests.get(f"{self.base_url}/health/detailed", timeout=10)
            if response.status_code == 200:
                result['detailed_health'] = True
                detailed_health = response.json()
                self.log("✅ Detailed health endpoint working")
                
                # Log service statuses
                services = detailed_health.get('services', {})
                for service, status in services.items():
                    status_val = status.get('status', 'unknown')
                    icon = "✅" if status_val == 'healthy' else "❌"
                    self.log(f"  {icon} {service}: {status_val}")
            else:
                self.log(f"⚠️ Detailed health endpoint failed: {response.status_code}", "WARNING")
            
            # Test bot endpoints
            bot_endpoints = [
                '/api/bot/status',
                '/api/bot/dashboard/metrics',
                '/api/bot/configuration'
            ]
            
            bot_endpoints_working = 0
            for endpoint in bot_endpoints:
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    if response.status_code == 200:
                        bot_endpoints_working += 1
                        self.log(f"✅ {endpoint} working")
                    else:
                        self.log(f"⚠️ {endpoint} returned {response.status_code}", "WARNING")
                except Exception as e:
                    self.log(f"⚠️ {endpoint} failed: {e}", "WARNING")
            
            if bot_endpoints_working >= 2:  # At least 2 out of 3 endpoints working
                result['bot_endpoints'] = True
                self.log("✅ Bot endpoints working")
            else:
                self.log("❌ Bot endpoints not working properly", "ERROR")
                result['error'] = f"Only {bot_endpoints_working}/3 bot endpoints working"
            
            # Test WebSocket endpoint (basic check)
            try:
                response = requests.get(f"{self.base_url}/ws", timeout=5)
                result['websocket_endpoint'] = True
                self.log("✅ WebSocket endpoint available")
            except Exception as e:
                self.log(f"⚠️ WebSocket endpoint check failed: {e}", "WARNING")
            
        except Exception as e:
            self.log(f"❌ Backend API verification failed: {e}", "ERROR")
            result['error'] = str(e)
        
        return result
    
    def verify_frontend_connection(self) -> Dict[str, Any]:
        """Verify frontend connection"""
        self.log("🔍 Verifying frontend connection...")
        
        result = {
            'connected': False,
            'error': None
        }
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                result['connected'] = True
                self.log("✅ Frontend connection successful")
            else:
                self.log(f"❌ Frontend connection failed: {response.status_code}", "ERROR")
                result['error'] = f"HTTP {response.status_code}"
                
        except Exception as e:
            self.log(f"❌ Frontend connection failed: {e}", "ERROR")
            result['error'] = str(e)
        
        return result
    
    def verify_websocket_connection(self) -> Dict[str, Any]:
        """Verify WebSocket connection"""
        self.log("🔍 Verifying WebSocket connection...")
        
        result = {
            'connected': False,
            'message_received': False,
            'error': None
        }
        
        try:
            import websocket
            
            ws_url = "ws://localhost:8000/ws"
            received_message = False
            
            def on_message(ws, message):
                nonlocal received_message
                received_message = True
                self.log(f"✅ Received WebSocket message: {message[:100]}...")
                ws.close()
            
            def on_error(ws, error):
                self.log(f"❌ WebSocket error: {error}", "ERROR")
                result['error'] = str(error)
            
            def on_close(ws, close_status_code, close_msg):
                self.log("WebSocket connection closed")
            
            def on_open(ws):
                self.log("✅ WebSocket connection established")
                result['connected'] = True
            
            ws = websocket.WebSocketApp(
                ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket for 5 seconds
            ws.run_forever(timeout=5)
            
            if received_message:
                result['message_received'] = True
                self.log("✅ WebSocket test successful")
            else:
                self.log("❌ No WebSocket message received", "ERROR")
                result['error'] = "No message received"
                
        except ImportError:
            self.log("⚠️ websocket-client not installed, skipping WebSocket test", "WARNING")
            result['error'] = "websocket-client not installed"
        except Exception as e:
            self.log(f"❌ WebSocket verification failed: {e}", "ERROR")
            result['error'] = str(e)
        
        return result
    
    def verify_bot_integration(self) -> Dict[str, Any]:
        """Verify bot integration with API"""
        self.log("🔍 Verifying bot integration...")
        
        result = {
            'toggle_works': False,
            'status_check_works': False,
            'metrics_available': False,
            'error': None
        }
        
        try:
            # Test bot toggle endpoint
            response = requests.post(f"{self.base_url}/api/bot/toggle", timeout=10)
            if response.status_code == 200:
                result['toggle_works'] = True
                toggle_result = response.json()
                self.log(f"✅ Bot toggle endpoint working: {toggle_result}")
                
                # Wait a moment and check status
                time.sleep(2)
                status_response = requests.get(f"{self.base_url}/api/bot/status", timeout=10)
                if status_response.status_code == 200:
                    result['status_check_works'] = True
                    status = status_response.json()
                    self.log(f"✅ Bot status check working: {status.get('is_running', False)}")
                
                # Test metrics endpoint
                metrics_response = requests.get(f"{self.base_url}/api/bot/dashboard/metrics", timeout=10)
                if metrics_response.status_code == 200:
                    result['metrics_available'] = True
                    self.log("✅ Bot metrics endpoint working")
                
                # Toggle bot back off
                time.sleep(2)
                requests.post(f"{self.base_url}/api/bot/toggle", timeout=10)
                
            else:
                self.log(f"❌ Bot toggle endpoint failed: {response.status_code}", "ERROR")
                result['error'] = f"Toggle endpoint returned {response.status_code}"
                
        except Exception as e:
            self.log(f"❌ Bot integration verification failed: {e}", "ERROR")
            result['error'] = str(e)
        
        return result
    
    def run_verification(self) -> Dict[str, Dict[str, Any]]:
        """Run all connection verifications"""
        self.log("🔍 Starting Connection Verification")
        self.log("=" * 50)
        
        verifications = [
            ("Database", self.verify_database_connection),
            ("Redis", self.verify_redis_connection),
            ("Backend API", self.verify_backend_api),
            ("Frontend", self.verify_frontend_connection),
            ("WebSocket", self.verify_websocket_connection),
            ("Bot Integration", self.verify_bot_integration)
        ]
        
        results = {}
        
        for name, verify_func in verifications:
            self.log(f"\n🔍 Verifying: {name}")
            self.log("-" * 30)
            
            try:
                result = verify_func()
                results[name] = result
                
                # Determine overall status for this component
                if isinstance(result, dict):
                    if result.get('error'):
                        self.log(f"❌ {name} verification failed: {result['error']}", "ERROR")
                    else:
                        # Check if all boolean fields are True
                        boolean_fields = [k for k, v in result.items() if isinstance(v, bool)]
                        if boolean_fields and all(result[field] for field in boolean_fields):
                            self.log(f"✅ {name} verification successful")
                        else:
                            self.log(f"⚠️ {name} verification partial success", "WARNING")
                else:
                    if result:
                        self.log(f"✅ {name} verification successful")
                    else:
                        self.log(f"❌ {name} verification failed", "ERROR")
                        
            except Exception as e:
                self.log(f"❌ {name} verification error: {e}", "ERROR")
                results[name] = {'error': str(e)}
            
            time.sleep(1)  # Brief pause between verifications
        
        # Summary
        self.log("\n" + "=" * 50)
        self.log("📊 CONNECTION VERIFICATION SUMMARY")
        self.log("=" * 50)
        
        successful_verifications = 0
        total_verifications = len(results)
        
        for name, result in results.items():
            if isinstance(result, dict):
                if result.get('error'):
                    status = "❌ FAIL"
                else:
                    boolean_fields = [k for k, v in result.items() if isinstance(v, bool)]
                    if boolean_fields and all(result[field] for field in boolean_fields):
                        status = "✅ PASS"
                        successful_verifications += 1
                    else:
                        status = "⚠️ PARTIAL"
            else:
                if result:
                    status = "✅ PASS"
                    successful_verifications += 1
                else:
                    status = "❌ FAIL"
            
            self.log(f"{status} {name}")
        
        self.log("-" * 30)
        self.log(f"Total: {successful_verifications}/{total_verifications} verifications successful")
        
        if successful_verifications == total_verifications:
            self.log("🎉 ALL CONNECTIONS VERIFIED! System is fully operational.")
        else:
            self.log(f"⚠️ {total_verifications - successful_verifications} verifications failed. Please check the issues above.", "WARNING")
        
        return results

def main():
    """Main function"""
    verifier = ConnectionVerifier()
    results = verifier.run_verification()
    
    # Exit with appropriate code
    successful = sum(1 for result in results.values() 
                    if isinstance(result, dict) and not result.get('error') 
                    or not isinstance(result, dict) and result)
    
    if successful == len(results):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
