import logging
import os
import re
from typing import Optional

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
    
    # Basic validation: should be numbers:letters format
    pattern = r'^\d+:[A-Za-z0-9_-]+$'
    return bool(re.match(pattern, token))

def validate_torrentleech_token(token: str) -> bool:
    """Validate TorrentLeech API token format."""
    if not token:
        return False
    
    # Basic validation: should be alphanumeric
    pattern = r'^[A-Za-z0-9]+$'
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