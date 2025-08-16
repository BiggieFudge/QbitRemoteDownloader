import qbittorrentapi
import logging
import asyncio
import os
import re
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
    
    def get_download_path(self, content_type: str, title: str, year: str = None, season: str = None) -> str:
        """
        Get the appropriate download path based on content type and title.
        
        Args:
            content_type: 'movie' or 'tv'
            title: Title of the content
            year: Year for movies
            season: Season for TV shows
        
        Returns:
            Full download path
        """
        if content_type == 'movie':
            base_path = Settings.MOVIES_DOWNLOAD_PATH
            # For movies: Movie Name (Year)
            if year:
                folder_name = f"{title} ({year})"
            else:
                folder_name = title
        else:
            base_path = Settings.TVSHOWS_DOWNLOAD_PATH
            # For TV shows: Extract just the show name from the torrent title
            folder_name = self._extract_tv_show_name(title)
        
        # Clean title for filesystem compatibility
        clean_folder_name = self._clean_title_for_path(folder_name)
        return os.path.join(base_path, clean_folder_name)
    
    def _extract_tv_show_name(self, torrent_title: str) -> str:
        """
        Extract the TV show name from a torrent title.
        
        Args:
            torrent_title: Full torrent title (e.g., "Family Guy S01-S20 The Uncensored Collection 1080p...")
        
        Returns:
            Clean TV show name (e.g., "Family Guy")
        """
        # First, try to find the show name by looking for common patterns
        # Look for patterns like "Show Name S01" or "Show Name Season 1"
        
        # Pattern 1: Show Name followed by S\d+ (most common)
        match = re.search(r'^(.+?)\s+S\d+', torrent_title, re.IGNORECASE)
        if match:
            show_name = match.group(1).strip()
            if show_name and len(show_name) > 1:
                return show_name
        
        # Pattern 2: Show Name followed by Season \d+
        match = re.search(r'^(.+?)\s+Season\s+\d+', torrent_title, re.IGNORECASE)
        if match:
            show_name = match.group(1).strip()
            if show_name and len(show_name) > 1:
                return show_name
        
        # Pattern 3: Show Name followed by S\d+E\d+
        match = re.search(r'^(.+?)\s+S\d+E\d+', torrent_title, re.IGNORECASE)
        if match:
            show_name = match.group(1).strip()
            if show_name and len(show_name) > 1:
                return show_name
        
        # Pattern 4: Show Name followed by Complete Series
        match = re.search(r'^(.+?)\s+Complete\s+Series', torrent_title, re.IGNORECASE)
        if match:
            show_name = match.group(1).strip()
            if show_name and len(show_name) > 1:
                return show_name
        
        # Pattern 5: Show Name followed by Collection
        match = re.search(r'^(.+?)\s+Collection', torrent_title, re.IGNORECASE)
        if match:
            show_name = match.group(1).strip()
            if show_name and len(show_name) > 1:
                return show_name
        
        # If no patterns match, try to extract by removing common suffixes
        # This is a fallback method
        cleaned_title = torrent_title
        
        # Remove common torrent metadata patterns
        patterns_to_remove = [
            # Season patterns
            r'\s+S\d{1,2}(?:-S?\d{1,2})?',
            r'\s+Season\s+\d+',
            r'\s+S\d{1,2}E\d{1,2}',
            # Quality patterns
            r'\s+\d{3,4}p',
            r'\s+4K',
            r'\s+UHD',
            # Source patterns
            r'\s+(?:BluRay|WEBRip|HDTV|DVDRip|BRRip)',
            # Audio patterns
            r'\s+(?:DDP\d+|DD\d+Ch|AAC|AC3)',
            # Video codec patterns
            r'\s+(?:HEVC|x264|x265|AVC)',
            # Bit depth patterns
            r'\s+\d+Bit',
            # Collection/Complete patterns
            r'\s+(?:Collection|Complete|Boxset|Box\s*Set|Series)',
            # Group names (usually at the end with - or .)
            r'\s*[-.]\s*[A-Za-z0-9]+$',
            # Additional descriptive text
            r'\s+(?:The\s+)?(?:Uncensored|Extended|Director\'s\s+Cut|Special\s+Edition)',
            # Year patterns
            r'\s+\(\d{4}\)',
            r'\s+\d{4}',
        ]
        
        for pattern in patterns_to_remove:
            cleaned_title = re.sub(pattern, '', cleaned_title, flags=re.IGNORECASE)
        
        # Clean up any remaining artifacts
        cleaned_title = re.sub(r'\s+', ' ', cleaned_title)  # Multiple spaces to single space
        cleaned_title = cleaned_title.strip()
        
        # If we end up with an empty string or very short string, fall back to the original title
        if not cleaned_title or len(cleaned_title) < 2:
            return torrent_title
        
        return cleaned_title
    
    def _clean_title_for_path(self, title: str) -> str:
        """Clean title for use as directory name."""
        # Remove special characters and replace with spaces
        clean_title = re.sub(r'[<>:"/\\|?*]', ' ', title)
        # Replace multiple spaces with single space
        clean_title = re.sub(r'\s+', ' ', clean_title)
        # Remove leading/trailing spaces
        clean_title = clean_title.strip()
        return clean_title
    
    def find_torrent_by_name(self, search_title: str, content_type: str = None, magnet_link: str = None) -> Optional[Dict]:
        """
        Find a torrent by name using improved search logic.
        
        Args:
            search_title: Title to search for
            content_type: 'movie' or 'tv' to help with search logic
            magnet_link: Optional magnet link to extract torrent name from
        
        Returns:
            Torrent info dict if found, None otherwise
        """
        try:
            all_torrents = self.get_all_torrents()
            
            # Create multiple search patterns
            search_patterns = []
            
            # If we have a magnet link, try to extract the torrent name from it first
            if magnet_link:
                from utils.helpers import extract_torrent_name_from_magnet, clean_torrent_name_for_search
                magnet_torrent_name = extract_torrent_name_from_magnet(magnet_link)
                if magnet_torrent_name:
                    cleaned_magnet_name = clean_torrent_name_for_search(magnet_torrent_name)
                    if cleaned_magnet_name:
                        # Add magnet-extracted name patterns
                        search_patterns.append(cleaned_magnet_name.lower())
                        search_patterns.append(cleaned_magnet_name.replace(' ', '.').lower())
                        search_patterns.append(cleaned_magnet_name.replace(' ', '_').lower())
                        logger.info(f"Using magnet-extracted name for search: {cleaned_magnet_name}")
            
            # Original title patterns
            search_patterns.append(search_title.lower())
            search_patterns.append(search_title.replace(' ', '.').lower())
            search_patterns.append(search_title.replace(' ', '_').lower())
            
            # Remove common words and search
            common_words = ['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']
            words = search_title.lower().split()
            filtered_words = [word for word in words if word not in common_words]
            if filtered_words:
                search_patterns.append(' '.join(filtered_words).lower())
                search_patterns.append('.'.join(filtered_words).lower())
            
            # For TV shows, also try without episode info
            if content_type == 'tv':
                # Remove season/episode patterns
                tv_title = re.sub(r'\s*S\d{1,2}E\d{1,2}.*$', '', search_title, flags=re.IGNORECASE)
                if tv_title != search_title:
                    search_patterns.append(tv_title.lower())
                    search_patterns.append(tv_title.replace(' ', '.').lower())
            
            # Remove duplicates while preserving order
            seen = set()
            unique_patterns = []
            for pattern in search_patterns:
                if pattern not in seen:
                    seen.add(pattern)
                    unique_patterns.append(pattern)
            
            logger.debug(f"Search patterns for '{search_title}': {unique_patterns}")
            
            # Search through all torrents
            for torrent in all_torrents:
                torrent_name = torrent['name'].lower()
                
                # Check each search pattern
                for pattern in unique_patterns:
                    if pattern in torrent_name:
                        logger.info(f"Found torrent '{torrent['name']}' matching pattern '{pattern}' for search '{search_title}'")
                        return torrent
            
            logger.info(f"No torrent found matching any pattern for '{search_title}'")
            return None
            
        except Exception as e:
            logger.error(f"Error finding torrent by name: {e}")
            return None

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
            logger.info(f"[RULE_CREATE] Creating rule: '{rule_name}'")
            logger.info(f"[RULE_CREATE] Rule definition: {rule_definition}")
            
            # Get RSS feeds and assign the rule to the first available feed
            try:
                feeds = self.client.rss_items()
                logger.info(f"[RULE_CREATE] Available feeds: {feeds}")
                
                # Find the first available feed URL
                feed_url = None
                if isinstance(feeds, dict):
                    for feed_name, feed_data in feeds.items():
                        if hasattr(feed_data, 'url') and feed_data.url:
                            feed_url = feed_data.url
                            logger.info(f"[RULE_CREATE] Using feed '{feed_name}': {feed_url}")
                            break
                        elif isinstance(feed_data, dict) and feed_data.get('url'):
                            feed_url = feed_data['url']
                            logger.info(f"[RULE_CREATE] Using feed '{feed_name}': {feed_url}")
                            break
                
                if feed_url:
                    rule_definition['affectedFeeds'] = [feed_url]
                    logger.info(f"[RULE_CREATE] Assigned rule to feed: {feed_url}")
                else:
                    # If no feeds found, try to get feeds using different method
                    try:
                        feed_list = self.client.rss_feeds()
                        if feed_list and len(feed_list) > 0:
                            first_feed = feed_list[0]
                            if hasattr(first_feed, 'url'):
                                feed_url = first_feed.url
                                rule_definition['affectedFeeds'] = [feed_url]
                                logger.info(f"[RULE_CREATE] Using first feed from rss_feeds(): {feed_url}")
                            elif isinstance(first_feed, dict) and first_feed.get('url'):
                                feed_url = first_feed['url']
                                rule_definition['affectedFeeds'] = [feed_url]
                                logger.info(f"[RULE_CREATE] Using first feed from rss_feeds(): {feed_url}")
                    except Exception as e2:
                        logger.warning(f"[RULE_CREATE] Could not get feeds from rss_feeds(): {e2}")
                    
                    if not feed_url:
                        logger.warning("[RULE_CREATE] No RSS feeds found, rule may not work properly")
                        rule_definition['affectedFeeds'] = []
                        
            except Exception as e:
                logger.error(f"Error getting RSS feeds: {e}")
                rule_definition['affectedFeeds'] = []
            
            logger.info(f"[RULE_CREATE] Final rule definition: {rule_definition}")
            
            # Use the qbittorrentapi method
            result = self.client.rss_set_rule(
                rule_name=rule_name,
                rule_def=rule_definition
            )
            
            logger.info(f"[RULE_CREATE] API response: {result}")
            logger.info(f"Successfully created auto-download rule: {rule_name}")
            return True
        except Exception as e:
            logger.error(f"Error creating auto-download rule: {e}")
            return False
    
    def create_movie_rule(self, movie_title: str, quality: str = "1080p", save_path: str = None, movie_data: dict = None) -> bool:
        """Create an auto-download rule for a movie."""
        if not save_path:
            save_path = self.get_download_path('movie', movie_title, movie_data.get('year') if movie_data else None)
        
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
            "ignoreDays": 365,  # Ignore subsequent matches for 365 days
            "lastMatch": "",
            "addPaused": False,
            "assignedCategory": "movies",
            "savePath": save_path
        }
        
        rule_name = f"{movie_title}_{quality}"
        logger.info(f"[MOVIE_RULE_CREATE] Creating rule with name: '{rule_name}'")
        logger.info(f"[MOVIE_RULE_CREATE] Movie title: '{movie_title}', Quality: '{quality}', Year: '{year}'")
        
        return self.create_auto_download_rule(rule_name, rule_definition)
    
    def create_upcoming_movie_rule(self, movie_title: str, quality: str = "1080p", save_path: str = None, movie_data: dict = None) -> bool:
        """Create an auto-download rule for an upcoming movie with ignore subsequent matches for 365 days."""
        if not save_path:
            save_path = self.get_download_path('movie', movie_title, movie_data.get('year') if movie_data else None)
        
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
            "ignoreDays": 365,  # Ignore subsequent matches for 365 days
            "lastMatch": "",
            "addPaused": False,
            "assignedCategory": "movies",
            "savePath": save_path
        }
        
        rule_name = f"{movie_title}_{quality}_Upcoming"
        logger.info(f"[UPCOMING_MOVIE_RULE_CREATE] Creating upcoming movie rule with name: '{rule_name}'")
        logger.info(f"[UPCOMING_MOVIE_RULE_CREATE] Movie title: '{movie_title}', Quality: '{quality}', Year: '{year}', IgnoreDays: 365")
        
        return self.create_auto_download_rule(rule_name, rule_definition)
    
    def create_tv_show_rule(self, show_title: str, quality: str = "1080p", save_path: str = None, tv_data: dict = None, season: str = None, episode: str = None) -> bool:
        """Create an auto-download rule for a TV show with user-specified season and episode."""
        if not save_path:
            save_path = self.get_download_path('tv', show_title)
        
        # Create regex pattern for the show title
        escaped_title = show_title.replace(' ', '\\s+').replace('(', '\\(').replace(')', '\\)')
        
        # Build the must contain pattern
        if season and episode:
            # Specific season and episode
            must_contain = f"{escaped_title}.*S{season.zfill(2)}E{episode.zfill(2)}.*{quality}"
            episode_filter = f"{season}x{episode.zfill(2)};"
        elif season:
            # Specific season only
            must_contain = f"{escaped_title}.*S{season.zfill(2)}.*{quality}"
            episode_filter = f"{season}x01-99;"
        else:
            # General show pattern
            must_contain = f"{escaped_title}.*{quality}"
            episode_filter = "1x01-99;"  # Default fallback
        
        rule_definition = {
            "enabled": True,
            "mustContain": must_contain,
            "mustNotContain": "",
            "useRegex": True,
            "episodeFilter": episode_filter,
            "smartFilter": True,
            "previouslyMatchedEpisodes": [],
            "affectedFeeds": [],
            "ignoreDays": 0,
            "lastMatch": "",
            "addPaused": False,
            "assignedCategory": "tv",
            "savePath": save_path
        }
        
        rule_name = f"{show_title}_{quality}"
        if season:
            rule_name += f"_S{season}"
        if episode:
            rule_name += f"_E{episode}"
        
        logger.info(f"[TV_RULE_CREATE] Creating rule with name: '{rule_name}'")
        logger.info(f"[TV_RULE_CREATE] Show title: '{show_title}', Quality: '{quality}', Season: '{season}'")
        
        return self.create_auto_download_rule(rule_name, rule_definition)
    
    def get_auto_download_rules(self) -> List[Dict]:
        """Get all auto-download rules."""
        try:
            logger.info("[RSS_RULES] Fetching RSS rules from qBittorrent...")
            rules = self.client.rss_rules()
            logger.info(f"[RSS_RULES] Raw response type: {type(rules)}")
            logger.info(f"[RSS_RULES] Raw response: {rules}")
            
            if rules:
                logger.info(f"[RSS_RULES] Successfully retrieved {len(rules)} rules")
                
                # Ensure we return a list that can be sliced
                if isinstance(rules, (list, tuple)):
                    return list(rules)  # Convert to list to ensure it's sliceable
                elif hasattr(rules, '__iter__'):
                    # If it's an iterable but not a list/tuple, convert it
                    try:
                        rules_list = list(rules)
                        logger.info(f"[RSS_RULES] Converted iterable to list with {len(rules_list)} items")
                        return rules_list
                    except Exception as convert_error:
                        logger.warning(f"[RSS_RULES] Could not convert rules to list: {convert_error}")
                        return [rules] if rules else []
                else:
                    # If it's a single object, wrap it in a list
                    logger.info("[RSS_RULES] Rules is a single object, wrapping in list")
                    return [rules] if rules else []
            else:
                logger.info("[RSS_RULES] No rules found or empty response")
                return []
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
    
    def rule_exists(self, rule_name: str) -> bool:
        """Check if a rule already exists by exact rule name."""
        try:
            rules = self.get_auto_download_rules()
            
            # Debug logging - print all rule names and structure
            logger.info(f"[RULE_CHECK] Looking for rule: '{rule_name}'")
            logger.info(f"[RULE_CHECK] Found {len(rules)} total rules")
            
            if not rules:
                logger.info("[RULE_CHECK] No rules found")
                return False
            
            # Log the first rule structure to understand the API response format
            if rules:
                first_rule = rules[0]
                logger.info(f"[RULE_CHECK] First rule structure: {first_rule}")
                logger.info(f"[RULE_CHECK] First rule keys: {list(first_rule.keys()) if hasattr(first_rule, 'keys') else 'No keys attribute'}")
            
            # Check each rule - try different possible key names
            for i, rule in enumerate(rules):
                # Try different possible key names for the rule name
                rule_name_value = None
                if hasattr(rule, 'name'):
                    rule_name_value = rule.name
                elif hasattr(rule, 'ruleName'):
                    rule_name_value = rule.ruleName
                elif isinstance(rule, dict):
                    rule_name_value = rule.get('name') or rule.get('ruleName')
                else:
                    # If it's a string or other type, use it directly
                    rule_name_value = str(rule)
                
                logger.info(f"[RULE_CHECK] Rule {i}: '{rule_name_value}' (type: {type(rule)})")
                
                if rule_name_value == rule_name:
                    logger.info(f"[RULE_CHECK] ✅ Found matching rule: '{rule_name}'")
                    return True
            
            logger.info(f"[RULE_CHECK] ❌ No matching rule found for: '{rule_name}'")
            return False
            
        except Exception as e:
            logger.error(f"Error checking if rule exists: {e}")
            return False
    
    def rule_exists_by_title_and_quality(self, title: str, quality: str) -> bool:
        """Check if a rule already exists for a specific title and quality combination."""
        try:
            rules = self.get_auto_download_rules()
            
            logger.info(f"[RULE_CHECK_TITLE] Looking for rule with title: '{title}' and quality: '{quality}'")
            logger.info(f"[RULE_CHECK_TITLE] Found {len(rules)} total rules")
            
            if not rules:
                logger.info("[RULE_CHECK_TITLE] No rules found")
                return False
            
            # Check each rule for title and quality match
            for i, rule in enumerate(rules):
                rule_name_value = None
                if hasattr(rule, 'name'):
                    rule_name_value = rule.name
                elif hasattr(rule, 'ruleName'):
                    rule_name_value = rule.ruleName
                elif isinstance(rule, dict):
                    rule_name_value = rule.get('name') or rule.get('ruleName')
                else:
                    rule_name_value = str(rule)
                
                if rule_name_value:
                    # Check if rule name contains the title and quality
                    # Rule names follow pattern: Auto_Title_Quality or Auto_Title_Quality_S01
                    rule_lower = rule_name_value.lower()
                    title_lower = title.lower()
                    quality_lower = quality.lower()
                    
                    # Check if rule contains both title and quality
                    if title_lower in rule_lower and quality_lower in rule_lower:
                        logger.info(f"[RULE_CHECK_TITLE] ✅ Found existing rule: '{rule_name_value}' for '{title}' with quality '{quality}'")
                        return True
            
            logger.info(f"[RULE_CHECK_TITLE] ❌ No existing rule found for '{title}' with quality '{quality}'")
            return False
            
        except Exception as e:
            logger.error(f"Error checking if rule exists by title and quality: {e}")
            return False
    
    def rule_exists_by_title(self, title: str) -> bool:
        """Check if ANY rule exists for a specific title (regardless of quality or season)."""
        try:
            rules = self.get_auto_download_rules()
            
            logger.info(f"[RULE_CHECK_TITLE_ONLY] Looking for ANY rule with title: '{title}'")
            logger.info(f"[RULE_CHECK_TITLE_ONLY] Found {len(rules)} total rules")
            
            if not rules:
                logger.info("[RULE_CHECK_TITLE_ONLY] No rules found")
                return False
            
            # Check each rule for title match
            for i, rule in enumerate(rules):
                rule_name_value = None
                if hasattr(rule, 'name'):
                    rule_name_value = rule.name
                elif hasattr(rule, 'ruleName'):
                    rule_name_value = rule.ruleName
                elif isinstance(rule, dict):
                    rule_name_value = rule.get('name') or rule.get('ruleName')
                else:
                    rule_name_value = str(rule)
                
                if rule_name_value:
                    # Check if rule name contains the title
                    rule_lower = rule_name_value.lower()
                    title_lower = title.lower()
                    
                    # Check if rule contains the title
                    if title_lower in rule_lower:
                        logger.info(f"[RULE_CHECK_TITLE_ONLY] ✅ Found existing rule: '{rule_name_value}' for '{title}'")
                        return True
            
            logger.info(f"[RULE_CHECK_TITLE_ONLY] ❌ No existing rule found for '{title}'")
            return False
            
        except Exception as e:
            logger.error(f"Error checking if rule exists by title: {e}")
            return False
    
    def get_rule_by_title(self, title: str) -> Optional[Dict]:
        """Get rule details for a specific title."""
        try:
            rules = self.get_auto_download_rules()
            
            if not rules:
                return None
            
            # Check each rule for title match
            for rule in rules:
                rule_name_value = None
                if hasattr(rule, 'name'):
                    rule_name_value = rule.name
                elif hasattr(rule, 'ruleName'):
                    rule_name_value = rule.ruleName
                elif isinstance(rule, dict):
                    rule_name_value = rule.get('name') or rule.get('ruleName')
                else:
                    rule_name_value = str(rule)
                
                if rule_name_value:
                    # Check if rule name contains the title
                    rule_lower = rule_name_value.lower()
                    title_lower = title.lower()
                    
                    # Check if rule contains the title
                    if title_lower in rule_lower:
                        logger.info(f"[GET_RULE_BY_TITLE] Found rule: '{rule_name_value}' for '{title}'")
                        return rule
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting rule by title: {e}")
            return None
    
    def delete_rule_by_title(self, title: str) -> bool:
        """Delete rule for a specific title."""
        try:
            rule = self.get_rule_by_title(title)
            if rule:
                rule_name = None
                if hasattr(rule, 'name'):
                    rule_name = rule.name
                elif hasattr(rule, 'ruleName'):
                    rule_name = rule.ruleName
                elif isinstance(rule, dict):
                    rule_name = rule.get('name') or rule.get('ruleName')
                else:
                    rule_name = str(rule)
                
                if rule_name:
                    logger.info(f"[DELETE_RULE_BY_TITLE] Deleting rule: '{rule_name}' for '{title}'")
                    return self.delete_auto_download_rule(rule_name)
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting rule by title: {e}")
            return False

    def test_rss_feeds_working(self) -> bool:
        """Test if RSS feeds are working and have content."""
        try:
            logger.info("[qBittorrent] Testing RSS feeds...")
            
            # Try multiple methods to get RSS feeds
            feeds = None
            items = None
            
            # Method 1: Try rss_items()
            try:
                items = self.client.rss_items()
                logger.info(f"[qBittorrent] rss_items() returned: {type(items)} - {items}")
            except Exception as e:
                logger.warning(f"[qBittorrent] rss_items() failed: {e}")
            
            # Method 2: Try rss_feeds() - this method doesn't exist in qBittorrent API
            # We'll skip this and use only rss_items()
            feeds = None
            
            # Check if we have any feeds
            if not feeds and not items:
                logger.warning("[qBittorrent] No RSS feeds found with any method")
                return False
            
            # Check items if available
            total_items = 0
            if items:
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
            
            # Check feeds if available
            if feeds:
                logger.info(f"[qBittorrent] Found {len(feeds)} RSS feeds")
                for i, feed in enumerate(feeds):
                    if hasattr(feed, 'url'):
                        logger.info(f"[qBittorrent] Feed {i}: {feed.url}")
                    elif isinstance(feed, dict):
                        logger.info(f"[qBittorrent] Feed {i}: {feed.get('url', 'No URL')}")
            
            if total_items > 0 or (feeds and len(feeds) > 0):
                logger.info(f"[qBittorrent] RSS feeds are working with {total_items} items and {len(feeds) if feeds else 0} feeds")
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
            logger.info("[qBittorrent] Refreshing RSS feeds...")
            
            # Try multiple refresh methods
            try:
                self.client.rss_refresh_item()
                logger.info("[qBittorrent] rss_refresh_item() successful")
            except Exception as e:
                logger.warning(f"[qBittorrent] rss_refresh_item() failed: {e}")
            
            # rss_refresh() method doesn't exist in qBittorrent API
            # We'll use only rss_refresh_item()
            
            logger.info("[qBittorrent] RSS feeds refresh attempted")
            return True
            
        except Exception as e:
            logger.error(f"[qBittorrent] Error refreshing RSS feeds: {e}")
            return False
    
    def test_rule_functionality(self, rule_name: str) -> bool:
        """Test if a specific rule is working properly."""
        try:
            logger.info(f"[RULE_TEST] Testing rule functionality for: '{rule_name}'")
            
            # Get the rule details
            rules = self.get_auto_download_rules()
            target_rule = None
            
            for rule in rules:
                rule_name_value = None
                if hasattr(rule, 'name'):
                    rule_name_value = rule.name
                elif hasattr(rule, 'ruleName'):
                    rule_name_value = rule.ruleName
                elif isinstance(rule, dict):
                    rule_name_value = rule.get('name') or rule.get('ruleName')
                
                if rule_name_value == rule_name:
                    target_rule = rule
                    break
            
            if not target_rule:
                logger.error(f"[RULE_TEST] Rule '{rule_name}' not found")
                return False
            
            logger.info(f"[RULE_TEST] Found rule: {target_rule}")
            
            # Check if rule is enabled
            is_enabled = False
            if hasattr(target_rule, 'enabled'):
                is_enabled = target_rule.enabled
            elif isinstance(target_rule, dict):
                is_enabled = target_rule.get('enabled', False)
            
            if not is_enabled:
                logger.warning(f"[RULE_TEST] Rule '{rule_name}' is disabled")
                return False
            
            # Check if rule has affected feeds
            has_feeds = False
            if hasattr(target_rule, 'affectedFeeds'):
                has_feeds = bool(target_rule.affectedFeeds)
            elif isinstance(target_rule, dict):
                has_feeds = bool(target_rule.get('affectedFeeds'))
            
            if not has_feeds:
                logger.warning(f"[RULE_TEST] Rule '{rule_name}' has no affected feeds")
                return False
            
            logger.info(f"[RULE_TEST] Rule '{rule_name}' appears to be properly configured")
            return True
            
        except Exception as e:
            logger.error(f"[RULE_TEST] Error testing rule functionality: {e}")
            return False 