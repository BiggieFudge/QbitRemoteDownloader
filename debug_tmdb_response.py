#!/usr/bin/env python3
"""
Debug script to print raw TMDB API responses.
"""

import os
import sys
import json
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

import requests

def debug_tmdb_response():
    """Print raw TMDB API responses."""
    print("🔍 Debugging TMDB API Responses")
    print("=" * 50)
    
    # Check if Bearer token is set
    bearer_token = os.getenv('TMDB_API_KEY')
    if not bearer_token or bearer_token == 'your_tmdb_bearer_token_here':
        print("❌ TMDB_API_KEY (Bearer token) not set in .env file")
        return False
    
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'accept': 'application/json'
    }
    
    # Test different TV shows
    test_shows = [
        "Breaking Bad",
        "Stranger Things", 
        "The Walking Dead",
        "The Mandalorian"
    ]
    
    for show_name in test_shows:
        print(f"\n🎬 Testing: {show_name}")
        print("-" * 30)
        
        # Search for the show
        search_url = "https://api.themoviedb.org/3/search/tv"
        search_params = {
            'query': show_name,
            'include_adult': False,
            'language': 'en-US'
        }
        
        try:
            response = requests.get(search_url, headers=headers, params=search_params)
            print(f"📡 Search Response Status: {response.status_code}")
            
            if response.status_code == 200:
                search_data = response.json()
                results = search_data.get('results', [])
                
                if results:
                    # Get the first result
                    show = results[0]
                    show_id = show.get('id')
                    
                    print(f"📺 Found: {show.get('name', 'Unknown')}")
                    print(f"🆔 ID: {show_id}")
                    print(f"📅 First Air: {show.get('first_air_date', 'Unknown')}")
                    print(f"🔮 Status: {show.get('status', 'Unknown')}")
                    
                    # Get detailed info
                    if show_id:
                        detail_url = f"https://api.themoviedb.org/3/tv/{show_id}"
                        detail_params = {
                            'append_to_response': 'next_episode_to_air'
                        }
                        
                        detail_response = requests.get(detail_url, headers=headers, params=detail_params)
                        print(f"📡 Detail Response Status: {detail_response.status_code}")
                        
                        if detail_response.status_code == 200:
                            detail_data = detail_response.json()
                            
                            print(f"📊 Detailed Status: {detail_data.get('status', 'Unknown')}")
                            print(f"📺 Name: {detail_data.get('name', 'Unknown')}")
                            print(f"📅 First Air: {detail_data.get('first_air_date', 'Unknown')}")
                            print(f"📅 Last Air: {detail_data.get('last_air_date', 'Unknown')}")
                            
                            next_episode = detail_data.get('next_episode_to_air')
                            if next_episode:
                                print(f"🔮 Next Episode: {next_episode.get('name', 'Unknown')}")
                                print(f"📅 Next Air Date: {next_episode.get('air_date', 'Unknown')}")
                            else:
                                print("🔮 No next episode info")
                            
                            # Print full response for debugging
                            print("\n📋 Full Response:")
                            print(json.dumps(detail_data, indent=2))
                        else:
                            print(f"❌ Detail request failed: {detail_response.text}")
                else:
                    print("❌ No search results found")
            else:
                print(f"❌ Search request failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n✅ Debug completed!")
    return True

if __name__ == "__main__":
    success = debug_tmdb_response()
    if success:
        print("\n🎉 TMDB response debugging completed!")
        print("📝 Check the output above to see the raw API responses")
    else:
        print("\n❌ Debug failed!") 