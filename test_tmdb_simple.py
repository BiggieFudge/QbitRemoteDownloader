#!/usr/bin/env python3
"""
Simple test for TMDB client functionality.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from services.tmdb_client import TMDBClient

def test_tmdb_basic():
    """Test basic TMDB functionality."""
    print("🧪 Testing TMDB Client (Basic)")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('TMDB_API_KEY')
    if not api_key or api_key == 'your_tmdb_bearer_token_here':
        print("❌ TMDB_API_KEY not set in .env file")
        print("Please add your TMDB Bearer token to the .env file")
        print("Get your Bearer token from: https://www.themoviedb.org/settings/api")
        return False
    
    client = TMDBClient()
    
    # Test movie search
    print("🔍 Testing movie search...")
    try:
        movies = client.search_movie("Avengers")
        print(f"✅ Found {len(movies)} movies")
        
        if movies:
            movie = movies[0]
            print(f"   First movie: {movie.get('title', 'Unknown')}")
            print(f"   Release date: {movie.get('release_date', 'Unknown')}")
            print(f"   Is upcoming: {client.is_upcoming_movie(movie)}")
    except Exception as e:
        print(f"❌ Error in movie search: {e}")
        return False
    
    # Test TV show search
    print("\n🔍 Testing TV show search...")
    try:
        tv_shows = client.search_tv_show("Breaking Bad")
        print(f"✅ Found {len(tv_shows)} TV shows")
        
        if tv_shows:
            tv_show = tv_shows[0]
            print(f"   First TV show: {tv_show.get('name', 'Unknown')}")
            print(f"   First air date: {tv_show.get('first_air_date', 'Unknown')}")
            print(f"   Is upcoming: {client.is_upcoming_tv_show(tv_show)}")
    except Exception as e:
        print(f"❌ Error in TV show search: {e}")
        return False
    
    print("\n✅ TMDB client test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_tmdb_basic()
    if success:
        print("\n🎉 TMDB integration is working!")
        print("📝 Next steps:")
        print("  1. Make sure your TMDB Bearer token is in .env file")
        print("  2. Test the Future Downloads feature in the bot")
    else:
        print("\n❌ TMDB integration failed!")
        print("📝 Please check:")
        print("  1. TMDB_API_KEY (Bearer token) in .env file")
        print("  2. Internet connection")
        print("  3. TMDB API service status") 