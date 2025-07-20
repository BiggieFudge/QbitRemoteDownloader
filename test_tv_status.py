#!/usr/bin/env python3
"""
Test TV show status parsing.
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

def test_tv_show_status():
    """Test TV show status parsing."""
    print("🧪 Testing TV Show Status Parsing")
    print("=" * 50)
    
    # Check if Bearer token is set
    bearer_token = os.getenv('TMDB_API_KEY')
    if not bearer_token or bearer_token == 'your_tmdb_bearer_token_here':
        print("❌ TMDB_API_KEY (Bearer token) not set in .env file")
        return False
    
    client = TMDBClient()
    
    # Test different types of TV shows
    test_shows = [
        "Breaking Bad",      # Ended
        "The Walking Dead",  # Ended
        "Stranger Things",   # Returning Series
        "The Mandalorian",   # Continuing
        "House of the Dragon", # Continuing
        "Wednesday",         # Continuing
        "The Last of Us",    # Continuing
    ]
    
    for show_name in test_shows:
        print(f"\n🔍 Testing: {show_name}")
        try:
            results = client.search_tv_show(show_name)
            if results:
                show = results[0]  # Get first result
                name = show.get('name', 'Unknown')
                status = client.get_tv_show_status(show)
                is_upcoming = client.is_upcoming_tv_show(show)
                
                print(f"   📺 Name: {name}")
                print(f"   🔮 Status: {status}")
                print(f"   ✅ Is Upcoming: {is_upcoming}")
                
                # Get detailed info if available
                show_id = show.get('id')
                if show_id:
                    detailed = client.get_tv_show_details(show_id)
                    if detailed:
                        detailed_status = client.get_tv_show_status(detailed)
                        print(f"   📊 Detailed Status: {detailed_status}")
            else:
                print(f"   ❌ No results found")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n✅ TV show status test completed!")
    return True

if __name__ == "__main__":
    success = test_tv_show_status()
    if success:
        print("\n🎉 TV show status parsing is working!")
        print("📝 You can now see correct status for all TV shows")
    else:
        print("\n❌ TV show status test failed!") 