#!/usr/bin/env python3
"""
Test script for production show filtering and regex pattern creation.
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

from services.tmdb_client import TMDBClient

def test_production_shows():
    """Test filtering for shows in production and regex pattern creation."""
    print("🧪 Testing Production Show Filtering")
    print("=" * 50)
    
    # Check if Bearer token is set
    bearer_token = os.getenv('TMDB_API_KEY')
    if not bearer_token or bearer_token == 'your_tmdb_bearer_token_here':
        print("❌ TMDB_API_KEY (Bearer token) not set in .env file")
        return False
    
    client = TMDBClient()
    
    # Test different TV shows
    test_shows = [
        "Stranger Things",
        "The Mandalorian", 
        "House of the Dragon",
        "Wednesday",
        "The Last of Us",
        "Breaking Bad",  # Should be ended - won't show
        "The Walking Dead"  # Should be ended - won't show
    ]
    
    production_shows = []
    
    for show_name in test_shows:
        print(f"\n🔍 Testing: {show_name}")
        print("-" * 30)
        
        try:
            # Search for the show
            results = client.search_tv_show(show_name)
            if not results:
                print(f"   ❌ No results found")
                continue
            
            show = results[0]
            show_id = show.get('id')
            name = show.get('name', 'Unknown')
            
            print(f"   📺 Name: {name}")
            print(f"   🆔 ID: {show_id}")
            
            # Get detailed info
            if show_id:
                detailed = client.get_tv_show_details(show_id)
                if detailed:
                    # Check if in production
                    is_in_production = client.is_show_in_production(detailed)
                    print(f"   🟢 In Production: {is_in_production}")
                    
                    # Only process shows in production
                    if is_in_production:
                        # Get last season info
                        last_season_info = client.get_last_season_info(detailed)
                        if last_season_info:
                            season_number = last_season_info['season_number']
                            episode_count = last_season_info['episode_count']
                            next_season = season_number + 1
                            
                            print(f"   📊 Last Season: {season_number} ({episode_count} episodes)")
                            print(f"   🔮 Next Season: {next_season}")
                            
                            # Create regex pattern
                            regex_pattern = client.create_tv_show_regex_pattern(detailed)
                            if regex_pattern:
                                print(f"   🎯 Regex Pattern: {regex_pattern}")
                                production_shows.append({
                                    'name': name,
                                    'id': show_id,
                                    'data': detailed,
                                    'regex': regex_pattern,
                                    'last_season': season_number,
                                    'episode_count': episode_count,
                                    'next_season': next_season
                                })
                            else:
                                print(f"   ❌ Could not create regex pattern")
                        else:
                            print(f"   ❌ No season info available")
                    else:
                        print(f"   🔴 Not in production - skipping")
                else:
                    print(f"   ❌ Could not get detailed info")
            else:
                print(f"   ❌ No show ID available")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Total shows tested: {len(test_shows)}")
    print(f"   Shows in production: {len(production_shows)}")
    
    if production_shows:
        print(f"\n🟢 Shows in Production (will be displayed):")
        for show in production_shows:
            print(f"   📺 {show['name']}")
            print(f"      🎯 Regex: {show['regex']}")
            print(f"      📊 Last Season: {show['last_season']} ({show['episode_count']} episodes)")
            print(f"      🔮 Next Season: {show['next_season']}")
            print()
    else:
        print(f"\n🔴 No shows in production found")
        print("   Only shows currently in production will be displayed in search results")
    
    return True

if __name__ == "__main__":
    success = test_production_shows()
    if success:
        print("\n🎉 Production show filtering test completed!")
        print("📝 Check the output above for regex patterns")
    else:
        print("\n❌ Production show filtering test failed!") 