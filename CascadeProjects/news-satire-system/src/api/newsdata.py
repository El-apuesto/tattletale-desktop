import requests
import datetime
from typing import List, Dict, Optional
from ..utils.config import Config
from ..utils.error_handling import retry_with_backoff
import logging

logger = logging.getLogger(__name__)

class NewsDataAPI:
    def __init__(self):
        self.api_key = Config.NEWSDATA_API_KEY
        self.base_url = Config.NEWSDATA_BASE_URL
    
    @retry_with_backoff(max_retries=Config.MAX_RETRIES, delay=Config.RETRY_DELAY_SECONDS)
    def fetch_news(self, hours_back: int = 12) -> List[Dict]:
        """
        Fetch news from the previous specified hours.
        
        Args:
            hours_back: Number of hours to look back for news
            
        Returns:
            List of news articles with metadata
        """
        try:
            # Calculate the time threshold
            threshold_time = datetime.datetime.now() - datetime.timedelta(hours=hours_back)
            
            params = {
                'apikey': self.api_key,
                'language': 'en',
                'country': 'us',
                'category': 'politics,business,technology,science,health',
                'size': 50  # Get more articles to filter for quality
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') != 'success':
                raise Exception(f"API returned status: {data.get('status')}")
            
            articles = data.get('results', [])
            
            # Filter articles by time and quality
            filtered_articles = []
            for article in articles:
                if self._is_recent_article(article, threshold_time):
                    if self._passes_quality_filter(article):
                        filtered_articles.append(article)
            
            logger.info(f"Fetched {len(filtered_articles)} quality articles from {len(articles)} total")
            return filtered_articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch news: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {str(e)}")
            raise
    
    def _is_recent_article(self, article: Dict, threshold_time: datetime.datetime) -> bool:
        """Check if article is more recent than threshold time."""
        try:
            pub_date = article.get('pubDate')
            if not pub_date:
                return False
            
            # Parse the publication date
            article_time = datetime.datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
            article_time = article_time.replace(tzinfo=None)  # Remove timezone for comparison
            
            return article_time >= threshold_time
        except Exception as e:
            logger.warning(f"Failed to parse article date: {str(e)}")
            return False
    
    def _passes_quality_filter(self, article: Dict) -> bool:
        """Apply basic quality filters to articles."""
        # Must have title and description
        if not article.get('title') or not article.get('description'):
            return False
        
        # Title must be reasonable length
        title = article.get('title', '')
        if len(title) < 10 or len(title) > 200:
            return False
        
        # Must have content
        if not article.get('content') and not article.get('description'):
            return False
        
        # Skip certain low-quality sources
        excluded_sources = ['clickbait-site.com', 'fake-news.net']
        source_id = article.get('source_id', '')
        if any(excluded in source_id.lower() for excluded in excluded_sources):
            return False
        
        return True
    
    def get_article_by_id(self, article_id: str) -> Optional[Dict]:
        """Fetch a specific article by ID."""
        try:
            params = {
                'apikey': self.api_key,
                'id': article_id
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'success' and data.get('results'):
                return data['results'][0]
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch article {article_id}: {str(e)}")
            return None
