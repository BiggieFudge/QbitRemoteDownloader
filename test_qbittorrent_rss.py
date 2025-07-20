#!/usr/bin/env python3
"""
Test script to check qBittorrent RSS API functionality.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from services.qbittorrent_client import QBittorrentClient

def test_qbittorrent_rss():
    """Test qBittorrent RSS API functionality."""
    print("🧪 Testing qBittorrent RSS API")
    print("=" * 50)
    
    client = QBittorrentClient()
    
    # Test RSS API availability
    print("🔍 Testing RSS API availability...")
    if not client.test_rss_api():
        print("❌ RSS API is not available!")
        print("📝 This might mean:")
        print("  1. qBittorrent version doesn't support RSS")
        print("  2. RSS feature is not enabled")
        print("  3. API endpoint is different")
        return False
    
    print("✅ RSS API is available")
    
    # Test RSS feeds functionality
    print("\n📡 Testing RSS feeds functionality...")
    if not client.test_rss_feeds_working():
        print("❌ RSS feeds are not working!")
        print("📝 This might mean:")
        print("  1. RSS feeds have no content")
        print("  2. RSS feeds are not configured properly")
        print("  3. RSS feeds need to be refreshed")
        return False
    
    print("✅ RSS feeds are working")
    
    # Test refreshing RSS feeds
    print("\n🔄 Testing RSS feed refresh...")
    if client.refresh_rss_feeds():
        print("✅ RSS feeds refreshed successfully")
    else:
        print("⚠️  Could not refresh RSS feeds")
    
    # Test getting RSS feeds
    print("\n📡 Testing RSS feeds...")
    try:
        feeds = client.get_rss_feeds()
        print(f"✅ Found {len(feeds)} RSS feeds")
        
        if feeds:
            print("RSS feeds:")
            # Handle the response format correctly
            if isinstance(feeds, dict):
                for feed_name, feed_data in list(feeds.items())[:3]:  # Show first 3
                    print(f"   📡 {feed_name}")
            else:
                for feed in feeds[:3]:  # Show first 3
                    feed_name = feed.get('title', 'Unknown') if isinstance(feed, dict) else str(feed)
                    print(f"   📡 {feed_name}")
        else:
            print("⚠️  No RSS feeds configured")
            print("📝 Auto-download rules need RSS feeds to work")
    except Exception as e:
        print(f"❌ Error getting RSS feeds: {e}")
    
    # Test getting current rules
    print("\n📋 Testing get auto-download rules...")
    try:
        rules = client.get_auto_download_rules()
        print(f"✅ Found {len(rules)} existing rules")
        
        if rules:
            print("Current rules:")
            # Handle the response format correctly
            if isinstance(rules, dict):
                for rule_name, rule_data in list(rules.items())[:5]:  # Show first 5
                    enabled = rule_data.get('enabled', False) if isinstance(rule_data, dict) else True
                    print(f"   {'✅' if enabled else '❌'} {rule_name}")
            else:
                for rule in rules[:5]:  # Show first 5
                    rule_name = rule.get('ruleName', 'Unknown') if isinstance(rule, dict) else str(rule)
                    enabled = rule.get('enabled', False) if isinstance(rule, dict) else True
                    print(f"   {'✅' if enabled else '❌'} {rule_name}")
    except Exception as e:
        print(f"❌ Error getting rules: {e}")
        return False
    
    # Test creating a simple rule
    print("\n🎬 Testing create movie rule...")
    try:
        success = client.create_movie_rule("Test Movie", "1080p")
        print(f"Movie rule creation: {'✅ Success' if success else '❌ Failed'}")
        
        if success:
            print("⏳ Waiting 2 seconds for rule to appear...")
            import time
            time.sleep(2)
    except Exception as e:
        print(f"❌ Error creating movie rule: {e}")
        return False
    
    # Test creating a TV show rule
    print("\n📺 Testing create TV show rule...")
    try:
        success = client.create_tv_show_rule("Test TV Show", "1080p")
        print(f"TV show rule creation: {'✅ Success' if success else '❌ Failed'}")
        
        if success:
            print("⏳ Waiting 2 seconds for rule to appear...")
            import time
            time.sleep(2)
    except Exception as e:
        print(f"❌ Error creating TV show rule: {e}")
        return False
    
    # Test getting rules again to see if new ones were added
    print("\n📋 Checking rules after creation...")
    try:
        rules = client.get_auto_download_rules()
        print(f"✅ Now have {len(rules)} rules")
        
        if rules:
            print("Updated rules:")
            # Handle the response format correctly
            if isinstance(rules, dict):
                for rule_name, rule_data in rules.items():
                    enabled = rule_data.get('enabled', False) if isinstance(rule_data, dict) else True
                    print(f"   {'✅' if enabled else '❌'} {rule_name}")
                    
                    # Show details for test rules
                    if 'Test' in rule_name:
                        print(f"      📊 Rule details: {rule_data}")
            else:
                for rule in rules:
                    rule_name = rule.get('ruleName', 'Unknown') if isinstance(rule, dict) else str(rule)
                    enabled = rule.get('enabled', False) if isinstance(rule, dict) else True
                    print(f"   {'✅' if enabled else '❌'} {rule_name}")
                    
                    # Show details for test rules
                    if 'Test' in rule_name:
                        print(f"      📊 Rule details: {rule}")
    except Exception as e:
        print(f"❌ Error getting updated rules: {e}")
        return False
    
    return True

def test_qbittorrent_connection():
    """Test basic qBittorrent connection."""
    print("\n🔌 Testing qBittorrent connection...")
    
    client = QBittorrentClient()
    
    try:
        # Test getting torrents
        torrents = client.get_all_torrents()
        print(f"✅ Connected to qBittorrent - found {len(torrents)} torrents")
        return True
    except Exception as e:
        print(f"❌ Error connecting to qBittorrent: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing qBittorrent RSS API functionality")
    print("=" * 60)
    
    # Test connection first
    if not test_qbittorrent_connection():
        print("\n❌ Cannot connect to qBittorrent!")
        print("📝 Please check:")
        print("  1. qBittorrent is running")
        print("  2. WebUI is enabled")
        print("  3. Connection settings in .env file")
        exit(1)
    
    # Test RSS functionality
    success = test_qbittorrent_rss()
    
    if success:
        print("\n🎉 qBittorrent RSS API test completed!")
        print("📝 Check the logs above for detailed information")
        print("\n📋 To view RSS rules in qBittorrent WebUI:")
        print("   1. Open qBittorrent WebUI")
        print("   2. Go to 'RSS' section in the left sidebar")
        print("   3. Click on 'Auto-downloading rules' tab")
        print("   4. You should see the created rules there")
        print("\n⚠️  Note: Rules only work if RSS feeds are configured")
        print("   Current RSS feed: TorrentLeech")
    else:
        print("\n❌ qBittorrent RSS API test failed!")
        print("📝 Check the logs above for error details") 