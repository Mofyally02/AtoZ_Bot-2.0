import os

from dotenv import load_dotenv

load_dotenv()

"""Central config for AtoZ bot.
Env vars can override defaults: ATOZ_BASE_URL, ATOZ_USERNAME, ATOZ_PASSWORD, REFRESH_INTERVAL_SEC, HEADLESS, MAX_ACCEPT_PER_RUN
"""

# Base URL and credentials (env overrides supported)
BASE_URL = os.getenv("ATOZ_BASE_URL", "https://portal.atozinterpreting.com")
ATOZ_USERNAME = os.getenv("ATOZ_USERNAME", "hussain02747@gmail.com")
ATOZ_PASSWORD = os.getenv("ATOZ_PASSWORD", "Ngoma2003#")

USER_CREDENTIALS = {
    "username": ATOZ_USERNAME,
    "password": ATOZ_PASSWORD,
}

# Job board path
ATOZ_INTERPRETER_JOBS_PATH = os.getenv("ATOZ_INTERPRETER_JOBS_PATH", "/interpreter-jobs")

# Bot configuration
BOT_CONFIG = {
    "check_interval": float(os.getenv("REFRESH_INTERVAL_SEC", "0.5")),
    "quick_check_interval": float(os.getenv("QUICK_CHECK_INTERVAL_SEC", "10")),  # 10-second job checking
    "results_report_interval": float(os.getenv("RESULTS_REPORT_INTERVAL_SEC", "5")),  # 5-second results reporting
    "rejected_report_interval": float(os.getenv("REJECTED_REPORT_INTERVAL_SEC", "43200")),  # 12-hour rejected jobs reporting (43200 seconds)
    "enable_quick_check": os.getenv("ENABLE_QUICK_CHECK", "false").lower() in ("1", "true", "yes"),
    "enable_results_reporting": os.getenv("ENABLE_RESULTS_REPORTING", "true").lower() in ("1", "true", "yes"),
    "enable_rejected_reporting": os.getenv("ENABLE_REJECTED_REPORTING", "true").lower() in ("1", "true", "yes"),
    "headless": os.getenv("HEADLESS", "true").lower() in ("1", "true", "yes"),
    "accept_preconditions": {
        "job_type": "Telephone interpreting",  # Exact match for details table
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
    "host_port": int(os.getenv("HOST_PORT", "5000")),
}

# Backward-compat constants
ATOZ_BASE_URL = BASE_URL
MAX_ACCEPT_PER_RUN = int(os.getenv("MAX_ACCEPT_PER_RUN", "5"))

print("✅ AtoZ config loaded.")


