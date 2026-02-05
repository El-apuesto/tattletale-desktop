# Image Setup Guide

## Option 1: Use XKCD Only (Easiest)

The system already includes XKCD comics. No setup needed.

## Option 2: Add Unsplash API

1. **Sign up for Unsplash:**
   - Go to https://unsplash.com/developers
   - Create a free account
   - Create a new application

2. **Get API Key:**
   - Copy your Access Key from the dashboard

3. **Add to .env file:**
   ```bash
   UNSPLASH_ACCESS_KEY=your_access_key_here
   ```

4. **Update config.py:**
   ```python
   UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
   ```

## Option 3: Add Pexels API

1. **Sign up for Pexels:**
   - Go to https://www.pexels.com/api/
   - Create a free account
   - Request API key

2. **Add to .env file:**
   ```bash
   PEXELS_API_KEY=your_pexels_api_key_here
   ```

3. **Update config.py:**
   ```python
   PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
   ```

## Option 4: Use Local Images

1. **Create images directory:**
   ```bash
   mkdir -p data/images
   ```

2. **Add your images:**
   - Place images in `data/images/`
   - Use naming convention: `category_name.jpg`

3. **Update ImageAPI to use local images:**
   ```python
   def _get_local_image(self, category: str) -> Dict:
       filename = f"data/images/{category}_default.jpg"
       if os.path.exists(filename):
           return {
               'url': f"/static/images/{category}_default.jpg",
               'alt_text': f'{category} satire image',
               'source': 'local'
           }
   ```

## Option 5: Use AI-Generated Images

### DALL-E API (Paid)
```python
def _generate_dalle_image(self, keywords: List[str]) -> Optional[Dict]:
    import openai
    
    prompt = f"Create a satirical illustration about {' '.join(keywords[:3])}. Style: political cartoon, black and white line art."
    
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    
    return {
        'url': response['data'][0]['url'],
        'source': 'dalle',
        'type': 'ai-generated'
    }
```

### Stable Diffusion (Free/Self-hosted)
```python
def _generate_stable_diffusion_image(self, keywords: List[str]) -> Optional[Dict]:
    # Use Automatic1111 or ComfyUI API
    prompt = f"satirical cartoon about {' '.join(keywords[:3])}, black and white, newspaper style"
    
    # API call to your Stable Diffusion instance
    # ...
```

## Integration with Existing System

Update the satire engine to use images:

```python
# In src/generation/satire_engine.py
from ..api.images import ImageAPI

class SatireEngine:
    def __init__(self):
        # ... existing init code
        self.image_api = ImageAPI()
    
    def transform_article(self, news_article: Dict) -> Dict:
        # ... existing transformation code
        
        # Add image
        keywords = self.extract_keywords_from_article(satire_article)
        category = satire_article.get('category', '')
        
        image_data = self.image_api.get_satire_image(keywords, category)
        satire_article['image'] = image_data
        satire_article['image_html'] = self.image_api.get_image_html(
            image_data, satire_article['headline']
        )
        
        return satire_article
```

## Testing Image Integration

```python
# Test the image API
from src.api.images import ImageAPI

image_api = ImageAPI()

# Test with sample keywords
keywords = ['ceo', 'layoffs', 'corporate']
image_data = image_api.get_satire_image(keywords, 'business')

print(f"Image URL: {image_data['url']}")
print(f"Source: {image_data['source']}")
```

## Image Storage and Caching

### Download Images Locally
```python
# Download and cache images
image_data = image_api.get_satire_image(keywords, category)
if image_data:
    filename = f"{category}_{hash(' '.join(keywords))}.jpg"
    image_api.download_image(image_data['url'], filename)
```

### Use CDN for Production
```python
# In production, upload to CDN (AWS S3, Cloudinary, etc.)
def upload_to_cdn(local_path: str, remote_path: str) -> str:
    # Upload logic here
    return f"https://cdn.yourdomain.com/{remote_path}"
```

## Legal Considerations

### Image Licenses
- **XKCD**: CC BY-NC 2.5 (non-commercial)
- **Unsplash**: Free for commercial use
- **Pexels**: Free for commercial use
- **AI-generated**: Check provider terms

### Attribution Requirements
- Always include proper attribution
- Link back to source when required
- Follow license terms carefully

## Performance Optimization

### Image Caching
```python
# Cache image URLs to avoid repeated API calls
image_cache = {}

def get_cached_image(keywords: List[str], category: str) -> Optional[Dict]:
    cache_key = f"{category}_{'_'.join(keywords[:3])}"
    
    if cache_key in image_cache:
        return image_cache[cache_key]
    
    image_data = get_satire_image(keywords, category)
    if image_data:
        image_cache[cache_key] = image_data
    
    return image_data
```

### Image Optimization
- Use WebP format for better compression
- Implement lazy loading
- Serve responsive images
- Use CDN for faster delivery

## Troubleshooting

### Common Issues
1. **API Rate Limits**: Implement backoff and caching
2. **Image Size**: Resize and optimize before serving
3. **Broken Links**: Use fallback images
4. **License Issues**: Double-check attribution requirements

### Debug Mode
```python
# Enable debug logging for image API
logging.getLogger('src.api.images').setLevel(logging.DEBUG)
```

## Security

### Sanitize Image URLs
```python
def sanitize_url(url: str) -> str:
    # Validate and sanitize image URLs
    if not url.startswith(('http://', 'https://')):
        return None
    return url
```

### Prevent Hotlinking
```python
# Implement referrer checking
def validate_referer(referer: str) -> bool:
    allowed_domains = ['yourdomain.com', 'www.yourdomain.com']
    return any(domain in referer for domain in allowed_domains)
```
