import qbittorrentapi
import logging
import asyncio
import os
from typing import Dict, Optional, List
from config.settings import Settings

logger = logging.getLogger(__name__)

class QBittorrentClient:
    def __init__(self):
        self.client = qbittorrentapi.Client(
            host=Settings.QBITTORRENT_HOST,
            port=Settings.QBITTORRENT_PORT,
            username=Settings.QBITTORRENT_USERNAME,
            password=Settings.QBITTORRENT_PASSWORD
        )
        self._connect()
    
    def _connect(self):
        """Connect to qBittorrent Web API."""
        try:
            self.client.auth_log_in()
            logger.info("Successfully connected to qBittorrent")
        except Exception as e:
            logger.error(f"Failed to connect to qBittorrent: {e}")
            raise
    
    def add_magnet_link(self, magnet_link: str, save_path: str, 
                       category: str = None) -> Optional[str]:
        """
        Add a magnet link to qBittorrent for downloading.
        
        Args:
            magnet_link: The magnet link to download
            save_path: Directory to save the download
            category: Optional category for the torrent
        
        Returns:
            Hash of the added torrent or None if failed
        """
        try:
            # Create save path if it doesn't exist
            os.makedirs(save_path, exist_ok=True)
            
            # Add the torrent
            torrent = self.client.torrents_add(
                urls=magnet_link,
                save_path=save_path,
                category=category
            )
            
            logger.info(f"Added torrent with hash: {torrent}")
            return torrent
            
        except Exception as e:
            logger.error(f"Error adding magnet link: {e}")
            return None
    
    def get_torrent_info(self, torrent_hash: str) -> Optional[Dict]:
        """Get information about a specific torrent."""
        try:
            torrents = self.client.torrents_info(hashes=torrent_hash)
            if torrents:
                torrent = torrents[0]
                return {
                    'hash': torrent.hash,
                    'name': torrent.name,
                    'size': torrent.size,
                    'progress': torrent.progress,
                    'download_speed': torrent.dlspeed,
                    'upload_speed': torrent.upspeed,
                    'state': torrent.state,
                    'save_path': torrent.save_path,
                    'category': torrent.category,
                    'ratio': torrent.ratio,
                    'eta': torrent.eta,
                    'num_seeds': torrent.num_seeds,
                    'num_leechs': torrent.num_leechs
                }
            return None
        except Exception as e:
            logger.error(f"Error getting torrent info: {e}")
            return None
    
    def get_all_torrents(self) -> List[Dict]:
        """Get information about all torrents."""
        try:
            torrents = self.client.torrents_info()
            return [
                {
                    'hash': torrent.hash,
                    'name': torrent.name,
                    'size': torrent.size,
                    'progress': torrent.progress,
                    'state': torrent.state,
                    'save_path': torrent.save_path,
                    'category': torrent.category
                }
                for torrent in torrents
            ]
        except Exception as e:
            logger.error(f"Error getting all torrents: {e}")
            return []
    
    def is_torrent_completed(self, torrent_hash: str) -> bool:
        """Check if a torrent has completed downloading."""
        try:
            torrent_info = self.get_torrent_info(torrent_hash)
            if torrent_info:
                return torrent_info['progress'] == 1.0
            return False
        except Exception as e:
            logger.error(f"Error checking torrent completion: {e}")
            return False
    
    def remove_torrent(self, torrent_hash: str, delete_files: bool = False):
        """Remove a torrent from qBittorrent."""
        try:
            self.client.torrents_delete(
                hashes=torrent_hash,
                delete_files=delete_files
            )
            logger.info(f"Removed torrent: {torrent_hash}")
        except Exception as e:
            logger.error(f"Error removing torrent: {e}")
    
    def pause_torrent(self, torrent_hash: str):
        """Pause a torrent."""
        try:
            self.client.torrents_pause(hashes=torrent_hash)
            logger.info(f"Paused torrent: {torrent_hash}")
        except Exception as e:
            logger.error(f"Error pausing torrent: {e}")
    
    def resume_torrent(self, torrent_hash: str):
        """Resume a torrent."""
        try:
            self.client.torrents_resume(hashes=torrent_hash)
            logger.info(f"Resumed torrent: {torrent_hash}")
        except Exception as e:
            logger.error(f"Error resuming torrent: {e}")
    
    def get_download_stats(self) -> Dict:
        """Get overall download statistics."""
        try:
            sync_maindata = self.client.sync_maindata()
            return {
                'total_download_speed': sync_maindata.get('server_state', {}).get('dl_info_speed', 0),
                'total_upload_speed': sync_maindata.get('server_state', {}).get('up_info_speed', 0),
                'total_downloaded': sync_maindata.get('server_state', {}).get('dl_info_data', 0),
                'total_uploaded': sync_maindata.get('server_state', {}).get('up_info_data', 0)
            }
        except Exception as e:
            logger.error(f"Error getting download stats: {e}")
            return {}
    
    def get_categories(self) -> List[str]:
        """Get all available categories."""
        try:
            return list(self.client.torrents_categories().keys())
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return []
    
    def create_category(self, category_name: str, save_path: str):
        """Create a new category."""
        try:
            self.client.torrents_create_category(
                name=category_name,
                save_path=save_path
            )
            logger.info(f"Created category: {category_name}")
        except Exception as e:
            logger.error(f"Error creating category: {e}")
    
    def get_download_path(self, content_type: str, title: str) -> str:
        """
        Get the appropriate download path based on content type and title.
        
        Args:
            content_type: 'movie' or 'tv'
            title: Title of the content
        
        Returns:
            Full download path
        """
        if content_type == 'movie':
            base_path = Settings.MOVIES_DOWNLOAD_PATH
        else:
            base_path = Settings.TVSHOWS_DOWNLOAD_PATH
        
        # Clean title for filesystem compatibility
        clean_title = self._clean_title_for_path(title)
        return os.path.join(base_path, clean_title)
    
    def _clean_title_for_path(self, title: str) -> str:
        """Clean title for use as directory name."""
        import re
        # Remove special characters and replace with spaces
        clean_title = re.sub(r'[<>:"/\\|?*]', ' ', title)
        # Replace multiple spaces with single space
        clean_title = re.sub(r'\s+', ' ', clean_title)
        # Remove leading/trailing spaces
        clean_title = clean_title.strip()
        return clean_title 

    def test_rss_api(self) -> bool:
        """Test if RSS API endpoints are available."""
        try:
            # Test getting RSS rules using the API
            rules = self.client.rss_rules()
            logger.info(f"[qBittorrent] RSS API is available - found {len(rules)} rules")
            return True
        except Exception as e:
            logger.error(f"[qBittorrent] Error testing RSS API: {e}")
            return False
    
    def get_rss_feeds(self) -> List[Dict]:
        """Get RSS feeds to check if any are configured."""
        try:
            feeds = self.client.rss_items()
            return feeds
        except Exception as e:
            logger.error(f"Error getting RSS feeds: {e}")
            return []
    
    def create_auto_download_rule(self, rule_name: str, rule_definition: dict) -> bool:
        """Create an auto-download rule in qBittorrent."""
        try:
            # Get the TorrentLeech feed URL to assign the rule properly
            try:
                feeds = self.client.rss_items()
                if isinstance(feeds, dict) and 'TorrentLeech' in feeds:
                    torrentleech_feed = feeds['TorrentLeech']
                    if hasattr(torrentleech_feed, 'url'):
                        feed_url = torrentleech_feed.url
                        rule_definition['affectedFeeds'] = [feed_url]
                    else:
                        rule_definition['affectedFeeds'] = []
                else:
                    rule_definition['affectedFeeds'] = []
            except Exception as e:
                logger.error(f"Error getting TorrentLeech feed URL: {e}")
                rule_definition['affectedFeeds'] = []
            
            # Use the qbittorrentapi method
            self.client.rss_set_rule(
                rule_name=rule_name,
                rule_def=rule_definition
            )
            
            logger.info(f"Successfully created auto-download rule: {rule_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating auto-download rule: {e}")
            return False
    
    def create_movie_rule(self, movie_title: str, quality: str = "1080p", save_path: str = None, movie_data: dict = None) -> bool:
        """Create an auto-download rule for a movie."""
        if not save_path:
            save_path = Settings.MOVIES_DOWNLOAD_PATH
        
        # Create regex pattern for the movie title
        # Escape special characters and create a flexible pattern
        escaped_title = movie_title.replace(' ', '\\s+').replace('(', '\\(').replace(')', '\\)')
        year = None
        if movie_data:
            year = movie_data.get('release_date', '')[:4]
            if not year:
                year = movie_data.get('year', '')
        if year and year.isdigit():
            must_contain = f"{escaped_title}.*{year}.*{quality}"
        else:
            must_contain = f"{escaped_title}.*{quality}"
        
        rule_definition = {
            "enabled": True,
            "mustContain": must_contain,
            "mustNotContain": "",
            "useRegex": True,
            "episodeFilter": "",
            "smartFilter": False,
            "previouslyMatchedEpisodes": [],
            "affectedFeeds": [],
            "ignoreDays": 0,
            "lastMatch": "",
            "addPaused": False,
            "assignedCategory": "movies",
            "savePath": save_path
        }
        
        rule_name = f"Auto_{movie_title}_{quality}"
        return self.create_auto_download_rule(rule_name, rule_definition)
    
    def create_tv_show_rule(self, show_title: str, quality: str = "1080p", save_path: str = None, tv_data: dict = None) -> bool:
        """Create an auto-download rule for a TV show with smart episode filtering."""
        if not save_path:
            save_path = Settings.TVSHOWS_DOWNLOAD_PATH
        
        # Use TMDB data to create regex pattern and episode filter if available
        episode_filter = "1x01-;"  # Default fallback
        if tv_data:
            from services.tmdb_client import TMDBClient
            tmdb_client = TMDBClient()
            regex_pattern = tmdb_client.create_tv_show_regex_pattern(tv_data)
            
            # Get episode filter based on last season info
            last_season_info = tmdb_client.get_last_season_info(tv_data)
            if last_season_info:
                season_number = last_season_info['season_number']
                episode_count = last_season_info['episode_count']
                
                # If episode_count is 0, use 99 as fallback, otherwise use the actual count
                if episode_count == 0:
                    episode_count = 99
                
                # Create episode filter: Sx01-EpisodeCount
                # For example: Season 3 with 10 episodes -> "3x01-10;"
                episode_filter = f"{season_number}x01-{episode_count};"
            
            if regex_pattern:
                # Add quality to the regex pattern
                must_contain = f"{regex_pattern}.*{quality}"
            else:
                # Fallback to simple pattern
                escaped_title = show_title.replace(' ', '\\s+').replace('(', '\\(').replace(')', '\\)')
                must_contain = f"{escaped_title}.*{quality}"
        else:
            # Create regex pattern for the show title (fallback)
            escaped_title = show_title.replace(' ', '\\s+').replace('(', '\\(').replace(')', '\\)')
            must_contain = f"{escaped_title}.*{quality}"
        
        rule_definition = {
            "enabled": True,
            "mustContain": must_contain,
            "mustNotContain": "",
            "useRegex": True,
            "episodeFilter": episode_filter,  # Dynamic episode filter based on TMDB data
            "smartFilter": True,
            "previouslyMatchedEpisodes": [],
            "affectedFeeds": [],
            "ignoreDays": 0,
            "lastMatch": "",
            "addPaused": False,
            "assignedCategory": "tv",
            "savePath": save_path
        }
        
        rule_name = f"Auto_{show_title}_{quality}"
        return self.create_auto_download_rule(rule_name, rule_definition)
    
    def get_auto_download_rules(self) -> List[Dict]:
        """Get all auto-download rules."""
        try:
            rules = self.client.rss_rules()
            return rules
        except Exception as e:
            logger.error(f"Error getting auto-download rules: {e}")
            return []
    
    def delete_auto_download_rule(self, rule_name: str) -> bool:
        """Delete an auto-download rule."""
        try:
            self.client.rss_remove_rule(rule_name=rule_name)
            logger.info(f"Successfully deleted auto-download rule: {rule_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting auto-download rule: {e}")
            return False 

    def test_rss_feeds_working(self) -> bool:
        """Test if RSS feeds are working and have content."""
        try:
            # Get RSS items
            items = self.client.rss_items()
            if not items:
                logger.warning("[qBittorrent] No RSS items found")
                return False
            
            # Check if items have content
            total_items = 0
            if isinstance(items, dict):
                for feed_name, feed_items in items.items():
                    if isinstance(feed_items, list):
                        total_items += len(feed_items)
                        logger.info(f"[qBittorrent] Feed '{feed_name}' has {len(feed_items)} items")
                    else:
                        logger.warning(f"[qBittorrent] Feed '{feed_name}' has no items")
            else:
                total_items = len(items)
                logger.info(f"[qBittorrent] Found {total_items} RSS items")
            
            if total_items > 0:
                logger.info(f"[qBittorrent] RSS feeds are working with {total_items} total items")
                return True
            else:
                logger.warning("[qBittorrent] RSS feeds have no content")
                return False
                
        except Exception as e:
            logger.error(f"[qBittorrent] Error testing RSS feeds: {e}")
            return False
    
    def refresh_rss_feeds(self) -> bool:
        """Refresh RSS feeds to get latest content."""
        try:
            self.client.rss_refresh_item()
            logger.info("[qBittorrent] RSS feeds refreshed")
            return True
        except Exception as e:
            logger.error(f"[qBittorrent] Error refreshing RSS feeds: {e}")
            return False 