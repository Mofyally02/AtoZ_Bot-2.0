#!/usr/bin/env python3
"""
Resilient Bot Runner for AtoZ Bot
Handles Playwright crashes gracefully and restarts automatically
"""

import asyncio
import logging
import time
import traceback
import sys
import os
from playwright.async_api import async_playwright

# Add the bot directory to Python path
sys.path.append(os.path.dirname(__file__))

# Import bot modules
from atoz_bot import run_bot_with_session, log
from config import ATOZ_BASE_URL, ATOZ_USERNAME, ATOZ_PASSWORD, BOT_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot_runner.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class ResilientBotRunner:
    def __init__(self, session_id: str, max_retries: int = 10, retry_delay: int = 30):
        self.session_id = session_id
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.retry_count = 0
        self.running = True
        
    async def run_bot_cycle(self):
        """Run one cycle of the bot with enhanced error handling"""
        try:
            logger.info(f"Starting bot cycle for session {self.session_id}")
            
            # Use the existing bot logic but with better error handling
            from atoz_bot import run_bot_with_session
            run_bot_with_session(self.session_id)
            
            logger.info(f"Bot cycle completed successfully for session {self.session_id}")
            self.retry_count = 0  # Reset retry count on success
            
        except Exception as e:
            logger.error(f"Bot cycle failed for session {self.session_id}: {str(e)}")
            logger.error(traceback.format_exc())
            self.retry_count += 1
            raise e
    
    async def run_resilient(self):
        """Continuously run bot cycles with error handling & retries"""
        logger.info(f"Starting resilient bot runner for session {self.session_id}")
        
        while self.running and self.retry_count < self.max_retries:
            try:
                await self.run_bot_cycle()
                
                # If we get here, the cycle completed successfully
                # Wait before next cycle
                cycle_delay = BOT_CONFIG.get("check_interval", 30)
                logger.info(f"Waiting {cycle_delay} seconds before next cycle...")
                await asyncio.sleep(cycle_delay)
                
            except Exception as e:
                logger.error(f"Bot crashed with error: {str(e)}")
                logger.error(traceback.format_exc())
                
                if self.retry_count >= self.max_retries:
                    logger.error(f"Max retries ({self.max_retries}) reached. Stopping bot runner.")
                    break
                
                logger.info(f"Restarting bot after crash... (attempt {self.retry_count + 1}/{self.max_retries})")
                await asyncio.sleep(self.retry_delay)
        
        logger.info(f"Bot runner stopped for session {self.session_id}")
    
    def stop(self):
        """Stop the bot runner gracefully"""
        logger.info("Stopping bot runner...")
        self.running = False

async def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python resilient_bot_runner.py <session_id> [max_retries] [retry_delay]")
        sys.exit(1)
    
    session_id = sys.argv[1]
    max_retries = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    retry_delay = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    
    runner = ResilientBotRunner(session_id, max_retries, retry_delay)
    
    try:
        await runner.run_resilient()
    except KeyboardInterrupt:
        logger.info("Bot runner stopped manually.")
        runner.stop()
    except Exception as e:
        logger.error(f"Fatal error in bot runner: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
