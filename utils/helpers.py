import logging
import os
import re
from typing import Optional
import urllib.parse
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )

def clean_filename(filename: str) -> str:
    """Clean filename for filesystem compatibility."""
    # Remove or replace invalid characters
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, ' ', filename)
    
    # Replace multiple spaces with single space
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    # Remove leading/trailing spaces
    cleaned = cleaned.strip()
    
    return cleaned

def format_size(size_bytes: int) -> str:
    """Format size in bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_speed(speed_bytes: int) -> str:
    """Format speed in bytes to human readable format."""
    if speed_bytes == 0:
        return "0 B/s"
    
    size_names = ["B/s", "KB/s", "MB/s", "GB/s"]
    i = 0
    while speed_bytes >= 1024 and i < len(size_names) - 1:
        speed_bytes /= 1024.0
        i += 1
    
    return f"{speed_bytes:.1f} {size_names[i]}"

def ensure_directory_exists(path: str) -> bool:
    """Ensure directory exists, create if it doesn't."""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {path}: {e}")
        return False

def validate_telegram_token(token: str) -> bool:
    """Validate Telegram bot token format."""
    if not token:
        return False
    
    # Telegram bot tokens are typically 46 characters long and contain letters, numbers, and colons
    # Format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, token))

def validate_torrentleech_token(token: str) -> bool:
    """Validate TorrentLeech API token format."""
    if not token:
        return False
    
    # TorrentLeech API tokens are typically alphanumeric and 32+ characters
    pattern = r'^[A-Za-z0-9]{32,}$'
    return bool(re.match(pattern, token))

def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."

def parse_torrent_name(name: str) -> dict:
    """Parse torrent name to extract information."""
    # This is a basic parser, can be enhanced based on your torrent naming conventions
    info = {
        'title': name,
        'year': None,
        'quality': None,
        'resolution': None,
        'group': None
    }
    
    # Try to extract year
    year_match = re.search(r'\((\d{4})\)', name)
    if year_match:
        info['year'] = year_match.group(1)
    
    # Try to extract quality
    quality_patterns = ['BluRay', 'WEB-DL', 'HDRip', 'BRRip', 'DVDRip']
    for quality in quality_patterns:
        if quality in name:
            info['quality'] = quality
            break
    
    # Try to extract resolution
    resolution_match = re.search(r'(\d{3,4}p)', name)
    if resolution_match:
        info['resolution'] = resolution_match.group(1)
    
    # Try to extract group (usually at the end)
    group_match = re.search(r'-([A-Za-z0-9]+)$', name)
    if group_match:
        info['group'] = group_match.group(1)
    
    return info 

def extract_torrent_name_from_magnet(magnet_link: str) -> str:
    """
    Extract torrent name from magnet link.
    
    Args:
        magnet_link: The magnet link URL
        
    Returns:
        Extracted torrent name or empty string if not found
    """
    try:
        if not magnet_link.startswith('magnet:'):
            return ""
        
        # Parse the magnet link
        parsed = urlparse(magnet_link)
        query_params = parse_qs(parsed.query)
        
        # Look for the 'dn' (display name) parameter
        if 'dn' in query_params:
            torrent_name = query_params['dn'][0]
            # URL decode the name
            decoded_name = urllib.parse.unquote(torrent_name)
            logger.info(f"Extracted torrent name from magnet: {decoded_name}")
            return decoded_name
        
        # If no 'dn' parameter, try to extract from other parameters
        # Some magnet links use 'xt' (exact topic) which might contain the name
        if 'xt' in query_params:
            xt_value = query_params['xt'][0]
            # Extract name from hash if possible
            if '&' in xt_value:
                parts = xt_value.split('&')
                for part in parts:
                    if part.startswith('dn='):
                        torrent_name = part[3:]  # Remove 'dn=' prefix
                        decoded_name = urllib.parse.unquote(torrent_name)
                        logger.info(f"Extracted torrent name from xt parameter: {decoded_name}")
                        return decoded_name
        
        logger.warning(f"Could not extract torrent name from magnet link: {magnet_link[:100]}...")
        return ""
        
    except Exception as e:
        logger.error(f"Error extracting torrent name from magnet link: {e}")
        return ""

def clean_torrent_name_for_search(torrent_name: str) -> str:
    """
    Clean torrent name for better search matching.
    
    Args:
        torrent_name: Raw torrent name
        
    Returns:
        Cleaned torrent name optimized for search
    """
    try:
        if not torrent_name:
            return ""
        
        # Remove common torrent suffixes and quality indicators
        cleaned = torrent_name
        
        # Remove file extensions
        cleaned = re.sub(r'\.(mkv|mp4|avi|mov|wmv|flv|webm)$', '', cleaned, flags=re.IGNORECASE)
        
        # Remove common quality indicators that might interfere with search
        cleaned = re.sub(r'\s*\[.*?\]\s*', ' ', cleaned)  # Remove [group] tags
        cleaned = re.sub(r'\s*\(.*?\)\s*', ' ', cleaned)  # Remove (year) and other parentheses
        
        # Remove common torrent metadata (but keep group names as they're useful for matching)
        # cleaned = re.sub(r'\s*-\s*[A-Za-z0-9]+$', '', cleaned)  # Remove -GROUP suffix
        # cleaned = re.sub(r'\s*\.\s*[A-Za-z0-9]+$', '', cleaned)  # Remove .GROUP suffix
        
        # Clean up multiple spaces
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        logger.debug(f"Cleaned torrent name: '{torrent_name}' -> '{cleaned}'")
        return cleaned
        
    except Exception as e:
        logger.error(f"Error cleaning torrent name: {e}")
        return torrent_name 