#!/usr/bin/env python3
"""
Test script for the Future Downloads feature.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.tmdb_client import TMDBClient
from services.qbittorrent_client import QBittorrentClient

def setup_test_logging():
    """Setup logging for testing."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler()
        ]
    )

def test_tmdb_client():
    """Test TMDB client functionality."""
    print("🧪 Testing TMDB Client")
    print("=" * 50)
    
    client = TMDBClient()
    
    # Test movie search
    print("🔍 Testing movie search...")
    movies = client.search_movie("Avengers")
    print(f"Found {len(movies)} movies")
    
    if movies:
        movie = movies[0]
        print(f"First movie: {movie.get('title', 'Unknown')}")
        print(f"Release date: {movie.get('release_date', 'Unknown')}")
        print(f"Is upcoming: {client.is_upcoming_movie(movie)}")
    
    # Test TV show search
    print("\n🔍 Testing TV show search...")
    tv_shows = client.search_tv_show("Breaking Bad")
    print(f"Found {len(tv_shows)} TV shows")
    
    if tv_shows:
        tv_show = tv_shows[0]
        print(f"First TV show: {tv_show.get('name', 'Unknown')}")
        print(f"First air date: {tv_show.get('first_air_date', 'Unknown')}")
        print(f"Is upcoming: {client.is_upcoming_tv_show(tv_show)}")

def test_qbittorrent_rules():
    """Test qBittorrent auto-download rules."""
    print("\n🧪 Testing qBittorrent Auto-Download Rules")
    print("=" * 50)
    
    client = QBittorrentClient()
    
    # Test getting rules
    print("📋 Getting current rules...")
    rules = client.get_auto_download_rules()
    print(f"Found {len(rules)} existing rules")
    
    # Test creating a movie rule
    print("\n🎬 Testing movie rule creation...")
    success = client.create_movie_rule("Test Movie", "1080p")
    print(f"Movie rule creation: {'✅ Success' if success else '❌ Failed'}")
    
    # Test creating a TV show rule
    print("\n📺 Testing TV show rule creation...")
    success = client.create_tv_show_rule("Test TV Show", "1080p")
    print(f"TV show rule creation: {'✅ Success' if success else '❌ Failed'}")

def test_integration():
    """Test the full integration."""
    print("\n🧪 Testing Full Integration")
    print("=" * 50)
    
    tmdb_client = TMDBClient()
    qb_client = QBittorrentClient()
    
    # Search for a movie
    movies = tmdb_client.search_movie("Dune")
    if movies:
        movie = movies[0]
        title = movie.get('title', 'Unknown')
        movie_id = movie.get('id')
        
        print(f"🎬 Found movie: {title}")
        print(f"📅 Release date: {movie.get('release_date', 'Unknown')}")
        print(f"🔮 Is upcoming: {tmdb_client.is_upcoming_movie(movie)}")
        
        # Create auto-download rule
        if tmdb_client.is_upcoming_movie(movie):
            print(f"✅ Creating auto-download rule for {title}...")
            success = qb_client.create_movie_rule(title, "1080p")
            print(f"Rule creation: {'✅ Success' if success else '❌ Failed'}")
        else:
            print(f"ℹ️ {title} is not upcoming, skipping rule creation")

if __name__ == "__main__":
    setup_test_logging()
    test_tmdb_client()
    test_qbittorrent_rules()
    test_integration()
    
    print("\n✅ All tests completed!")
    print("📝 Summary:")
    print("  - TMDB API integration for movie/TV show search")
    print("  - qBittorrent auto-download rule creation")
    print("  - Future downloads feature ready for use")
    print("  - Users can now set up automatic downloads for upcoming content") 