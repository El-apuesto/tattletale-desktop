#!/usr/bin/env python3
"""
Automated News Satire System

Main entry point for the automated news satire generation system.
Transforms real news into deadpan satire with XKCD integration.
"""

import logging
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.utils.config import Config
from src.publishing.scheduler import PublishingScheduler
from src.utils.error_handling import ErrorContext

def setup_logging():
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    os.makedirs(Config.LOG_DIR, exist_ok=True)
    
    # Configure logging
    log_filename = os.path.join(Config.LOG_DIR, f"satire_system_{datetime.now().strftime('%Y%m%d')}.log")
    
    logging.basicConfig(
        level=getattr(logging, Config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Logging system initialized")
    return logger

def main():
    """Main entry point."""
    logger = setup_logging()
    
    try:
        logger.info("Starting Automated News Satire System")
        logger.info(f"Configuration: {Config.PUBLISH_TIMES} publishing schedule")
        
        # Initialize and start the scheduler
        scheduler = PublishingScheduler()
        
        if len(sys.argv) > 1 and sys.argv[1] == '--test':
            # Run immediate test cycle
            logger.info("Running test cycle...")
            scheduler.run_immediate_cycle()
        else:
            # Start the normal scheduler
            logger.info("Starting scheduler (press Ctrl+C to stop)")
            scheduler.start_scheduler()
            
    except KeyboardInterrupt:
        logger.info("System stopped by user")
    except Exception as e:
        logger.error(f"System error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
