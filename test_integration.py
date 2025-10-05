#!/usr/bin/env python3
"""
Integration Test Script for AtoZ Bot System
Tests all component connections and functionality
"""

import os
import sys
import time
import requests
import json
import psycopg2
import redis
from datetime import datetime, timezone
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

class IntegrationTester:
    """Integration tester for all system components"""
    
    def __init__(self):
        self.test_results = {}
        self.base_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        
    def log(self, message: str, level: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_database_connection(self) -> bool:
        """Test PostgreSQL database connection"""
        self.log("Testing database connection...")
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="atoz_bot_db",
                user="atoz_user",
                password="atoz_password"
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if result[0] == 1:
                self.log("✅ Database connection successful")
                return True
            else:
                self.log("❌ Database query failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Database connection failed: {e}", "ERROR")
            return False
    
    def test_redis_connection(self) -> bool:
        """Test Redis connection"""
        self.log("Testing Redis connection...")
        
        try:
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            
            # Test basic operations
            r.set("test_key", "test_value")
            value = r.get("test_key")
            r.delete("test_key")
            
            if value == "test_value":
                self.log("✅ Redis connection successful")
                return True
            else:
                self.log("❌ Redis operations failed", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Redis connection failed: {e}", "ERROR")
            return False
    
    def test_backend_api(self) -> bool:
        """Test backend API endpoints"""
        self.log("Testing backend API...")
        
        try:
            # Test health endpoint
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code != 200:
                self.log(f"❌ Health endpoint failed: {response.status_code}", "ERROR")
                return False
            
            health_data = response.json()
            self.log(f"✅ Health check passed: {health_data.get('status', 'unknown')}")
            
            # Test detailed health endpoint
            response = requests.get(f"{self.base_url}/health/detailed", timeout=10)
            if response.status_code == 200:
                detailed_health = response.json()
                self.log(f"✅ Detailed health check passed")
                
                # Log service statuses
                services = detailed_health.get('services', {})
                for service, status in services.items():
                    status_val = status.get('status', 'unknown')
                    icon = "✅" if status_val == 'healthy' else "❌"
                    self.log(f"  {icon} {service}: {status_val}")
            else:
                self.log(f"⚠️ Detailed health check failed: {response.status_code}", "WARNING")
            
            # Test bot status endpoint
            response = requests.get(f"{self.base_url}/api/bot/status", timeout=10)
            if response.status_code == 200:
                bot_status = response.json()
                self.log(f"✅ Bot status endpoint working: {bot_status.get('is_running', False)}")
            else:
                self.log(f"⚠️ Bot status endpoint failed: {response.status_code}", "WARNING")
            
            # Test dashboard metrics endpoint
            response = requests.get(f"{self.base_url}/api/bot/dashboard/metrics", timeout=10)
            if response.status_code == 200:
                metrics = response.json()
                self.log(f"✅ Dashboard metrics endpoint working")
            else:
                self.log(f"⚠️ Dashboard metrics endpoint failed: {response.status_code}", "WARNING")
            
            return True
            
        except Exception as e:
            self.log(f"❌ Backend API test failed: {e}", "ERROR")
            return False
    
    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection"""
        self.log("Testing WebSocket connection...")
        
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
            
            def on_close(ws, close_status_code, close_msg):
                self.log("WebSocket connection closed")
            
            def on_open(ws):
                self.log("✅ WebSocket connection established")
            
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
                self.log("✅ WebSocket test successful")
                return True
            else:
                self.log("❌ No WebSocket message received", "ERROR")
                return False
                
        except ImportError:
            self.log("⚠️ websocket-client not installed, skipping WebSocket test", "WARNING")
            return True
        except Exception as e:
            self.log(f"❌ WebSocket test failed: {e}", "ERROR")
            return False
    
    def test_frontend_connection(self) -> bool:
        """Test frontend connection"""
        self.log("Testing frontend connection...")
        
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                self.log("✅ Frontend connection successful")
                return True
            else:
                self.log(f"❌ Frontend connection failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Frontend connection failed: {e}", "ERROR")
            return False
    
    def test_bot_integration(self) -> bool:
        """Test bot integration with API"""
        self.log("Testing bot integration...")
        
        try:
            # Test bot toggle endpoint
            response = requests.post(f"{self.base_url}/api/bot/toggle", timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ Bot toggle endpoint working: {result}")
                
                # Wait a moment and check status
                time.sleep(2)
                status_response = requests.get(f"{self.base_url}/api/bot/status", timeout=10)
                if status_response.status_code == 200:
                    status = status_response.json()
                    self.log(f"✅ Bot status check working: {status.get('is_running', False)}")
                
                # Toggle bot back off
                time.sleep(2)
                requests.post(f"{self.base_url}/api/bot/toggle", timeout=10)
                
                return True
            else:
                self.log(f"❌ Bot toggle endpoint failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"❌ Bot integration test failed: {e}", "ERROR")
            return False
    
    def test_database_schema(self) -> bool:
        """Test database schema and tables"""
        self.log("Testing database schema...")
        
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="atoz_bot_db",
                user="atoz_user",
                password="atoz_password"
            )
            
            cursor = conn.cursor()
            
            # Check if required tables exist
            required_tables = [
                'bot_sessions',
                'job_records', 
                'analytics_periods',
                'bot_configurations',
                'system_logs'
            ]
            
            for table in required_tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    );
                """, (table,))
                
                exists = cursor.fetchone()[0]
                if exists:
                    self.log(f"✅ Table '{table}' exists")
                else:
                    self.log(f"❌ Table '{table}' missing", "ERROR")
                    cursor.close()
                    conn.close()
                    return False
            
            # Test inserting and querying data
            cursor.execute("""
                INSERT INTO bot_sessions (session_name, status, login_status)
                VALUES ('test-session', 'testing', 'success')
                RETURNING id;
            """)
            
            session_id = cursor.fetchone()[0]
            self.log(f"✅ Test session created: {session_id}")
            
            # Clean up test data
            cursor.execute("DELETE FROM bot_sessions WHERE id = %s", (session_id,))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            self.log("✅ Database schema test successful")
            return True
            
        except Exception as e:
            self.log(f"❌ Database schema test failed: {e}", "ERROR")
            return False
    
    def test_end_to_end_flow(self) -> bool:
        """Test end-to-end bot flow"""
        self.log("Testing end-to-end bot flow...")
        
        try:
            # 1. Start bot
            response = requests.post(f"{self.base_url}/api/bot/toggle", timeout=10)
            if response.status_code != 200:
                self.log("❌ Failed to start bot", "ERROR")
                return False
            
            self.log("✅ Bot started")
            
            # 2. Check bot status
            time.sleep(3)
            response = requests.get(f"{self.base_url}/api/bot/status", timeout=10)
            if response.status_code != 200:
                self.log("❌ Failed to get bot status", "ERROR")
                return False
            
            bot_status = response.json()
            self.log(f"✅ Bot status: {bot_status.get('is_running', False)}")
            
            # 3. Check dashboard metrics
            response = requests.get(f"{self.base_url}/api/bot/dashboard/metrics", timeout=10)
            if response.status_code != 200:
                self.log("❌ Failed to get dashboard metrics", "ERROR")
                return False
            
            metrics = response.json()
            self.log(f"✅ Dashboard metrics retrieved")
            
            # 4. Stop bot
            time.sleep(2)
            response = requests.post(f"{self.base_url}/api/bot/toggle", timeout=10)
            if response.status_code != 200:
                self.log("❌ Failed to stop bot", "ERROR")
                return False
            
            self.log("✅ Bot stopped")
            
            # 5. Verify bot is stopped
            time.sleep(2)
            response = requests.get(f"{self.base_url}/api/bot/status", timeout=10)
            if response.status_code == 200:
                bot_status = response.json()
                if not bot_status.get('is_running', True):
                    self.log("✅ Bot successfully stopped")
                    return True
                else:
                    self.log("❌ Bot still running after stop command", "ERROR")
                    return False
            else:
                self.log("❌ Failed to verify bot stop", "ERROR")
                return False
            
        except Exception as e:
            self.log(f"❌ End-to-end flow test failed: {e}", "ERROR")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all integration tests"""
        self.log("🧪 Starting Integration Tests")
        self.log("=" * 50)
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("Database Schema", self.test_database_schema),
            ("Redis Connection", self.test_redis_connection),
            ("Backend API", self.test_backend_api),
            ("WebSocket Connection", self.test_websocket_connection),
            ("Frontend Connection", self.test_frontend_connection),
            ("Bot Integration", self.test_bot_integration),
            ("End-to-End Flow", self.test_end_to_end_flow)
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            self.log(f"\n🔍 Running: {test_name}")
            self.log("-" * 30)
            
            try:
                result = test_func()
                results[test_name] = result
                
                if result:
                    self.log(f"✅ {test_name} PASSED")
                else:
                    self.log(f"❌ {test_name} FAILED", "ERROR")
                    
            except Exception as e:
                self.log(f"❌ {test_name} ERROR: {e}", "ERROR")
                results[test_name] = False
            
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        self.log("\n" + "=" * 50)
        self.log("📊 INTEGRATION TEST SUMMARY")
        self.log("=" * 50)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.log(f"{status} {test_name}")
        
        self.log("-" * 30)
        self.log(f"Total: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! System is fully integrated.")
        else:
            self.log(f"⚠️ {total - passed} tests failed. Please check the issues above.", "WARNING")
        
        return results

def main():
    """Main function"""
    tester = IntegrationTester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure

if __name__ == "__main__":
    main()
