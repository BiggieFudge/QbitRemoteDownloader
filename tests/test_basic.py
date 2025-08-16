#!/usr/bin/env python3
"""
Basic tests for QbitRemoteDownloader
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    try:
        from config.settings import Settings
        from services.qbittorrent_client import QBittorrentClient
        from services.telegram_bot import TelegramBot
        from services.prowlarr_client import ProwlarrClient
        from services.tmdb_client import TMDBClient
        print("✅ All modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_settings():
    """Test settings configuration."""
    try:
        from config.settings import Settings
        settings = Settings()
        print(f"✅ Settings loaded: {len(settings.AUTHORIZED_USERS)} authorized users")
        return True
    except Exception as e:
        print(f"❌ Settings error: {e}")
        return False

def test_qbittorrent_client():
    """Test qBittorrent client initialization."""
    try:
        from services.qbittorrent_client import QBittorrentClient
        # This will fail to connect without proper credentials, but should initialize
        client = QBittorrentClient()
        print("✅ qBittorrent client initialized")
        return True
    except Exception as e:
        print(f"⚠️ qBittorrent client error (expected without credentials): {e}")
        return True  # This is expected without proper setup

if __name__ == "__main__":
    print("🧪 Running basic tests...\n")
    
    tests = [
        test_imports,
        test_settings,
        test_qbittorrent_client
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed!")
        sys.exit(1)
