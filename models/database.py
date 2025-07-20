import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str = "downloads.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Downloads table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS downloads (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        title TEXT NOT NULL,
                        torrent_id TEXT NOT NULL,
                        magnet_link TEXT NOT NULL,
                        download_path TEXT NOT NULL,
                        status TEXT DEFAULT 'downloading',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP NULL
                    )
                ''')
                
                # User sessions table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_sessions (
                        user_id INTEGER PRIMARY KEY,
                        current_state TEXT DEFAULT 'idle',
                        search_query TEXT NULL,
                        current_page INTEGER DEFAULT 0,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("Database initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def add_download(self, user_id: int, title: str, torrent_id: str, 
                     magnet_link: str, download_path: str) -> int:
        """Add a new download to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO downloads (user_id, title, torrent_id, magnet_link, download_path)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, title, torrent_id, magnet_link, download_path))
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"Error adding download: {e}")
            return None
    
    def update_download_status(self, download_id: int, status: str):
        """Update download status."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if status == 'completed':
                    cursor.execute('''
                        UPDATE downloads 
                        SET status = ?, completed_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    ''', (status, download_id))
                else:
                    cursor.execute('''
                        UPDATE downloads 
                        SET status = ?
                        WHERE id = ?
                    ''', (status, download_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating download status: {e}")
    
    def get_user_downloads(self, user_id: int) -> List[Dict]:
        """Get all downloads for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, torrent_id, status, created_at, completed_at
                    FROM downloads 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting user downloads: {e}")
            return []
    
    def update_user_session(self, user_id: int, state: str, search_query: str = None, 
                           current_page: int = 0):
        """Update user session state."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    (user_id, current_state, search_query, current_page, last_activity)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, state, search_query, current_page))
                conn.commit()
        except Exception as e:
            logger.error(f"Error updating user session: {e}")
    
    def get_user_session(self, user_id: int) -> Optional[Dict]:
        """Get user session state."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT current_state, search_query, current_page
                    FROM user_sessions 
                    WHERE user_id = ?
                ''', (user_id,))
                result = cursor.fetchone()
                if result:
                    return {
                        'current_state': result[0],
                        'search_query': result[1],
                        'current_page': result[2]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting user session: {e}")
            return None 