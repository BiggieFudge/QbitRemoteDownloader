import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

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
    
    def get_user_downloads(self, user_id: int, hours: int = 24) -> List[Dict]:
        """Get downloads for a user from the last N hours (default: 24 hours)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, torrent_id, status, created_at, completed_at
                    FROM downloads 
                    WHERE user_id = ?
                    AND created_at >= datetime('now', '-{} hours')
                    ORDER BY created_at DESC
                '''.format(hours), (user_id,))
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
                logger.info(f"[DB] Updated session for user {user_id}: state={state}, query={search_query}, page={current_page}")
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
                    session_data = {
                        'current_state': result[0],
                        'search_query': result[1],
                        'current_page': result[2]
                    }
                    logger.debug(f"[DB] Retrieved session for user {user_id}: {session_data}")
                    return session_data
                logger.debug(f"[DB] No session found for user {user_id}")
                return None
        except Exception as e:
            logger.error(f"Error getting user session: {e}")
            return None
    
    def create_user_session(self, user_id: int, state: str = 'idle'):
        """Create a new user session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO user_sessions 
                    (user_id, current_state, last_activity)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, state))
                conn.commit()
                logger.info(f"[DB] Created session for user {user_id} with state: {state}")
        except Exception as e:
            logger.error(f"Error creating user session: {e}")
    
    def clear_user_session(self, user_id: int):
        """Clear user session state."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM user_sessions 
                    WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                logger.info(f"[DB] Cleared session for user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing user session: {e}") 

    def cleanup_old_downloads(self, hours: int = 24) -> int:
        """Clean up downloads older than N hours (default: 24 hours). Returns number of deleted records."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM downloads 
                    WHERE created_at < datetime('now', '-{} hours')
                '''.format(hours))
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"[DB] Cleaned up {deleted_count} downloads older than {hours} hours")
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old downloads: {e}")
            return 0
    
    def get_download_statistics(self, user_id: int, hours: int = 24) -> Dict:
        """Get download statistics for a user from the last N hours."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get total downloads in time period
                cursor.execute('''
                    SELECT COUNT(*) FROM downloads 
                    WHERE user_id = ? 
                    AND created_at >= datetime('now', '-{} hours')
                '''.format(hours), (user_id,))
                total_downloads = cursor.fetchone()[0]
                
                # Get completed downloads
                cursor.execute('''
                    SELECT COUNT(*) FROM downloads 
                    WHERE user_id = ? 
                    AND status = 'completed'
                    AND created_at >= datetime('now', '-{} hours')
                '''.format(hours), (user_id,))
                completed_downloads = cursor.fetchone()[0]
                
                # Get downloading count
                cursor.execute('''
                    SELECT COUNT(*) FROM downloads 
                    WHERE user_id = ? 
                    AND status = 'downloading'
                    AND created_at >= datetime('now', '-{} hours')
                '''.format(hours), (user_id,))
                downloading_count = cursor.fetchone()[0]
                
                return {
                    'total_downloads': total_downloads,
                    'completed_downloads': completed_downloads,
                    'downloading_count': downloading_count,
                    'time_period_hours': hours
                }
        except Exception as e:
            logger.error(f"Error getting download statistics: {e}")
            return {
                'total_downloads': 0,
                'completed_downloads': 0,
                'downloading_count': 0,
                'time_period_hours': hours
            }
    
    def get_all_downloads_older_than(self, hours: int) -> List[Tuple]:
        """Get all downloads older than N hours (for cleanup purposes)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, user_id, title, created_at
                    FROM downloads 
                    WHERE created_at < datetime('now', '-{} hours')
                    ORDER BY created_at ASC
                '''.format(hours))
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting old downloads: {e}")
            return [] 