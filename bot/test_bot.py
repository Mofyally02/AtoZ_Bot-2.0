#!/usr/bin/env python3
"""
Simple test bot that runs continuously for testing purposes
"""
import sys
import time
import signal
import os
from datetime import datetime, timezone

def signal_handler(sig, frame):
    print(f"[{datetime.now(timezone.utc).isoformat()}] Bot received stop signal, shutting down...")
    sys.exit(0)

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_bot.py <session_id>")
        sys.exit(1)
    
    session_id = sys.argv[1]
    print(f"[{datetime.now(timezone.utc).isoformat()}] Starting test bot for session {session_id}")
    
    # Set up signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        counter = 0
        while True:
            print(f"[{datetime.now(timezone.utc).isoformat()}] Bot running... (iteration {counter})")
            time.sleep(5)  # Run every 5 seconds
            counter += 1
            
    except KeyboardInterrupt:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Bot stopped by user")
    except Exception as e:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Bot error: {e}")
    finally:
        print(f"[{datetime.now(timezone.utc).isoformat()}] Bot shutdown complete")

if __name__ == "__main__":
    main()



