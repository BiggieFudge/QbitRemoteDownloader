#!/usr/bin/env python3
"""
Test TMDB Bearer token authentication.
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

def test_tmdb_auth():
    """Test TMDB Bearer token authentication."""
    print("🧪 Testing TMDB Bearer Token Authentication")
    print("=" * 60)
    
    # Check if Bearer token is set
    bearer_token = os.getenv('TMDB_API_KEY')
    if not bearer_token or bearer_token == 'your_tmdb_bearer_token_here':
        print("❌ TMDB_API_KEY (Bearer token) not set in .env file")
        print("Please add your TMDB Bearer token to the .env file")
        print("Get your Bearer token from: https://www.themoviedb.org/settings/api")
        return False
    
    print(f"✅ Bearer token found: {bearer_token[:20]}...")
    
    # Test direct API call
    import requests
    
    headers = {
        'Authorization': f'Bearer {bearer_token}',
        'accept': 'application/json'
    }
    
    # Test with a simple movie endpoint
    url = "https://api.themoviedb.org/3/movie/11"  # Star Wars: A New Hope
    
    print("🔍 Testing API call to TMDB...")
    try:
        response = requests.get(url, headers=headers)
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            title = data.get('title', 'Unknown')
            print(f"✅ Authentication successful!")
            print(f"🎬 Movie title: {title}")
            return True
        else:
            print(f"❌ Authentication failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False

if __name__ == "__main__":
    success = test_tmdb_auth()
    if success:
        print("\n🎉 TMDB Bearer token authentication is working!")
        print("📝 You can now use the Future Downloads feature")
    else:
        print("\n❌ TMDB authentication failed!")
        print("📝 Please check your Bearer token") 