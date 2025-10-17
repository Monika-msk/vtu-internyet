#!/usr/bin/env python3
"""
Local scheduler for VTU Internship Watcher
Use this to run the watcher locally with scheduling instead of GitHub Actions
"""

import schedule
import time
import logging
from internship_watcher import InternshipWatcher

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_watcher():
    """Run the internship watcher."""
    try:
        logger.info("Starting scheduled internship check...")
        watcher = InternshipWatcher()
        watcher.check_for_new_internships()
        logger.info("Scheduled check completed successfully")
    except Exception as e:
        logger.error(f"Error during scheduled check: {e}")

def main():
    """Main scheduler function."""
    logger.info("🚀 Starting VTU Internship Watcher Scheduler")
    logger.info("Press Ctrl+C to stop the scheduler")
    
    # Schedule the job
    # You can modify this to change the frequency
    schedule.every(30).minutes.do(run_watcher)  # Every 30 minutes
    # schedule.every().hour.do(run_watcher)     # Every hour
    # schedule.every(2).hours.do(run_watcher)   # Every 2 hours
    
    # Run once immediately
    logger.info("Running initial check...")
    run_watcher()
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute for scheduled jobs
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")

if __name__ == "__main__":
    main()
