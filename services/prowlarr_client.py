import requests
import logging
import re
from typing import List, Dict, Optional
from config.settings import Settings
import json

logger = logging.getLogger(__name__)

MAX_SIZE_BYTES = 150 * 1024 * 1024 * 1024  # 150GB
MIN_SEEDERS = 1  # Only show torrents with at least this many seeders

MOVIE_CATEGORIES = [2000, 2010, 2030, 2040, 2045, 2050, 2070, 2080]
TV_EPISODE_CATEGORIES = [100032]
TV_BOXSET_CATEGORIES = [100027]

class ProwlarrClient:
    def __init__(self):
        self.api_key = Settings.PROWLARR_API_KEY or ''
        self.base_url = str(Settings.PROWLARR_BASE_URL or '')
        self.session = requests.Session()
        self.session.headers['X-Api-Key'] = self.api_key
        self.session.headers['accept'] = 'application/json'
        self.indexer_ids = '1'  # Default indexer ID
    
    def _extract_title(self, filename: str) -> str:
        """Extract the clean title from a filename by removing metadata."""
        # Remove file extension if present
        filename = re.sub(r'\.[a-z0-9]{2,4}$', '', filename, flags=re.IGNORECASE)

        # Define split keywords — what marks the end of the title
        split_keywords = [
            r'\b\d{4}\b',                   # Year like 2003
            r'\b(720|1080|2160)p\b',        # Resolutions
            r'\b(UHD|HDR|HDR10|DV|SDR)\b',
            r'\b(BluRay|WEB[- ]?DL|HDRip|DVDRip|HDTV|NF|AMZN)\b',
            r'\b(HEVC|H\.?264|H\.?265|x264|x265)\b',
            r'\b(DTS|DDP?|AAC|TrueHD|FLAC)\b',
            r'\b(MA|ATMOS|5\.1|7\.1|2\.0|2\.1|Mono|Stereo)\b',
            r'\b(REMUX|HYBRID|REPACK|EXTENDED|PROPER|UNRATED|LIMITED)\b',
            r'-[A-Za-z0-9]+$',              # Release group
        ]

        pattern = re.compile('|'.join(split_keywords), re.IGNORECASE)

        # Replace underscores and dots with space
        clean = re.sub(r'[._]+', ' ', filename)

        # Split on the first metadata keyword match
        parts = pattern.split(clean, maxsplit=1)
        title = parts[0].strip()

        return title
    
    def _create_search_pattern(self, title: str) -> str:
        """Convert title to dot-separated pattern for duplicate detection."""
        # Replace spaces with dots and clean up
        pattern = re.sub(r'\s+', '.', title.strip())
        # Remove any remaining special characters except dots
        pattern = re.sub(r'[^\w.]', '', pattern)
        return pattern.lower()
    
    def _is_duplicate(self, search_pattern: str, torrent_name: str) -> bool:
        """Check if a torrent is a duplicate based on the search pattern."""
        if not search_pattern or not torrent_name:
            return False
        
        # Convert torrent name to the same format for comparison
        torrent_pattern = self._create_search_pattern(torrent_name)
        
        # Check if search pattern is contained in torrent pattern
        is_duplicate = search_pattern in torrent_pattern
        
        if is_duplicate:
            logger.info(f"[Prowlarr] DUPLICATE DETECTED - Search pattern: '{search_pattern}' found in torrent: '{torrent_name}' (pattern: '{torrent_pattern}')")
        else:
            logger.debug(f"[Prowlarr] No duplicate - Search pattern: '{search_pattern}' not found in torrent: '{torrent_name}' (pattern: '{torrent_pattern}')")
        
        return is_duplicate
    
    def search_torrents(self, query: str, category: str = None, 
                        freeleech_only: bool = True, page: int = 0) -> Dict:
        try:
            # Extract clean title from query
            clean_title = self._extract_title(query)
            search_pattern = self._create_search_pattern(clean_title)
            
            logger.info(f"[Prowlarr] Original query: {query}")
            logger.info(f"[Prowlarr] Clean title: {clean_title}")
            logger.info(f"[Prowlarr] Search pattern: {search_pattern}")
            
            search_url = f"{self.base_url}/api/v1/search"
            # Get more results from API to account for filtering
            api_limit = 50  # Request more results from API
            results_per_page = int(Settings.RESULTS_PER_PAGE)
            # Determine categories to use
            category_ids = []
            if category == 'movies':
                category_ids = MOVIE_CATEGORIES
            elif category == 'tv_boxsets':
                category_ids = TV_BOXSET_CATEGORIES
            elif category == 'tv_episodes':
                category_ids = TV_EPISODE_CATEGORIES
            params = {
                'query': query,
                'indexerIds': self.indexer_ids,
                'limit': api_limit,  # Request more from API
                'offset': 0,  # Always start from 0, we'll paginate locally
                'type': 'search'
            }
            # Add categories as multiple parameters
            if category_ids:
                params['categories'] = [str(cat_id) for cat_id in category_ids]
            logger.info(f"[Prowlarr] Request URL: {search_url}")
            logger.info(f"[Prowlarr] Request params: {params}")
            response = self.session.get(search_url, params=params)
            logger.info(f"[Prowlarr] Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            return self._format_search_results(data, page, results_per_page, search_pattern)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching Prowlarr: {e}")
            return {
                'torrents': [],
                'total_pages': 0,
                'current_page': page,
                'total_results': 0
            }
    
    def get_torrent_info(self, guid: str) -> Optional[Dict]:
        return None
    
    def get_magnet_link(self, guid: str) -> Optional[str]:
        return guid
    
    def _is_freeleech(self, item: dict) -> bool:
        flags = item.get('indexerFlags', [])
        if isinstance(flags, list) and 'freeleech' in [str(f).lower() for f in flags]:
            return True
        title = str(item.get('title', ''))
        freeleech_indicators = [
            'freeleech', 'fl', 'free', '0%', '0x', 'free leech',
            'free-leech', 'free_leech'
        ]
        title_lower = title.lower()
        return any(indicator in title_lower for indicator in freeleech_indicators)
    
    def _format_search_results(self, data: List[Dict], page: int, results_per_page: int, search_pattern: str = None) -> Dict:
        torrents = []
        # Get existing downloads from qBittorrent for duplicate checking
        existing_torrents = []
        try:
            from services.qbittorrent_client import QBittorrentClient
            qb_client = QBittorrentClient()
            existing_torrents = qb_client.get_all_torrents()
        except Exception as e:
            logger.warning(f"[Prowlarr] Could not get qBittorrent downloads for duplicate check: {e}")
        
        # Process all items from API first
        for item in data:
            try:
                size = item.get('size', 0)
                try:
                    size = int(float(size))
                except Exception:
                    size = 0
                if size >= MAX_SIZE_BYTES:
                    continue  # Skip torrents >= 150GB
                seeders = item.get('seeders', 0)
                leechers = item.get('leechers', 0)
                try:
                    seeders = int(float(seeders))
                except Exception:
                    seeders = 0
                try:
                    leechers = int(float(leechers))
                except Exception:
                    leechers = 0
                if seeders < MIN_SEEDERS:
                    continue  # Skip torrents with too few seeders
                
                # Check for duplicates against qBittorrent downloads if search pattern is provided
                torrent_name = str(item.get('title', ''))
                if existing_torrents:
                    is_duplicate = False
                    # Extract clean title from the search result using shared script
                    clean_search_result = self._extract_title(torrent_name)
                    # Replace spaces with dots for comparison
                    search_result_normalized = clean_search_result.replace(' ', '.').lower()
                    
                    for existing_torrent in existing_torrents:
                        # Extract clean title from existing torrent using shared script
                        clean_existing = self._extract_title(existing_torrent['name'])
                        # Replace spaces with dots for comparison
                        existing_normalized = clean_existing.replace(' ', '.').lower()
                        
                        # Check if the normalized search result is present in existing torrent
                        if search_result_normalized in existing_normalized or existing_normalized in search_result_normalized:
                            is_duplicate = True
                            logger.info(f"[Prowlarr] Skipping duplicate torrent: '{torrent_name}' (matches: '{existing_torrent['name']}')")
                            break
                    
                    if is_duplicate:
                        continue
                
                categories = item.get('categories', [])
                if not isinstance(categories, list):
                    categories = []
                if categories and isinstance(categories[0], int):
                    categories = [{'id': c, 'name': str(c)} for c in categories]
                formatted_torrent = {
                    'id': item.get('guid', item.get('link', '')),
                    'name': torrent_name,
                    'size': self._format_size(size),
                    'seeders': seeders,
                    'leechers': leechers,
                    'category': self._get_category(categories),
                    'freeleech': self._is_freeleech(item),
                    'year': self._extract_year(torrent_name),
                    'quality': self._extract_quality(torrent_name),
                    'resolution': self._extract_resolution(torrent_name),
                    'codec': self._extract_codec(torrent_name),
                    'group': self._extract_group(torrent_name),
                    'magnet_link': item.get('link', ''),
                    'download_url': item.get('downloadUrl', '')
                }
                torrents.append(formatted_torrent)
            except Exception as e:
                logger.error(f"[Prowlarr] Error parsing item: {item}\nException: {e}")
                continue
        
        # Now paginate the filtered results locally
        total_filtered_results = len(torrents)
        start_index = page * results_per_page
        end_index = start_index + results_per_page
        paginated_torrents = torrents[start_index:end_index]
        
        # Calculate total pages based on filtered results
        total_pages = (total_filtered_results + results_per_page - 1) // results_per_page
        
        logger.info(f"[Prowlarr] Processed {len(data)} items from API, filtered to {total_filtered_results} results")
        logger.info(f"[Prowlarr] Page {page}: showing {len(paginated_torrents)} results (start: {start_index}, end: {end_index})")
        logger.info(f"[Prowlarr] Total pages: {total_pages}")
        
        return {
            'torrents': paginated_torrents,
            'total_pages': total_pages,
            'current_page': page,
            'total_results': total_filtered_results
        }
    def _get_category(self, categories: List[Dict]) -> str:
        if not categories:
            return 'unknown'
        for cat in categories:
            if isinstance(cat, dict):
                if cat.get('id') == 2000:
                    return 'movies'
                elif cat.get('id') == 5000:
                    return 'tv'
                elif cat.get('id') == 100027:
                    return 'tv_boxsets'
                elif cat.get('id') == 100032:
                    return 'tv_episodes'
        return 'other'
    def _extract_year(self, title: str) -> Optional[str]:
        import re
        year_match = re.search(r'\((\d{4})\)', title)
        if year_match:
            return year_match.group(1)
        return None
    def _extract_quality(self, title: str) -> Optional[str]:
        quality_patterns = ['BluRay', 'WEB-DL', 'HDRip', 'BRRip', 'DVDRip', 'HDTV']
        title_lower = title.lower()
        for quality in quality_patterns:
            if quality.lower() in title_lower:
                return quality
        return None
    def _extract_resolution(self, title: str) -> Optional[str]:
        import re
        resolution_match = re.search(r'(\d{3,4}p)', title)
        if resolution_match:
            return resolution_match.group(1)
        return None
    def _extract_codec(self, title: str) -> Optional[str]:
        codec_patterns = ['x264', 'x265', 'H.264', 'H.265', 'AVC', 'HEVC']
        title_lower = title.lower()
        for codec in codec_patterns:
            if codec.lower() in title_lower:
                return codec
        return None
    def _extract_group(self, title: str) -> Optional[str]:
        import re
        group_match = re.search(r'-([A-Za-z0-9]+)$', title)
        if group_match:
            return group_match.group(1)
        return None
    def _format_size(self, size_bytes: int) -> str:
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"
    def search_movies(self, query: str, page: int = 0) -> Dict:
        return self.search_torrents(query, category='movies', freeleech_only=True, page=page)
    def search_tv_episodes(self, query: str, page: int = 0) -> Dict:
        return self.search_torrents(query, category='tv_episodes', freeleech_only=True, page=page)
    def search_tv_boxsets(self, query: str, page: int = 0) -> Dict:
        return self.search_torrents(query, category='tv_boxsets', freeleech_only=True, page=page) 