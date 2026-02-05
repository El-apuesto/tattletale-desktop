# API Reference

## Core Classes

### NewsDataAPI

Fetches real news articles from NewsData.io.

#### Methods

##### `fetch_news(hours_back: int = 12) -> List[Dict]`

Fetches news from the previous specified hours.

**Parameters:**
- `hours_back`: Number of hours to look back for news (default: 12)

**Returns:**
- List of news articles with metadata

**Example:**
```python
from src.api.newsdata import NewsDataAPI

api = NewsDataAPI()
articles = api.fetch_news(hours_back=12)
```

##### `get_article_by_id(article_id: str) -> Optional[Dict]`

Fetches a specific article by ID.

**Parameters:**
- `article_id`: Unique article identifier

**Returns:**
- Article data or None if not found

---

### XKCDAPI

Fetches XKCD comics for article integration.

#### Methods

##### `get_latest_comic() -> Optional[Dict]`

Gets the latest XKCD comic.

**Returns:**
- Comic data or None if failed

##### `get_comic_by_number(comic_number: int) -> Optional[Dict]`

Gets a specific XKCD comic by number.

**Parameters:**
- `comic_number`: Comic number to fetch

**Returns:**
- Comic data or None if failed

##### `find_relevant_comic(keywords: List[str], category: str = None) -> Optional[Dict]`

Finds a relevant XKCD comic based on keywords and category.

**Parameters:**
- `keywords`: List of keywords to search for
- `category`: News category for broader matching

**Returns:**
- Relevant comic data or None

##### `get_comic_html(comic: Dict) -> str`

Generates HTML for displaying a comic.

**Parameters:**
- `comic`: Comic data dictionary

**Returns:**
- HTML string for comic display

---

### SatireEngine

Transforms real news into deadpan satire.

#### Methods

##### `transform_article(news_article: Dict) -> Dict`

Transforms a real news article into deadpan satire.

**Parameters:**
- `news_article`: Original news article from NewsData.io

**Returns:**
- Transformed satire article with metadata

**Example:**
```python
from src.generation.satire_engine import SatireEngine

engine = SatireEngine()
satire_article = engine.transform_article(news_article)
```

##### `_calculate_satire_potential(article: Dict) -> float`

Calculates the satirical potential of an article (0-10 scale).

**Parameters:**
- `article`: News article to analyze

**Returns:**
- Satire potential score

---

### QualityController

Verifies articles meet quality standards.

#### Methods

##### `verify_article(article: Dict) -> Tuple[bool, List[str]]`

Verifies article meets all quality control requirements.

**Parameters:**
- `article`: Generated satire article

**Returns:**
- Tuple of (passed, list_of_issues)

**Example:**
```python
from src.generation.quality_control import QualityController

qc = QualityController()
passed, issues = qc.verify_article(article)
if not passed:
    print(f"Issues: {issues}")
```

---

### PublishingScheduler

Manages the 8 AM/8 PM CST publishing schedule.

#### Methods

##### `start_scheduler()`

Starts the publishing scheduler.

##### `run_publishing_cycle(cycle_time: str)`

Runs a complete publishing cycle.

**Parameters:**
- `cycle_time`: The scheduled time for this cycle

##### `run_immediate_cycle()`

Runs an immediate publishing cycle (for testing).

---

### ArchiveManager

Manages article archiving and retrieval.

#### Methods

##### `archive_article(article: Dict) -> str`

Archives an article with full metadata.

**Parameters:**
- `article`: Complete article with all metadata

**Returns:**
- Article ID

##### `get_article_by_id(article_id: str) -> Optional[Dict]`

Retrieves an article by ID.

**Parameters:**
- `article_id`: Unique article identifier

**Returns:**
- Article data or None

##### `search_articles(query: str, category: str = None, date_from: datetime = None, date_to: datetime = None, limit: int = 50) -> List[Dict]`

Searches archived articles.

**Parameters:**
- `query`: Search query
- `category`: Filter by category
- `date_from`: Start date filter
- `date_to`: End date filter
- `limit`: Maximum results

**Returns:**
- List of matching articles

##### `get_related_articles(article: Dict, limit: int = 5) -> List[Dict]`

Finds articles related to the given article.

**Parameters:**
- `article`: Reference article
- `limit`: Maximum related articles

**Returns:**
- List of related articles

---

### MetadataGenerator

Generates SEO, social media, and internal metadata.

#### Methods

##### `generate_seo_metadata(article: Dict) -> Dict`

Generates SEO metadata for an article.

**Parameters:**
- `article`: The satire article

**Returns:**
- Dictionary containing SEO metadata

##### `generate_social_metadata(article: Dict) -> Dict`

Generates social media metadata for different platforms.

**Parameters:**
- `article`: The satire article

**Returns:**
- Dictionary containing social media metadata

##### `generate_internal_metadata(article: Dict) -> Dict`

Generates internal metadata for tagging and organization.

**Parameters:**
- `article`: The satire article

**Returns:**
- Dictionary containing internal metadata

---

### TaggingSystem

Intelligent tagging system for organizing articles.

#### Methods

##### `generate_tags(article: Dict) -> Dict[str, List[str]]`

Generates comprehensive tags for an article.

**Parameters:**
- `article`: Complete article with all metadata

**Returns:**
- Dictionary containing different types of tags

##### `find_related_articles_by_tags(article_tags: Dict[str, List[str]], all_article_tags: List[Dict], limit: int = 5) -> List[Tuple[str, float]]`

Finds related articles based on tag similarity.

**Parameters:**
- `article_tags`: Tags for reference article
- `all_article_tags`: List of tags for all articles
- `limit`: Maximum related articles

**Returns:**
- List of (article_id, similarity_score) tuples

---

## Configuration

### Config Class

Central configuration management.

#### Key Attributes

- `NEWSDATA_API_KEY`: NewsData.io API key
- `PUBLISH_TIMES`: Publishing schedule times
- `SATIRE_THRESHOLD`: Minimum quality score (0-10)
- `DATABASE_URL`: Database connection string
- `HEADLINE_MIN_WORDS`/`HEADLINE_MAX_WORDS`: Headline length limits
- `MAX_RETRIES`: Maximum retry attempts
- `RETRY_DELAY_SECONDS`: Retry delay in seconds

---

## Error Handling

### Custom Exceptions

- `SatireSystemError`: Base exception
- `NewsFetchError`: News fetching failures
- `ComicFetchError`: Comic fetching failures
- `ContentGenerationError`: Content generation failures
- `QualityControlError`: Quality control failures
- `PublishingError`: Publishing failures
- `StorageError`: Storage operation failures

### Decorators

##### `@retry_with_backoff(max_retries=3, delay=60, backoff_factor=2.0)`

Retries functions with exponential backoff.

##### `@handle_api_error`

Handles API errors consistently.

##### `@log_function_call`

Logs function calls for debugging.

---

## Data Structures

### Article Structure

```python
{
    'headline': str,
    'opening_paragraph': str,
    'body_paragraphs': List[str],
    'expert_quotes': List[Dict],
    'category': str,
    'original_article': Dict,
    'satire_score': float,
    'byline': str,
    'timestamp': str,
    'xkcd_comic': Dict,
    'comic_html': str,
    'seo_metadata': Dict,
    'social_metadata': Dict,
    'internal_metadata': Dict,
    'published': bool,
    'publish_date': str,
    'id': str
}
```

### Expert Quote Structure

```python
{
    'expert': str,
    'quote': str,
    'affiliation': str
}
```

### XKCD Comic Structure

```python
{
    'num': int,
    'title': str,
    'img': str,
    'alt': str,
    'width': int,
    'height': int
}
```

---

## Usage Examples

### Complete Workflow

```python
from src.api.newsdata import NewsDataAPI
from src.generation.satire_engine import SatireEngine
from src.generation.quality_control import QualityController
from src.storage.archive import ArchiveManager

# Fetch news
news_api = NewsDataAPI()
news_articles = news_api.fetch_news(hours_back=12)

# Generate satire
engine = SatireEngine()
qc = QualityController()
archive = ArchiveManager()

for news_article in news_articles:
    try:
        # Transform to satire
        satire_article = engine.transform_article(news_article)
        
        # Quality check
        passed, issues = qc.verify_article(satire_article)
        
        if passed:
            # Archive
            article_id = archive.archive_article(satire_article)
            print(f"Published: {satire_article['headline']}")
        else:
            print(f"Failed QC: {issues}")
            
    except Exception as e:
        print(f"Error: {e}")
```

### Custom Quality Control

```python
from src.generation.quality_control import QualityController

qc = QualityController()

# Custom quality check
article = {...}  # Your article
passed, issues = qc.verify_article(article)

if not passed:
    print("Quality issues found:")
    for issue in issues:
        print(f"- {issue}")
```

### Search and Retrieval

```python
from src.storage.archive import ArchiveManager
from datetime import datetime, timedelta

archive = ArchiveManager()

# Search articles
results = archive.search_articles(
    query="CEO layoffs",
    category="business",
    limit=10
)

# Get related articles
article_id = "20231201_0800_1234"
article = archive.get_article_by_id(article_id)
related = archive.get_related_articles(article)

# Historical articles
historical = archive.get_this_day_in_history(years_back=3)
```
