#!/usr/bin/env python3
"""
Mock AtoZ Bot for testing purposes
This simulates bot activity without requiring external dependencies
"""

import time
import sys
import json
import random
from datetime import datetime

def log(message: str) -> None:
    """Log message with timestamp"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [MockBot] {message}")

def simulate_bot_activity():
    """Simulate bot activity"""
    log("Starting mock bot...")
    
    # Simulate login
    log("Attempting login...")
    time.sleep(2)
    log("Login successful!")
    
    # Simulate job checking cycles
    cycle_count = 0
    while True:
        cycle_count += 1
        log(f"Starting job check cycle #{cycle_count}")
        
        # Simulate job checking
        time.sleep(random.uniform(1, 3))
        
        # Simulate finding jobs
        jobs_found = random.randint(0, 3)
        if jobs_found > 0:
            log(f"Found {jobs_found} jobs")
            
            # Simulate job processing
            for i in range(jobs_found):
                time.sleep(random.uniform(0.5, 1.5))
                action = random.choice(["accepted", "rejected", "skipped"])
                log(f"Job {i+1}: {action}")
        else:
            log("No jobs found")
        
        # Simulate cycle completion
        log(f"Cycle #{cycle_count} completed")
        
        # Wait before next cycle
        time.sleep(random.uniform(5, 10))

if __name__ == "__main__":
    try:
        simulate_bot_activity()
    except KeyboardInterrupt:
        log("Bot stopped by user")
    except Exception as e:
        log(f"Bot error: {e}")
        sys.exit(1)
