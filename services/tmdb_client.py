import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from config.settings import Settings

logger = logging.getLogger(__name__)

class TMDBClient:
    def __init__(self):
        self.api_key = Settings.TMDB_API_KEY
        self.base_url = Settings.TMDB_BASE_URL
        self.session = requests.Session()
        # Use Bearer token authentication
        self.session.headers['Authorization'] = f'Bearer {self.api_key}'
        self.session.headers['accept'] = 'application/json'
    
    def search_movie(self, query: str) -> List[Dict]:
        """Search for movies by title."""
        try:
            url = f"{self.base_url}/search/movie"
            params = {
                'query': query,
                'include_adult': False,
                'language': 'en-US'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Log the response for inspection
            logger.info(f"[TMDB] Movie search response for '{query}': {data}")
            
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error searching movies: {e}")
            return []
    
    def search_tv_show(self, query: str) -> List[Dict]:
        """Search for TV shows by title."""
        try:
            url = f"{self.base_url}/search/tv"
            params = {
                'query': query,
                'include_adult': False,
                'language': 'en-US'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            # Only log errors, not the full response
            return data.get('results', [])
        except Exception as e:
            logger.error(f"Error searching TV shows: {e}")
            return []
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed information about a movie."""
        try:
            url = f"{self.base_url}/movie/{movie_id}"
            params = {
                'append_to_response': 'release_dates'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Log the response for inspection
            logger.info(f"[TMDB] Movie details response for ID {movie_id}: {data}")
            
            return data
        except Exception as e:
            logger.error(f"Error getting movie details: {e}")
            return None
    
    def get_tv_show_details(self, tv_id: int) -> Optional[Dict]:
        """Get detailed information about a TV show."""
        try:
            url = f"{self.base_url}/tv/{tv_id}"
            params = {
                'append_to_response': 'next_episode_to_air'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Log the response for inspection
            logger.info(f"[TMDB] TV show details response for ID {tv_id}: {data}")
            
            return data
        except Exception as e:
            logger.error(f"Error getting TV show details: {e}")
            return None
    
    def is_show_in_production(self, tv_data: Dict) -> bool:
        """Check if a TV show is in production."""
        in_production = tv_data.get('in_production', False)
        logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' in_production: {in_production}")
        return in_production
    
    def get_last_season_info(self, tv_data: Dict) -> Optional[Dict]:
        """Get information about the last season of a TV show."""
        seasons = tv_data.get('seasons', [])
        if not seasons:
            logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' has no seasons")
            return None
        
        # Sort seasons by season number and get the last one
        sorted_seasons = sorted(seasons, key=lambda x: x.get('season_number', 0))
        last_season = sorted_seasons[-1] if sorted_seasons else None
        
        if last_season:
            season_number = last_season.get('season_number', 0)
            episode_count = last_season.get('episode_count', 0)
            air_date = last_season.get('air_date')
            
            logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' last season: {season_number}, episodes: {episode_count}, air date: {air_date}")
            
            return {
                'season_number': season_number,
                'episode_count': episode_count,
                'air_date': air_date,
                'season_data': last_season
            }
        
        return None
    
    def create_tv_show_regex_pattern(self, tv_data: Dict) -> Optional[str]:
        """Create a regex pattern for a TV show based on last season info."""
        if not self.is_show_in_production(tv_data):
            return None
        
        last_season_info = self.get_last_season_info(tv_data)
        if not last_season_info:
            return None
        
        show_name = tv_data.get('name', 'Unknown')
        season_number = last_season_info['season_number']
        episode_count = last_season_info['episode_count']
        
        # If episode_count is 0, this is the next season to be released
        # Use the current season number (not next season) for the regex pattern
        target_season = season_number
        
        # Escape special characters in show name
        escaped_name = show_name.replace(' ', '\\s+').replace('(', '\\(').replace(')', '\\)')
        
        # Create the regex pattern: ^ShowName\s+S0X\s+E\d{2}.*Quality.*
        season_pattern = f"S{target_season:02d}"
        episode_pattern = "E\\d{2}"  # Match any episode number
        
        # Create the regex pattern with proper format
        regex_pattern = f"^{escaped_name}\\s+{season_pattern}{episode_pattern}"
        
        return regex_pattern
    
    def is_upcoming_movie(self, movie_data: Dict) -> bool:
        """Check if a movie is upcoming (not yet released)."""
        release_date = movie_data.get('release_date')
        if not release_date:
            logger.debug(f"[TMDB] Movie '{movie_data.get('title', 'Unknown')}' has no release date")
            return False
        
        try:
            release_dt = datetime.strptime(release_date, '%Y-%m-%d')
            today = datetime.now()
            is_upcoming = release_dt > today
            logger.debug(f"[TMDB] Movie '{movie_data.get('title', 'Unknown')}' release date: {release_date}, is upcoming: {is_upcoming}")
            return is_upcoming
        except:
            logger.debug(f"[TMDB] Movie '{movie_data.get('title', 'Unknown')}' has invalid release date: {release_date}")
            return False
    
    def is_upcoming_tv_show(self, tv_data: Dict) -> bool:
        """Check if a TV show has upcoming episodes or is still airing."""
        # Check if show is still airing
        status = tv_data.get('status', '').lower()
        logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' status: '{status}'")
        
        if status in ['returning series', 'continuing']:
            logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' is returning/continuing")
            return True
        
        # Check for next episode
        next_episode = tv_data.get('next_episode_to_air')
        if next_episode:
            air_date = next_episode.get('air_date')
            if air_date:
                try:
                    air_dt = datetime.strptime(air_date, '%Y-%m-%d')
                    today = datetime.now()
                    is_upcoming = air_dt > today
                    logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' next episode air date: {air_date}, is upcoming: {is_upcoming}")
                    return is_upcoming
                except:
                    logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' has invalid next episode air date: {air_date}")
                    pass
        
        # Check if show is planned or in production
        if status in ['planned', 'in production', 'post production']:
            logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' is planned/in production")
            return True
            
        logger.debug(f"[TMDB] TV show '{tv_data.get('name', 'Unknown')}' is not upcoming")
        return False
    
    def get_tv_show_status(self, tv_data: Dict) -> str:
        """Get a human-readable status for a TV show."""
        status = tv_data.get('status', '').lower()
        
        status_map = {
            'returning series': '🟢 Returning Series',
            'continuing': '🟢 Continuing',
            'ended': '🔴 Ended',
            'canceled': '🔴 Canceled',
            'planned': '🟡 Planned',
            'in production': '🟡 In Production',
            'post production': '🟡 Post Production'
        }
        
        return status_map.get(status, f'❓ {status.title()}')
    
    def get_upcoming_movies(self, days_ahead: int = 30) -> List[Dict]:
        """Get upcoming movies in the next N days."""
        try:
            url = f"{self.base_url}/movie/upcoming"
            params = {
                'language': 'en-US',
                'region': 'US'
            }
            response = self.session.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            upcoming_movies = []
            today = datetime.now()
            cutoff_date = today + timedelta(days=days_ahead)
            
            for movie in data.get('results', []):
                release_date = movie.get('release_date')
                if release_date:
                    try:
                        release_dt = datetime.strptime(release_date, '%Y-%m-%d')
                        if today <= release_dt <= cutoff_date:
                            upcoming_movies.append(movie)
                    except:
                        continue
            
            return upcoming_movies
        except Exception as e:
            logger.error(f"Error getting upcoming movies: {e}")
            return []
    
    def format_movie_info(self, movie: Dict) -> str:
        """Format movie information for display."""
        title = movie.get('title', 'Unknown')
        release_date = movie.get('release_date', 'Unknown')
        overview = movie.get('overview', 'No overview available')
        
        return f"🎬 **{title}**\n📅 Release: {release_date}\n📝 {overview[:100]}..."
    
    def format_tv_show_info(self, tv_show: Dict) -> str:
        """Format TV show information for display."""
        name = tv_show.get('name', 'Unknown')
        first_air_date = tv_show.get('first_air_date', 'Unknown')
        overview = tv_show.get('overview', 'No overview available')
        
        return f"📺 **{name}**\n📅 First Air: {first_air_date}\n📝 {overview[:100]}..." 