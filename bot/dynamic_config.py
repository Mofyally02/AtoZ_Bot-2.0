#!/usr/bin/env python3
"""
Dynamic configuration loader for AtoZ Bot
Fetches configuration from database and provides real-time updates
"""
import os
import sys
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Add backend to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend'))

try:
    from app.database.connection import get_db
    from app.models.bot_models import BotConfiguration
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Database import failed: {e}")
    DATABASE_AVAILABLE = False

class DynamicConfig:
    """Dynamic configuration manager that fetches settings from database"""
    
    def __init__(self):
        self._config = None
        self._last_fetch = 0
        self._fetch_interval = 30  # Fetch config every 30 seconds
        self._fallback_config = self._get_fallback_config()
        
    def _get_fallback_config(self) -> Dict[str, Any]:
        """Get fallback configuration from environment variables"""
        return {
            "check_interval_seconds": float(os.getenv("REFRESH_INTERVAL_SEC", "10.0")),
            "quick_check_interval_seconds": float(os.getenv("QUICK_CHECK_INTERVAL_SEC", "10")),
            "results_report_interval_seconds": float(os.getenv("RESULTS_REPORT_INTERVAL_SEC", "5")),
            "rejected_report_interval_seconds": float(os.getenv("REJECTED_REPORT_INTERVAL_SEC", "43200")),
            "enable_quick_check": os.getenv("ENABLE_QUICK_CHECK", "false").lower() in ("1", "true", "yes"),
            "enable_results_reporting": os.getenv("ENABLE_RESULTS_REPORTING", "true").lower() in ("1", "true", "yes"),
            "enable_rejected_reporting": os.getenv("ENABLE_REJECTED_REPORTING", "true").lower() in ("1", "true", "yes"),
            "max_accept_per_run": int(os.getenv("MAX_ACCEPT_PER_RUN", "5")),
            "job_type_filter": os.getenv("JOB_TYPE_FILTER", "Telephone interpreting"),
            "headless": os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes"),
            "accept_preconditions": {
                "job_type": os.getenv("JOB_TYPE_FILTER", "Telephone interpreting"),
                "exclude_types": ["Face-to-Face", "Face to Face", "In-Person", "Onsite"],
                "required_fields": [
                    "ref",
                    "submitted", 
                    "appt_date",
                    "appt_time",
                    "duration",
                    "language",
                    "status",
                ],
            },
            "bot_running": False,
            "host_port": int(os.getenv("HOST_PORT", "5000"))
        }
    
    def _fetch_config_from_db(self) -> Optional[Dict[str, Any]]:
        """Fetch configuration from database"""
        if not DATABASE_AVAILABLE:
            return None
            
        try:
            db = next(get_db())
            config = db.query(BotConfiguration).filter(BotConfiguration.is_active == True).first()
            
            if config:
                return {
                    "check_interval_seconds": float(config.check_interval_seconds),
                    "quick_check_interval_seconds": config.quick_check_interval_seconds,
                    "results_report_interval_seconds": config.results_report_interval_seconds,
                    "rejected_report_interval_seconds": config.rejected_report_interval_seconds,
                    "enable_quick_check": config.enable_quick_check,
                    "enable_results_reporting": config.enable_results_reporting,
                    "enable_rejected_reporting": config.enable_rejected_reporting,
                    "max_accept_per_run": config.max_accept_per_run,
                    "job_type_filter": config.job_type_filter,
                    "headless": os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes"),
                    "accept_preconditions": {
                        "job_type": config.job_type_filter,
                        "exclude_types": config.exclude_types or ["Face-to-Face", "Face to Face", "In-Person", "Onsite"],
                        "required_fields": [
                            "ref",
                            "submitted",
                            "appt_date", 
                            "appt_time",
                            "duration",
                            "language",
                            "status",
                        ],
                    },
                    "bot_running": False,
                    "host_port": int(os.getenv("HOST_PORT", "5000"))
                }
        except Exception as e:
            print(f"⚠️ Failed to fetch config from database: {e}")
            
        return None
    
    def get_config(self, force_refresh: bool = False) -> Dict[str, Any]:
        """Get current configuration, fetching from database if needed"""
        current_time = time.time()
        
        # Check if we need to refresh the config
        if (force_refresh or 
            self._config is None or 
            current_time - self._last_fetch > self._fetch_interval):
            
            print(f"🔄 Fetching configuration from database...")
            new_config = self._fetch_config_from_db()
            
            if new_config:
                self._config = new_config
                self._last_fetch = current_time
                print(f"✅ Configuration updated from database")
                print(f"   Check interval: {self._config['check_interval_seconds']}s")
                print(f"   Max accept per run: {self._config['max_accept_per_run']}")
                print(f"   Job type filter: {self._config['job_type_filter']}")
            else:
                print(f"⚠️ Using fallback configuration")
                self._config = self._fallback_config.copy()
                self._last_fetch = current_time
        
        return self._config
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a specific configuration value"""
        config = self.get_config()
        return config.get(key, default)
    
    def get_check_interval(self) -> float:
        """Get the check interval in seconds"""
        return self.get("check_interval_seconds", 10.0)
    
    def get_quick_check_interval(self) -> int:
        """Get the quick check interval in seconds"""
        return self.get("quick_check_interval_seconds", 10)
    
    def get_max_accept_per_run(self) -> int:
        """Get maximum jobs to accept per run"""
        return self.get("max_accept_per_run", 5)
    
    def get_job_type_filter(self) -> str:
        """Get the job type filter"""
        return self.get("job_type_filter", "Telephone interpreting")
    
    def is_quick_check_enabled(self) -> bool:
        """Check if quick check is enabled"""
        return self.get("enable_quick_check", False)
    
    def is_results_reporting_enabled(self) -> bool:
        """Check if results reporting is enabled"""
        return self.get("enable_results_reporting", True)
    
    def is_rejected_reporting_enabled(self) -> bool:
        """Check if rejected reporting is enabled"""
        return self.get("enable_rejected_reporting", True)
    
    def force_refresh(self) -> Dict[str, Any]:
        """Force refresh configuration from database"""
        return self.get_config(force_refresh=True)

# Global instance
dynamic_config = DynamicConfig()

# Compatibility functions for existing code
def get_bot_config() -> Dict[str, Any]:
    """Get current bot configuration"""
    return dynamic_config.get_config()

def get_check_interval() -> float:
    """Get check interval"""
    return dynamic_config.get_check_interval()

def get_quick_check_interval() -> int:
    """Get quick check interval"""
    return dynamic_config.get_quick_check_interval()

def get_max_accept_per_run() -> int:
    """Get max accept per run"""
    return dynamic_config.get_max_accept_per_run()

def get_job_type_filter() -> str:
    """Get job type filter"""
    return dynamic_config.get_job_type_filter()

def is_quick_check_enabled() -> bool:
    """Check if quick check is enabled"""
    return dynamic_config.is_quick_check_enabled()

def is_results_reporting_enabled() -> bool:
    """Check if results reporting is enabled"""
    return dynamic_config.is_results_reporting_enabled()

def is_rejected_reporting_enabled() -> bool:
    """Check if rejected reporting is enabled"""
    return dynamic_config.is_rejected_reporting_enabled()

def refresh_config() -> Dict[str, Any]:
    """Force refresh configuration"""
    return dynamic_config.force_refresh()
