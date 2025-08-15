#!/usr/bin/env python3
"""
Test script to run the bot with enhanced logging for troubleshooting.
"""

import logging
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Run the bot with enhanced logging."""
    try:
        logger.info("=" * 60)
        logger.info("🚀 Starting Telegram Bot with Enhanced Logging")
        logger.info("=" * 60)
        
        # Import and test settings
        from config.settings import Settings
        settings = Settings()
        
        logger.info(f"✅ Settings loaded successfully")
        logger.info(f"📊 Authorized users: {settings.AUTHORIZED_USERS}")
        logger.info(f"🔢 Total authorized users: {len(settings.AUTHORIZED_USERS)}")
        
        # Test database
        from models.database import Database
        db = Database()
        logger.info("✅ Database initialized successfully")
        
        # Test other components
        from services.prowlarr_client import ProwlarrClient
        from services.qbittorrent_client import QBittorrentClient
        from services.tmdb_client import TMDBClient
        
        prowlarr = ProwlarrClient()
        qbittorrent = QBittorrentClient()
        tmdb = TMDBClient()
        
        logger.info("✅ All service clients initialized successfully")
        
        # Start the bot
        from services.telegram_bot import TelegramBot
        bot = TelegramBot()
        
        logger.info("✅ Bot initialized successfully")
        logger.info("🤖 Bot is now running...")
        logger.info("📝 Check bot.log for detailed logs")
        logger.info("🔍 Use /debug command in the bot to troubleshoot")
        
        bot.run()
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 