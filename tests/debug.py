#!/usr/bin/env python3
"""
Debug script for QbitRemoteDownloader
Tests each component individually to identify issues.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import Settings
from services.prowlarr_client import ProwlarrClient
from services.qbittorrent_client import QBittorrentClient
from utils.helpers import setup_logging, validate_telegram_token, validate_torrentleech_token

def setup_debug_logging():
    """Setup detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler()
        ]
    )

def test_configuration():
    """Test configuration loading and validation."""
    print("🔧 Testing Configuration...")
    
    try:
        settings = Settings()
        print("✅ Settings loaded successfully")
        
        # Test each setting
        print(f"📱 Telegram Bot Token: {'✅ Set' if settings.TELEGRAM_BOT_TOKEN else '❌ Missing'}")
        print(f"🔗 Prowlarr API Key: {'✅ Set' if settings.PROWLARR_API_KEY else '❌ Missing'}")
        print(f"👥 Authorized Users: {'✅ Set' if settings.AUTHORIZED_USERS else '❌ Missing'}")
        print(f"📁 Movies Path: {settings.MOVIES_DOWNLOAD_PATH}")
        print(f"📺 TV Shows Path: {settings.TVSHOWS_DOWNLOAD_PATH}")
        print(f"🔧 qBittorrent: {settings.QBITTORRENT_HOST}:{settings.QBITTORRENT_PORT}")
        
        # Validate tokens
        if settings.TELEGRAM_BOT_TOKEN:
            if validate_telegram_token(settings.TELEGRAM_BOT_TOKEN):
                print("✅ Telegram token format is valid")
            else:
                print("❌ Telegram token format is invalid")
        
        if settings.PROWLARR_API_KEY:
            print("✅ Prowlarr API key format is valid")
        else:
            print("❌ Prowlarr API key is missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_prowlarr_connection():
    """Test Prowlarr API connection."""
    print("\n🔗 Testing Prowlarr Connection...")
    
    try:
        client = ProwlarrClient()
        
        # Test a simple search
        print("🔍 Testing search functionality...")
        results = client.search_movies("test", page=0)
        
        if results and 'torrents' in results:
            print(f"✅ Prowlarr connection successful")
            print(f"📊 Found {len(results['torrents'])} test results")
            return True
        else:
            print("❌ No results returned from Prowlarr")
            return False
            
    except Exception as e:
        print(f"❌ Prowlarr connection failed: {e}")
        return False

def test_qbittorrent_connection():
    """Test qBittorrent connection."""
    print("\n🔧 Testing qBittorrent Connection...")
    
    try:
        client = QBittorrentClient()
        print("✅ qBittorrent connection successful")
        
        # Test getting torrents
        torrents = client.get_all_torrents()
        print(f"📊 Found {len(torrents)} torrents in qBittorrent")
        
        # Test getting stats
        stats = client.get_download_stats()
        print(f"📈 Download stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ qBittorrent connection failed: {e}")
        print("💡 Make sure qBittorrent is running and Web UI is enabled on port 8080")
        return False

def test_database():
    """Test database functionality."""
    print("\n🗄️ Testing Database...")
    
    try:
        from models.database import Database
        db = Database()
        print("✅ Database initialized successfully")
        
        # Test adding a user session
        db.update_user_session(123456789, 'test_state', 'test_query', 0)
        print("✅ User session test successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_directories():
    """Test if download directories exist."""
    print("\n📁 Testing Download Directories...")
    
    settings = Settings()
    
    movies_path = settings.MOVIES_DOWNLOAD_PATH
    tv_path = settings.TVSHOWS_DOWNLOAD_PATH
    
    if os.path.exists(movies_path):
        print(f"✅ Movies directory exists: {movies_path}")
    else:
        print(f"❌ Movies directory missing: {movies_path}")
        print("💡 Create this directory or update MOVIES_DOWNLOAD_PATH in .env")
    
    if os.path.exists(tv_path):
        print(f"✅ TV Shows directory exists: {tv_path}")
    else:
        print(f"❌ TV Shows directory missing: {tv_path}")
        print("💡 Create this directory or update TVSHOWS_DOWNLOAD_PATH in .env")
    
    return os.path.exists(movies_path) and os.path.exists(tv_path)

def test_telegram_bot():
    """Test Telegram bot initialization."""
    print("\n🤖 Testing Telegram Bot...")
    
    try:
        from services.telegram_bot import TelegramBot
        bot = TelegramBot()
        print("✅ Telegram bot initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Telegram bot initialization failed: {e}")
        return False

def run_all_tests():
    """Run all debug tests."""
    print("🚀 Starting Debug Tests...\n")
    
    setup_debug_logging()
    
    tests = [
        ("Configuration", test_configuration),
        ("Prowlarr Connection", test_prowlarr_connection),
        ("qBittorrent Connection", test_qbittorrent_connection),
        ("Database", test_database),
        ("Directories", test_directories),
        ("Telegram Bot", test_telegram_bot),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*50)
    print("📊 DEBUG SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your bot should work correctly.")
    else:
        print("⚠️  Some tests failed. Check the errors above and fix the issues.")
    
    return results

if __name__ == "__main__":
    run_all_tests() 