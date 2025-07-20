#!/usr/bin/env python3
"""
Test script to trigger TMDB API calls and log responses.
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

# Setup logging to see TMDB responses
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('tmdb_responses.log')
    ]
)

from services.tmdb_client import TMDBClient

def test_tmdb_with_logging():
    """Test TMDB API calls with logging."""
    print("🧪 Testing TMDB API with Logging")
    print("=" * 50)
    print("📝 Responses will be logged to 'tmdb_responses.log'")
    
    # Check if Bearer token is set
    bearer_token = os.getenv('TMDB_API_KEY')
    if not bearer_token or bearer_token == 'your_tmdb_bearer_token_here':
        print("❌ TMDB_API_KEY (Bearer token) not set in .env file")
        return False
    
    client = TMDBClient()
    
    # Test TV show search
    print("\n🔍 Testing TV show search...")
    test_shows = ["Breaking Bad", "Stranger Things", "The Walking Dead"]
    
    for show_name in test_shows:
        print(f"\n📺 Searching for: {show_name}")
        try:
            results = client.search_tv_show(show_name)
            print(f"✅ Found {len(results)} results")
            
            if results:
                show = results[0]
                show_id = show.get('id')
                name = show.get('name', 'Unknown')
                status = show.get('status', 'Unknown')
                
                print(f"   📺 Name: {name}")
                print(f"   🔮 Status: {status}")
                print(f"   🆔 ID: {show_id}")
                
                # Get detailed info
                if show_id:
                    print(f"   📊 Getting detailed info...")
                    detailed = client.get_tv_show_details(show_id)
                    if detailed:
                        detailed_status = detailed.get('status', 'Unknown')
                        print(f"   📊 Detailed Status: {detailed_status}")
                        
                        # Test status checking
                        is_upcoming = client.is_upcoming_tv_show(detailed)
                        print(f"   ✅ Is Upcoming: {is_upcoming}")
                        
                        # Test status formatting
                        formatted_status = client.get_tv_show_status(detailed)
                        print(f"   🎨 Formatted Status: {formatted_status}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test movie search
    print("\n🎬 Testing movie search...")
    test_movies = ["Avengers", "Dune"]
    
    for movie_name in test_movies:
        print(f"\n🎬 Searching for: {movie_name}")
        try:
            results = client.search_movie(movie_name)
            print(f"✅ Found {len(results)} results")
            
            if results:
                movie = results[0]
                movie_id = movie.get('id')
                title = movie.get('title', 'Unknown')
                release_date = movie.get('release_date', 'Unknown')
                
                print(f"   🎬 Title: {title}")
                print(f"   📅 Release Date: {release_date}")
                print(f"   🆔 ID: {movie_id}")
                
                # Get detailed info
                if movie_id:
                    print(f"   📊 Getting detailed info...")
                    detailed = client.get_movie_details(movie_id)
                    if detailed:
                        # Test status checking
                        is_upcoming = client.is_upcoming_movie(detailed)
                        print(f"   ✅ Is Upcoming: {is_upcoming}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ Test completed!")
    print("📝 Check 'tmdb_responses.log' for detailed API responses")
    return True

if __name__ == "__main__":
    success = test_tmdb_with_logging()
    if success:
        print("\n🎉 TMDB logging test completed!")
        print("📝 Check the log file for detailed responses")
    else:
        print("\n❌ TMDB logging test failed!") 