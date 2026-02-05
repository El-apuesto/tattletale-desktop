import requests
import random
from typing import Optional, Dict, List
from ..utils.config import Config
from ..utils.error_handling import retry_with_backoff
import logging

logger = logging.getLogger(__name__)

class ImageAPI:
    """
    Fetches images from various sources for article illustrations.
    """
    
    def __init__(self):
        self.unsplash_access_key = None  # Add to config if needed
        self.pexels_api_key = None      # Add to config if needed
        self.image_cache = {}
    
    def get_satire_image(self, keywords: List[str], category: str = None) -> Optional[Dict]:
        """
        Get a relevant image for satire article.
        
        Args:
            keywords: List of keywords from article
            category: Article category
            
        Returns:
            Image data dictionary or None
        """
        # Try different sources in order of preference
        
        # 1. XKCD comics (best for satire)
        from .xkcd import XKCDAPI
        xkcd_api = XKCDAPI()
        comic = xkcd_api.find_relevant_comic(keywords, category)
        if comic:
            return self._format_xkcd_as_image(comic)
        
        # 2. Unsplash (if API key available)
        if self.unsplash_access_key:
            unsplash_image = self._get_unsplash_image(keywords)
            if unsplash_image:
                return unsplash_image
        
        # 3. Pexels (if API key available)
        if self.pexels_api_key:
            pexels_image = self._get_pexels_image(keywords)
            if pexels_image:
                return pexels_image
        
        # 4. Placeholder/default image
        return self._get_default_image(category)
    
    def _format_xkcd_as_image(self, comic: Dict) -> Dict:
        """Format XKCD comic as standard image data."""
        return {
            'url': comic.get('img', ''),
            'alt_text': comic.get('alt', ''),
            'title': comic.get('title', ''),
            'width': comic.get('width', 500),
            'height': comic.get('height', 400),
            'source': 'xkcd',
            'source_url': f"https://xkcd.com/{comic.get('num', '')}",
            'type': 'comic',
            'license': 'CC BY-NC 2.5'
        }
    
    @retry_with_backoff(max_retries=2, delay=60)
    def _get_unsplash_image(self, keywords: List[str]) -> Optional[Dict]:
        """Get image from Unsplash API."""
        try:
            if not self.unsplash_access_key:
                return None
            
            search_query = ' '.join(keywords[:3])  # Use first 3 keywords
            
            url = "https://api.unsplash.com/search/photos"
            params = {
                'query': search_query,
                'per_page': 1,
                'orientation': 'landscape'
            }
            headers = {
                'Authorization': f'Client-ID {self.unsplash_access_key}'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            if results:
                photo = results[0]
                return {
                    'url': photo['urls']['regular'],
                    'alt_text': photo.get('alt_description', ''),
                    'title': photo.get('description', ''),
                    'width': photo['width'],
                    'height': photo['height'],
                    'source': 'unsplash',
                    'source_url': photo['links']['html'],
                    'type': 'photograph',
                    'license': 'Unsplash License',
                    'photographer': photo['user']['name'],
                    'photographer_url': photo['user']['links']['html']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch Unsplash image: {str(e)}")
            return None
    
    @retry_with_backoff(max_retries=2, delay=60)
    def _get_pexels_image(self, keywords: List[str]) -> Optional[Dict]:
        """Get image from Pexels API."""
        try:
            if not self.pexels_api_key:
                return None
            
            search_query = ' '.join(keywords[:3])
            
            url = "https://api.pexels.com/v1/search"
            params = {
                'query': search_query,
                'per_page': 1,
                'orientation': 'landscape'
            }
            headers = {
                'Authorization': self.pexels_api_key
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            photos = data.get('photos', [])
            
            if photos:
                photo = photos[0]
                return {
                    'url': photo['src']['large'],
                    'alt_text': photo.get('alt', ''),
                    'title': '',  # Pexels doesn't provide titles
                    'width': photo['width'],
                    'height': photo['height'],
                    'source': 'pexels',
                    'source_url': photo['url'],
                    'type': 'photograph',
                    'license': 'Pexels License',
                    'photographer': photo['photographer'],
                    'photographer_url': photo['photographer_url']
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch Pexels image: {str(e)}")
            return None
    
    def _get_default_image(self, category: str = None) -> Dict:
        """Get default/fallback image."""
        default_images = {
            'politics': {
                'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&h=630&fit=crop',
                'alt_text': 'Political satire illustration',
                'title': 'Political Satire',
                'source': 'unsplash',
                'type': 'default'
            },
            'business': {
                'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&h=630&fit=crop',
                'alt_text': 'Business satire illustration',
                'title': 'Business Satire',
                'source': 'unsplash',
                'type': 'default'
            },
            'technology': {
                'url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&h=630&fit=crop',
                'alt_text': 'Technology satire illustration',
                'title': 'Technology Satire',
                'source': 'unsplash',
                'type': 'default'
            }
        }
        
        return default_images.get(category, default_images['politics'])
    
    def download_image(self, image_url: str, filename: str) -> bool:
        """
        Download image to local storage.
        
        Args:
            image_url: URL of image to download
            filename: Local filename to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Create images directory if it doesn't exist
            import os
            os.makedirs('data/images', exist_ok=True)
            
            filepath = f'data/images/{filename}'
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download image {image_url}: {str(e)}")
            return False
    
    def get_image_html(self, image_data: Dict, article_headline: str) -> str:
        """
        Generate HTML for displaying an image with proper attribution.
        
        Args:
            image_data: Image metadata dictionary
            article_headline: Article headline for context
            
        Returns:
            HTML string for image display
        """
        if not image_data:
            return ""
        
        img_url = image_data.get('url', '')
        alt_text = image_data.get('alt_text', '')
        title = image_data.get('title', '')
        source = image_data.get('source', '')
        
        # Basic image tag
        img_html = f'<img src="{img_url}" alt="{alt_text}" title="{title}" class="article-image" />'
        
        # Add attribution based on source
        attribution_html = ""
        
        if source == 'xkcd':
            comic_num = image_data.get('source_url', '').split('/')[-2]
            attribution_html = f'''
            <div class="image-attribution">
                <p><a href="{image_data.get('source_url', '')}" target="_blank" rel="noopener noreferrer">
                    "{title}" - XKCD #{comic_num}
                </a></p>
            </div>
            '''
        elif source == 'unsplash':
            attribution_html = f'''
            <div class="image-attribution">
                <p>Photo by <a href="{image_data.get('photographer_url', '')}" target="_blank" rel="noopener noreferrer">
                    {image_data.get('photographer', 'Unknown')}
                </a> on <a href="https://unsplash.com" target="_blank" rel="noopener noreferrer">Unsplash</a></p>
            </div>
            '''
        elif source == 'pexels':
            attribution_html = f'''
            <div class="image-attribution">
                <p>Photo by <a href="{image_data.get('photographer_url', '')}" target="_blank" rel="noopener noreferrer">
                    {image_data.get('photographer', 'Unknown')}
                </a> on <a href="https://pexels.com" target="_blank" rel="noopener noreferrer">Pexels</a></p>
            </div>
            '''
        
        return f'''
        <div class="article-image-container">
            <figure>
                {img_html}
                {attribution_html}
            </figure>
        </div>
        '''
