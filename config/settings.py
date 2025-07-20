import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    
    # Authorized Users
    AUTHORIZED_USERS = [
        int(user_id.strip()) 
        for user_id in os.getenv('AUTHORIZED_USERS', '').split(',') 
        if user_id.strip()
    ]
    
    # Pagination
    RESULTS_PER_PAGE = 8
    
    # Prowlarr API
    PROWLARR_API_BASE_URL = "http://localhost:9696"
    
    # TMDB API Configuration
    TMDB_API_KEY = os.getenv('TMDB_API_KEY')  # This should be your Bearer token
    TMDB_BASE_URL = "https://api.themoviedb.org/3" 