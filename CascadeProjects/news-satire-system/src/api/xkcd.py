import requests
import random
from typing import Optional, Dict, List
from ..utils.config import Config
from ..utils.error_handling import retry_with_backoff
import logging

logger = logging.getLogger(__name__)

class XKCDAPI:
    def __init__(self):
        self.base_url = Config.XKCD_BASE_URL
        self.info_url = Config.XKCD_INFO_URL
        self._comic_cache = {}
    
    @retry_with_backoff(max_retries=2, delay=60)  # Less retries for XKCD
    def get_latest_comic(self) -> Optional[Dict]:
        """Get the latest XKCD comic."""
        try:
            response = requests.get(self.info_url, timeout=10)
            response.raise_for_status()
            
            comic = response.json()
            self._cache_comic(comic)
            
            logger.info(f"Fetched latest XKCD comic: {comic.get('title')}")
            return comic
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch latest XKCD comic: {str(e)}")
            return self._get_cached_comic()
        except Exception as e:
            logger.error(f"Unexpected error fetching XKCD comic: {str(e)}")
            return self._get_cached_comic()
    
    def get_comic_by_number(self, comic_number: int) -> Optional[Dict]:
        """Get a specific XKCD comic by number."""
        try:
            url = f"{self.base_url}/{comic_number}/info.0.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            comic = response.json()
            self._cache_comic(comic)
            
            return comic
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch XKCD comic {comic_number}: {str(e)}")
            return self._get_cached_comic()
        except Exception as e:
            logger.error(f"Unexpected error fetching XKCD comic {comic_number}: {str(e)}")
            return self._get_cached_comic()
    
    def get_random_comic(self) -> Optional[Dict]:
        """Get a random XKCD comic."""
        try:
            # First get the latest comic to know the range
            latest = self.get_latest_comic()
            if not latest:
                return None
            
            max_num = latest.get('num', 2500)  # Fallback to 2500 if we can't get latest
            
            # Try a few random numbers to avoid 404s
            for _ in range(3):
                random_num = random.randint(1, max_num)
                comic = self.get_comic_by_number(random_num)
                if comic:
                    return comic
            
            # Fallback to latest if random fails
            return latest
            
        except Exception as e:
            logger.error(f"Failed to get random XKCD comic: {str(e)}")
            return self._get_cached_comic()
    
    def find_relevant_comic(self, keywords: List[str], category: str = None) -> Optional[Dict]:
        """
        Find a relevant XKCD comic based on keywords and category.
        
        Args:
            keywords: List of keywords to search for in comic title/transcript
            category: News category for broader matching
            
        Returns:
            Relevant comic data or None
        """
        # For now, return a random comic
        # In a production system, you might implement:
        # 1. A local database of XKCD comics with full text search
        # 2. Semantic matching using embeddings
        # 3. Category-based heuristics
        
        comic = self.get_random_comic()
        
        if comic and self._is_comic_relevant(comic, keywords, category):
            return comic
        
        # Fallback to latest if no relevant comic found
        return self.get_latest_comic()
    
    def _is_comic_relevant(self, comic: Dict, keywords: List[str], category: str = None) -> bool:
        """Basic relevance check for a comic."""
        if not comic:
            return False
        
        title = comic.get('title', '').lower()
        transcript = comic.get('transcript', '').lower()
        alt_text = comic.get('alt', '').lower()
        
        # Combine all text for searching
        searchable_text = f"{title} {transcript} {alt_text}"
        
        # Check keyword matches
        keyword_matches = sum(1 for keyword in keywords if keyword.lower() in searchable_text)
        
        # Category-based matching
        category_keywords = {
            'politics': ['government', 'politics', 'election', 'vote', 'congress', 'senate'],
            'business': ['business', 'company', 'work', 'job', 'office', 'meeting'],
            'technology': ['tech', 'computer', 'internet', 'software', 'programming', 'code'],
            'science': ['science', 'research', 'study', 'experiment', 'data', 'analysis']
        }
        
        if category and category in category_keywords:
            category_matches = sum(1 for cat_keyword in category_keywords[category] 
                                 if cat_keyword in searchable_text)
            return keyword_matches > 0 or category_matches > 0
        
        return keyword_matches > 0
    
    def _cache_comic(self, comic: Dict):
        """Cache a comic for fallback purposes."""
        if comic and comic.get('num'):
            self._comic_cache[comic['num']] = comic
            
            # Keep cache size manageable
            if len(self._comic_cache) > 50:
                oldest_key = next(iter(self._comic_cache))
                del self._comic_cache[oldest_key]
    
    def _get_cached_comic(self) -> Optional[Dict]:
        """Get a cached comic as fallback."""
        if self._comic_cache:
            # Return a random cached comic
            return random.choice(list(self._comic_cache.values()))
        return None
    
    def get_comic_html(self, comic: Dict) -> str:
        """Generate HTML for displaying a comic."""
        if not comic:
            return ""
        
        image_url = comic.get('img', '')
        title = comic.get('title', 'XKCD Comic')
        alt_text = comic.get('alt', '')
        comic_number = comic.get('num', '')
        comic_url = f"{self.base_url}/{comic_number}/"
        
        return f"""
        <div class="xkcd-comic">
            <a href="{comic_url}" target="_blank" rel="noopener noreferrer">
                <img src="{image_url}" 
                     alt="{alt_text}" 
                     title="{alt_text}"
                     class="comic-image" />
            </a>
            <div class="comic-attribution">
                <p><a href="{comic_url}" target="_blank" rel="noopener noreferrer">
                    "{title}" - XKCD #{comic_number}
                </a></p>
            </div>
        </div>
        """
