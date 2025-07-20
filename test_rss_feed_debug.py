#!/usr/bin/env python3
"""
Debug script to check RSS feed status and provide solutions.
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

def debug_rss_feeds():
    """Debug RSS feed issues."""
    print("🔍 Debugging RSS Feed Issues")
    print("=" * 50)
    
    client = QBittorrentClient()
    
    # Test RSS API
    print("🔍 Testing RSS API...")
    if not client.test_rss_api():
        print("❌ RSS API not available")
        return False
    
    print("✅ RSS API available")
    
    # Get RSS feeds
    print("\n📡 Getting RSS feeds...")
    try:
        feeds = client.get_rss_feeds()
        print(f"Found {len(feeds)} RSS feeds")
        
        if isinstance(feeds, dict):
            for feed_name, feed_data in feeds.items():
                print(f"\n📡 Feed: {feed_name}")
                print(f"   Type: {type(feed_data)}")
                print(f"   Content: {feed_data}")
        else:
            for feed in feeds:
                print(f"\n📡 Feed: {feed}")
    except Exception as e:
        print(f"❌ Error getting feeds: {e}")
        return False
    
    # Test RSS items
    print("\n📋 Testing RSS items...")
    try:
        items = client.client.rss_items()
        print(f"RSS items type: {type(items)}")
        print(f"RSS items content: {items}")
        
        if isinstance(items, dict):
            for feed_name, feed_items in items.items():
                print(f"\n📡 Feed '{feed_name}':")
                print(f"   Items type: {type(feed_items)}")
                print(f"   Items count: {len(feed_items) if isinstance(feed_items, list) else 'N/A'}")
                if isinstance(feed_items, list) and feed_items:
                    print(f"   First item: {feed_items[0]}")
        else:
            print(f"Items: {items}")
    except Exception as e:
        print(f"❌ Error getting RSS items: {e}")
        return False
    
    # Test RSS refresh
    print("\n🔄 Testing RSS refresh...")
    try:
        client.refresh_rss_feeds()
        print("✅ RSS refresh completed")
    except Exception as e:
        print(f"❌ Error refreshing RSS: {e}")
    
    return True

def provide_solutions():
    """Provide solutions for RSS feed issues."""
    print("\n📝 Solutions for RSS Feed Issues:")
    print("=" * 50)
    print("1. **Check RSS Feed URL**")
    print("   - Go to qBittorrent WebUI")
    print("   - Navigate to RSS section")
    print("   - Check if TorrentLeech feed URL is correct")
    print("   - Verify the feed URL is accessible")
    print()
    print("2. **Add Working RSS Feeds**")
    print("   - Add popular torrent site RSS feeds")
    print("   - Examples:")
    print("     * https://rss.torrentleech.org/feed.xml")
    print("     * https://rarbg.to/rssdd.php")
    print("     * https://eztv.re/ezrss.xml")
    print()
    print("3. **Test RSS Feed Manually**")
    print("   - Open the RSS feed URL in browser")
    print("   - Check if it returns valid XML")
    print("   - Verify it contains torrent items")
    print()
    print("4. **Alternative: Manual Downloads**")
    print("   - Use the regular search feature")
    print("   - Manually download torrents")
    print("   - Auto-download rules need working RSS feeds")
    print()
    print("5. **Check qBittorrent Settings**")
    print("   - Ensure RSS is enabled in qBittorrent")
    print("   - Check RSS refresh interval")
    print("   - Verify RSS download path settings")

if __name__ == "__main__":
    success = debug_rss_feeds()
    provide_solutions()
    
    if success:
        print("\n🎉 RSS feed debugging completed!")
    else:
        print("\n❌ RSS feed debugging failed!") 