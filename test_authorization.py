#!/usr/bin/env python3
"""
Test script to verify authorization setup and troubleshoot user access issues.
"""

import os
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_authorization_setup():
    """Test the authorization setup and environment variables."""
    print("🔍 Testing Authorization Setup")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Test environment variables
    print("\n📋 Environment Variables:")
    print("-" * 30)
    
    telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    print(f"TELEGRAM_BOT_TOKEN: {'✅ Set' if telegram_token else '❌ Missing'}")
    if telegram_token:
        print(f"  Token preview: {telegram_token[:10]}...")
    
    prowlarr_api = os.getenv('PROWLARR_API_KEY')
    print(f"PROWLARR_API_KEY: {'✅ Set' if prowlarr_api else '❌ Missing'}")
    
    tmdb_api = os.getenv('TMDB_API_KEY')
    print(f"TMDB_API_KEY: {'✅ Set' if tmdb_api else '❌ Missing'}")
    
    # Test authorized users parsing
    print("\n👥 Authorized Users:")
    print("-" * 30)
    
    authorized_users_str = os.getenv('AUTHORIZED_USERS', '')
    print(f"Raw AUTHORIZED_USERS: '{authorized_users_str}'")
    
    if not authorized_users_str.strip():
        print("❌ AUTHORIZED_USERS is empty or not set!")
        print("\n💡 To fix this:")
        print("1. Add your Telegram user ID to the .env file:")
        print("   AUTHORIZED_USERS=123456789")
        print("2. For multiple users, separate with commas:")
        print("   AUTHORIZED_USERS=123456789,987654321")
        print("3. Get your user ID from @userinfobot on Telegram")
        return
    
    # Parse authorized users
    try:
        user_ids = []
        for user_id_str in authorized_users_str.split(','):
            user_id_str = user_id_str.strip()
            if user_id_str:
                try:
                    user_id = int(user_id_str)
                    user_ids.append(user_id)
                    print(f"✅ Parsed user ID: {user_id}")
                except ValueError as e:
                    print(f"❌ Failed to parse '{user_id_str}': {e}")
        
        print(f"\n📊 Summary:")
        print(f"Total authorized users: {len(user_ids)}")
        print(f"User IDs: {user_ids}")
        
        if len(user_ids) == 0:
            print("❌ No valid user IDs found!")
            print("Check your .env file and make sure AUTHORIZED_USERS contains valid numbers.")
        
    except Exception as e:
        print(f"❌ Error parsing authorized users: {e}")
    
    # Test settings import
    print("\n⚙️ Testing Settings Import:")
    print("-" * 30)
    
    try:
        from config.settings import Settings
        settings = Settings()
        print(f"✅ Settings imported successfully")
        print(f"Authorized users from settings: {settings.AUTHORIZED_USERS}")
        print(f"Number of authorized users: {len(settings.AUTHORIZED_USERS)}")
        
        if len(settings.AUTHORIZED_USERS) == 0:
            print("❌ No authorized users in settings!")
            print("This means only the bot owner can use the bot.")
        
    except Exception as e:
        print(f"❌ Error importing settings: {e}")
    
    print("\n" + "=" * 50)
    print("🔧 Troubleshooting Tips:")
    print("1. Make sure your .env file exists in the project root")
    print("2. Get your Telegram user ID from @userinfobot")
    print("3. Add your user ID to AUTHORIZED_USERS in .env")
    print("4. Restart the bot after changing .env")
    print("5. Use /debug command in the bot to check your user ID")

if __name__ == "__main__":
    test_authorization_setup() 