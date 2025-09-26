import os
import time

from atoz_bot import run_once

REFRESH_INTERVAL_SEC = int(os.getenv("REFRESH_INTERVAL_SEC", "20"))

if __name__ == "__main__":
    total = 0
    while True:
        try:
            accepted = run_once()
            total += accepted
            print(f"Accepted: {accepted} | Total: {total}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(REFRESH_INTERVAL_SEC)


