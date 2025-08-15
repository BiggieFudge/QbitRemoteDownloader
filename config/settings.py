import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class Settings:
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Prowlarr Configuration
    PROWLARR_API_KEY = os.getenv('PROWLARR_API_KEY')
    PROWLARR_BASE_URL = os.getenv('PROWLARR_BASE_URL', 'http://localhost:9696')
    
    # qBittorrent Configuration
    QBITTORRENT_HOST = os.getenv('QBITTORRENT_HOST', 'localhost')
    QBITTORRENT_PORT = int(os.getenv('QBITTORRENT_PORT', 8080))
    QBITTORRENT_USERNAME = os.getenv('QBITTORRENT_USERNAME', 'admin')
    QBITTORRENT_PASSWORD = os.getenv('QBITTORRENT_PASSWORD', 'admin')
    
    # Download Paths
    MOVIES_DOWNLOAD_PATH = os.getenv('MOVIES_DOWNLOAD_PATH', 'E:\\Movies')
    TVSHOWS_DOWNLOAD_PATH = os.getenv('TVSHOWS_DOWNLOAD_PATH', 'E:\\TVShows')
    
    # Authorized Users - Improved parsing with better error handling
    def _parse_authorized_users():
        """Parse authorized users from environment variable with better error handling."""
        authorized_users_str = os.getenv('AUTHORIZED_USERS', '')
        logger.info(f"Raw AUTHORIZED_USERS environment variable: '{authorized_users_str}'")
        
        if not authorized_users_str.strip():
            logger.warning("AUTHORIZED_USERS environment variable is empty or not set!")
            return []
        
        try:
            # Split by comma and clean up each user ID
            user_ids = []
            for user_id_str in authorized_users_str.split(','):
                user_id_str = user_id_str.strip()
                if user_id_str:  # Only process non-empty strings
                    try:
                        user_id = int(user_id_str)
                        user_ids.append(user_id)
                        logger.debug(f"Successfully parsed user ID: {user_id}")
                    except ValueError as e:
                        logger.error(f"Failed to parse user ID '{user_id_str}': {e}")
            
            logger.info(f"Successfully parsed {len(user_ids)} authorized users: {user_ids}")
            return user_ids
            
        except Exception as e:
            logger.error(f"Error parsing AUTHORIZED_USERS: {e}")
            return []
    
    AUTHORIZED_USERS = _parse_authorized_users()
    
    # Pagination
    RESULTS_PER_PAGE = 8
    
    # Prowlarr API
    PROWLARR_API_BASE_URL = "http://localhost:9696"
    
    # TMDB API Configuration
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')  # This should be your Bearer token
    TMDB_BASE_URL = "https://api.themoviedb.org/3" 