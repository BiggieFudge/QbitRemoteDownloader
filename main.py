#!/usr/bin/env python3
"""
QbitRemoteDownloader - Telegram Bot for Torrent Downloads

A private Telegram bot that allows authorized users to search for movies and TV shows
on TorrentLeech and automatically download them to qBittorrent with organized file structure.
"""

import sys
import os
import logging
from pathlib import Path
with open("C:\\Users\\eytan\\env_debug.txt", "w") as f:
    f.write("sys.executable: " + sys.executable + "\n")
    f.write("sys.path:\n" + "\n".join(sys.path) + "\n")
    f.write("ENVIRONMENT:\n")
    f.write("\n".join([f"{k}={v}" for k, v in os.environ.items()]))
# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from services.telegram_bot import TelegramBot
from utils.helpers import setup_logging, validate_telegram_token, validate_torrentleech_token

def main():
    """Main entry point for the application."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting QbitRemoteDownloader...")
    
    try:
        # Validate configuration
        settings = Settings()
        
        # Check required environment variables
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("TELEGRAM_BOT_TOKEN not set in environment variables")
            print("❌ Error: TELEGRAM_BOT_TOKEN not set. Please add it to your .env file.")
            return 1
        
        if not settings.PROWLARR_API_KEY:
            logger.error("PROWLARR_API_KEY not set in environment variables")
            print("❌ Error: PROWLARR_API_KEY not set. Please add it to your .env file.")
            return 1
        
        if not settings.AUTHORIZED_USERS:
            logger.error("AUTHORIZED_USERS not set in environment variables")
            print("❌ Error: AUTHORIZED_USERS not set. Please add your Telegram user ID to the .env file.")
            return 1
        
        # Validate tokens
        if not validate_telegram_token(settings.TELEGRAM_BOT_TOKEN):
            logger.error("Invalid Telegram bot token format")
            print("❌ Error: Invalid Telegram bot token format.")
            return 1
        
        if not settings.PROWLARR_API_KEY:
            logger.error("Invalid Prowlarr API key format")
            print("❌ Error: Invalid Prowlarr API key format.")
            return 1
        
        # Check if download directories exist
        if not os.path.exists(settings.MOVIES_DOWNLOAD_PATH):
            logger.warning(f"Movies download path does not exist: {settings.MOVIES_DOWNLOAD_PATH}")
            print(f"⚠️  Warning: Movies download path does not exist: {settings.MOVIES_DOWNLOAD_PATH}")
        
        if not os.path.exists(settings.TVSHOWS_DOWNLOAD_PATH):
            logger.warning(f"TV Shows download path does not exist: {settings.TVSHOWS_DOWNLOAD_PATH}")
            print(f"⚠️  Warning: TV Shows download path does not exist: {settings.TVSHOWS_DOWNLOAD_PATH}")
        
        # Print configuration summary
        print("✅ Configuration validated successfully!")
        print(f"📱 Telegram Bot: Configured")
        print(f"🔗 Prowlarr API: Configured")
        print(f"📁 Movies Path: {settings.MOVIES_DOWNLOAD_PATH}")
        print(f"📺 TV Shows Path: {settings.TVSHOWS_DOWNLOAD_PATH}")
        print(f"👥 Authorized Users: {len(settings.AUTHORIZED_USERS)}")
        print(f"🔧 qBittorrent: {settings.QBITTORRENT_HOST}:{settings.QBITTORRENT_PORT}")
        print("\n🚀 Starting Telegram bot...")
        
        # Create and start the bot
        bot = TelegramBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n👋 Bot stopped by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 